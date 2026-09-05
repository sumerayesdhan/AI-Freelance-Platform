from fastapi import APIRouter, HTTPException
from datetime import datetime
import uuid
import math
import re

from bson import ObjectId

from app.utils.security import hash_password

from app.database.mongodb import (
    negotiation_requests_collection,
    freelancers_collection,
    projects_collection,
    complexity_analysis_collection,
)

from app.schemas.negotiation_schema import (
    NegotiationRequestCreate
)

from app.services.freelancer_service import (
    get_freelancer_by_id
)

# IMPORTANT:
# Use the RULE-BASED negotiation engine.
# DO NOT import rl_negotiation here.
from rule_based_negotiation.engine.negotiation_engine import (
    NegotiationEngine
)


router = APIRouter(
    prefix="/negotiation",
    tags=["Negotiation"]
)


# ============================================================
# DEMO FREELANCER LOGIN CONFIGURATION
# ============================================================

# Keep this exactly as before.
# This is only for your project demonstration.
DEMO_FREELANCER_PASSWORD = "123456"


# ============================================================
# AUTOMATIC FREELANCER EMAIL
# ============================================================

def generate_freelancer_email(
    freelancer_id: int
) -> str:

    return (
        f"freelancer{freelancer_id}"
        f"@example.com"
    )


# ============================================================
# SAFE FLOAT CONVERSION
# ============================================================

def _to_float(
    value,
    default=None
):

    if value is None:
        return default

    try:

        if isinstance(value, str):

            cleaned = (
                value
                .replace(",", "")
                .replace("₹", "")
                .replace("$", "")
                .strip()
            )

            if not cleaned:
                return default

            value = cleaned

        number = float(value)

        if not math.isfinite(number):
            return default

        return number

    except (
        TypeError,
        ValueError
    ):

        return default


# ============================================================
# OBJECT ID / STRING PROJECT LOOKUP
# ============================================================

def _find_project(
    project_id
):

    # --------------------------------------------------------
    # First try exact stored value.
    # --------------------------------------------------------

    project = projects_collection.find_one(
        {
            "_id": project_id
        }
    )

    if project is not None:
        return project

    # --------------------------------------------------------
    # Then try ObjectId.
    # --------------------------------------------------------

    try:

        if ObjectId.is_valid(
            str(project_id)
        ):

            project = projects_collection.find_one(
                {
                    "_id": ObjectId(
                        str(project_id)
                    )
                }
            )

            if project is not None:
                return project

    except Exception:
        pass

    # --------------------------------------------------------
    # Finally try project_id field.
    # --------------------------------------------------------

    project = projects_collection.find_one(
        {
            "project_id": str(project_id)
        }
    )

    return project


# ============================================================
# FIND COMPLEXITY ANALYSIS
# ============================================================

def _find_complexity_analysis(
    project_id
):

    # --------------------------------------------------------
    # Exact value
    # --------------------------------------------------------

    analysis = complexity_analysis_collection.find_one(
        {
            "project_id": project_id
        }
    )

    if analysis is not None:
        return analysis

    # --------------------------------------------------------
    # String value
    # --------------------------------------------------------

    analysis = complexity_analysis_collection.find_one(
        {
            "project_id": str(project_id)
        }
    )

    if analysis is not None:
        return analysis

    # --------------------------------------------------------
    # ObjectId value
    # --------------------------------------------------------

    try:

        if ObjectId.is_valid(
            str(project_id)
        ):

            analysis = (
                complexity_analysis_collection.find_one(
                    {
                        "project_id":
                            ObjectId(
                                str(project_id)
                            )
                    }
                )
            )

            if analysis is not None:
                return analysis

    except Exception:
        pass

    return None


# ============================================================
# PARSE ESTIMATED DURATION
# ============================================================

