from datetime import datetime

from app.database.mongodb import (
    requirement_analysis_collection
)





def save_requirement_analysis(
    project_id: str,
    analysis: dict
):


    requirement_analysis_collection.update_one(

        {
            "project_id": project_id
        },


        {

            "$set":
            {

                "project_id": project_id,

                "analysis": analysis,

                "updated_at":
                datetime.utcnow()

            },


            "$setOnInsert":
            {

                "created_at":
                datetime.utcnow()

            }

        },


        upsert=True

    )








def get_requirement_analysis(
    project_id: str
):


    return requirement_analysis_collection.find_one(

        {
            "project_id": project_id
        }

    )