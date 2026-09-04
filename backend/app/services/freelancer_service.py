import os
import pandas as pd


# ============================================================
# EXISTING RECOMMENDATION FUNCTION
# ============================================================

def get_freelancer_recommendations(
    requirement_analysis,
    complexity_analysis
):

    # IMPORTANT:
    # Load the heavy ML recommendation module only when
    # recommendations are actually requested.
    from freelancer_recommendation.recommendation import (
        recommend_freelancers
    )

    title = (
        requirement_analysis
        .get("project_type", "")
    )

    description = " ".join(
        requirement_analysis
        .get("features", [])
    )

    skills = " ".join(
        requirement_analysis
        .get("technology_preference", [])
        or []
    )

    budget = (
        requirement_analysis
        .get("budget_range", None)
    )

    result = recommend_freelancers(
        project_title=title,
        project_description=description,
        project_skills=skills,
        project_budget=budget,
        top_k=5
    )

    return result


# ============================================================
# FREELANCER DATASET
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

FREELANCER_DATA_PATH = os.path.join(
    BASE_DIR,
    "freelancer_recommendation",
    "data",
    "freelancers.csv"
)


# ============================================================
# GET FREELANCER BY ID
# ============================================================

def get_freelancer_by_id(freelancer_id):

    try:

        freelancer_id = int(freelancer_id)

    except (ValueError, TypeError):

        return None


    # Read freelancer dataset

    freelancers = pd.read_csv(
        FREELANCER_DATA_PATH
    )


    # Find selected freelancer

    freelancer = freelancers[
        freelancers["freelancer_id"] == freelancer_id
    ]


    if freelancer.empty:

        return None


    # Get first matching row

    freelancer = freelancer.iloc[0]


    # Convert NaN values safely

    def safe_value(value):

        if pd.isna(value):

            return None

        return value


    return {

        "freelancer_id":
            int(freelancer["freelancer_id"]),

        "name":
            safe_value(freelancer["name"]),

        "title":
            safe_value(freelancer["title"]),

        "skills":
            safe_value(freelancer["skills"]),

        "description":
            safe_value(freelancer["description"]),

        "hourly_rate":
            safe_value(freelancer["hourly_rate"]),

        "job_success":
            safe_value(freelancer["job_success"]),

        "total_hours":
            safe_value(freelancer["total_hours"]),

        "total_jobs":
            safe_value(freelancer["total_jobs"]),

        "country":
            safe_value(freelancer["country"]),

        "experienceScore":
            safe_value(freelancer["experienceScore"]),

        "profile_text":
            safe_value(freelancer["profile_text"])

    }