def _parse_duration(
    duration
):

    if not duration:
        return (
            None,
            None
        )

    text = str(
        duration
    ).lower().strip()

    # --------------------------------------------------------
    # Months
    # Example:
    # "6-12 months"
    # --------------------------------------------------------

    month_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-to]+\s*"
        r"(\d+(?:\.\d+)?)\s*months?",
        text
    )

    if month_match:

        minimum = float(
            month_match.group(1)
        )

        maximum = float(
            month_match.group(2)
        )

        return (
            minimum * 30,
            maximum * 30
        )

    # --------------------------------------------------------
    # Single month value
    # --------------------------------------------------------

    month_single = re.search(
        r"(\d+(?:\.\d+)?)\s*months?",
        text
    )

    if month_single:

        days = (
            float(
                month_single.group(1)
            )
            * 30
        )

        return (
            days,
            days
        )

    # --------------------------------------------------------
    # Weeks
    # --------------------------------------------------------

    week_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-to]+\s*"
        r"(\d+(?:\.\d+)?)\s*weeks?",
        text
    )

    if week_match:

        minimum = float(
            week_match.group(1)
        )

        maximum = float(
            week_match.group(2)
        )

        return (
            minimum * 7,
            maximum * 7
        )

    # --------------------------------------------------------
    # Days
    # --------------------------------------------------------

    day_match = re.search(
        r"(\d+(?:\.\d+)?)\s*[-to]+\s*"
        r"(\d+(?:\.\d+)?)\s*days?",
        text
    )

    if day_match:

        return (
            float(
                day_match.group(1)
            ),
            float(
                day_match.group(2)
            )
        )

    single_day = re.search(
        r"(\d+(?:\.\d+)?)\s*days?",
        text
    )

    if single_day:

        days = float(
            single_day.group(1)
        )

        return (
            days,
            days
        )

    return (
        None,
        None
    )


# ============================================================
# BUILD REAL NEGOTIATION INPUT
# ============================================================

def _build_negotiation_parameters(
    project,
    complexity_document,
    freelancer
):
    """
    Convert the real MongoDB project,
    complexity analysis and freelancer profile
    into parameters required by NegotiationEngine.

    This follows the same prototype calculation that
    was already tested in negotiation_input_builder.py.
    """

    # ========================================================
    # COMPLEXITY
    # ========================================================

    analysis = {}

    if complexity_document:

        analysis = complexity_document.get(
            "analysis",
            {}
        )

    complexity_level = str(
        analysis.get(
            "complexity_level",
            "Medium"
        )
    ).strip()

    risk_level = str(
        analysis.get(
            "risk_level",
            "Medium"
        )
    ).strip()

    complexity_scores = {
        "low": 1,
        "medium": 2,
        "high": 3,
    }

    risk_scores = {
        "low": 1,
        "medium": 2,
        "high": 3,
    }

    complexity_score = (
        complexity_scores.get(
            complexity_level.lower(),
            2
        )
    )

    risk_score = (
        risk_scores.get(
            risk_level.lower(),
            2
        )
    )

    # ========================================================
    # DURATION
    # ========================================================

    estimated_duration = analysis.get(
        "estimated_duration"
    )

    days_min, days_max = (
        _parse_duration(
            estimated_duration
        )
    )

    # Fallback if complexity analysis does not
    # contain a usable duration.
    if days_min is None:

        days_min = 30.0
        days_max = 90.0

    days_min = max(
        1.0,
        float(days_min)
    )

    days_max = max(
        days_min,
        float(days_max)
    )

    # ========================================================
    # FREELANCER INFORMATION
    # ========================================================

    hourly_rate = _to_float(
        freelancer.get(
            "hourly_rate"
        ),
        30.0
    )

    job_success = _to_float(
        freelancer.get(
            "job_success"
        ),
        0.0
    )

    experience_score = _to_float(
        freelancer.get(
            "experienceScore"
        ),
        1.0
    )

    total_jobs = _to_float(
        freelancer.get(
            "total_jobs"
        ),
        0.0
    )

    hourly_rate = max(
        1.0,
        hourly_rate
    )

    # ========================================================
    # ESTIMATED EFFORT
    # ========================================================

    # Prototype assumption:
    # 8 working hours per estimated day.
    estimated_hours = (
        days_min * 8.0
    )

    # ========================================================
    # BASE PROJECT VALUE
    # ========================================================

    base_project_value = (
        hourly_rate
        *
        estimated_hours
    )

    # ========================================================
    # COMPLEXITY MULTIPLIER
    # ========================================================

    complexity_multipliers = {
        1: 1.00,
        2: 1.15,
        3: 1.35,
    }

    complexity_multiplier = (
        complexity_multipliers.get(
            complexity_score,
            1.15
        )
    )

    # ========================================================
    # RISK MULTIPLIER
    # ========================================================

    risk_multipliers = {
        1: 1.00,
        2: 1.10,
        3: 1.20,
    }

    risk_multiplier = (
        risk_multipliers.get(
            risk_score,
            1.10
        )
    )

    # ========================================================
    # ADJUSTED PROJECT VALUE
    # ========================================================

    adjusted_project_value = (
        base_project_value
        *
        complexity_multiplier
        *
        risk_multiplier
    )

    # ========================================================
    # FREELANCER RESERVATION PRICE
    # ========================================================

    freelancer_min_price = max(
        hourly_rate * 8.0,
        adjusted_project_value * 0.55
    )

    freelancer_preferred_price = max(
        freelancer_min_price,
        adjusted_project_value * 0.85
    )

    # ========================================================
    # CLIENT BUDGET
    # ========================================================

    client_budget = max(
        freelancer_min_price,
        adjusted_project_value * 1.10
    )

    client_target_budget = (
        client_budget * 0.85
    )

    # ========================================================
    # TIMELINE
    # ========================================================

    freelancer_min_days = days_min

    freelancer_preferred_days = (
        days_min + days_max
    ) / 2.0

    client_desired_days = days_min

    client_maximum_days = days_max

    # ========================================================
    # RETURN
    # ========================================================

    return {

        "client_budget":
            round(
                client_budget,
                2
            ),

        "client_target_budget":
            round(
                client_target_budget,
                2
            ),

        "client_desired_days":
            round(
                client_desired_days,
                2
            ),

        "client_maximum_days":
            round(
                client_maximum_days,
                2
            ),

        "freelancer_min_price":
            round(
                freelancer_min_price,
                2
            ),

        "freelancer_preferred_price":
            round(
                freelancer_preferred_price,
                2
            ),

        "freelancer_min_days":
            round(
                freelancer_min_days,
                2
            ),

        "freelancer_preferred_days":
            round(
                freelancer_preferred_days,
                2
            ),

        # Additional information for debugging
        # and MongoDB storage.
        "complexity_level":
            complexity_level,

        "complexity_score":
            complexity_score,

        "risk_level":
            risk_level,

        "risk_score":
            risk_score,

        "estimated_duration":
            estimated_duration,

        "estimated_days_min":
            days_min,

        "estimated_days_max":
            days_max,

        "hourly_rate":
            hourly_rate,

        "job_success":
            job_success,

        "experience_score":
            experience_score,

        "total_jobs":
            total_jobs,

        "estimated_hours":
            round(
                estimated_hours,
                2
            ),

        "base_project_value":
            round(
                base_project_value,
                2
            ),

        "adjusted_project_value":
            round(
                adjusted_project_value,
                2
            ),
    }


