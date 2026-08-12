from freelancer_recommendation.recommendation import (
    recommend_freelancers
)


def get_freelancer_recommendations(
    requirement_analysis,
    complexity_analysis
):

    title = (
        requirement_analysis
        .get("project_type","")
    )


    description = " ".join(
        requirement_analysis
        .get("features",[])
    )


    skills = " ".join(
        requirement_analysis
        .get("technology_preference",[])
        or []
    )


    budget = (
        requirement_analysis
        .get("budget_range",None)
    )


    result = recommend_freelancers(

        project_title=title,

        project_description=description,

        project_skills=skills,

        project_budget=budget,

        top_k=5
    )


    return result