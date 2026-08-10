from datetime import datetime

from app.database.mongodb import conversations_collection



def save_conversation(
    project_id: str,
    messages: list,
    completed: bool = False
):

    conversations_collection.update_one(

        {
            "project_id": project_id
        },

        {

            "$set":
            {

                "messages": messages,

                "completed": completed,

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





def get_conversation(project_id: str):


    conversation = conversations_collection.find_one(

        {
            "project_id": project_id
        }

    )


    if conversation:

        return conversation.get(

            "messages",

            []

        )


    return []






def get_conversation_document(project_id: str):


    return conversations_collection.find_one(

        {
            "project_id": project_id
        }

    )






def mark_conversation_completed(project_id: str):


    conversations_collection.update_one(

        {
            "project_id": project_id
        },


        {

            "$set":
            {

                "completed": True,

                "updated_at":
                datetime.utcnow()

            }

        }

    )