# ============================================================
# CONTRACT / TIMELINE AGENT HELPERS
# ============================================================


def _clean_text(value, fallback="Project work"):

    if value is None:
        return fallback

    text = re.sub(
        r"\s+",
        " ",
        str(value)
    ).strip()

    return text if text else fallback



def build_contract_summary(
    project,
    negotiation_result,
    freelancer=None,
    project_reference=None,
):

    project_title = _clean_text(
        project.get("title"),
        "Project"
    )

    project_description = _clean_text(
        project.get("description"),
        "User registration/login, product catalog/listing, search and filter, shopping cart, implementation, testing, and maintenance support."
    )

    freelancer_name = (
        freelancer.get("name")
        if freelancer and freelancer.get("name")
        else "Freelancer"
    )

    freelancer_id = (
        freelancer.get("freelancer_id")
        if freelancer and freelancer.get("freelancer_id") is not None
        else None
    )

    freelancer_email = (
        freelancer.get("email")
        if freelancer and freelancer.get("email")
        else (
            generate_freelancer_email(freelancer_id)
            if freelancer_id is not None
            else "N/A"
        )
    )

    freelancer_profile = {
        "name": freelancer.get("name") if freelancer else "Freelancer",
        "email": freelancer_email,
        "title": freelancer.get("title") if freelancer else None,
        "skills": freelancer.get("skills") if freelancer else [],
        "hourly_rate": freelancer.get("hourly_rate") if freelancer else None,
        "country": freelancer.get("country") if freelancer else None,
        "freelancer_id": freelancer_id,
    }

    final_price = (
        negotiation_result.get(
            "final_price",
            0
        )
        if negotiation_result
        else 0
    )

    timeline_days = (
        negotiation_result.get(
            "final_timeline_days",
            30
        )
        if negotiation_result
        else 30
    )

    scope_keywords = [
        "login",
        "registration",
        "catalog",
        "listing",
        "search",
        "filter",
        "cart",
        "checkout",
        "dashboard",
        "api",
        "testing",
        "deployment",
        "bug",
        "fix",
        "design",
        "auth",
    ]

    description_lower = project_description.lower()
    matched_scope = [
        keyword
        for keyword in scope_keywords
        if keyword in description_lower
    ]

    if matched_scope:
        scope = ", ".join(
            {
                item: True
                for item in matched_scope
            }.keys()
        )
    else:
        scope = (
            "User registration/login, "
            "product catalog/listing, "
            "search and filter, shopping cart, "
            "implementation, testing, and "
            "reasonable defect fixes"
        )

    estimated_hours = max(
        20,
        int(round(float(timeline_days) * 8.0))
    )

    safe_reference = project_reference or "N/A"
    download_filename = f"project-contract-{safe_reference}.txt"

    return {
        "project_title": project_title,
        "project_reference": safe_reference,
        "parties": {
            "client": "Client",
            "freelancer": freelancer_name,
        },
        "freelancer_profile": freelancer_profile,
        "scope": scope,
        "fixed_price": float(final_price),
        "estimated_hours": estimated_hours,
        "timeline_days": int(round(float(timeline_days))),
        "deadline_days": int(round(float(timeline_days))),
        "approvals": {
            "client": "Approved",
            "freelancer": "Approved",
        },
        "status": "Contract ready",
        "download_enabled": True,
        "download_filename": download_filename,
        "note": (
            "This contract reflects the negotiated scope and fixed project price."
        )
    }



