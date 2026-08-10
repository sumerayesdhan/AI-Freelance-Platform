from bson import ObjectId
from bson.errors import InvalidId

from app.database.mongodb import (
    projects_collection
)





def create_project(
    document: dict
):

    return projects_collection.insert_one(

        document

    )







def get_client_projects(
    email: str
):


    return list(

        projects_collection.find(

            {
                "client_email":
                email
            }

        )

    )







def get_project_by_id(
    project_id: str
):


    try:

        project = projects_collection.find_one(

            {
                "_id":
                ObjectId(project_id)
            }

        )


        return project



    except InvalidId:


        return None







def update_project_status(

    project_id: str,

    status: str

):


    try:


        return projects_collection.update_one(

            {
                "_id":
                ObjectId(project_id)
            },


            {

                "$set":
                {

                    "status":
                    status

                }

            }

        )


    except InvalidId:


        return None