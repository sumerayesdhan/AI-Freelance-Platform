import math


class ClientAgent:
    """
    Autonomous rule-based client negotiation agent.

    The client tries to:
    - Stay within the maximum budget.
    - Stay close to the target budget.
    - Achieve the desired timeline.
    - Never exceed hard budget/timeline limits.
    - Gradually concede as negotiation progresses.
    - Avoid accepting unrealistic offers.
    - Avoid repeated offers.
    - Reject invalid or impossible proposals.
    """

    def __init__(
        self,
        maximum_budget: float,
        target_budget: float,
        desired_days: float,
        maximum_days: float,
        minimum_quality_score: float = 0.0,
        max_rounds: int = 10,
    ):

        # =====================================================
        # VALIDATE INPUTS
        # =====================================================

        self.maximum_budget = self._validate_number(
            maximum_budget,
            "maximum_budget"
        )

        self.target_budget = self._validate_number(
            target_budget,
            "target_budget"
        )

        self.desired_days = self._validate_number(
            desired_days,
            "desired_days"
        )

        self.maximum_days = self._validate_number(
            maximum_days,
            "maximum_days"
        )

        self.minimum_quality_score = self._validate_number(
            minimum_quality_score,
            "minimum_quality_score"
        ) if minimum_quality_score > 0 else 0.0

        self.max_rounds = max(
            1,
            int(max_rounds)
        )

        # =====================================================
        # NORMALIZE TARGET VALUES
        # =====================================================

        # Target budget cannot exceed maximum budget.
        self.target_budget = min(
            self.target_budget,
            self.maximum_budget
        )

        # Desired timeline cannot exceed maximum timeline.
        self.desired_days = min(
            self.desired_days,
            self.maximum_days
        )

        # =====================================================
        # STATE
        # =====================================================

        self.last_offer = None

        self.offer_history = []

    # =========================================================
    # NUMBER VALIDATION
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
                self.target_budget,
                2
            ),

            "timeline_days": round(
                self.desired_days,
                2
            )
        }

        self._store_offer(offer)

        return offer

    # =========================================================
    # EVALUATE FREELANCER OFFER
    # =========================================================

    def evaluate_offer(
        self,
        price,
        timeline_days,
        quality_score=1.0,
        round_number=1,
    ):

        # -----------------------------------------------------
        # SAFE CONVERSION
        # -----------------------------------------------------

        try:

            price = float(price)
            timeline_days = float(timeline_days)
            quality_score = float(quality_score)

        except (
            TypeError,
            ValueError
        ):

            return "REJECT"

        # -----------------------------------------------------
        # INVALID NUMBERS
        # -----------------------------------------------------

        if not math.isfinite(price):
            return "REJECT"

        if not math.isfinite(timeline_days):
            return "REJECT"

        if not math.isfinite(quality_score):
            return "REJECT"

        if price <= 0:
            return "REJECT"

        if timeline_days <= 0:
            return "REJECT"

        # -----------------------------------------------------
        # QUALITY CHECK
        # -----------------------------------------------------

        if quality_score < self.minimum_quality_score:

            return "REJECT"

        # -----------------------------------------------------
        # EXTREMELY UNREALISTIC PRICE
        # -----------------------------------------------------

        # A very low price is not automatically good.
        #
        # This prevents the client from accepting an
        # unrealistic proposal simply because it is cheap.

        if price < self.maximum_budget * 0.50:

            return "REJECT"

        # -----------------------------------------------------
        # EXTREMELY UNREALISTIC TIMELINE
        # -----------------------------------------------------

        if timeline_days < self.desired_days * 0.50:

            return "REJECT"

        # -----------------------------------------------------
        # ABOVE HARD BUDGET
        # -----------------------------------------------------

        if price > self.maximum_budget:

            # If the offer is excessively above the budget,
            # there is no realistic negotiation value.

            if price > self.maximum_budget * 1.40:

                return "REJECT"

            return "COUNTER"

        # -----------------------------------------------------
        # ABOVE HARD TIMELINE
        # -----------------------------------------------------

        if timeline_days > self.maximum_days:

            # Extremely excessive timeline.

            if timeline_days > self.maximum_days * 1.60:

                return "REJECT"

            return "COUNTER"

        # -----------------------------------------------------
        # CALCULATE UTILITY
        # -----------------------------------------------------

        utility = self.calculate_utility(
            price,
            timeline_days
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
    # CLIENT UTILITY
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

        if self.maximum_budget == self.target_budget:

            price_score = 1.0

        else:

            price_score = (
                self.maximum_budget - price
            ) / (
                self.maximum_budget
                - self.target_budget
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

        if self.maximum_days == self.desired_days:

            timeline_score = 1.0

        else:

            timeline_score = (
                self.maximum_days - timeline_days
            ) / (
                self.maximum_days
                - self.desired_days
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

        # Client gives more importance to price,
        # but timeline also matters.

        utility = (
            0.70 * price_score
            +
            0.30 * timeline_score
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

        # Early negotiation:
        # client is strict.

        starting_threshold = 0.90

        # Late negotiation:
        # client becomes more flexible.

        ending_threshold = 0.60

        if self.max_rounds == 1:

            return ending_threshold

        # -----------------------------------------------------
        # NEGOTIATION PROGRESS
        # -----------------------------------------------------

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
        freelancer_price,
        freelancer_days,
        round_number,
        freelancer_min_price,
        freelancer_min_days=1.0,
    ):

        # -----------------------------------------------------
        # VALIDATE INPUT
        # -----------------------------------------------------

        freelancer_price = self._validate_number(
            freelancer_price,
            "freelancer_price"
        )

        freelancer_days = self._validate_number(
            freelancer_days,
            "freelancer_days"
        )

        freelancer_min_price = self._validate_number(
            freelancer_min_price,
            "freelancer_min_price"
        )

        freelancer_min_days = self._validate_number(
            freelancer_min_days,
            "freelancer_min_days"
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

        # Keep progress inside [0, 1].

        progress = max(
            0.0,
            min(
                1.0,
                progress
            )
        )

        # -----------------------------------------------------
        # CLIENT PRICE LIMIT FOR THIS ROUND
        # -----------------------------------------------------

        client_price_limit = (
            self.target_budget
            +
            (
                self.maximum_budget
                -
                self.target_budget
            )
            * progress
        )

        # -----------------------------------------------------
        # PRICE COUNTER
        # -----------------------------------------------------

        if freelancer_price > client_price_limit:

            new_price = (
                freelancer_price
                +
                client_price_limit
            ) / 2.0

        else:

            new_price = freelancer_price

        # Never exceed maximum budget.

        new_price = min(
            new_price,
            self.maximum_budget
        )

        # Never knowingly offer below freelancer minimum.

        new_price = max(
            new_price,
            freelancer_min_price
        )

        # -----------------------------------------------------
        # CLIENT TIMELINE LIMIT
        # -----------------------------------------------------

        client_days_limit = (
            self.desired_days
            +
            (
                self.maximum_days
                -
                self.desired_days
            )
            * progress
        )

        # -----------------------------------------------------
        # TIMELINE COUNTER
        # -----------------------------------------------------

        if freelancer_days > client_days_limit:

            new_days = (
                freelancer_days
                +
                client_days_limit
            ) / 2.0

        else:

            new_days = freelancer_days

        # Never exceed client's maximum timeline.

        new_days = min(
            new_days,
            self.maximum_days
        )

        # Never go below freelancer's minimum feasible
        # timeline.

        new_days = max(
            new_days,
            freelancer_min_days
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

            # Make a tiny controlled concession to prevent
            # negotiation from becoming stuck.

            price_step = max(
                self.maximum_budget * 0.01,
                1.0
            )

            days_step = max(
                self.maximum_days * 0.02,
                1.0
            )

            new_price = min(
                self.maximum_budget,
                offer["price"] + price_step
            )

            new_days = min(
                self.maximum_days,
                offer["timeline_days"] + days_step
            )

            new_price = max(
                new_price,
                freelancer_min_price
            )

            new_days = max(
                new_days,
                freelancer_min_days
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
    # DUPLICATE OFFER CHECK
    # =========================================================

    def has_made_offer(
        self,
        price,
        timeline_days,
        tolerance=0.01
    ):

        price = float(price)
        timeline_days = float(timeline_days)

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

            if same_price and same_timeline:

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