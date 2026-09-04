from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid

from app.utils.security import hash_password

from app.database.mongodb import (
    negotiation_requests_collection,
    freelancers_collection,
    projects_collection
)

from app.schemas.negotiation_schema import (
    NegotiationRequestCreate
)

from app.services.freelancer_service import (
    get_freelancer_by_id
)

from rl_negotiation.engine.negotiation_engine import NegotiationEngine


router = APIRouter(
    prefix="/negotiation",
    tags=["Negotiation"]
)


# ============================================================
# DEMO FREELANCER LOGIN CONFIGURATION
# ============================================================

# Same password for all automatically-created freelancer
# accounts.
#
# NOTE:
# This is for your demo/project only.
# Passwords are stored as hashes in the database.

DEMO_FREELANCER_PASSWORD = "123456"


# ============================================================
# AUTOMATIC FREELANCER EMAIL GENERATOR
# ============================================================

def generate_freelancer_email(freelancer_id: int) -> str:
    """
    Automatically generates a freelancer email
    from the freelancer ID.

    Example:
        freelancer_id = 4
        -> freelancer4@example.com
    """

    return f"freelancer{freelancer_id}@example.com"


# ============================================================
# CREATE NEGOTIATION REQUEST
# ============================================================

@router.post("/request")
def create_negotiation_request(
    request: NegotiationRequestCreate
):

    # --------------------------------------------------------
    # STEP 1: FIND FREELANCER
    # --------------------------------------------------------

    freelancer = get_freelancer_by_id(
        request.freelancer_id
    )

    if freelancer is None:
        raise HTTPException(
            status_code=404,
            detail="Freelancer not found"
        )

    # --------------------------------------------------------
    # STEP 2: CHECK WHETHER FREELANCER ACCOUNT EXISTS
    # --------------------------------------------------------

    existing_freelancer = freelancers_collection.find_one(
        {
            "freelancer_id": request.freelancer_id
        }
    )

    freelancer_account_created = False

    # ========================================================
    # STEP 3: CREATE FREELANCER ACCOUNT IF IT DOESN'T EXIST
    # ========================================================

    if existing_freelancer is None:

        # ----------------------------------------------------
        # Automatically generate email
        # ----------------------------------------------------

        freelancer_email = generate_freelancer_email(
            request.freelancer_id
        )

        # ----------------------------------------------------
        # CHECK WHETHER GENERATED EMAIL ALREADY EXISTS
        # ----------------------------------------------------

        existing_email = freelancers_collection.find_one(
            {
                "email": freelancer_email
            }
        )

        if existing_email:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Generated email {freelancer_email} "
                    f"is already registered."
                )
            )

        # ----------------------------------------------------
        # CREATE FREELANCER ACCOUNT
        # ----------------------------------------------------

        freelancer_account = {

            "freelancer_id":
                freelancer["freelancer_id"],

            "full_name":
                freelancer["name"],

            "email":
                freelancer_email,

            "password":
                hash_password(DEMO_FREELANCER_PASSWORD),

            "role":
                "FREELANCER",

            "title":
                freelancer.get("title"),

            "skills":
                freelancer.get("skills"),

            "hourly_rate":
                freelancer.get("hourly_rate"),

            "country":
                freelancer.get("country"),

            "created_at":
                datetime.utcnow(),

            "created_via":
                "AUTO_NEGOTIATION"
        }

        # ----------------------------------------------------
        # SAVE FREELANCER ACCOUNT
        # ----------------------------------------------------

        freelancers_collection.insert_one(
            freelancer_account
        )

        freelancer_account_created = True

    # ========================================================
    # STEP 4: CHECK DUPLICATE PENDING REQUEST
    # ========================================================

    existing_request = (
        negotiation_requests_collection.find_one(
            {
                "project_id":
                    request.project_id,

                "freelancer_id":
                    request.freelancer_id,

                "status":
                    "PENDING"
            }
        )
    )

    if existing_request:

        return {

            "message":
                "Negotiation request already exists",

            "request_id":
                existing_request["request_id"],

            "freelancer_id":
                existing_request["freelancer_id"],

            "freelancer_name":
                freelancer["name"],

            "status":
                existing_request["status"],

            "freelancer_email":
                generate_freelancer_email(
                    request.freelancer_id
                ),

            "freelancer_account_created":
                freelancer_account_created
        }

    # ========================================================
    # STEP 5: GENERATE NEGOTIATION REQUEST ID
    # ========================================================

    request_id = (
        "NEG-" +
        uuid.uuid4().hex[:8].upper()
    )

    # ========================================================
    # STEP 6: CREATE NEGOTIATION DOCUMENT
    # ========================================================

    now = datetime.utcnow()

    negotiation_document = {

        "request_id":
            request_id,

        "project_id":
            request.project_id,

        "freelancer_id":
            freelancer["freelancer_id"],

        "freelancer":
            freelancer,

        "status":
            "PENDING",

        "created_at":
            now,

        "updated_at":
            now
    }

    # ========================================================
    # STEP 7: SAVE NEGOTIATION REQUEST
    # ========================================================

    negotiation_requests_collection.insert_one(
        negotiation_document
    )

    # ========================================================
    # STEP 8: RETURN RESPONSE
    # ========================================================

    return {

        "message":
            "Negotiation request created successfully",

        "request_id":
            request_id,

        "freelancer_id":
            freelancer["freelancer_id"],

        "freelancer_name":
            freelancer["name"],

        "freelancer_email":
            generate_freelancer_email(
                request.freelancer_id
            ),

        "status":
            "PENDING",

        "freelancer_account_created":
            freelancer_account_created
    }


