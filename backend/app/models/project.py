from datetime import datetime




def project_document(
    data: dict
):


    return {


        "client_email":
        data.get(
            "client_email"
        ),



        "title":
        data.get(
            "title"
        ),



        "description":
        data.get(
            "description"
        ),



        "status":
        "submitted",



        "analysis_status":
        "pending",



        "created_at":
        datetime.utcnow()


    }