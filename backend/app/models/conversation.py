from datetime import datetime


def conversation_document(
    project_id,
    messages
):

    return {

        "project_id": project_id,

        "messages": messages,

        "completed": False,

        "created_at": datetime.utcnow()

    }