from datetime import date, datetime, timedelta

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.database.mongodb import (
    clients_collection,
    complexity_analysis_collection,
    freelancers_collection,
    negotiation_requests_collection,
    projects_collection,
    requirement_analysis_collection,
)
from app.utils.auth import get_current_user


router = APIRouter(
    prefix="/contract",
    tags=["Contract and Timeline"],
)


def _project(project_id):
    queries = [{"_id": project_id}]
    if ObjectId.is_valid(str(project_id)):
        queries.append({"_id": ObjectId(str(project_id))})
    queries.append({"project_id": str(project_id)})

    for query in queries:
        document = projects_collection.find_one(query)
        if document:
            return document
    return None


def _serialize(value):
    if isinstance(value, ObjectId):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    return value


def _accepted_request(request_id):
    request = negotiation_requests_collection.find_one(
        {"request_id": request_id},
        {"_id": 0},
    )
    if request is None:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    if request.get("status") != "BOTH_ACCEPTED":
        raise HTTPException(
            status_code=403,
            detail="This page is available after both parties accept the terms",
        )
    return request


def _supporting_data(request):
    project = _project(request.get("project_id"))
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    requirement = requirement_analysis_collection.find_one(
        {"project_id": str(request.get("project_id"))},
        {"_id": 0},
    ) or {}
    complexity = complexity_analysis_collection.find_one(
        {"project_id": str(request.get("project_id"))},
        {"_id": 0},
    ) or {}

    freelancer = request.get("freelancer") or freelancers_collection.find_one(
        {"freelancer_id": request.get("freelancer_id")},
        {"_id": 0, "password": 0},
    ) or {}
    client = clients_collection.find_one(
        {"email": project.get("client_email")},
        {"_id": 0, "password": 0},
    ) or {"email": project.get("client_email")}

    return project, requirement.get("analysis", {}), complexity.get("analysis", {}), client, freelancer


def _timeline_items(final_days, features, final_price, phase_states):
    total_days = max(1, int(round(float(final_days or 1))))
    phase_names = ["Planning and requirements", "Design and implementation", "Testing and delivery"]
    weights = [0.2, 0.6, 0.2]
    items = []
    current_day = 0

    for index, (name, weight) in enumerate(zip(phase_names, weights), start=1):
        duration = max(1, round(total_days * weight))
        end_day = total_days if index == len(phase_names) else min(total_days, current_day + duration)
        start_date = date.today() + timedelta(days=current_day)
        end_date = date.today() + timedelta(days=max(current_day, end_day - 1))
        task_list = {
            1: ["Confirm scope", "Review requirements", "Approve project plan"],
            2: ["Implement core features", "Integrate project requirements", "Review working build"],
            3: ["Run acceptance testing", "Resolve final issues", "Prepare final delivery"],
        }[index]
        if index == 2 and features:
            task_list.insert(1, f"Deliver: {features[0]}")

        items.append({
            "phase": index,
            "name": name,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "tasks": task_list,
            "milestone": ["Scope approved", "Working build ready", "Final delivery"][index - 1],
            "dependency": None if index == 1 else phase_names[index - 2],
            "progress": 0,
            "payment": _payment_breakdown(final_price)[index - 1],
            "phase_status": phase_states.get(str(index), {}).get(
                "phase_status", "IN_PROGRESS"
            ),
            "payment_request_status": phase_states.get(str(index), {}).get(
                "payment_request_status", "NOT_REQUESTED"
            ),
            "notification": phase_states.get(str(index), {}).get(
                "notification"
            ),
        })
        current_day = end_day

    return items


def _payment_breakdown(final_price):
    price = float(final_price or 0)
    return [
        {"label": "Project kickoff", "percentage": 30, "amount": round(price * 0.30, 2)},
        {"label": "Working build milestone", "percentage": 40, "amount": round(price * 0.40, 2)},
        {"label": "Final delivery", "percentage": 30, "amount": round(price * 0.30, 2)},
    ]


def _phase_state(request, phase_number):
    if phase_number not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Invalid phase number")
    return request.get("phase_states", {}).get(str(phase_number), {})


def _save_phase_state(request_id, phase_number, state):
    request = negotiation_requests_collection.find_one(
        {"request_id": request_id},
        {"_id": 0},
    )
    phase_states = request.get("phase_states", {}) if request else {}
    phase_states[str(phase_number)] = state
    negotiation_requests_collection.update_one(
        {"request_id": request_id},
        {"$set": {"phase_states": phase_states, "updated_at": datetime.utcnow()}},
    )
    return state


@router.get("/client-projects")
def get_client_working_projects(
    user_email: str = Depends(get_current_user),
):
    projects = list(projects_collection.find({"client_email": user_email}))
    project_ids = {str(project["_id"]): project for project in projects}
    requests = list(
        negotiation_requests_collection.find({
            "project_id": {"$in": list(project_ids.keys())},
            "status": {"$in": ["BOTH_ACCEPTED", "CLIENT_ACCEPTED", "FREELANCER_ACCEPTED"]},
        }, {"_id": 0})
    )
    return _serialize([
        {
            "request_id": request["request_id"],
            "project_id": request["project_id"],
            "title": project_ids.get(request["project_id"], {}).get("title", "Untitled project"),
            "status": request.get("status"),
            "project_status": request.get("project_status", "IN_PROGRESS"),
            "payment_request_status": request.get("payment_request_status", "NOT_REQUESTED"),
            "notification": request.get("client_notification"),
            "final_price": (request.get("negotiation_result") or {}).get("final_price"),
        }
        for request in requests
    ])


