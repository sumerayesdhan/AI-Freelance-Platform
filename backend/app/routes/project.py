from fastapi import APIRouter, Depends

from app.schemas.project_schema import ProjectCreate

from app.models.project import project_document

from app.services.project_service import (
    create_project,
    get_project_by_id
)

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