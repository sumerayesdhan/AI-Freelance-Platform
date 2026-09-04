import math

from rule_based_negotiation.agents.client_agent import ClientAgent
from rule_based_negotiation.agents.freelancer_agent import FreelancerAgent


class NegotiationEngine:
    """
    Autonomous two-agent rule-based negotiation engine.

    Negotiation flow:

        Client initial offer
              ↓
        Freelancer evaluates
              ↓
        Freelancer counter
              ↓
        Client evaluates
              ↓
        Client counter
              ↓
            repeat
              ↓
        Agreement / Failure

    The engine handles:
    - Hard budget constraints
    - Hard timeline constraints
    - Reservation values
    - Multi-round negotiation
    - Controlled concessions
    - Compromise detection
    - Duplicate offers
    - Oscillation prevention
    - Invalid values
    - Impossible negotiations
    - Maximum rounds
    - Complete negotiation history
    """

    def __init__(
        self,
        client_budget,
        client_target_budget,
        client_desired_days,
        client_maximum_days,
        freelancer_min_price,
        freelancer_preferred_price,
        freelancer_min_days,
        freelancer_preferred_days,
        max_rounds=10,
        client_quality_requirement=0.0,
        freelancer_quality_score=1.0,
    ):

        # =====================================================
        # VALIDATE INPUT
        # =====================================================

        self.client_budget = self._validate_number(
            client_budget,
            "client_budget"
        )

        self.client_target_budget = self._validate_number(
            client_target_budget,
            "client_target_budget"
        )

        self.client_desired_days = self._validate_number(
            client_desired_days,
            "client_desired_days"
        )

        self.client_maximum_days = self._validate_number(
            client_maximum_days,
            "client_maximum_days"
        )

        self.freelancer_min_price = self._validate_number(
            freelancer_min_price,
            "freelancer_min_price"
        )

        self.freelancer_preferred_price = self._validate_number(
            freelancer_preferred_price,
            "freelancer_preferred_price"
        )

        self.freelancer_min_days = self._validate_number(
            freelancer_min_days,
            "freelancer_min_days"
        )

        self.freelancer_preferred_days = self._validate_number(
            freelancer_preferred_days,
            "freelancer_preferred_days"
        )

        self.max_rounds = max(
            1,
            int(max_rounds)
        )

        # =====================================================
        # NORMALIZE PREFERENCES
        # =====================================================

        self.client_target_budget = min(
            self.client_target_budget,
            self.client_budget
        )

        self.client_desired_days = min(
            self.client_desired_days,
            self.client_maximum_days
        )

        self.freelancer_preferred_price = max(
            self.freelancer_preferred_price,
            self.freelancer_min_price
        )

        self.freelancer_preferred_days = max(
            self.freelancer_preferred_days,
            self.freelancer_min_days
        )

        # =====================================================
        # AGENTS
        # =====================================================

        self.client_agent = ClientAgent(
            maximum_budget=self.client_budget,
            target_budget=self.client_target_budget,
            desired_days=self.client_desired_days,
            maximum_days=self.client_maximum_days,
            minimum_quality_score=client_quality_requirement,
            max_rounds=self.max_rounds,
        )

        self.freelancer_agent = FreelancerAgent(
            minimum_price=self.freelancer_min_price,
            preferred_price=self.freelancer_preferred_price,
            minimum_days=self.freelancer_min_days,
            preferred_days=self.freelancer_preferred_days,
            maximum_rounds=self.max_rounds,
            quality_score=freelancer_quality_score,
        )

        # =====================================================
        # STATE
        # =====================================================

        self.history = []

        self.previous_offers = []

        self.agreement = False

        self.final_price = None

        self.final_timeline_days = None

        self.failure_reason = None

    # =========================================================
    # VALIDATE NUMBER
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
    # VALIDATE OFFER
    # =========================================================

    def _validate_offer(
        self,
        offer
    ):

        if not isinstance(
            offer,
            dict
        ):
            return False

        if "price" not in offer:
            return False

        if "timeline_days" not in offer:
            return False

        try:

            price = float(
                offer["price"]
            )

            days = float(
                offer["timeline_days"]
            )

        except (
            TypeError,
            ValueError
        ):

            return False

        if not math.isfinite(price):
            return False

        if not math.isfinite(days):
            return False

        if price <= 0:
            return False

        if days <= 0:
            return False

        return True

    # =========================================================
    # GLOBAL FEASIBILITY
    # =========================================================

    def _is_feasible(
        self,
        price,
        timeline_days
    ):

        price = float(price)
        timeline_days = float(timeline_days)

        price_ok = (
            self.freelancer_min_price
            <= price
            <= self.client_budget
        )

        timeline_ok = (
            self.freelancer_min_days
            <= timeline_days
            <= self.client_maximum_days
        )

        return (
            price_ok
            and timeline_ok
        )

    # =========================================================
    # PRICE RANGE
    # =========================================================

    def _price_range_exists(self):

        return (
            self.freelancer_min_price
            <= self.client_budget
        )

    # =========================================================
    # TIMELINE RANGE
    # =========================================================

    def _timeline_range_exists(self):

        return (
            self.freelancer_min_days
            <= self.client_maximum_days
        )

    # =========================================================
    # DUPLICATE OFFER
    # =========================================================

    def _is_duplicate_offer(
        self,
        price,
        timeline_days,
        tolerance=0.01
    ):

        price = float(price)
        timeline_days = float(timeline_days)

        for previous in self.previous_offers:

            price_same = (
                abs(
                    previous["price"]
                    - price
                )
                <= tolerance
            )

            days_same = (
                abs(
                    previous["timeline_days"]
                    - timeline_days
                )
                <= tolerance
            )

            if price_same and days_same:

                return True

        return False

    # =========================================================
    # LAST OFFER BY AGENT
    # =========================================================

    def _last_offer_by_agent(
        self,
        agent_name
    ):

        for record in reversed(
            self.history
        ):

            if record["agent"] == agent_name:

                return {
                    "price": record["price"],
                    "timeline_days": record["timeline_days"]
                }

        return None

    # =========================================================
    # RECORD OFFER
    # =========================================================

    def _record_offer(
        self,
        round_number,
        agent,
        action,
        offer
    ):

        record = {

            "round": int(
                round_number
            ),

            "agent": agent,

            "action": action,

            "price": round(
                float(
                    offer["price"]
                ),
                2
            ),

            "timeline_days": round(
                float(
                    offer["timeline_days"]
                ),
                2
            )
        }

        self.history.append(
            record
        )

        self.previous_offers.append({

            "price": float(
                offer["price"]
            ),

            "timeline_days": float(
                offer["timeline_days"]
            )
        })

    # =========================================================
    # SET AGREEMENT
    # =========================================================

    def _set_agreement(
        self,
        price,
        timeline_days
    ):

        self.agreement = True

        self.final_price = round(
            float(price),
            2
        )

        self.final_timeline_days = round(
            float(timeline_days),
            2
        )

        self.failure_reason = None

    # =========================================================
    # DISTANCE BETWEEN OFFERS
    # =========================================================

    def _offer_distance(
        self,
        offer_a,
        offer_b
    ):

        price_range = max(
            self.client_budget
            - self.freelancer_min_price,
            1.0
        )

        days_range = max(
            self.client_maximum_days
            - self.freelancer_min_days,
            1.0
        )

        price_distance = abs(
            float(offer_a["price"])
            -
            float(offer_b["price"])
        ) / price_range

        days_distance = abs(
            float(offer_a["timeline_days"])
            -
            float(offer_b["timeline_days"])
        ) / days_range

        return (
            0.70 * price_distance
            +
            0.30 * days_distance
        )

    # =========================================================
    # CHECK NEAR AGREEMENT
    # =========================================================

    def _is_near_agreement(
        self,
        client_offer,
        freelancer_offer
    ):

        distance = self._offer_distance(
            client_offer,
            freelancer_offer
        )

        # 5% normalized distance is considered close enough
        # to attempt a compromise.

        return distance <= 0.05

    # =========================================================
    # CALCULATE COMPROMISE
    # =========================================================

    def _calculate_compromise(
        self,
        client_offer,
        freelancer_offer
    ):

        # -----------------------------------------------------
        # PRICE
        # -----------------------------------------------------

        client_price = float(
            client_offer["price"]
        )

        freelancer_price = float(
            freelancer_offer["price"]
        )

        price = (
            client_price
            +
            freelancer_price
        ) / 2.0

        # -----------------------------------------------------
        # TIMELINE
        # -----------------------------------------------------

        client_days = float(
            client_offer["timeline_days"]
        )

        freelancer_days = float(
            freelancer_offer["timeline_days"]
        )

        days = (
            client_days
            +
            freelancer_days
        ) / 2.0

        # -----------------------------------------------------
        # HARD CONSTRAINT CLAMP
        # -----------------------------------------------------

        price = max(
            self.freelancer_min_price,
            price
        )

        price = min(
            self.client_budget,
            price
        )

        days = max(
            self.freelancer_min_days,
            days
        )

        days = min(
            self.client_maximum_days,
            days
        )

        return {

            "price": round(
                price,
                2
            ),

            "timeline_days": round(
                days,
                2
            )
        }

    # =========================================================
    # FORCE CONTROLLED CONCESSION
    # =========================================================

    def _controlled_client_concession(
        self,
        current_offer,
        round_number
    ):

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

        # Client moves from target toward maximum.

        target_price = (
            self.client_target_budget
            +
            (
                self.client_budget
                -
                self.client_target_budget
            )
            * progress
        )

        current_price = float(
            current_offer["price"]
        )

        # Move at least partially toward target.

        new_price = (
            current_price
            +
            target_price
        ) / 2.0

        new_price = min(
            new_price,
            self.client_budget
        )

        new_price = max(
            new_price,
            self.freelancer_min_price
        )

        # Timeline.

        target_days = (
            self.client_desired_days
            +
            (
                self.client_maximum_days
                -
                self.client_desired_days
            )
            * progress
        )

        current_days = float(
            current_offer["timeline_days"]
        )

        new_days = (
            current_days
            +
            target_days
        ) / 2.0

        new_days = min(
            new_days,
            self.client_maximum_days
        )

        new_days = max(
            new_days,
            self.freelancer_min_days
        )

        return {

            "price": round(
                new_price,
                2
            ),

            "timeline_days": round(
                new_days,
                2
            )
        }

    # =========================================================
    # FORCE CONTROLLED FREELANCER CONCESSION
    # =========================================================

    def _controlled_freelancer_concession(
        self,
        current_offer,
        round_number
    ):

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

        # Freelancer moves from preferred price
        # toward minimum price.

        target_price = (
            self.freelancer_preferred_price
            -
            (
                self.freelancer_preferred_price
                -
                self.freelancer_min_price
            )
            * progress
        )

        current_price = float(
            current_offer["price"]
        )

        new_price = (
            current_price
            +
            target_price
        ) / 2.0

        new_price = max(
            new_price,
            self.freelancer_min_price
        )

        new_price = min(
            new_price,
            self.client_budget
        )

        # Timeline.

        target_days = (
            self.freelancer_preferred_days
            -
            (
                self.freelancer_preferred_days
                -
                self.freelancer_min_days
            )
            * progress
        )

        current_days = float(
            current_offer["timeline_days"]
        )

        new_days = (
            current_days
            +
            target_days
        ) / 2.0

        new_days = max(
            new_days,
            self.freelancer_min_days
        )

        new_days = min(
            new_days,
            self.client_maximum_days
        )

        return {

            "price": round(
                new_price,
                2
            ),

            "timeline_days": round(
                new_days,
                2
            )
        }

    # =========================================================
    # MAKE UNIQUE OFFER
    # =========================================================

    def _make_unique_offer(
        self,
        candidate,
        agent,
        round_number
    ):

        if not self._validate_offer(
            candidate
        ):
            return None

        # Already unique.
        if not self._is_duplicate_offer(
            candidate["price"],
            candidate["timeline_days"]
        ):
            return candidate

        # -----------------------------------------------------
        # Try small controlled adjustments.
        # -----------------------------------------------------

        price = float(
            candidate["price"]
        )

        days = float(
            candidate["timeline_days"]
        )

        if agent == "CLIENT":

            price_step = max(
                self.client_budget * 0.01,
                1.0
            )

            days_step = max(
                self.client_maximum_days * 0.02,
                1.0
            )

            for _ in range(5):

                price = min(
                    self.client_budget,
                    price + price_step
                )

                days = min(
                    self.client_maximum_days,
                    days + days_step
                )

                candidate = {

                    "price": round(
                        price,
                        2
                    ),

                    "timeline_days": round(
                        days,
                        2
                    )
                }

                if not self._is_duplicate_offer(
                    candidate["price"],
                    candidate["timeline_days"]
                ):
                    return candidate

        else:

            price_step = max(
                self.freelancer_preferred_price
                * 0.01,
                1.0
            )

            days_step = max(
                self.freelancer_preferred_days
                * 0.02,
                1.0
            )

            for _ in range(5):

                price = max(
                    self.freelancer_min_price,
                    price - price_step
                )

                days = max(
                    self.freelancer_min_days,
                    days - days_step
                )

                candidate = {

                    "price": round(
                        price,
                        2
                    ),

                    "timeline_days": round(
                        days,
                        2
                    )
                }

                if not self._is_duplicate_offer(
                    candidate["price"],
                    candidate["timeline_days"]
                ):
                    return candidate

        return None

    # =========================================================
    # NEGOTIATE
    # =========================================================

    def negotiate(self):

        # -----------------------------------------------------
        # RESET
        # -----------------------------------------------------

        self.history = []

        self.previous_offers = []

        self.agreement = False

        self.final_price = None

        self.final_timeline_days = None

        self.failure_reason = None

        # =====================================================
        # PRE-CHECK
        # =====================================================

        if not self._price_range_exists():

            self.failure_reason = (
                "No feasible price range: "
                "freelancer minimum price exceeds "
                "client maximum budget."
            )

            return self._build_result()

        if not self._timeline_range_exists():

            self.failure_reason = (
                "No feasible timeline range: "
                "freelancer minimum timeline exceeds "
                "client maximum timeline."
            )

            return self._build_result()

        # =====================================================
        # INITIAL CLIENT OFFER
        # =====================================================

        current_offer = (
            self.client_agent.get_initial_offer()
        )

        if not self._validate_offer(
            current_offer
        ):

            self.failure_reason = (
                "Client generated an invalid initial offer."
            )

            return self._build_result()

        # Make sure initial offer is globally feasible.

        if not self._is_feasible(
            current_offer["price"],
            current_offer["timeline_days"]
        ):

            current_offer = {
                "price": round(
                    max(
                        self.freelancer_min_price,
                        min(
                            self.client_budget,
                            current_offer["price"]
                        )
                    ),
                    2
                ),

                "timeline_days": round(
                    max(
                        self.freelancer_min_days,
                        min(
                            self.client_maximum_days,
                            current_offer["timeline_days"]
                        )
                    ),
                    2
                )
            }

        self._record_offer(
            1,
            "CLIENT",
            "INITIAL_OFFER",
            current_offer
        )

        # =====================================================
        # NEGOTIATION LOOP
        # =====================================================

        for round_number in range(
            1,
            self.max_rounds + 1
        ):

            # =================================================
            # FREELANCER EVALUATES CLIENT
            # =================================================

            freelancer_decision = (
                self.freelancer_agent.evaluate_offer(
                    client_price=current_offer["price"],
                    client_days=current_offer["timeline_days"],
                    round_number=round_number
                )
            )

            # -------------------------------------------------
            # FREELANCER ACCEPTS
            # -------------------------------------------------

            if (
                freelancer_decision
                == "ACCEPT"
                and
                self._is_feasible(
                    current_offer["price"],
                    current_offer["timeline_days"]
                )
            ):

                self._record_offer(
                    round_number,
                    "FREELANCER",
                    "ACCEPT",
                    current_offer
                )

                self._set_agreement(
                    current_offer["price"],
                    current_offer["timeline_days"]
                )

                return self._build_result()

            # -------------------------------------------------
            # FREELANCER REJECTS
            # -------------------------------------------------

            if freelancer_decision == "REJECT":

                # Try compromise before final rejection.

                freelancer_last = (
                    self._last_offer_by_agent(
                        "FREELANCER"
                    )
                )

                if freelancer_last:

                    compromise = (
                        self._calculate_compromise(
                            current_offer,
                            freelancer_last
                        )
                    )

                    if self._is_feasible(
                        compromise["price"],
                        compromise["timeline_days"]
                    ):

                        client_ok = (
                            self.client_agent.evaluate_offer(
                                compromise["price"],
                                compromise["timeline_days"],
                                round_number=round_number
                            )
                        )

                        freelancer_ok = (
                            self.freelancer_agent.evaluate_offer(
                                compromise["price"],
                                compromise["timeline_days"],
                                round_number=round_number
                            )
                        )

                        if (
                            client_ok == "ACCEPT"
                            and
                            freelancer_ok == "ACCEPT"
                        ):

                            self._record_offer(
                                round_number,
                                "SYSTEM",
                                "COMPROMISE_ACCEPTED",
                                compromise
                            )

                            self._set_agreement(
                                compromise["price"],
                                compromise["timeline_days"]
                            )

                            return self._build_result()

                self._record_offer(
                    round_number,
                    "FREELANCER",
                    "REJECT",
                    current_offer
                )

                self.failure_reason = (
                    "Freelancer rejected the client's offer."
                )

                return self._build_result()

            # =================================================
            # FREELANCER COUNTER
            # =================================================

            freelancer_counter = (
                self.freelancer_agent.make_counter_offer(
                    client_price=current_offer["price"],
                    client_days=current_offer["timeline_days"],
                    round_number=round_number
                )
            )

            # -------------------------------------------------
            # UNIQUE FREELANCER COUNTER
            # -------------------------------------------------

            freelancer_counter = (
                self._make_unique_offer(
                    freelancer_counter,
                    "FREELANCER",
                    round_number
                )
            )

            if freelancer_counter is None:

                # Attempt compromise.

                compromise = (
                    self._calculate_compromise(
                        current_offer,
                        {
                            "price":
                                self.freelancer_preferred_price,

                            "timeline_days":
                                self.freelancer_preferred_days
                        }
                    )
                )

                if (
                    self._is_feasible(
                        compromise["price"],
                        compromise["timeline_days"]
                    )
                    and
                    not self._is_duplicate_offer(
                        compromise["price"],
                        compromise["timeline_days"]
                    )
                ):

                    freelancer_counter = compromise

                else:

                    self.failure_reason = (
                        "No new feasible freelancer offer "
                        "could be generated."
                    )

                    return self._build_result()

            self._record_offer(
                round_number,
                "FREELANCER",
                "COUNTER",
                freelancer_counter
            )

            # =================================================
            # CLIENT EVALUATES FREELANCER
            # =================================================

            client_decision = (
                self.client_agent.evaluate_offer(
                    price=freelancer_counter["price"],
                    timeline_days=freelancer_counter["timeline_days"],
                    quality_score=1.0,
                    round_number=round_number
                )
            )

            # -------------------------------------------------
            # CLIENT ACCEPTS
            # -------------------------------------------------

            if (
                client_decision
                == "ACCEPT"
                and
                self._is_feasible(
                    freelancer_counter["price"],
                    freelancer_counter["timeline_days"]
                )
            ):

                self._record_offer(
                    round_number,
                    "CLIENT",
                    "ACCEPT",
                    freelancer_counter
                )

                self._set_agreement(
                    freelancer_counter["price"],
                    freelancer_counter["timeline_days"]
                )

                return self._build_result()

            # -------------------------------------------------
            # CLIENT REJECTS
            # -------------------------------------------------

            if client_decision == "REJECT":

                self._record_offer(
                    round_number,
                    "CLIENT",
                    "REJECT",
                    freelancer_counter
                )

                self.failure_reason = (
                    "Client rejected the freelancer's offer."
                )

                return self._build_result()

            # =================================================
            # CHECK NEAR AGREEMENT
            # =================================================

            if self._is_near_agreement(
                current_offer,
                freelancer_counter
            ):

                compromise = (
                    self._calculate_compromise(
                        current_offer,
                        freelancer_counter
                    )
                )

                if self._is_feasible(
                    compromise["price"],
                    compromise["timeline_days"]
                ):

                    client_check = (
                        self.client_agent.evaluate_offer(
                            compromise["price"],
                            compromise["timeline_days"],
                            round_number=round_number
                        )
                    )

                    freelancer_check = (
                        self.freelancer_agent.evaluate_offer(
                            compromise["price"],
                            compromise["timeline_days"],
                            round_number=round_number
                        )
                    )

                    if (
                        client_check == "ACCEPT"
                        and
                        freelancer_check == "ACCEPT"
                    ):

                        self._record_offer(
                            round_number,
                            "SYSTEM",
                            "COMPROMISE_ACCEPTED",
                            compromise
                        )

                        self._set_agreement(
                            compromise["price"],
                            compromise["timeline_days"]
                        )

                        return self._build_result()

            # =================================================
            # CLIENT COUNTER
            # =================================================

            client_counter = (
                self.client_agent.make_counter_offer(
                    freelancer_price=freelancer_counter["price"],
                    freelancer_days=freelancer_counter["timeline_days"],
                    round_number=round_number,
                    freelancer_min_price=self.freelancer_min_price,
                    freelancer_min_days=self.freelancer_min_days
                )
            )

            # -------------------------------------------------
            # MAKE UNIQUE CLIENT OFFER
            # -------------------------------------------------

            client_counter = (
                self._make_unique_offer(
                    client_counter,
                    "CLIENT",
                    round_number
                )
            )

            if client_counter is None:

                # Try controlled concession.

                client_counter = (
                    self._controlled_client_concession(
                        freelancer_counter,
                        round_number
                    )
                )

                client_counter = (
                    self._make_unique_offer(
                        client_counter,
                        "CLIENT",
                        round_number
                    )
                )

            if client_counter is None:

                self.failure_reason = (
                    "No new feasible client offer "
                    "could be generated."
                )

                return self._build_result()

            # -------------------------------------------------
            # FEASIBILITY
            # -------------------------------------------------

            if not self._is_feasible(
                client_counter["price"],
                client_counter["timeline_days"]
            ):

                client_counter = (
                    self._controlled_client_concession(
                        client_counter,
                        round_number
                    )
                )

            if not self._validate_offer(
                client_counter
            ):

                self.failure_reason = (
                    "Client generated an invalid counter offer."
                )

                return self._build_result()

            # -------------------------------------------------
            # RECORD
            # -------------------------------------------------

            self._record_offer(
                round_number,
                "CLIENT",
                "COUNTER",
                client_counter
            )

            # -------------------------------------------------
            # NEXT ROUND
            # -------------------------------------------------

            current_offer = client_counter

        # =====================================================
        # MAX ROUNDS
        # =====================================================

        # One final compromise attempt.

        client_last = (
            self._last_offer_by_agent(
                "CLIENT"
            )
        )

        freelancer_last = (
            self._last_offer_by_agent(
                "FREELANCER"
            )
        )

        if (
            client_last
            and
            freelancer_last
        ):

            final_compromise = (
                self._calculate_compromise(
                    client_last,
                    freelancer_last
                )
            )

            if self._is_feasible(
                final_compromise["price"],
                final_compromise["timeline_days"]
            ):

                client_check = (
                    self.client_agent.evaluate_offer(
                        final_compromise["price"],
                        final_compromise["timeline_days"],
                        round_number=self.max_rounds
                    )
                )

                freelancer_check = (
                    self.freelancer_agent.evaluate_offer(
                        final_compromise["price"],
                        final_compromise["timeline_days"],
                        round_number=self.max_rounds
                    )
                )

                if (
                    client_check == "ACCEPT"
                    and
                    freelancer_check == "ACCEPT"
                ):

                    self._record_offer(
                        self.max_rounds,
                        "SYSTEM",
                        "FINAL_COMPROMISE_ACCEPTED",
                        final_compromise
                    )

                    self._set_agreement(
                        final_compromise["price"],
                        final_compromise["timeline_days"]
                    )

                    return self._build_result()

        self.failure_reason = (
            f"No agreement reached within "
            f"{self.max_rounds} negotiation rounds."
        )

        return self._build_result()

    # =========================================================
    # RESULT
    # =========================================================

    def _build_result(self):

        return {

            "agreement":
                self.agreement,

            "final_price":
                self.final_price,

            "final_timeline_days":
                self.final_timeline_days,

            "rounds":
                self._calculate_rounds(),

            "failure_reason":
                self.failure_reason,

            "history":
                self.history.copy()
        }

    # =========================================================
    # ROUND COUNT
    # =========================================================

    def _calculate_rounds(self):

        if not self.history:

            return 0

        return max(
            record["round"]
            for record in self.history
        )