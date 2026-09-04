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
    # 1. GET FREELANCER PROFILE
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
    # 2. GET NEGOTIATIONS THAT REQUIRE /
    #    ALLOW FREELANCER TO SEE FINAL TERMS
    # --------------------------------------------------------
    #
    # Possible states:
    #
    # NEGOTIATION_COMPLETED
    #     -> AI negotiation finished
    #     -> both humans still need to decide
    #
    # CLIENT_ACCEPTED
    #     -> client accepted
    #     -> freelancer still needs to decide
    #
    # FREELANCER_ACCEPTED
    #     -> freelancer accepted
    #     -> client still needs to decide
    #
    # BOTH_ACCEPTED
    #     -> both accepted
    #     -> contract can be generated
    #
    # We intentionally DO NOT show PENDING here because
    # the freelancer does not participate in AI negotiation.
    #
    # --------------------------------------------------------

    visible_statuses = [
        "NEGOTIATION_COMPLETED",
        "CLIENT_ACCEPTED",
        "FREELANCER_ACCEPTED",
        "BOTH_ACCEPTED"
    ]


    requests = list(
        negotiation_requests_collection.find(
            {
                "freelancer_id": freelancer_id,

                "status": {
                    "$in": visible_statuses
                }
            },
            {
                "_id": 0
            }
        ).sort(
            "updated_at",
            -1
        )
    )


    # --------------------------------------------------------
    # 3. RETURN DASHBOARD DATA
    # --------------------------------------------------------

    return {

        "freelancer":
            freelancer,

        "negotiation_requests":
            requests,

        "completed_negotiations":
            len(requests),

        "pending_requests":
            0

    }