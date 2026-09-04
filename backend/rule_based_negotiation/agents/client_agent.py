import math


class ClientAgent:
    """
    Rule-based autonomous Client Agent.

    The client tries to:
    - Stay close to the target budget.
    - Prefer the desired timeline.
    - Never exceed the maximum budget.
    - Never exceed the maximum timeline.
    - Gradually concede when negotiation continues.
    """

    def __init__(
        self,
        client_budget,
        client_target_budget,
        client_desired_days,
        client_maximum_days,
        max_rounds=10,
    ):
        self.client_budget = self._validate_number(
            client_budget,
            "client_budget",
        )

        self.client_target_budget = self._validate_number(
            client_target_budget,
            "client_target_budget",
        )

        self.client_desired_days = self._validate_number(
            client_desired_days,
            "client_desired_days",
        )

        self.client_maximum_days = self._validate_number(
            client_maximum_days,
            "client_maximum_days",
        )

        self.max_rounds = max(1, int(max_rounds))

        # Normalize preferences.
        self.client_target_budget = min(
            self.client_target_budget,
            self.client_budget,
        )

        self.client_desired_days = min(
            self.client_desired_days,
            self.client_maximum_days,
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_number(value, field_name):

        try:
            value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{field_name} must be a valid number."
            )

        if not math.isfinite(value):
            raise ValueError(
                f"{field_name} must be finite."
            )

        if value <= 0:
            raise ValueError(
                f"{field_name} must be greater than zero."
            )

        return value

    # =========================================================
    # RESET
    # =========================================================

    def reset(self):
        """
        Reset internal state.
        """

        return None

    # =========================================================
    # INITIAL OFFER
    # =========================================================

    def get_initial_offer(self):

        return {
            "price": round(
                self.client_target_budget,
                2,
            ),
            "timeline_days": round(
                self.client_desired_days,
                2,
            ),
        }

    # =========================================================
    # UTILITY
    # =========================================================

    def calculate_utility(
        self,
        price,
        timeline_days,
    ):
        """
        Higher utility is better for the client.

        Price has higher importance than timeline.
        """

        price = float(price)
        timeline_days = float(timeline_days)

        # -----------------------------------------------------
        # PRICE UTILITY
        # -----------------------------------------------------

        if price <= self.client_target_budget:

            price_utility = 1.0

        elif price >= self.client_budget:

            price_utility = 0.0

        else:

            price_range = (
                self.client_budget
                - self.client_target_budget
            )

            if price_range <= 0:
                price_utility = 1.0
            else:
                price_utility = (
                    self.client_budget - price
                ) / price_range

        # -----------------------------------------------------
        # TIMELINE UTILITY
        # -----------------------------------------------------

        if timeline_days <= self.client_desired_days:

            timeline_utility = 1.0

        elif timeline_days >= self.client_maximum_days:

            timeline_utility = 0.0

        else:

            timeline_range = (
                self.client_maximum_days
                - self.client_desired_days
            )

            if timeline_range <= 0:
                timeline_utility = 1.0
            else:
                timeline_utility = (
                    self.client_maximum_days
                    - timeline_days
                ) / timeline_range

        return round(
            (
                0.70 * price_utility
                +
                0.30 * timeline_utility
            ),
            4,
        )

    # =========================================================
    # ACCEPTANCE THRESHOLD
    # =========================================================

    def _acceptance_threshold(self, round_number):

        progress = (
            float(round_number)
            /
            float(self.max_rounds)
        )

        progress = max(
            0.0,
            min(
                1.0,
                progress,
            ),
        )

        # Client becomes more flexible as negotiation progresses.
        return (
            0.82
            -
            (0.22 * progress)
        )

    # =========================================================
    # EVALUATE OFFER
    # =========================================================

    def evaluate_offer(
        self,
        price,
        timeline_days,
        round_number=1,
        quality_score=1.0,
    ):

        price = self._validate_number(
            price,
            "price",
        )

        timeline_days = self._validate_number(
            timeline_days,
            "timeline_days",
        )

        # -----------------------------------------------------
        # HARD REJECTION
        # -----------------------------------------------------

        if price > self.client_budget * 1.35:
            return "REJECT"

        if timeline_days > self.client_maximum_days * 1.50:
            return "REJECT"

        # -----------------------------------------------------
        # HARD CLIENT CONSTRAINTS
        # -----------------------------------------------------

        if price > self.client_budget:
            return "COUNTER"

        if timeline_days > self.client_maximum_days:
            return "COUNTER"

        # -----------------------------------------------------
        # UTILITY
        # -----------------------------------------------------

        utility = self.calculate_utility(
            price,
            timeline_days,
        )

        threshold = self._acceptance_threshold(
            round_number,
        )

        # Quality can slightly influence acceptance.
        quality_score = max(
            0.0,
            min(
                1.0,
                float(quality_score),
            ),
        )

        adjusted_threshold = (
            threshold
            -
            (0.05 * quality_score)
        )

        # -----------------------------------------------------
        # ACCEPT
        # -----------------------------------------------------

        if utility >= adjusted_threshold:
            return "ACCEPT"

        return "COUNTER"

    # =========================================================
    # COUNTER OFFER
    # =========================================================

    def make_counter_offer(
        self,
        freelancer_price,
        freelancer_days,
        round_number=1,
        **kwargs,
    ):

        freelancer_price = self._validate_number(
            freelancer_price,
            "freelancer_price",
        )

        freelancer_days = self._validate_number(
            freelancer_days,
            "freelancer_days",
        )

        progress = (
            float(round_number)
            /
            float(self.max_rounds)
        )

        progress = max(
            0.0,
            min(
                1.0,
                progress,
            ),
        )

        # -----------------------------------------------------
        # PRICE
        # -----------------------------------------------------

        # Start near target and progressively move toward
        # the freelancer's requested price.
        concession_strength = (
            0.30
            +
            (0.50 * progress)
        )

        price = (
            self.client_target_budget
            +
            (
                freelancer_price
                -
                self.client_target_budget
            )
            *
            concession_strength
        )

        price = max(
            self.client_target_budget,
            price,
        )

        price = min(
            self.client_budget,
            price,
        )

        # -----------------------------------------------------
        # TIMELINE
        # -----------------------------------------------------

        timeline_concession = (
            0.30
            +
            (0.50 * progress)
        )

        days = (
            self.client_desired_days
            +
            (
                freelancer_days
                -
                self.client_desired_days
            )
            *
            timeline_concession
        )

        days = max(
            self.client_desired_days,
            days,
        )

        days = min(
            self.client_maximum_days,
            days,
        )

        return {
            "price": round(
                price,
                2,
            ),
            "timeline_days": round(
                days,
                2,
            ),
        }