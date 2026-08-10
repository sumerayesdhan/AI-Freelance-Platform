from fastapi import APIRouter, HTTPException


from app.agents.requirement_understanding import (
    understand_requirement
)


from app.agents.requirement_gathering import (
    gather_requirement
)


from app.agents.complexity_prediction import (
    predict_complexity
)



from app.services.conversation_service import (

    get_conversation,

    save_conversation,

    mark_conversation_completed,

    get_conversation_document

)



from app.services.requirement_service import (

    save_requirement_analysis

)



from app.services.complexity_service import (

    save_complexity_analysis

)



from app.database.mongodb import (

    requirement_analysis_collection,

    complexity_analysis_collection

)




router = APIRouter(

    prefix="/conversation",

    tags=["AI Requirement Agent"]

)





# =====================================
# AI CHAT MESSAGE
# =====================================


@router.post("/message")
def chat(data: dict):


    if (

        "project_id" not in data

        or

        "message" not in data

    ):


        raise HTTPException(

            status_code=400,

            detail="project_id and message required"

        )





    project_id = data["project_id"]




    user_message = {


        "role":"user",

        "content":data["message"]


    }





    messages = get_conversation(

        project_id

    )





    messages.append(

        user_message

    )






    ai_response = gather_requirement(

        messages

    )






    assistant_message = {


        "role":"assistant",

        "content":ai_response


    }





    messages.append(

        assistant_message

    )






    completed = (

        "REQUIREMENT_COMPLETE"

        in ai_response.upper()

    )






    save_conversation(

        project_id,

        messages,

        completed

    )







    if completed:


        mark_conversation_completed(

            project_id

        )







    return {


        "response":

        ai_response,


        "conversation":

        messages,


        "completed":

        completed

    }








# =====================================
# GENERATE REQUIREMENT + COMPLEXITY
# =====================================



@router.get("/analysis/{project_id}")
def generate_analysis(project_id: str):


    # Check conversation exists


    conversation_doc = get_conversation_document(

        project_id

    )



    if not conversation_doc:


        raise HTTPException(

            status_code=404,

            detail="Conversation not found"

        )






    # Check requirement completion


    if not conversation_doc.get(

        "completed",

        False

    ):


        raise HTTPException(

            status_code=400,

            detail="Requirement gathering not completed"

        )








    # Check existing requirement analysis


    existing_requirement = requirement_analysis_collection.find_one(

        {

            "project_id": project_id

        }

    )





    # Check existing complexity analysis


    existing_complexity = complexity_analysis_collection.find_one(

        {

            "project_id": project_id

        }

    )








    if existing_requirement and existing_complexity:


        return {


            "requirement_analysis":

            existing_requirement["analysis"],



            "complexity_analysis":

            existing_complexity["analysis"]

        }








    # Get conversation history


    conversation = get_conversation(

        project_id

    )






    # Requirement Understanding Agent


    requirement = understand_requirement(

        conversation

    )






    save_requirement_analysis(

        project_id,

        requirement

    )







    # Complexity Prediction Agent


    complexity = predict_complexity(

        requirement

    )






    save_complexity_analysis(

        project_id,

        complexity

    )







    return {


        "requirement_analysis":

        requirement,



        "complexity_analysis":

        complexity


    }