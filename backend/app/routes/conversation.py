from datetime import datetime

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
    contract_messages_collection,
    negotiation_requests_collection,
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

    # Validate request
    if (
        "project_id" not in data
        or "message" not in data
    ):
        raise HTTPException(
            status_code=400,
            detail="project_id and message required"
        )

    project_id = data["project_id"]

    user_message = {
        "role": "user",
        "content": data["message"]
    }

    # Get previous conversation
    messages = get_conversation(project_id)

    # Add user's new message
    messages.append(user_message)

    # Generate AI response
    try:
        ai_response = gather_requirement(messages)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI requirement gathering failed: {str(e)}"
        )

    # =====================================
    # HANDLE AI RESPONSE
    # =====================================

    # gather_requirement() may return a dictionary.
    # Convert it into the actual response text.
    if isinstance(ai_response, dict):

        ai_response = (
            ai_response.get("response")
            or ai_response.get("content")
            or ai_response.get("message")
            or ai_response.get("text")
        )

    # Make sure we actually received text
    if not isinstance(ai_response, str):

        raise HTTPException(
            status_code=500,
            detail="AI response format is invalid"
        )

    # =====================================
    # SAVE ASSISTANT MESSAGE
    # =====================================

    assistant_message = {
        "role": "assistant",
        "content": ai_response
    }

    messages.append(assistant_message)

    # =====================================
    # CHECK REQUIREMENT COMPLETION
    # =====================================

    completed = (
        "REQUIREMENT_COMPLETE"
        in ai_response.upper()
    )

    # Save conversation
    save_conversation(
        project_id,
        messages,
        completed
    )

    # Mark completed if requirement gathering is finished
    if completed:

        mark_conversation_completed(
            project_id
        )

    # =====================================
    # RETURN RESPONSE
    # =====================================

    return {
        "response": ai_response,
        "conversation": messages,
        "completed": completed
    }


# =====================================
# CONTRACT WORKSPACE CHAT
# =====================================

def _contract_request(request_id: str):

    request = negotiation_requests_collection.find_one(
        {
            "request_id": request_id
        },
        {
            "_id": 0
        }
    )

    if request is None:
        raise HTTPException(
            status_code=404,
            detail="Negotiation request not found"
        )

    return request


@router.get("/contract/{request_id}")
def get_contract_messages(request_id: str):

    _contract_request(request_id)

    messages = list(
        contract_messages_collection.find(
            {
                "request_id": request_id
            },
            {
                "_id": 0
            }
        ).sort("created_at", 1)
    )

    return {
        "messages": messages
    }


@router.post("/contract/{request_id}")
def add_contract_message(request_id: str, data: dict):

    _contract_request(request_id)

    message = str(data.get("message", "")).strip()
    sender_role = str(data.get("sender_role", "")).strip().upper()

    if not message or sender_role not in {"CLIENT", "FREELANCER"}:
        raise HTTPException(
            status_code=400,
            detail="message and a valid sender_role are required"
        )

    contract_message = {
        "request_id": request_id,
        "message": message,
        "sender_role": sender_role,
        "created_at": datetime.utcnow()
    }

    contract_messages_collection.insert_one(contract_message)

    return {
        "message": "Contract message sent",
        "conversation": {
            **contract_message,
            "created_at": contract_message["created_at"].isoformat()
        }
    }


# =====================================
# GENERATE REQUIREMENT + COMPLEXITY
# =====================================

@router.get("/analysis/{project_id}")
def generate_analysis(project_id: str):

    # -------------------------------------
    # Check conversation exists
    # -------------------------------------

    conversation_doc = get_conversation_document(
        project_id
    )

    if not conversation_doc:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    # -------------------------------------
    # Check existing requirement analysis
    # -------------------------------------

    existing_requirement = (
        requirement_analysis_collection.find_one(
            {
                "project_id": project_id
            }
        )
    )

    # -------------------------------------
    # Check existing complexity analysis
    # -------------------------------------

    existing_complexity = (
        complexity_analysis_collection.find_one(
            {
                "project_id": project_id
            }
        )
    )

    # -------------------------------------
    # Return existing analysis
    # -------------------------------------

    if (
        existing_requirement
        and existing_complexity
    ):

        return {
            "requirement_analysis":
                existing_requirement["analysis"],

            "complexity_analysis":
                existing_complexity["analysis"]
        }

    # -------------------------------------
    # Get conversation history
    # -------------------------------------

    conversation = get_conversation(
        project_id
    )

    if not conversation:

        raise HTTPException(
            status_code=400,
            detail="Conversation has no messages"
        )

    # -------------------------------------
    # Requirement Understanding Agent
    # -------------------------------------

    try:

        requirement = understand_requirement(
            conversation
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Requirement analysis failed: {str(e)}"
        )

    save_requirement_analysis(
        project_id,
        requirement
    )

    # -------------------------------------
    # Complexity Prediction Agent
    # -------------------------------------

    try:

        complexity = predict_complexity(
            requirement
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Complexity prediction failed: {str(e)}"
        )

    save_complexity_analysis(
        project_id,
        complexity
    )

    # -------------------------------------
    # Return analysis
    # -------------------------------------

    return {
        "requirement_analysis": requirement,
        "complexity_analysis": complexity
    }