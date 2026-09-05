from datetime import datetime


class NegotiationInputBuilder:
    """
    Converts project, complexity and freelancer information
    into structured negotiation parameters.

    This acts as the bridge between the main application
    and the rule-based negotiation engine.
    """

    # ========================================================
    # COMPLEXITY MAPPING
    # ========================================================

    COMPLEXITY_SCORES = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    RISK_SCORES = {
        "Low": 1,
        "Medium": 2,
        "High": 3
    }

    # ========================================================
    # BUILD NEGOTIATION INPUT
    # ========================================================

    @staticmethod
    def build(
        project,
        complexity_analysis,
        freelancer
    ):
        """
        Build negotiation parameters from MongoDB data.
        """

        if project is None:
            raise ValueError(
                "Project information is missing."
            )

        if freelancer is None:
            raise ValueError(
                "Freelancer information is missing."
            )

        # ----------------------------------------------------
        # COMPLEXITY DATA
        # ----------------------------------------------------

        analysis = {}

        if complexity_analysis:

            analysis = complexity_analysis.get(
                "analysis",
                {}
            )

        complexity_level = analysis.get(
            "complexity_level",
            "Medium"
        )

        risk_level = analysis.get(
            "risk_level",
            "Medium"
        )

        estimated_duration = analysis.get(
            "estimated_duration",
            "1-3 months"
        )

        complexity_score = (
            NegotiationInputBuilder
            .COMPLEXITY_SCORES
            .get(
                complexity_level,
                2
            )
        )

        risk_score = (
            NegotiationInputBuilder
            .RISK_SCORES
            .get(
                risk_level,
                2
            )
        )

        # ----------------------------------------------------
        # ESTIMATE TIMELINE
        # ----------------------------------------------------

        estimated_days_min, estimated_days_max = (
            NegotiationInputBuilder
            .parse_duration(
                estimated_duration
            )
        )

        estimated_days = (
            estimated_days_min
            + estimated_days_max
        ) / 2

        # ----------------------------------------------------
        # FREELANCER RATE
        # ----------------------------------------------------

        hourly_rate = (
            NegotiationInputBuilder
            .to_float(
                freelancer.get(
                    "hourly_rate"
                ),
                25.0
            )
        )

        # ----------------------------------------------------
        # FREELANCER EXPERIENCE
        # ----------------------------------------------------

        job_success = (
            NegotiationInputBuilder
            .to_float(
                freelancer.get(
                    "job_success"
                ),
                80.0
            )
        )

        experience_score = (
            NegotiationInputBuilder
            .to_float(
                freelancer.get(
                    "experienceScore"
                ),
                1.0
            )
        )

        total_jobs = (
            NegotiationInputBuilder
            .to_float(
                freelancer.get(
                    "total_jobs"
                ),
                0.0
            )
        )

        # ----------------------------------------------------
        # PROJECT COMPLEXITY ADJUSTMENT
        # ----------------------------------------------------

        complexity_multiplier = {
            1: 1.00,
            2: 1.15,
            3: 1.35
        }.get(
            complexity_score,
            1.15
        )

        risk_multiplier = {
            1: 1.00,
            2: 1.10,
            3: 1.20
        }.get(
            risk_score,
            1.10
        )

        # ----------------------------------------------------
        # ESTIMATED EFFORT
        # ----------------------------------------------------

        estimated_hours = (
            estimated_days * 8
        )

        # ----------------------------------------------------
        # PROJECT VALUE
        # ----------------------------------------------------

        base_project_value = (
            hourly_rate
            * estimated_hours
        )

        adjusted_project_value = (
            base_project_value
            * complexity_multiplier
            * risk_multiplier
        )

        # ----------------------------------------------------
        # FREELANCER PRICE
        # ----------------------------------------------------

        freelancer_min_price = max(
            hourly_rate * 8,
            adjusted_project_value * 0.55
        )

        freelancer_preferred_price = max(
            freelancer_min_price,
            adjusted_project_value * 0.85
        )

        # ----------------------------------------------------
        # CLIENT BUDGET
        # ----------------------------------------------------

        # Client budget is derived from project value.
        #
        # This gives the negotiation system a realistic
        # budget instead of using a hardcoded number.

        client_budget = max(
            freelancer_min_price,
            adjusted_project_value * 1.10
        )

        client_target_budget = (
            client_budget * 0.85
        )

        # ----------------------------------------------------
        # TIMELINE
        # ----------------------------------------------------

        freelancer_min_days = max(
            1.0,
            estimated_days_min
        )

        freelancer_preferred_days = max(
            freelancer_min_days,
            estimated_days
        )

        client_desired_days = max(
            1.0,
            estimated_days_min
        )

        client_maximum_days = max(
            client_desired_days,
            estimated_days_max
        )

        # ----------------------------------------------------
        # RETURN STRUCTURED INPUT
        # ----------------------------------------------------

        return {

            # Project
            "project_id":
                str(project.get("_id")),

            "project_title":
                project.get("title"),

            "project_description":
                project.get("description"),

            # Complexity
            "complexity_level":
                complexity_level,

            "complexity_score":
                complexity_score,

            "risk_level":
                risk_level,

            "risk_score":
                risk_score,

            "estimated_duration":
                estimated_duration,

            "estimated_days_min":
                round(
                    estimated_days_min,
                    2
                ),

            "estimated_days_max":
                round(
                    estimated_days_max,
                    2
                ),

            # Freelancer
            "freelancer_id":
                freelancer.get(
                    "freelancer_id"
                ),

            "hourly_rate":
                hourly_rate,

            "job_success":
                job_success,

            "experience_score":
                experience_score,

            "total_jobs":
                total_jobs,

            # Negotiation
            "client_budget":
                round(
                    client_budget,
                    2
                ),

            "client_target_budget":
                round(
                    client_target_budget,
                    2
                ),

            "client_desired_days":
                round(
                    client_desired_days,
                    2
                ),

            "client_maximum_days":
                round(
                    client_maximum_days,
                    2
                ),

            "freelancer_min_price":
                round(
                    freelancer_min_price,
                    2
                ),

            "freelancer_preferred_price":
                round(
                    freelancer_preferred_price,
                    2
                ),

            "freelancer_min_days":
                round(
                    freelancer_min_days,
                    2
                ),

            "freelancer_preferred_days":
                round(
                    freelancer_preferred_days,
                    2
                )
        }

    # ========================================================
    # PARSE DURATION
    # ========================================================

    @staticmethod
    def parse_duration(duration):
        """
        Convert duration text into minimum and maximum days.

        Examples:

        6-12 months
        -> 180, 365

        1-3 months
        -> 30, 90

        2-4 weeks
        -> 14, 28

        10-20 days
        -> 10, 20
        """

        if not duration:
            return 30.0, 90.0

        text = str(duration).lower().strip()

        # ----------------------------------------------------
        # Remove spaces
        # ----------------------------------------------------

        text = text.replace(" ", "")

        # ----------------------------------------------------
        # DAYS
        # ----------------------------------------------------

        if "day" in text:

            numbers = (
                NegotiationInputBuilder
                .extract_numbers(text)
            )

            if len(numbers) >= 2:

                return (
                    numbers[0],
                    numbers[1]
                )

            if len(numbers) == 1:

                return (
                    numbers[0],
                    numbers[0]
                )

        # ----------------------------------------------------
        # WEEKS
        # ----------------------------------------------------

        if "week" in text:

            numbers = (
                NegotiationInputBuilder
                .extract_numbers(text)
            )

            if len(numbers) >= 2:

                return (
                    numbers[0] * 7,
                    numbers[1] * 7
                )

            if len(numbers) == 1:

                return (
                    numbers[0] * 7,
                    numbers[0] * 7
                )

        # ----------------------------------------------------
        # MONTHS
        # ----------------------------------------------------

        if "month" in text:

            numbers = (
                NegotiationInputBuilder
                .extract_numbers(text)
            )

            if len(numbers) >= 2:

                return (
                    numbers[0] * 30,
                    numbers[1] * 30
                )

            if len(numbers) == 1:

                return (
                    numbers[0] * 30,
                    numbers[0] * 30
                )

        # ----------------------------------------------------
        # YEARS
        # ----------------------------------------------------

        if "year" in text:

            numbers = (
                NegotiationInputBuilder
                .extract_numbers(text)
            )

            if len(numbers) >= 2:

                return (
                    numbers[0] * 365,
                    numbers[1] * 365
                )

            if len(numbers) == 1:

                return (
                    numbers[0] * 365,
                    numbers[0] * 365
                )

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        return 30.0, 90.0

    # ========================================================
    # EXTRACT NUMBERS
    # ========================================================

    @staticmethod
    def extract_numbers(text):

        import re

        matches = re.findall(
            r"\d+(?:\.\d+)?",
            text
        )

        return [
            float(value)
            for value in matches
        ]

    # ========================================================
    # SAFE FLOAT CONVERSION
    # ========================================================

    @staticmethod
    def to_float(
        value,
        default=0.0
    ):

        try:

            if value is None:
                return default

            return float(value)

        except (
            TypeError,
            ValueError
        ):

            return default