# ============================================================
# AUTONOMOUS TWO-AGENT NEGOTIATION
# ============================================================

@router.post("/auto-negotiate")
def auto_negotiate(request_id: str):

    # --------------------------------------------------------
    # STEP 1: FIND NEGOTIATION REQUEST
    # --------------------------------------------------------

    negotiation_request = (
        negotiation_requests_collection.find_one(
            {
                "request_id": request_id
            }
        )
    )

    if negotiation_request is None:

        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    # --------------------------------------------------------
    # STEP 2: CHECK WHETHER ALREADY NEGOTIATED
    # --------------------------------------------------------

    if negotiation_request.get("status") in [
        "NEGOTIATION_COMPLETED",
        "NEGOTIATION_FAILED"
    ]:

        return {
            "message":
                "Negotiation already completed",

            "request_id":
                request_id,

            "status":
                negotiation_request.get("status"),

            "negotiation_result":
                negotiation_request.get(
                    "negotiation_result"
                ),

            "negotiation_history":
                negotiation_request.get(
                    "negotiation_history",
                    []
                ),

            "client_decision":
                negotiation_request.get(
                    "client_decision"
                ),

            "freelancer_decision":
                negotiation_request.get(
                    "freelancer_decision"
                )
        }

    # --------------------------------------------------------
    # STEP 3: GET FREELANCER INFORMATION
    # --------------------------------------------------------

    freelancer = negotiation_request.get(
        "freelancer"
    )

    if freelancer is None:

        raise HTTPException(
            status_code=404,
            detail="Freelancer information not found"
        )

    # --------------------------------------------------------
    # STEP 4: NEGOTIATION PARAMETERS
    # --------------------------------------------------------
    #
    # TEMPORARY DEMO VALUES
    #
    # Later we will connect these values to:
    #
    # Project requirements
    #        ↓
    # Requirement analysis
    #        ↓
    # Complexity prediction
    #        ↓
    # Budget / timeline
    #
    # --------------------------------------------------------

    client_budget = 1100.0

    client_desired_days = 18.0

    freelancer_min_price = float(
        freelancer.get("hourly_rate") or 750.0
    )

    freelancer_min_days = 12.0

    freelancer_initial_price = 1200.0

    # --------------------------------------------------------
    # STEP 5: CREATE NEGOTIATION ENGINE
    # --------------------------------------------------------

    try:

        engine = NegotiationEngine(

            client_budget=
                client_budget,

            client_desired_days=
                client_desired_days,

            freelancer_min_price=
                freelancer_min_price,

            freelancer_min_days=
                freelancer_min_days,

            freelancer_initial_price=
                freelancer_initial_price,

            max_rounds=
                10
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to initialize "
                f"negotiation engine: {str(e)}"
            )
        )

    # --------------------------------------------------------
    # STEP 6: RUN AUTONOMOUS NEGOTIATION
    # --------------------------------------------------------

    try:

        result = engine.negotiate()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Autonomous negotiation failed: "
                f"{str(e)}"
            )
        )

    # --------------------------------------------------------
    # STEP 7: DETERMINE NEGOTIATION STATUS
    # --------------------------------------------------------

    if result["agreement"]:

        status = "NEGOTIATION_COMPLETED"

    else:

        status = "NEGOTIATION_FAILED"

    # --------------------------------------------------------
    # STEP 8: PREPARE RESULT
    # --------------------------------------------------------

    negotiation_result = {

        "agreement":
            result["agreement"],

        "final_price":
            result["final_price"],

        "final_timeline_days":
            result["final_timeline_days"],

        "rounds":
            result["rounds"]
    }

    # --------------------------------------------------------
    # STEP 9: SAVE RESULT IN MONGODB
    # --------------------------------------------------------

    negotiation_requests_collection.update_one(

        {
            "request_id":
                request_id
        },

        {
            "$set": {

                "status":
                    status,

                "negotiation_result":
                    negotiation_result,

                "negotiation_history":
                    result["history"],

                # Human decisions happen AFTER
                # autonomous agent negotiation.

                "client_decision":
                    None,

                "freelancer_decision":
                    None,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    # --------------------------------------------------------
    # STEP 10: RETURN RESULT
    # --------------------------------------------------------

    return {

        "message":
            "Autonomous two-agent negotiation completed",

        "request_id":
            request_id,

        "status":
            status,

        "agreement":
            result["agreement"],

        "final_price":
            result["final_price"],

        "final_timeline_days":
            result["final_timeline_days"],

        "rounds":
            result["rounds"],

        "history":
            result["history"],

        # These remain NULL until the
        # human users make their decisions.

        "client_decision":
            None,

        "freelancer_decision":
            None
    }


# ============================================================
# GET PENDING NEGOTIATION REQUESTS FOR FREELANCER
# ============================================================

@router.get("/requests/{freelancer_id}")
def get_freelancer_negotiation_requests(
    freelancer_id: int
):

    # --------------------------------------------------------
    # FIND PENDING REQUESTS
    # --------------------------------------------------------

    requests = list(

        negotiation_requests_collection.find(

            {
                "freelancer_id":
                    freelancer_id,

                "status":
                    "PENDING"
            },

            {
                "_id": 0
            }

        )

    )

    # --------------------------------------------------------
    # RETURN REQUESTS
    # --------------------------------------------------------

    return {

        "freelancer_id":
            freelancer_id,

        "count":
            len(requests),

        "requests":
            requests
    }


# ============================================================
# ACCEPT NEGOTIATION REQUEST
# ============================================================

@router.post("/request/{request_id}/accept")
def accept_negotiation_request(
    request_id: str
):

    # --------------------------------------------------------
    # FIND REQUEST
    # --------------------------------------------------------

    request = negotiation_requests_collection.find_one(
        {
            "request_id":
                request_id
        }
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    # --------------------------------------------------------
    # CHECK CURRENT STATUS
    # --------------------------------------------------------

    if request["status"] != "PENDING":

        raise HTTPException(
            status_code=400,
            detail=(
                "Request cannot be accepted because "
                f"its current status is {request['status']}"
            )
        )

    # --------------------------------------------------------
    # UPDATE REQUEST STATUS
    # --------------------------------------------------------

    negotiation_requests_collection.update_one(

        {
            "request_id":
                request_id,

            "status":
                "PENDING"
        },

        {
            "$set": {

                "status":
                    "ACCEPTED",

                "updated_at":
                    datetime.utcnow()

            }
        }

    )

    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return {

        "message":
            "Negotiation request accepted",

        "request_id":
            request_id,

        "status":
            "ACCEPTED"
    }


# ============================================================
# REJECT NEGOTIATION REQUEST
# ============================================================

@router.post("/request/{request_id}/reject")
def reject_negotiation_request(
    request_id: str
):

    # --------------------------------------------------------
    # FIND REQUEST
    # --------------------------------------------------------

    request = negotiation_requests_collection.find_one(
        {
            "request_id":
                request_id
        }
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    # --------------------------------------------------------
    # CHECK CURRENT STATUS
    # --------------------------------------------------------

    if request["status"] != "PENDING":

        raise HTTPException(
            status_code=400,
            detail=(
                "Request cannot be rejected because "
                f"its current status is {request['status']}"
            )
        )

    # --------------------------------------------------------
    # UPDATE REQUEST STATUS
    # --------------------------------------------------------

    negotiation_requests_collection.update_one(

        {
            "request_id":
                request_id,

            "status":
                "PENDING"
        },

        {
            "$set": {

                "status":
                    "REJECTED",

                "updated_at":
                    datetime.utcnow()

            }
        }

    )

    # --------------------------------------------------------
    # RETURN RESPONSE
    # --------------------------------------------------------

    return {

        "message":
            "Negotiation request rejected",

        "request_id":
            request_id,

        "status":
            "REJECTED"
    }