def build_timeline_summary(
    project,
    negotiation_result,
    complexity_analysis=None,
):

    total_days = (
        negotiation_result.get(
            "final_timeline_days",
            30
        )
        if negotiation_result
        else 30
    )

    total_days = max(7, int(round(float(total_days))))

    base_phases = [
        {
            "name": "Discovery & planning",
            "weight": 0.20,
            "description": "Requirements review, architecture planning, and milestone alignment.",
        },
        {
            "name": "UX & design",
            "weight": 0.25,
            "description": "UI structure, workflows, and visual design refinement.",
        },
        {
            "name": "Build & integration",
            "weight": 0.35,
            "description": "Core implementation, feature wiring, and system integration.",
        },
        {
            "name": "QA & fixes",
            "weight": 0.20,
            "description": "Testing, bug triage, polish, and final release checklist.",
        },
    ]

    phases = []
    running_day = 1

    for index, phase in enumerate(base_phases):
        days = int(round(total_days * phase["weight"]))
        if index == len(base_phases) - 1:
            days = max(1, total_days - sum(item["days"] for item in phases))

        phase_record = {
            "name": phase["name"],
            "days": days,
            "start_day": running_day,
            "end_day": running_day + days - 1,
            "description": phase["description"],
        }

        phases.append(phase_record)
        running_day += days

    if sum(item["days"] for item in phases) < total_days:
        phases[-1]["days"] += total_days - sum(item["days"] for item in phases)
        phases[-1]["end_day"] = phases[-1]["start_day"] + phases[-1]["days"] - 1

    summary = (
        f"The project is planned across {total_days} days with a phased delivery cycle "
        f"for discovery, implementation, quality review, and final release support."
    )

    return {
        "project_title": _clean_text(project.get("title"), "Project"),
        "total_days": total_days,
        "phases": phases,
        "summary": summary,
    }


# ============================================================
# CREATE NEGOTIATION REQUEST
# ============================================================

