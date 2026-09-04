from fastapi import APIRouter, HTTPException

from app.database.mongodb import (
    freelancers_collection,
    negotiation_requests_collection
)


router = APIRouter(
    prefix="/freelancer",
    tags=["Freelancer Dashboard"]
)


# ============================================================
# FREELANCER DASHBOARD
# ============================================================

@router.get("/dashboard/{freelancer_id}")
def freelancer_dashboard(
    freelancer_id: int
):

    # --------------------------------------------------------
    # Get freelancer profile
    # --------------------------------------------------------

    freelancer = freelancers_collection.find_one(
        {
            "freelancer_id": freelancer_id
        },
        {
            "_id": 0,
            "password": 0
        }
    )


    if freelancer is None:

        raise HTTPException(
            status_code=404,
            detail="Freelancer not found"
        )


    # --------------------------------------------------------
    # Get pending negotiation requests
    # --------------------------------------------------------

    requests = list(
        negotiation_requests_collection.find(
            {
                "freelancer_id": freelancer_id,
                "status": "PENDING"
            },
            {
                "_id": 0
            }
        )
    )


    # --------------------------------------------------------
    # Return dashboard data
    # --------------------------------------------------------

    return {

        "freelancer": freelancer,

        "negotiation_requests": requests,

        "pending_requests":
            len(requests)
    }