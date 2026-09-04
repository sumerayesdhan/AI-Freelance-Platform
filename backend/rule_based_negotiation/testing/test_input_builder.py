from rule_based_negotiation.services.negotiation_input_builder import (
    NegotiationInputBuilder
)


def main():

    project = {
        "_id": "6a7c0549b51f827082ec8167",

        "title":
            "Smart Healthcare Appointment and "
            "Patient Management System",

        "description":
            "Develop a web-based healthcare "
            "management platform.",

        "client_email":
            "sameera@test.com"
    }

    complexity_analysis = {

        "analysis": {

            "complexity_level":
                "High",

            "estimated_duration":
                "6-12 months",

            "risk_level":
                "High",

            "reason":
                "Multiple user roles, numerous features",

            "technical_factors": [
                "Multiple user roles",
                "Numerous features",
                "Security and scalability requirements",
                "Integrations",
                "Technical uncertainty"
            ]
        }
    }

    freelancer = {

        "freelancer_id":
            21,

        "full_name":
            "Mani V.",

        "hourly_rate":
            "30",

        "job_success":
            "92",

        "total_hours":
            "902",

        "total_jobs":
            "160",

        "experienceScore":
            1.1812
    }

    result = NegotiationInputBuilder.build(
        project,
        complexity_analysis,
        freelancer
    )

    print()
    print("=" * 70)
    print("NEGOTIATION INPUT BUILDER TEST")
    print("=" * 70)

    for key, value in result.items():

        print(
            f"{key:35} : {value}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()
