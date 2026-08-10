from pymongo import MongoClient
from dotenv import load_dotenv
import os


load_dotenv()



# -----------------------------
# Environment Variables
# -----------------------------

MONGO_URI = os.getenv(
    "MONGO_URI"
)


DATABASE_NAME = os.getenv(
    "DATABASE_NAME"
)



if not MONGO_URI:

    raise Exception(
        "MONGO_URI is missing in .env"
    )


if not DATABASE_NAME:

    raise Exception(
        "DATABASE_NAME is missing in .env"
    )




# -----------------------------
# MongoDB Connection
# -----------------------------


try:


    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )


    # Verify connection

    client.admin.command(
        "ping"
    )


    print(
        "MongoDB Connected Successfully"
    )



except Exception as e:


    print(
        "MongoDB Connection Failed:",
        e
    )

    raise e





# Database

db = client[DATABASE_NAME]





# -----------------------------
# Collections
# -----------------------------


clients_collection = (
    db["clients"]
)


projects_collection = (
    db["projects"]
)


predictions_collection = (
    db["predictions"]
)


conversations_collection = (
    db["conversations"]
)


requirement_analysis_collection = (
    db["requirement_analysis"]
)


complexity_analysis_collection = (
    db["complexity_analysis"]
)