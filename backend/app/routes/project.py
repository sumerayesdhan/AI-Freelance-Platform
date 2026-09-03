from fastapi import APIRouter, Depends, HTTPException

from app.schemas.project_schema import ProjectCreate

from app.models.project import project_document

from app.services.project_service import (
    create_project,
    get_project_by_id,
    get_client_projects
)

from app.database.mongodb import agreements_collection, projects_collection

from app.utils.auth import get_current_user



router = APIRouter(

    prefix="/projects",

    tags=["Projects"]

)





@router.post("/create")
def create_new_project(

    project: ProjectCreate,

    user_email: str = Depends(get_current_user)

):


    data = {


        "client_email":
        user_email,


        "title":
        project.title,


        "description":
        project.description,


        "status":
        "submitted"

    }



    document = project_document(

        data

    )



    result = create_project(

        document

    )



    return {


        "message":
        "Project submitted successfully",


        "project_id":
        str(result.inserted_id)

    }







@router.get("/{project_id}")
def get_project(

    project_id:str,

    user_email:str = Depends(get_current_user)

):


    project = get_project_by_id(

        project_id

    )



    if not project:


        return {


            "message":
            "Project not found"

        }



    return {


        "project_id":
        str(project["_id"]),


        "title":
        project["title"],


        "description":
        project["description"],


        "status":
        project.get(
            "status",
            "submitted"
        )

    }



@router.get("/history/list")
def project_history(
    user_email: str = Depends(get_current_user)
):
    projects = get_client_projects(user_email)
    history = []
    for project in projects:
        agreement = agreements_collection.find_one(
            {"project_id": str(project["_id"])}
        )
        completed = bool(
            agreement
            and agreement.get("client_approved")
            and agreement.get("freelancer_approved")
        )
        history.append({
            "project_id": str(project["_id"]),
            "title": project.get("title", "Untitled project"),
            "description": project.get("description", ""),
            "status": "completed" if completed else project.get("status", "ongoing"),
            "budget": agreement.get("final_agreed_price") if agreement else None,
            "freelancer_name": agreement.get("freelancer_name") if agreement else None,
            "contract_ready": completed
        })
    return {"projects": history}


@router.delete("/{project_id}")
def delete_project(
    project_id: str,
    user_email: str = Depends(get_current_user)
):
    project = get_project_by_id(project_id)
    if not project or project.get("client_email") != user_email:
        raise HTTPException(status_code=404, detail="Project not found")

    projects_collection.delete_one({"_id": project["_id"]})
    agreements_collection.delete_one({"project_id": project_id})
    return {"message": "Project deleted", "project_id": project_id}