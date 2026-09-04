from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database.mongodb import db

from app.routes.auth import router as auth_router
from app.routes.project import router as project_router
from app.routes.conversation import router as conversation_router
from app.routes.freelancer import router as freelancer_router
from app.routes.freelancer_auth import router as freelancer_auth_router
from app.routes.freelancer_dashboard import (
    router as freelancer_dashboard_router
)
from app.routes.negotiation import router as negotiation_router
from app.utils.auth import get_current_user
from app.services.auth_service import get_client_by_email



app = FastAPI(

    title="AI Freelance Platform API",

    version="1.0.0",

    description=
    """
    AI powered freelance project analysis platform.

    Features:
    - Authentication
    - Project submission
    - AI requirement gathering
    - Requirement understanding
    - Complexity prediction
    """

)



# -----------------------------
# CORS Configuration
# -----------------------------


app.add_middleware(

    CORSMiddleware,

    allow_origins=[

        "http://localhost:5173"

    ],

    allow_credentials=True,

    allow_methods=[

        "*"

    ],

    allow_headers=[

        "*"

    ]

)



# -----------------------------
# Include Routes
# -----------------------------


app.include_router(

    auth_router

)


app.include_router(

    project_router

)


app.include_router(

    conversation_router

)

app.include_router(
    freelancer_router
)

app.include_router(
    freelancer_auth_router
)

app.include_router(
    freelancer_dashboard_router
)

app.include_router(
    negotiation_router
)

# -----------------------------
# Startup Check
# -----------------------------


@app.on_event("startup")
def startup_event():

    try:

        db.command("ping")

        print(
            "MongoDB connection successful"
        )

    except Exception as e:

        print(
            "MongoDB connection failed:",
            e
        )





# -----------------------------
# Global Exception Handler
# -----------------------------


@app.exception_handler(Exception)
async def global_exception_handler(
    request,
    exc
):

    return JSONResponse(

        status_code=500,

        content={

            "message":
            "Internal server error",

            "error":
            str(exc)

        }

    )





# -----------------------------
# Health Check
# -----------------------------


@app.get("/")
def home():

    return {

        "message":
        "AI Freelance Platform Backend Running",

        "status":
        "healthy"

    }





@app.get("/database-test")
def database_test():

    try:

        db.command("ping")


        return {

            "database":
            db.name,

            "status":
            "Connected Successfully"

        }


    except Exception as e:


        return {

            "status":
            "Database connection failed",

            "error":
            str(e)

        }





# -----------------------------
# Protected Dashboard
# -----------------------------


@app.get("/dashboard")
def dashboard(

    current_user: str = Depends(
        get_current_user
    )

):

    client = get_client_by_email(current_user)

    return {


        "message":
        "Welcome to Dashboard",


        "email":
        current_user,

        "full_name":
        client.get("full_name", "") if client else ""

    }