from datetime import datetime




def client_document(data: dict):


    return {


        "full_name":
        data.get(
            "full_name"
        ),


        "email":
        data.get(
            "email"
        ).lower(),


        "password":
        data.get(
            "password"
        ),


        "role":
        data.get(
            "role",
            "CLIENT"
        ),


        "created_at":
        datetime.utcnow()


    }