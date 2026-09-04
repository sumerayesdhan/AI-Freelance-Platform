from fastapi import APIRouter, HTTPException

from app.database.mongodb import freelancers_collection

from app.schemas.freelancer_schema import (
    FreelancerRegister,
    FreelancerLogin
)

from app.utils.security import (
    hash_password,
    verify_password
)

from app.utils.jwt_handler import (
    create_access_token
)

from datetime import datetime


router = APIRouter(
    prefix="/freelancer",
    tags=["Freelancer Authentication"]
)


# ============================================================
# FREELANCER REGISTER
# ============================================================

@router.post("/register")
def register_freelancer(
    freelancer: FreelancerRegister
):

    # --------------------------------------------------------
    # CHECK FREELANCER ID
    # --------------------------------------------------------

    existing_freelancer = freelancers_collection.find_one(
        {
            "freelancer_id":
                freelancer.freelancer_id
        }
    )

    if existing_freelancer:

        raise HTTPException(
            status_code=400,
            detail="Freelancer ID already registered"
        )


    # --------------------------------------------------------
    # CHECK EMAIL
    # --------------------------------------------------------

    existing_email = freelancers_collection.find_one(
        {
            "email":
                freelancer.email
        }
    )

    if existing_email:

        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )


    # --------------------------------------------------------
    # HASH PASSWORD
    # --------------------------------------------------------

    hashed_password = hash_password(
        freelancer.password
    )


    # --------------------------------------------------------
    # CREATE DOCUMENT
    # --------------------------------------------------------

    freelancer_document = {

        "freelancer_id":
            freelancer.freelancer_id,

        "full_name":
            freelancer.full_name,

        "email":
            freelancer.email,

        "password":
            hashed_password,

        "role":
            "FREELANCER",

        "title":
            freelancer.title,

        "skills":
            freelancer.skills,

        "hourly_rate":
            freelancer.hourly_rate,

        "country":
            freelancer.country,

        "created_at":
            datetime.utcnow(),

        "created_via":
            "MANUAL_REGISTER"

    }


    freelancers_collection.insert_one(
        freelancer_document
    )


    return {

        "message":
            "Freelancer registered successfully",

        "freelancer_id":
            freelancer.freelancer_id,

        "email":
            freelancer.email

    }


# ============================================================
# FREELANCER LOGIN
# ============================================================

@router.post("/login")
def login_freelancer(
    freelancer: FreelancerLogin
):

    # --------------------------------------------------------
    # FIND FREELANCER BY EMAIL
    # --------------------------------------------------------

    db_freelancer = freelancers_collection.find_one(
        {
            "email":
                freelancer.email
        }
    )


    if not db_freelancer:

        raise HTTPException(
            status_code=404,
            detail="Freelancer not found"
        )


    # --------------------------------------------------------
    # VERIFY PASSWORD
    # --------------------------------------------------------

    password_match = verify_password(
        freelancer.password,
        db_freelancer["password"]
    )


    if not password_match:

        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )


    # --------------------------------------------------------
    # CREATE JWT TOKEN
    # --------------------------------------------------------

    token = create_access_token(
        {
            "sub":
                db_freelancer["email"],

            "role":
                "FREELANCER",

            "freelancer_id":
                db_freelancer["freelancer_id"]
        }
    )


    # --------------------------------------------------------
    # RETURN LOGIN RESPONSE
    # --------------------------------------------------------

    return {

        "message":
            "Freelancer login successful",

        "access_token":
            token,

        "token_type":
            "bearer",

        "user":
            {
                "freelancer_id":
                    db_freelancer["freelancer_id"],

                "email":
                    db_freelancer["email"],

                "full_name":
                    db_freelancer["full_name"],

                "role":
                    "FREELANCER"
            }

    }