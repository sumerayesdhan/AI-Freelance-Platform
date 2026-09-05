from app.routes.negotiation import build_contract_summary, build_timeline_summary


sample_project = {
    "title": "E-commerce storefront",
    "description": "User registration, product catalog, search and filter, shopping cart, checkout flow, and bug fixes.",
    "client_email": "client@example.com",
}

sample_negotiation = {
    "final_price": 3000,
    "final_timeline_days": 30,
    "agreement": True,
    "rounds": 4,
}

sample_freelancer = {
    "name": "Mfonabasi I.",
    "email": "freelancer@example.com",
    "title": "Full-stack Developer",
    "skills": ["React", "Python", "MongoDB"],
    "hourly_rate": 45,
    "country": "United States",
    "freelancer_id": 101,
}

sample_complexity = {
    "complexity_level": "Medium",
    "estimated_days_min": 15,
    "estimated_days_max": 30,
}


def test_contract_summary_generation():
    contract = build_contract_summary(
        project=sample_project,
        negotiation_result=sample_negotiation,
        freelancer=sample_freelancer,
        project_reference="6a99210ce0176639d3265b66",
    )

    assert contract["project_reference"] == "6a99210ce0176639d3265b66"
    assert contract["parties"]["client"] == "Client"
    assert contract["parties"]["freelancer"] == "Mfonabasi I."
    assert contract["fixed_price"] == 3000
    assert contract["timeline_days"] == 30
    assert "registration" in contract["scope"].lower()


def test_timeline_summary_generation():
    timeline = build_timeline_summary(
        project=sample_project,
        negotiation_result=sample_negotiation,
        complexity_analysis=sample_complexity,
    )

    assert timeline["total_days"] == 30
    assert timeline["phases"]
    assert sum(phase["days"] for phase in timeline["phases"]) >= 30
    assert timeline["summary"]


def test_contract_summary_includes_stored_freelancer_details_and_download_state():
    contract = build_contract_summary(
        project=sample_project,
        negotiation_result=sample_negotiation,
        freelancer=sample_freelancer,
        project_reference="6a99210ce0176639d3265b66",
    )

    assert contract["freelancer_profile"]["name"] == "Mfonabasi I."
    assert contract["freelancer_profile"]["title"] == "Full-stack Developer"
    assert contract["freelancer_profile"]["country"] == "United States"
    assert contract["freelancer_profile"]["email"] == "freelancer@example.com"
    assert contract["download_enabled"] is True
    assert contract["download_filename"].endswith(".txt")


def test_contract_summary_generates_email_when_missing_from_freelancer_snapshot():
    freelancer_without_email = {
        "name": "Mahmoud D.",
        "title": "Excel, pbi, sql expert, data analyst, loughborough engineering, mba",
        "skills": ["Excel", "Power BI", "SQL"],
        "hourly_rate": 30,
        "country": "Egypt",
        "freelancer_id": 101,
    }

    contract = build_contract_summary(
        project=sample_project,
        negotiation_result=sample_negotiation,
        freelancer=freelancer_without_email,
        project_reference="6a99210ce0176639d3265b66",
    )

    assert contract["freelancer_profile"]["email"] == "freelancer101@example.com"
