from fastapi import APIRouter, HTTPException

from app.schemas.client_schema import (
    ClientRegister,
    ClientLogin
)

from app.models.client import (
    client_document
)

from app.utils.security import (
    hash_password,
    verify_password
)

from app.utils.jwt_handler import (
    create_access_token
)

from app.services.auth_service import (
    get_client_by_email,
    create_client
)



router = APIRouter(

    prefix="/auth",

    tags=["Authentication"]

)





# ==========================
# REGISTER
# ==========================


@router.post("/register")
def register(
    client: ClientRegister
):


    existing_client = get_client_by_email(

        client.email

    )


    if existing_client:

        raise HTTPException(

            status_code=400,

            detail="Email already registered"

        )



    client_data = client.model_dump()



    client_data["password"] = hash_password(

        client_data["password"]

    )



    document = client_document(

        client_data

    )



    result = create_client(

        document

    )



    return {


        "message":
        "Client registered successfully",


        "client_id":
        str(result.inserted_id),


        "email":
        client.email

    }







# ==========================
# LOGIN
# ==========================


@router.post("/login")
def login(
    client: ClientLogin
):

    selected_role = (client.role or "client").lower()

    if (
        selected_role == "freelancer"
        and client.email.lower() == "freelancer@demo.com"
        and client.password == "freelancer123"
    ):
        token = create_access_token(
            {
                "sub": client.email.lower(),
                "role": "freelancer"
            }
        )
        return {
            "message": "Freelancer demo login successful",
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": client.email.lower(),
                "role": "freelancer",
                "full_name": "Freelancer"
            }
        }


    if selected_role == "freelancer":
        raise HTTPException(
            status_code=403,
            detail="Freelancer account not found"
        )


    db_client = get_client_by_email(

        client.email

    )



    if not db_client:


        raise HTTPException(

            status_code=404,

            detail="Client not found"

        )




    password_match = verify_password(

        client.password,

        db_client["password"]

    )



    if not password_match:


        raise HTTPException(

            status_code=401,

            detail="Invalid password"

        )




    token = create_access_token(

        {

            "sub":
            db_client["email"],

            "role":
            "client"

        }

    )



    return {


        "message":
        "Login successful",


        "access_token":
        token,


        "token_type":
        "bearer",


        "user":

        {

            "email":
            db_client["email"],

            "role":
            "client",

            "full_name":
            db_client.get("full_name", "Client")

        }

    }