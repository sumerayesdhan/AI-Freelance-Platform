from app.database.mongodb import clients_collection





def get_client_by_email(
    email: str
):


    return clients_collection.find_one(

        {
            "email":
            email.lower()
        }

    )







def create_client(
    document: dict
):


    if "email" in document:

        document["email"] = (
            document["email"]
            .lower()
        )


    return clients_collection.insert_one(

        document

    )