@router.post("/payment-request/{request_id}")
def request_payment(request_id: str):
    request = _accepted_request(request_id)
    now = datetime.utcnow()
    notification = {
        "type": "PAYMENT_REQUESTED",
        "message": "The freelancer has requested payment for the completed project.",
        "created_at": now,
        "read": False,
    }
    negotiation_requests_collection.update_one(
        {"request_id": request_id},
        {"$set": {
            "payment_request_status": "REQUESTED",
            "client_notification": notification,
            "updated_at": now,
        }},
    )
    return {"message": "Payment request sent to the client", "status": "REQUESTED"}


@router.post("/mark-completed/{request_id}")
def mark_project_completed(request_id: str):
    request = _accepted_request(request_id)
    now = datetime.utcnow()
    negotiation_requests_collection.update_one(
        {"request_id": request_id},
        {"$set": {
            "project_status": "COMPLETED",
            "client_notification": None,
            "updated_at": now,
        }},
    )
    return {"message": "Project marked as completed", "status": "COMPLETED"}


@router.post("/phase-payment-request/{request_id}/{phase_number}")
def request_phase_payment(request_id: str, phase_number: int):
    request = _accepted_request(request_id)
    current = _phase_state(request, phase_number)
    now = datetime.utcnow()
    state = {
        **current,
        "payment_request_status": "REQUESTED",
        "notification": {
            "type": "PHASE_PAYMENT_REQUESTED",
            "message": f"Payment requested for phase {phase_number}.",
            "created_at": now,
            "read": False,
        },
    }
    _save_phase_state(request_id, phase_number, state)
    return {"message": f"Payment requested for phase {phase_number}", "status": "REQUESTED"}


@router.post("/phase-complete/{request_id}/{phase_number}")
def complete_phase(request_id: str, phase_number: int):
    request = _accepted_request(request_id)
    current = _phase_state(request, phase_number)
    state = {
        **current,
        "phase_status": "COMPLETED",
        "notification": None,
    }
    _save_phase_state(request_id, phase_number, state)
    return {"message": f"Phase {phase_number} marked as completed", "status": "COMPLETED"}


@router.get("/{request_id}")
def get_contract(request_id: str):
    request = _accepted_request(request_id)
    project, requirement, complexity, client, freelancer = _supporting_data(request)
    result = request.get("negotiation_result") or {}

    return _serialize({
        "request_id": request_id,
        "contract_status": "CONTRACT_READY",
        "agreement_date": request.get("updated_at") or datetime.utcnow(),
        "client": {
            "name": client.get("full_name") or client.get("name") or "Client",
            "email": client.get("email") or project.get("client_email"),
        },
        "freelancer": {
            "name": freelancer.get("full_name") or freelancer.get("name") or "Freelancer",
            "email": freelancer.get("email"),
            "title": freelancer.get("title"),
        },
        "project": {
            "title": project.get("title") or "Untitled project",
            "description": project.get("description") or "No description provided.",
            "deliverables": requirement.get("features") or ["Agreed project deliverables"],
        },
        "terms": {
            "final_price": result.get("final_price"),
            "final_timeline_days": result.get("final_timeline_days"),
            "payment_terms": "Payment follows the final negotiated project price and agreed delivery terms.",
            "responsibilities": {
                "client": "Provide timely feedback, access, and approvals required for delivery.",
                "freelancer": "Complete the agreed deliverables within the negotiated timeline.",
            },
        },
        "complexity": complexity,
    })


@router.get("/timeline/{request_id}")
def get_timeline(request_id: str):
    request = _accepted_request(request_id)
    project, requirement, _, _, _ = _supporting_data(request)
    result = request.get("negotiation_result") or {}
    phase_states = request.get("phase_states", {})
    phases = _timeline_items(
        result.get("final_timeline_days"),
        requirement.get("features") or [],
        result.get("final_price"),
        phase_states,
    )

    completed_phases = sum(
        phase.get("phase_status") == "COMPLETED"
        for phase in phases
    )

    return _serialize({
        "request_id": request_id,
        "project_title": project.get("title") or "Untitled project",
        "start_date": date.today(),
        "final_duration_days": result.get("final_timeline_days"),
        "status": "NOT_STARTED",
        "overall_progress": round(completed_phases / len(phases) * 100),
        "payment_breakdown": _payment_breakdown(result.get("final_price")),
        "payment_request_status": request.get("payment_request_status", "NOT_REQUESTED"),
        "project_status": request.get("project_status", "IN_PROGRESS"),
        "client_notification": request.get("client_notification"),
        "phases": phases,
    })
