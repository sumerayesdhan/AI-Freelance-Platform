import math


class FreelancerAgent:
    """
    Rule-based autonomous Freelancer Agent.

    The freelancer tries to:
    - Protect the minimum acceptable price.
    - Prefer the preferred price.
    - Protect the minimum acceptable timeline.
    - Prefer the preferred timeline.
    - Gradually concede as negotiation progresses.
    """

    def __init__(
        self,
        freelancer_min_price,
        freelancer_preferred_price,
        freelancer_min_days,
        freelancer_preferred_days,
        max_rounds=10,
    ):
        self.freelancer_min_price = self._validate_number(
            freelancer_min_price,
            "freelancer_min_price",
        )

        self.freelancer_preferred_price = self._validate_number(
            freelancer_preferred_price,
            "freelancer_preferred_price",
        )

        self.freelancer_min_days = self._validate_number(
            freelancer_min_days,
            "freelancer_min_days",
        )

        self.freelancer_preferred_days = self._validate_number(
            freelancer_preferred_days,
            "freelancer_preferred_days",
        )

        self.max_rounds = max(
            1,
            int(max_rounds),
        )

        # Normalize preferences.
        self.freelancer_preferred_price = max(
            self.freelancer_preferred_price,
            self.freelancer_min_price,
        )

        self.freelancer_preferred_days = max(
            self.freelancer_preferred_days,
            self.freelancer_min_days,
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_number(
        value,
        field_name,
    ):

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

        return None

    # =========================================================
    # INITIAL OFFER
    # =========================================================

    def get_initial_offer(self):

        return {
            "price": round(
                self.freelancer_preferred_price,
                2,
            ),
            "timeline_days": round(
                self.freelancer_preferred_days,
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
        Higher utility is better for the freelancer.
        """

        price = float(price)
        timeline_days = float(timeline_days)

        # -----------------------------------------------------
        # PRICE UTILITY
        # -----------------------------------------------------

        if price >= self.freelancer_preferred_price:

            price_utility = 1.0

        elif price <= self.freelancer_min_price:

            price_utility = 0.0

        else:

            price_range = (
                self.freelancer_preferred_price
                -
                self.freelancer_min_price
            )

            if price_range <= 0:

                price_utility = 1.0

            else:

                price_utility = (
                    price
                    -
                    self.freelancer_min_price
                ) / price_range

        # -----------------------------------------------------
        # TIMELINE UTILITY
        # -----------------------------------------------------

        if timeline_days >= self.freelancer_preferred_days:

            timeline_utility = 1.0

        elif timeline_days <= self.freelancer_min_days:

            timeline_utility = 0.0

        else:

            timeline_range = (
                self.freelancer_preferred_days
                -
                self.freelancer_min_days
            )

            if timeline_range <= 0:

                timeline_utility = 1.0

            else:

                timeline_utility = (
                    timeline_days
                    -
                    self.freelancer_min_days
                ) / timeline_range

        return round(
            (
                0.80 * price_utility
                +
                0.20 * timeline_utility
            ),
            4,
        )

    # =========================================================
    # ACCEPTANCE THRESHOLD
    # =========================================================

    def _acceptance_threshold(
        self,
        round_number,
    ):

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

        # Important:
        # Freelancer becomes considerably more flexible
        # toward the end of negotiation.
        return (
            0.65
            -
            (0.35 * progress)
        )

    # =========================================================
    # EVALUATE OFFER
    # =========================================================

    def evaluate_offer(
        self,
        client_price,
        client_days,
        round_number=1,
        **kwargs,
    ):

        price = self._validate_number(
            client_price,
            "client_price",
        )

        days = self._validate_number(
            client_days,
            "client_days",
        )

        # -----------------------------------------------------
        # HARD REJECTION
        # -----------------------------------------------------

        if price < self.freelancer_min_price * 0.70:

            return "REJECT"

        if days < self.freelancer_min_days * 0.70:

            return "REJECT"

        # -----------------------------------------------------
        # ACCEPTANCE
        # -----------------------------------------------------

        utility = self.calculate_utility(
            price,
            days,
        )

        threshold = self._acceptance_threshold(
            round_number,
        )

        # Normal utility-based acceptance.
        if (
            price >= self.freelancer_min_price
            and
            days >= self.freelancer_min_days
            and
            utility >= threshold
        ):
            return "ACCEPT"

        # -----------------------------------------------------
        # LATE-ROUND MINIMUM SETTLEMENT
        # -----------------------------------------------------

        # When negotiation reaches the final stage, the
        # freelancer can accept an offer close to the minimum
        # reservation values rather than negotiating forever.
        progress = (
            float(round_number)
            /
            float(self.max_rounds)
        )

        if progress >= 0.80:

            price_gap = (
                self.freelancer_preferred_price
                -
                self.freelancer_min_price
            )

            days_gap = (
                self.freelancer_preferred_days
                -
                self.freelancer_min_days
            )

            acceptable_price = (
                self.freelancer_min_price
                +
                (price_gap * 0.05)
            )

            acceptable_days = (
                self.freelancer_min_days
                +
                (days_gap * 0.05)
            )

            if (
                price >= acceptable_price
                and
                days >= acceptable_days
            ):
                return "ACCEPT"

        return "COUNTER"

    # =========================================================
    # COUNTER OFFER
    # =========================================================

    def make_counter_offer(
        self,
        client_price,
        client_days,
        round_number=1,
        **kwargs,
    ):

        client_price = self._validate_number(
            client_price,
            "client_price",
        )

        client_days = self._validate_number(
            client_days,
            "client_days",
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

        concession_strength = (
            0.25
            +
            (0.65 * progress)
        )

        price = (
            self.freelancer_preferred_price
            +
            (
                client_price
                -
                self.freelancer_preferred_price
            )
            *
            concession_strength
        )

        price = max(
            self.freelancer_min_price,
            price,
        )

        # Client budget may be lower than preferred price.
        if "client_budget" in kwargs:

            try:
                client_budget = float(
                    kwargs["client_budget"]
                )

                price = min(
                    client_budget,
                    price,
                )

            except (TypeError, ValueError):

                pass

        # -----------------------------------------------------
        # TIMELINE
        # -----------------------------------------------------

        timeline_concession = (
            0.25
            +
            (0.65 * progress)
        )

        days = (
            self.freelancer_preferred_days
            +
            (
                client_days
                -
                self.freelancer_preferred_days
            )
            *
            timeline_concession
        )

        days = max(
            self.freelancer_min_days,
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