import re

import numpy as np
import pandas as pd

from fastapi import APIRouter, HTTPException

from app.database.mongodb import (
    requirement_analysis_collection,
    complexity_analysis_collection
)

from app.services.freelancer_service import (
    get_freelancer_recommendations
)


router = APIRouter(
    prefix="/freelancers",
    tags=["Freelancer Recommendation"]
)



def make_json_serializable(obj):

    if obj is None:
        return None


    if isinstance(obj, (np.integer,)):
        return int(obj)


    if isinstance(obj, (np.floating,)):
        return float(obj)


    if isinstance(obj, np.ndarray):
        return obj.tolist()


    if isinstance(obj, pd.DataFrame):
        return obj.to_dict(
            orient="records"
        )


    if isinstance(obj, pd.Series):
        return obj.to_dict()



    if isinstance(obj, dict):

        return {
            str(k): make_json_serializable(v)
            for k,v in obj.items()
        }



    if isinstance(obj, (list,tuple)):

        return [
            make_json_serializable(x)
            for x in obj
        ]


    return obj




@router.get("/recommend/{project_id}")
def recommend(project_id:str):


    requirement = requirement_analysis_collection.find_one(
        {
            "project_id":project_id
        }
    )


    complexity = complexity_analysis_collection.find_one(
        {
            "project_id":project_id
        }
    )



    if not requirement:

        raise HTTPException(
            status_code=404,
            detail="Requirement analysis not found"
        )


    if not complexity:

        raise HTTPException(
            status_code=404,
            detail="Complexity analysis not found"
        )



    result = get_freelancer_recommendations(

        requirement["analysis"],

        complexity["analysis"]

    )



    print(
        "BEFORE CONVERSION:",
        type(result)
    )



    result = make_json_serializable(result)



    print(
        "AFTER CONVERSION:",
        type(result)
    )



    return {

        "project_id":project_id,

        "recommendations":result

    }


@router.post("/negotiate/{project_id}")
def negotiate(project_id: str, data: dict):

    requirement_doc = requirement_analysis_collection.find_one(
        {"project_id": project_id}
    )

    if not requirement_doc:
        raise HTTPException(
            status_code=404,
            detail="Requirement analysis not found"
        )

    freelancer = data.get("freelancer") or {}
    requirement = requirement_doc.get("analysis", {})
    features = requirement.get("features", []) or []
    if not isinstance(features, list):
        features = [str(features)]

    def number(value, fallback):
        match = re.search(r"\d+(?:\.\d+)?", str(value or ""))
        return float(match.group()) if match else fallback

    budget_value = requirement.get("budget_range")
    budget_text = str(budget_value or "")
    budget_tokens = re.findall(
        r"\d[\d,]*(?:\.\d+)?\s*[kK]?",
        budget_text
    )
    budget_values = []
    for token in budget_tokens:
        value = float(token.replace(",", "").lower().replace("k", "").strip())
        if "k" in token.lower():
            value *= 1000
        budget_values.append(value)
    if "k" in budget_text.lower() and budget_values and max(budget_values) < 1000:
        budget_values = [value * 1000 for value in budget_values]
    budget_floor = min(budget_values, default=0)
    budget_ceiling = max(budget_values, default=0)

    hourly_rate = number(freelancer.get("hourly_rate"), 1000)
    estimated_hours = max(20, round(number(
        freelancer.get("estimated_hours") or freelancer.get("working_hours"),
        40
    )))
    # Only the selected freelancer's hourly rate influences the fixed price.
    if budget_ceiling > 0:
        client_offer = round(budget_floor, -2)
        rate_adjustment = min(0, round((hourly_rate - 35) * 300))
        final_price = round(max(budget_floor, budget_ceiling + rate_adjustment), -2)
        initial_price = round(final_price + 3000, -2)
    else:
        client_offer = 50000
        rate_adjustment = min(0, round((hourly_rate - 35) * 300))
        final_price = round(max(40000, 50000 + rate_adjustment), -2)
        initial_price = round(final_price + 3000, -2)
    scope = ", ".join(str(feature) for feature in features[:4]) or "the agreed core functionality"
    deadline = requirement.get("deadline") or "the agreed project deadline"
    name = freelancer.get("freelancer_name") or "the selected freelancer"

    messages = [
        {"speaker": "Client", "content": f"I would like to move forward on {scope}. My total project budget is {requirement.get('budget_range') or 'limited'}, so can we keep the full core scope within ₹{client_offer:,.0f}?"},
        {"speaker": "Freelancer", "content": f"I understand the budget constraint. Considering the functionality, testing, and quality checks, my initial fixed project proposal is ₹{initial_price:,.0f}, which is ₹3,000 above the top of your range."},
        {"speaker": "Client", "content": "The essential features are the priority. I can remove optional polish and provide feedback quickly. Could you offer a meaningful reduction without affecting reliability?"},
        {"speaker": "Freelancer", "content": "I can streamline non-essential presentation work, but I need to retain implementation, integration, testing, and bug-fix time. That keeps the result maintainable rather than rushed."},
        {"speaker": "Client", "content": f"If I confirm the requirements today and pay promptly at milestones, would ₹{round(initial_price * 0.84, -2):,.0f} be workable?"},
        {"speaker": "Freelancer", "content": f"Prompt milestone payments help. I can apply a limited discount and commit to the essential scope for ₹{round(initial_price * 0.92, -2):,.0f}, with optional enhancements excluded from this price."},
        {"speaker": "Client", "content": f"That is closer. I need the agreed scope delivered by {deadline}; I can accept a fixed price if the essential functionality and quality checks are explicitly included."},
        {"speaker": "Freelancer", "content": f"Agreed. I will include {scope}, validation, and reasonable defect fixes for a fixed project price of ₹{final_price:,.0f}."},
        {"speaker": "Client", "content": f"₹{final_price:,.0f} is a fair balance for the scope and timeline. I accept the fixed price, with optional features handled separately."},
        {"speaker": "Freelancer", "content": f"I agree to ₹{final_price:,.0f} for the defined scope, payable against milestones. We have reached an agreement."}
    ]

    return {
        "project_id": project_id,
        "messages": messages,
        "final_agreed_price": final_price,
        "estimated_hours": estimated_hours,
        "freelancer_hourly_rate": round(final_price / estimated_hours),
        "final_scope": f"{scope}; implementation, testing, and reasonable defect fixes",
        "deadline": deadline,
        "status": "Agreement Reached",
        "freelancer_name": name
    }