@router.post("/request")
def create_negotiation_request(
    request: NegotiationRequestCreate
):

    # ========================================================
    # FIND FREELANCER FROM CSV SERVICE
    # ========================================================

    freelancer = get_freelancer_by_id(
        request.freelancer_id
    )

    if freelancer is None:

        raise HTTPException(
            status_code=404,
            detail="Freelancer not found"
        )

    # ========================================================
    # CHECK MONGODB FREELANCER ACCOUNT
    # ========================================================

    existing_freelancer = (
        freelancers_collection.find_one(
            {
                "freelancer_id":
                    request.freelancer_id
            }
        )
    )

    freelancer_account_created = False

    # ========================================================
    # CREATE DEMO FREELANCER ACCOUNT
    # ========================================================

    if existing_freelancer is None:

        freelancer_email = (
            generate_freelancer_email(
                request.freelancer_id
            )
        )

        existing_email = (
            freelancers_collection.find_one(
                {
                    "email":
                        freelancer_email
                }
            )
        )

        if existing_email:

            raise HTTPException(
                status_code=400,
                detail=(
                    f"Generated email "
                    f"{freelancer_email} "
                    f"is already registered."
                )
            )

        freelancer_account = {

            "freelancer_id":
                freelancer["freelancer_id"],

            "full_name":
                freelancer["name"],

            "email":
                freelancer_email,

            "password":
                hash_password(
                    DEMO_FREELANCER_PASSWORD
                ),

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

            "job_success":
                freelancer.get("job_success"),

            "total_hours":
                freelancer.get("total_hours"),

            "total_jobs":
                freelancer.get("total_jobs"),

            "experienceScore":
                freelancer.get(
                    "experienceScore"
                ),

            "created_at":
                datetime.utcnow(),

            "created_via":
                "AUTO_NEGOTIATION"
        }

        freelancers_collection.insert_one(
            freelancer_account
        )

        freelancer_account_created = True

    # ========================================================
    # CHECK DUPLICATE ACTIVE REQUEST
    # ========================================================

    existing_request = (
        negotiation_requests_collection.find_one(
            {
                "project_id":
                    request.project_id,

                "freelancer_id":
                    request.freelancer_id,

                "status":
                    {
                        "$in": [
                            "PENDING",
                            "NEGOTIATING",
                            "NEGOTIATION_COMPLETED"
                        ]
                    }
            }
        )
    )

    if existing_request:

        return {

            "message":
                "Negotiation request already exists",

            "request_id":
                existing_request[
                    "request_id"
                ],

            "freelancer_id":
                existing_request[
                    "freelancer_id"
                ],

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
    # CREATE REQUEST ID
    # ========================================================

    request_id = (
        "NEG-"
        +
        uuid.uuid4().hex[:8].upper()
    )

    now = datetime.utcnow()

    # ========================================================
    # CREATE DOCUMENT
    # ========================================================

    negotiation_document = {

        "request_id":
            request_id,

        "project_id":
            request.project_id,

        "freelancer_id":
            freelancer[
                "freelancer_id"
            ],

        # Keep snapshot.
        "freelancer":
            freelancer,

        # AI negotiation has not started yet.
        "status":
            "PENDING",

        # Will be filled after AI negotiation.
        "negotiation_result":
            None,

        "negotiation_history":
            [],

        # Human decisions are separate.
        "client_decision":
            None,

        "freelancer_decision":
            None,

        "contract_status":
            "NOT_READY",

        "created_at":
            now,

        "updated_at":
            now
    }

    negotiation_requests_collection.insert_one(
        negotiation_document
    )

    # ========================================================
    # RESPONSE
    # ========================================================

    return {

        "message":
            "Negotiation request created successfully",

        "request_id":
            request_id,

        "freelancer_id":
            freelancer[
                "freelancer_id"
            ],

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
# START AUTONOMOUS NEGOTIATION
# ============================================================

@router.post("/auto-negotiate")
def auto_negotiate(
    request_id: str
):

    # ========================================================
    # FIND REQUEST
    # ========================================================

    negotiation_request = (
        negotiation_requests_collection.find_one(
            {
                "request_id":
                    request_id
            }
        )
    )

    if negotiation_request is None:

        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    # ========================================================
    # ALREADY COMPLETED?
    # ========================================================

    if negotiation_request.get(
        "status"
    ) in [
        "NEGOTIATION_COMPLETED",
        "NEGOTIATION_FAILED",
        "CONTRACT_READY",
        "BOTH_ACCEPTED"
    ]:

        return {

            "message":
                "Negotiation already completed",

            "request_id":
                request_id,

            "status":
                negotiation_request.get(
                    "status"
                ),

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
                ),

            "contract_status":
                negotiation_request.get(
                    "contract_status",
                    "NOT_READY"
                )
        }

    # ========================================================
    # GET PROJECT
    # ========================================================

    project_id = negotiation_request.get(
        "project_id"
    )

    project = _find_project(
        project_id
    )

    if project is None:

        raise HTTPException(
            status_code=404,
            detail=(
                "Project not found for "
                f"project_id={project_id}"
            )
        )

    # ========================================================
    # GET COMPLEXITY ANALYSIS
    # ========================================================

    complexity_document = (
        _find_complexity_analysis(
            project_id
        )
    )

    if complexity_document is None:

        raise HTTPException(
            status_code=400,
            detail=(
                "Complexity analysis not found "
                "for this project. "
                "Run complexity analysis before "
                "starting negotiation."
            )
        )

    # ========================================================
    # GET FREELANCER
    # ========================================================

    freelancer = (
        negotiation_request.get(
            "freelancer"
        )
    )

    if freelancer is None:

        freelancer = (
            freelancers_collection.find_one(
                {
                    "freelancer_id":
                        negotiation_request[
                            "freelancer_id"
                        ]
                },
                {
                    "_id": 0,
                    "password": 0
                }
            )
        )

    if freelancer is None:

        raise HTTPException(
            status_code=404,
            detail="Freelancer information not found"
        )

    # ========================================================
    # BUILD REAL NEGOTIATION PARAMETERS
    # ========================================================

    try:

        parameters = (
            _build_negotiation_parameters(
                project,
                complexity_document,
                freelancer
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to build negotiation "
                f"parameters: {str(e)}"
            )
        )

    # ========================================================
    # MARK NEGOTIATION AS RUNNING
    # ========================================================

    negotiation_requests_collection.update_one(

        {
            "request_id":
                request_id
        },

        {
            "$set": {

                "status":
                    "NEGOTIATING",

                "negotiation_parameters":
                    parameters,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    # ========================================================
    # CREATE RULE-BASED ENGINE
    # ========================================================

    try:

        engine = NegotiationEngine(

            client_budget=
                parameters[
                    "client_budget"
                ],

            client_target_budget=
                parameters[
                    "client_target_budget"
                ],

            client_desired_days=
                parameters[
                    "client_desired_days"
                ],

            client_maximum_days=
                parameters[
                    "client_maximum_days"
                ],

            freelancer_min_price=
                parameters[
                    "freelancer_min_price"
                ],

            freelancer_preferred_price=
                parameters[
                    "freelancer_preferred_price"
                ],

            freelancer_min_days=
                parameters[
                    "freelancer_min_days"
                ],

            freelancer_preferred_days=
                parameters[
                    "freelancer_preferred_days"
                ],

            max_rounds=10
        )

    except Exception as e:

        negotiation_requests_collection.update_one(

            {
                "request_id":
                    request_id
            },

            {
                "$set": {

                    "status":
                        "NEGOTIATION_FAILED",

                    "failure_reason":
                        str(e),

                    "updated_at":
                        datetime.utcnow()
                }
            }
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to initialize "
                f"rule-based negotiation: {str(e)}"
            )
        )

    # ========================================================
    # RUN AUTONOMOUS NEGOTIATION
    # ========================================================

    try:

        result = engine.negotiate()

    except Exception as e:

        negotiation_requests_collection.update_one(

            {
                "request_id":
                    request_id
            },

            {
                "$set": {

                    "status":
                        "NEGOTIATION_FAILED",

                    "failure_reason":
                        str(e),

                    "updated_at":
                        datetime.utcnow()
                }
            }
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Autonomous negotiation failed: "
                f"{str(e)}"
            )
        )

    # ========================================================
    # DETERMINE STATUS
    # ========================================================

    if result["agreement"]:

        status = (
            "NEGOTIATION_COMPLETED"
        )

    else:

        status = (
            "NEGOTIATION_FAILED"
        )

    # ========================================================
    # RESULT
    # ========================================================

    negotiation_result = {

        "agreement":
            result["agreement"],

        "final_price":
            result["final_price"],

        "final_timeline_days":
            result[
                "final_timeline_days"
            ],

        "rounds":
            result["rounds"],

        "failure_reason":
            result.get(
                "failure_reason"
            )
    }

    # ========================================================
    # SAVE RESULT
    # ========================================================

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

                # VERY IMPORTANT:
                # humans have not decided yet.
                "client_decision":
                    None,

                "freelancer_decision":
                    None,

                "contract_status":
                    "NOT_READY",

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    # ========================================================
    # RETURN ONLY FINAL INFORMATION
    # ========================================================

    return {

        "message":
            "Autonomous negotiation completed",

        "request_id":
            request_id,

        "status":
            status,

        "agreement":
            result["agreement"],

        "final_price":
            result["final_price"],

        "final_timeline_days":
            result[
                "final_timeline_days"
            ],

        "rounds":
            result["rounds"],

        # History is returned for development/testing.
        # Frontend can later show only final terms.
        "history":
            result["history"],

        "client_decision":
            None,

        "freelancer_decision":
            None,

        "contract_status":
            "NOT_READY"
    }


# ============================================================
# CONTRACT / TIMELINE AGENT OUTPUTS
# ============================================================

@router.get("/{request_id}/contract")
def get_contract_agent_output(request_id: str):

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

    if negotiation_request.get("status") != "BOTH_ACCEPTED":
        raise HTTPException(
            status_code=409,
            detail="Contract is generated only after both client and freelancer approve the final terms."
        )

    project_id = negotiation_request.get("project_id")
    project = _find_project(project_id)

    freelancer = negotiation_request.get("freelancer") or freelancers_collection.find_one(
        {"freelancer_id": negotiation_request.get("freelancer_id")},
        {"_id": 0, "password": 0},
    )

    return build_contract_summary(
        project=project or {},
        negotiation_result=negotiation_request.get("negotiation_result") or {},
        freelancer=freelancer or {},
        project_reference=str(project_id)[:20] if project_id else "N/A",
    )


@router.get("/{request_id}/timeline")
def get_timeline_agent_output(request_id: str):

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

    if negotiation_request.get("status") != "BOTH_ACCEPTED":
        raise HTTPException(
            status_code=409,
            detail="Timeline is generated only after both client and freelancer approve the final terms."
        )

    project_id = negotiation_request.get("project_id")
    project = _find_project(project_id)

    complexity_document = _find_complexity_analysis(project_id)

    return build_timeline_summary(
        project=project or {},
        negotiation_result=negotiation_request.get("negotiation_result") or {},
        complexity_analysis=complexity_document,
    )


# ============================================================
# GET NEGOTIATION RESULT
# ============================================================

@router.get("/{request_id}")
def get_negotiation(
    request_id: str
):

    negotiation_request = (
        negotiation_requests_collection.find_one(
            {
                "request_id":
                    request_id
            },
            {
                "_id": 0
            }
        )
    )

    if negotiation_request is None:

        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    return negotiation_request


# ============================================================
# GET PENDING REQUESTS FOR FREELANCER
# ============================================================

@router.get("/requests/{freelancer_id}")
def get_freelancer_negotiation_requests(
    freelancer_id: int
):

    # IMPORTANT:
    # This remains for the existing freelancer login flow.
    #
    # However, PENDING means the request exists.
    # The freelancer does NOT start negotiation.
    #
    # The client starts it.

    requests = list(

        negotiation_requests_collection.find(

            {
                "freelancer_id":
                    freelancer_id,

                "status":
                    {
                        "$in": [
                            "PENDING",
                            "NEGOTIATION_COMPLETED"
                        ]
                    }
            },

            {
                "_id": 0
            }
        )
    )

    return {

        "freelancer_id":
            freelancer_id,

        "count":
            len(requests),

        "requests":
            requests
    }


# ============================================================
# HUMAN CLIENT DECISION
# ============================================================

@router.post(
    "/request/{request_id}/client-decision"
)
def client_decision(
    request_id: str,
    decision: str
):

    decision = (
        str(decision)
        .upper()
        .strip()
    )

    if decision not in [
        "ACCEPT",
        "REJECT"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be ACCEPT "
                "or REJECT."
            )
        )

    request = (
        negotiation_requests_collection.find_one(
            {
                "request_id":
                    request_id
            }
        )
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    # Human decision is allowed ONLY after
    # autonomous negotiation completed.
    if request.get(
        "status"
    ) != "NEGOTIATION_COMPLETED":

        raise HTTPException(
            status_code=400,
            detail=(
                "Client can make a decision "
                "only after autonomous "
                "negotiation is completed."
            )
        )

    if not request.get(
        "negotiation_result",
        {}
    ).get(
        "agreement",
        False
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "There is no negotiated agreement "
                "to accept."
            )
        )

    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    if decision == "REJECT":

        negotiation_requests_collection.update_one(

            {
                "request_id":
                    request_id
            },

            {
                "$set": {

                    "client_decision":
                        "REJECT",

                    "status":
                        "REJECTED_BY_CLIENT",

                    "contract_status":
                        "NOT_READY",

                    "updated_at":
                        datetime.utcnow()
                }
            }
        )

        return {

            "message":
                "Client rejected the negotiated terms",

            "request_id":
                request_id,

            "client_decision":
                "REJECT",

            "freelancer_decision":
                request.get(
                    "freelancer_decision"
                ),

            "status":
                "REJECTED_BY_CLIENT",

            "contract_status":
                "NOT_READY"
        }

    # --------------------------------------------------------
    # ACCEPT
    # --------------------------------------------------------

    freelancer_decision_value = (
        request.get(
            "freelancer_decision"
        )
    )

    if (
        freelancer_decision_value
        == "ACCEPT"
    ):

        new_status = (
            "BOTH_ACCEPTED"
        )

        contract_status = (
            "CONTRACT_READY"
        )

    else:

        new_status = (
            "CLIENT_ACCEPTED"
        )

        contract_status = (
            "WAITING_FOR_FREELANCER"
        )

    negotiation_requests_collection.update_one(

        {
            "request_id":
                request_id
        },

        {
            "$set": {

                "client_decision":
                    "ACCEPT",

                "status":
                    new_status,

                "contract_status":
                    contract_status,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return {

        "message":
            "Client accepted the negotiated terms",

        "request_id":
            request_id,

        "client_decision":
            "ACCEPT",

        "freelancer_decision":
            freelancer_decision_value,

        "status":
            new_status,

        "contract_status":
            contract_status
    }


# ============================================================
# HUMAN FREELANCER DECISION
# ============================================================

@router.post(
    "/request/{request_id}/freelancer-decision"
)
def freelancer_decision(
    request_id: str,
    decision: str
):

    decision = (
        str(decision)
        .upper()
        .strip()
    )

    if decision not in [
        "ACCEPT",
        "REJECT"
    ]:

        raise HTTPException(
            status_code=400,
            detail=(
                "Decision must be ACCEPT "
                "or REJECT."
            )
        )

    request = (
        negotiation_requests_collection.find_one(
            {
                "request_id":
                    request_id
            }
        )
    )

    if request is None:

        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    # --------------------------------------------------------
    # Freelancer can decide only after AI negotiation.
    # --------------------------------------------------------

    allowed_statuses = [
        "NEGOTIATION_COMPLETED",
        "CLIENT_ACCEPTED"
    ]

    if request.get(
        "status"
    ) not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Freelancer can make a decision "
                "only after autonomous negotiation "
                "is completed."
            )
        )

    if not request.get(
        "negotiation_result",
        {}
    ).get(
        "agreement",
        False
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "There is no negotiated agreement "
                "to accept."
            )
        )

    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    if decision == "REJECT":

        negotiation_requests_collection.update_one(

            {
                "request_id":
                    request_id
            },

            {
                "$set": {

                    "freelancer_decision":
                        "REJECT",

                    "status":
                        "REJECTED_BY_FREELANCER",

                    "contract_status":
                        "NOT_READY",

                    "updated_at":
                        datetime.utcnow()
                }
            }
        )

        return {

            "message":
                "Freelancer rejected the negotiated terms",

            "request_id":
                request_id,

            "client_decision":
                request.get(
                    "client_decision"
                ),

            "freelancer_decision":
                "REJECT",

            "status":
                "REJECTED_BY_FREELANCER",

            "contract_status":
                "NOT_READY"
        }

    # --------------------------------------------------------
    # ACCEPT
    # --------------------------------------------------------

    client_decision_value = (
        request.get(
            "client_decision"
        )
    )

    if (
        client_decision_value
        == "ACCEPT"
    ):

        new_status = (
            "BOTH_ACCEPTED"
        )

        contract_status = (
            "CONTRACT_READY"
        )

    else:

        new_status = (
            "FREELANCER_ACCEPTED"
        )

        contract_status = (
            "WAITING_FOR_CLIENT"
        )

    negotiation_requests_collection.update_one(

        {
            "request_id":
                request_id
        },

        {
            "$set": {

                "freelancer_decision":
                    "ACCEPT",

                "status":
                    new_status,

                "contract_status":
                    contract_status,

                "updated_at":
                    datetime.utcnow()
            }
        }
    )

    return {

        "message":
            "Freelancer accepted the negotiated terms",

        "request_id":
            request_id,

        "client_decision":
            client_decision_value,

        "freelancer_decision":
            "ACCEPT",

        "status":
            new_status,

        "contract_status":
            contract_status
    }


# ============================================================
# OLD ACCEPT ENDPOINT
# ============================================================
#
# Kept so an old frontend call does not silently behave
# incorrectly.
#
# IMPORTANT:
# It is no longer used for accepting the initial request.
# Human acceptance happens only AFTER negotiation.
# ============================================================

@router.post(
    "/request/{request_id}/accept"
)
def old_accept_endpoint(
    request_id: str
):

    raise HTTPException(
        status_code=400,
        detail=(
            "The negotiation request itself cannot "
            "be accepted. The client must start "
            "the autonomous negotiation first. "
            "After negotiation, use the client-decision "
            "or freelancer-decision endpoint."
        )
    )


# ============================================================
# OLD REJECT ENDPOINT
# ============================================================

@router.post(
    "/request/{request_id}/reject"
)
def old_reject_endpoint(
    request_id: str
):

    raise HTTPException(
        status_code=400,
        detail=(
            "The negotiation request itself cannot "
            "be rejected at this stage. "
            "Use the appropriate human decision "
            "endpoint after autonomous negotiation."
        )
    )