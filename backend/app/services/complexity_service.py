from datetime import datetime

from app.database.mongodb import (
    complexity_analysis_collection
)





def save_complexity_analysis(

    project_id: str,

    analysis: dict

):


    complexity_analysis_collection.update_one(

        {
            "project_id": project_id
        },


        {

            "$set":
            {

                "project_id":
                project_id,


                "analysis":
                analysis,


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








def get_complexity_analysis(

    project_id: str

):


    return complexity_analysis_collection.find_one(

        {
            "project_id":
            project_id
        }

    )