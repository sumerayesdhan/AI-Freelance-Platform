import math


class FreelancerAgent:
    """
    Autonomous rule-based freelancer negotiation agent.

    Freelancer objectives:
    - Protect minimum acceptable project price.
    - Prefer a higher project price.
    - Protect minimum feasible timeline.
    - Prefer a comfortable timeline.
    - Gradually reduce price during negotiation.
    - Gradually improve timeline when necessary.
    - Avoid accepting unrealistic proposals.
    - Avoid repeated offers.
    """

    def __init__(
        self,
        minimum_price: float,
        preferred_price: float,
        minimum_days: float,
        preferred_days: float,
        maximum_rounds: int = 10,
        quality_score: float = 1.0,
    ):

        # =====================================================
        # VALIDATE INPUTS
        # =====================================================

        self.minimum_price = self._validate_number(
            minimum_price,
            "minimum_price"
        )

        self.preferred_price = self._validate_number(
            preferred_price,
            "preferred_price"
        )

        self.minimum_days = self._validate_number(
            minimum_days,
            "minimum_days"
        )

        self.preferred_days = self._validate_number(
            preferred_days,
            "preferred_days"
        )

        self.max_rounds = max(
            1,
            int(maximum_rounds)
        )

        self.quality_score = max(
            0.0,
            min(
                1.0,
                float(quality_score)
            )
        )

        # =====================================================
        # NORMALIZE VALUES
        # =====================================================

        # Preferred price should never be below minimum price.

        self.preferred_price = max(
            self.preferred_price,
            self.minimum_price
        )

        # Preferred timeline should never be below
        # minimum feasible timeline.

        self.preferred_days = max(
            self.preferred_days,
            self.minimum_days
        )

        # =====================================================
        # STATE
        # =====================================================

        self.last_offer = None

        self.offer_history = []

    # =========================================================
    # VALIDATION
    # =========================================================

    @staticmethod
    def _validate_number(
        value,
        field_name
    ):

        try:

            value = float(value)

        except (
            TypeError,
            ValueError
        ):

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
    # INITIAL OFFER
    # =========================================================

    def get_initial_offer(self):

        offer = {

            "price": round(
                self.preferred_price,
                2
            ),

            "timeline_days": round(
                self.preferred_days,
                2
            )
        }

        self._store_offer(
            offer
        )

        return offer

    # =========================================================
    # EVALUATE CLIENT OFFER
    # =========================================================

    def evaluate_offer(
        self,
        client_price,
        client_days,
        round_number=1,
    ):

        # -----------------------------------------------------
        # SAFE CONVERSION
        # -----------------------------------------------------

        try:

            client_price = float(
                client_price
            )

            client_days = float(
                client_days
            )

        except (
            TypeError,
            ValueError
        ):

            return "REJECT"

        # -----------------------------------------------------
        # INVALID VALUES
        # -----------------------------------------------------

        if not math.isfinite(client_price):

            return "REJECT"

        if not math.isfinite(client_days):

            return "REJECT"

        if client_price <= 0:

            return "REJECT"

        if client_days <= 0:

            return "REJECT"

        # -----------------------------------------------------
        # EXTREMELY LOW PRICE
        # -----------------------------------------------------

        if client_price < self.minimum_price * 0.70:

            return "REJECT"

        # -----------------------------------------------------
        # IMPOSSIBLY SHORT TIMELINE
        # -----------------------------------------------------

        if client_days < self.minimum_days * 0.70:

            return "REJECT"

        # -----------------------------------------------------
        # HARD MINIMUM PRICE
        # -----------------------------------------------------

        if client_price < self.minimum_price:

            return "COUNTER"

        # -----------------------------------------------------
        # HARD MINIMUM TIMELINE
        # -----------------------------------------------------

        if client_days < self.minimum_days:

            return "COUNTER"

        # -----------------------------------------------------
        # CALCULATE UTILITY
        # -----------------------------------------------------

        utility = self.calculate_utility(
            client_price,
            client_days
        )

        # -----------------------------------------------------
        # ACCEPTANCE THRESHOLD
        # -----------------------------------------------------

        threshold = self.acceptance_threshold(
            round_number
        )

        # -----------------------------------------------------
        # ACCEPT
        # -----------------------------------------------------

        if utility >= threshold:

            return "ACCEPT"

        # -----------------------------------------------------
        # OTHERWISE COUNTER
        # -----------------------------------------------------

        return "COUNTER"

    # =========================================================
    # FREELANCER UTILITY
    # =========================================================

    def calculate_utility(
        self,
        price,
        timeline_days
    ):

        price = float(price)
        timeline_days = float(timeline_days)

        # -----------------------------------------------------
        # PRICE SCORE
        # -----------------------------------------------------

        if self.preferred_price == self.minimum_price:

            price_score = 1.0

        else:

            price_score = (
                price - self.minimum_price
            ) / (
                self.preferred_price
                - self.minimum_price
            )

        price_score = max(
            0.0,
            min(
                1.0,
                price_score
            )
        )

        # -----------------------------------------------------
        # TIMELINE SCORE
        # -----------------------------------------------------

        if self.preferred_days == self.minimum_days:

            timeline_score = 1.0

        else:

            timeline_score = (
                timeline_days
                - self.minimum_days
            ) / (
                self.preferred_days
                - self.minimum_days
            )

        timeline_score = max(
            0.0,
            min(
                1.0,
                timeline_score
            )
        )

        # -----------------------------------------------------
        # WEIGHTED UTILITY
        # -----------------------------------------------------

        # Freelancer prioritizes price more strongly,
        # while timeline still matters.

        utility = (
            0.80 * price_score
            +
            0.20 * timeline_score
        )

        return round(
            utility,
            6
        )

    # =========================================================
    # ACCEPTANCE THRESHOLD
    # =========================================================

    def acceptance_threshold(
        self,
        round_number
    ):

        round_number = max(
            1,
            min(
                int(round_number),
                self.max_rounds
            )
        )

        # Freelancer is strict initially.

        starting_threshold = 0.90

        # Freelancer becomes more flexible later.

        ending_threshold = 0.55

        if self.max_rounds == 1:

            return ending_threshold

        progress = (
            round_number - 1
        ) / (
            self.max_rounds - 1
        )

        threshold = (
            starting_threshold
            -
            (
                starting_threshold
                - ending_threshold
            )
            * progress
        )

        return round(
            threshold,
            6
        )

    # =========================================================
    # MAKE COUNTER OFFER
    # =========================================================

    def make_counter_offer(
        self,
        client_price,
        client_days,
        round_number
    ):

        client_price = self._validate_number(
            client_price,
            "client_price"
        )

        client_days = self._validate_number(
            client_days,
            "client_days"
        )

        round_number = max(
            1,
            min(
                int(round_number),
                self.max_rounds
            )
        )

        # -----------------------------------------------------
        # NEGOTIATION PROGRESS
        # -----------------------------------------------------

        if self.max_rounds == 1:

            progress = 1.0

        else:

            progress = (
                round_number
                /
                self.max_rounds
            )

        progress = max(
            0.0,
            min(
                1.0,
                progress
            )
        )

        # -----------------------------------------------------
        # TARGET PRICE FOR THIS ROUND
        # -----------------------------------------------------

        target_price = (
            self.preferred_price
            -
            (
                self.preferred_price
                -
                self.minimum_price
            )
            * progress
        )

        # -----------------------------------------------------
        # PRICE COUNTER
        # -----------------------------------------------------

        if client_price < target_price:

            new_price = (
                client_price
                +
                target_price
            ) / 2.0

        else:

            new_price = client_price

        # Never go below minimum price.

        new_price = max(
            new_price,
            self.minimum_price
        )

        # -----------------------------------------------------
        # TARGET TIMELINE
        # -----------------------------------------------------

        target_days = (
            self.preferred_days
            -
            (
                self.preferred_days
                -
                self.minimum_days
            )
            * progress
        )

        # -----------------------------------------------------
        # TIMELINE COUNTER
        # -----------------------------------------------------

        if client_days < target_days:

            new_days = (
                client_days
                +
                target_days
            ) / 2.0

        else:

            new_days = client_days

        # Never go below minimum feasible timeline.

        new_days = max(
            new_days,
            self.minimum_days
        )

        # -----------------------------------------------------
        # CREATE OFFER
        # -----------------------------------------------------

        offer = {

            "price": round(
                new_price,
                2
            ),

            "timeline_days": round(
                new_days,
                2
            )
        }

        # -----------------------------------------------------
        # PREVENT DUPLICATE OFFER
        # -----------------------------------------------------

        if self.has_made_offer(
            offer["price"],
            offer["timeline_days"]
        ):

            price_step = max(
                self.preferred_price * 0.01,
                1.0
            )

            days_step = max(
                self.preferred_days * 0.02,
                1.0
            )

            # Freelancer should not lower price further
            # when breaking a duplicate.

            new_price = max(
                self.minimum_price,
                offer["price"] - price_step
            )

            # Freelancer can accept a slightly longer
            # timeline to make the proposal different.

            new_days = max(
                self.minimum_days,
                offer["timeline_days"] + days_step
            )

            offer = {

                "price": round(
                    new_price,
                    2
                ),

                "timeline_days": round(
                    new_days,
                    2
                )
            }

        # -----------------------------------------------------
        # STORE OFFER
        # -----------------------------------------------------

        self._store_offer(
            offer
        )

        return offer

    # =========================================================
    # STORE OFFER
    # =========================================================

    def _store_offer(
        self,
        offer
    ):

        stored_offer = {

            "price": float(
                offer["price"]
            ),

            "timeline_days": float(
                offer["timeline_days"]
            )
        }

        self.last_offer = stored_offer.copy()

        self.offer_history.append(
            stored_offer.copy()
        )

    # =========================================================
    # DUPLICATE CHECK
    # =========================================================

    def has_made_offer(
        self,
        price,
        timeline_days,
        tolerance=0.01
    ):

        price = float(price)

        timeline_days = float(
            timeline_days
        )

        for offer in self.offer_history:

            same_price = (
                abs(
                    offer["price"]
                    - price
                )
                <= tolerance
            )

            same_timeline = (
                abs(
                    offer["timeline_days"]
                    - timeline_days
                )
                <= tolerance
            )

            if (
                same_price
                and
                same_timeline
            ):

                return True

        return False

    # =========================================================
    # GET LAST OFFER
    # =========================================================

    def get_last_offer(self):

        if self.last_offer is None:

            return None

        return self.last_offer.copy()

    # =========================================================
    # GET OFFER HISTORY
    # =========================================================

    def get_offer_history(self):

        return [
            offer.copy()
            for offer in self.offer_history
        ]

    # =========================================================
    # RESET AGENT
    # =========================================================

    def reset(self):

        self.last_offer = None

        self.offer_history = []