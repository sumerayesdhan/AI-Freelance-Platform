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