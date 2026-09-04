import math

from rule_based_negotiation.agents.client_agent import ClientAgent
from rule_based_negotiation.agents.freelancer_agent import FreelancerAgent


DEFAULT_MAX_ROUNDS = 10


class NegotiationEngine:
    """
    Autonomous two-agent rule-based negotiation engine.

    Flow:

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
        Repeat
              ↓
        Agreement / Failure

    Important:

    This engine only performs autonomous agent negotiation.

    Human client/freelancer acceptance is NOT handled here.
    Human acceptance will happen later after the final
    negotiation result is displayed.
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
        max_rounds=DEFAULT_MAX_ROUNDS,
    ):

        # =====================================================
        # VALIDATE INPUT
        # =====================================================

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

        # =====================================================
        # NORMALIZE
        # =====================================================

        self.client_target_budget = min(
            self.client_target_budget,
            self.client_budget,
        )

        self.client_desired_days = min(
            self.client_desired_days,
            self.client_maximum_days,
        )

        self.freelancer_preferred_price = max(
            self.freelancer_preferred_price,
            self.freelancer_min_price,
        )

        self.freelancer_preferred_days = max(
            self.freelancer_preferred_days,
            self.freelancer_min_days,
        )

        # =====================================================
        # CREATE AGENTS
        # =====================================================

        self.client_agent = ClientAgent(
            client_budget=self.client_budget,
            client_target_budget=self.client_target_budget,
            client_desired_days=self.client_desired_days,
            client_maximum_days=self.client_maximum_days,
            max_rounds=self.max_rounds,
        )

        self.freelancer_agent = FreelancerAgent(
            freelancer_min_price=self.freelancer_min_price,
            freelancer_preferred_price=self.freelancer_preferred_price,
            freelancer_min_days=self.freelancer_min_days,
            freelancer_preferred_days=self.freelancer_preferred_days,
            max_rounds=self.max_rounds,
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
    # NUMBER VALIDATION
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
    # OFFER VALIDATION
    # =========================================================

    @staticmethod
    def _validate_offer(offer):

        if not isinstance(
            offer,
            dict,
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

        except (TypeError, ValueError):

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
        timeline_days,
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
            and
            timeline_ok
        )

    # =========================================================
    # FEASIBLE RANGE CHECK
    # =========================================================

    def _price_range_exists(self):

        return (
            self.freelancer_min_price
            <= self.client_budget
        )

    def _timeline_range_exists(self):

        return (
            self.freelancer_min_days
            <= self.client_maximum_days
        )

    # =========================================================
    # CLAMP OFFER
    # =========================================================

    def _clamp_offer(
        self,
        offer,
    ):

        price = max(
            self.freelancer_min_price,
            min(
                self.client_budget,
                float(offer["price"]),
            ),
        )

        days = max(
            self.freelancer_min_days,
            min(
                self.client_maximum_days,
                float(offer["timeline_days"]),
            ),
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

    # =========================================================
    # DUPLICATE CHECK
    # =========================================================

    def _is_duplicate_offer(
        self,
        price,
        timeline_days,
        tolerance=0.01,
    ):

        price = float(price)
        timeline_days = float(timeline_days)

        for previous in self.previous_offers:

            same_price = (
                abs(
                    previous["price"]
                    -
                    price
                )
                <= tolerance
            )

            same_days = (
                abs(
                    previous["timeline_days"]
                    -
                    timeline_days
                )
                <= tolerance
            )

            if same_price and same_days:

                return True

        return False

    # =========================================================
    # RECORD OFFER
    # =========================================================

    def _record_offer(
        self,
        round_number,
        agent,
        action,
        offer,
    ):

        record = {
            "round": int(round_number),
            "agent": agent,
            "action": action,
            "price": round(
                float(offer["price"]),
                2,
            ),
            "timeline_days": round(
                float(offer["timeline_days"]),
                2,
            ),
        }

        self.history.append(
            record
        )

        self.previous_offers.append(
            {
                "price": float(
                    offer["price"]
                ),
                "timeline_days": float(
                    offer["timeline_days"]
                ),
            }
        )

    # =========================================================
    # LAST OFFER
    # =========================================================

    def _last_offer_by_agent(
        self,
        agent_name,
    ):

        for record in reversed(
            self.history
        ):

            if record["agent"] == agent_name:

                return {
                    "price": record["price"],
                    "timeline_days": record["timeline_days"],
                }

        return None

    # =========================================================
    # OFFER DISTANCE
    # =========================================================

    def _offer_distance(
        self,
        offer_a,
        offer_b,
    ):

        price_range = max(
            self.client_budget
            -
            self.freelancer_min_price,
            1.0,
        )

        days_range = max(
            self.client_maximum_days
            -
            self.freelancer_min_days,
            1.0,
        )

        price_distance = (
            abs(
                float(offer_a["price"])
                -
                float(offer_b["price"])
            )
            /
            price_range
        )

        days_distance = (
            abs(
                float(offer_a["timeline_days"])
                -
                float(offer_b["timeline_days"])
            )
            /
            days_range
        )

        return (
            0.70 * price_distance
            +
            0.30 * days_distance
        )

    # =========================================================
    # NEAR AGREEMENT
    # =========================================================

    def _is_near_agreement(
        self,
        client_offer,
        freelancer_offer,
    ):

        distance = self._offer_distance(
            client_offer,
            freelancer_offer,
        )

        return distance <= 0.08

    # =========================================================
    # COMPROMISE
    # =========================================================

    def _calculate_compromise(
        self,
        client_offer,
        freelancer_offer,
    ):

        client_price = float(
            client_offer["price"]
        )

        freelancer_price = float(
            freelancer_offer["price"]
        )

        client_days = float(
            client_offer["timeline_days"]
        )

        freelancer_days = float(
            freelancer_offer["timeline_days"]
        )

        # -----------------------------------------------------
        # PRICE
        # -----------------------------------------------------

        # Slightly freelancer-friendly midpoint.
        price = (
            (client_price * 0.45)
            +
            (freelancer_price * 0.55)
        )

        # -----------------------------------------------------
        # TIMELINE
        # -----------------------------------------------------

        days = (
            (client_days * 0.45)
            +
            (freelancer_days * 0.55)
        )

        compromise = {
            "price": price,
            "timeline_days": days,
        }

        return self._clamp_offer(
            compromise
        )

    # =========================================================
    # AGREEMENT
    # =========================================================

    def _set_agreement(
        self,
        price,
        timeline_days,
    ):

        self.agreement = True

        self.final_price = round(
            float(price),
            2,
        )

        self.final_timeline_days = round(
            float(timeline_days),
            2,
        )

        self.failure_reason = None

    # =========================================================
    # ACCEPT COMPROMISE
    # =========================================================

    def _try_compromise(
        self,
        client_offer,
        freelancer_offer,
        round_number,
        action="COMPROMISE_ACCEPTED",
    ):

        if not client_offer:
            return False

        if not freelancer_offer:
            return False

        compromise = self._calculate_compromise(
            client_offer,
            freelancer_offer,
        )

        if not self._is_feasible(
            compromise["price"],
            compromise["timeline_days"],
        ):
            return False

        # -----------------------------------------------------
        # IMPORTANT:
        # If both offers are already close enough and the
        # compromise is inside both hard reservation zones,
        # settlement is valid.
        # -----------------------------------------------------

        if not self._is_near_agreement(
            client_offer,
            freelancer_offer,
        ):
            return False

        client_decision = (
            self.client_agent.evaluate_offer(
                price=compromise["price"],
                timeline_days=compromise["timeline_days"],
                round_number=round_number,
            )
        )

        freelancer_decision = (
            self.freelancer_agent.evaluate_offer(
                client_price=compromise["price"],
                client_days=compromise["timeline_days"],
                round_number=round_number,
            )
        )

        # -----------------------------------------------------
        # NORMAL BOTH-AGREE PATH
        # -----------------------------------------------------

        if (
            client_decision == "ACCEPT"
            and
            freelancer_decision == "ACCEPT"
        ):

            self._record_offer(
                round_number,
                "SYSTEM",
                action,
                compromise,
            )

            self._set_agreement(
                compromise["price"],
                compromise["timeline_days"],
            )

            return True

        # -----------------------------------------------------
        # LATE-ROUND FEASIBLE SETTLEMENT
        # -----------------------------------------------------

        # If both parties are within their hard reservation
        # limits and we are near the end, settle instead of
        # allowing endless oscillation.
        if round_number >= max(
            3,
            int(self.max_rounds * 0.80),
        ):

            client_feasible = (
                compromise["price"]
                <= self.client_budget
                and
                compromise["timeline_days"]
                <= self.client_maximum_days
            )

            freelancer_feasible = (
                compromise["price"]
                >= self.freelancer_min_price
                and
                compromise["timeline_days"]
                >= self.freelancer_min_days
            )

            if (
                client_feasible
                and
                freelancer_feasible
            ):

                self._record_offer(
                    round_number,
                    "SYSTEM",
                    "LATE_ROUND_SETTLEMENT",
                    compromise,
                )

                self._set_agreement(
                    compromise["price"],
                    compromise["timeline_days"],
                )

                return True

        return False

    # =========================================================
    # NEGOTIATE
    # =========================================================

    def negotiate(self):

        # =====================================================
        # RESET
        # =====================================================

        self.history = []
        self.previous_offers = []

        self.agreement = False
        self.final_price = None
        self.final_timeline_days = None
        self.failure_reason = None

        self.client_agent.reset()
        self.freelancer_agent.reset()

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

        current_offer = self._clamp_offer(
            current_offer
        )

        if not self._validate_offer(
            current_offer
        ):

            self.failure_reason = (
                "Client generated an invalid initial offer."
            )

            return self._build_result()

        self._record_offer(
            1,
            "CLIENT",
            "INITIAL_OFFER",
            current_offer,
        )

        # =====================================================
        # NEGOTIATION LOOP
        # =====================================================

        for round_number in range(
            1,
            self.max_rounds + 1,
        ):

            # =================================================
            # FREELANCER EVALUATES CLIENT
            # =================================================

            freelancer_decision = (
                self.freelancer_agent.evaluate_offer(
                    client_price=current_offer["price"],
                    client_days=current_offer["timeline_days"],
                    round_number=round_number,
                )
            )

            # -------------------------------------------------
            # FREELANCER ACCEPTS
            # -------------------------------------------------

            if (
                freelancer_decision == "ACCEPT"
                and
                self._is_feasible(
                    current_offer["price"],
                    current_offer["timeline_days"],
                )
            ):

                self._record_offer(
                    round_number,
                    "FREELANCER",
                    "ACCEPT",
                    current_offer,
                )

                self._set_agreement(
                    current_offer["price"],
                    current_offer["timeline_days"],
                )

                return self._build_result()

            # -------------------------------------------------
            # FREELANCER REJECTS
            # -------------------------------------------------

            if freelancer_decision == "REJECT":

                previous_freelancer = (
                    self._last_offer_by_agent(
                        "FREELANCER"
                    )
                )

                if previous_freelancer:

                    if self._try_compromise(
                        current_offer,
                        previous_freelancer,
                        round_number,
                    ):
                        return self._build_result()

                self._record_offer(
                    round_number,
                    "FREELANCER",
                    "REJECT",
                    current_offer,
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
                    round_number=round_number,
                    client_budget=self.client_budget,
                )
            )

            freelancer_counter = self._clamp_offer(
                freelancer_counter
            )

            # -------------------------------------------------
            # DUPLICATE PROTECTION
            # -------------------------------------------------

            if self._is_duplicate_offer(
                freelancer_counter["price"],
                freelancer_counter["timeline_days"],
            ):

                # Move directly toward compromise.
                freelancer_counter = (
                    self._calculate_compromise(
                        current_offer,
                        {
                            "price":
                                self.freelancer_preferred_price,
                            "timeline_days":
                                self.freelancer_preferred_days,
                        },
                    )
                )

            if self._is_duplicate_offer(
                freelancer_counter["price"],
                freelancer_counter["timeline_days"],
            ):

                self.failure_reason = (
                    "Freelancer could not generate "
                    "a new offer."
                )

                return self._build_result()

            self._record_offer(
                round_number,
                "FREELANCER",
                "COUNTER",
                freelancer_counter,
            )

            # =================================================
            # CLIENT EVALUATES FREELANCER
            # =================================================

            client_decision = (
                self.client_agent.evaluate_offer(
                    price=freelancer_counter["price"],
                    timeline_days=freelancer_counter["timeline_days"],
                    round_number=round_number,
                )
            )

            # -------------------------------------------------
            # CLIENT ACCEPTS
            # -------------------------------------------------

            if (
                client_decision == "ACCEPT"
                and
                self._is_feasible(
                    freelancer_counter["price"],
                    freelancer_counter["timeline_days"],
                )
            ):

                self._record_offer(
                    round_number,
                    "CLIENT",
                    "ACCEPT",
                    freelancer_counter,
                )

                self._set_agreement(
                    freelancer_counter["price"],
                    freelancer_counter["timeline_days"],
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
                    freelancer_counter,
                )

                self.failure_reason = (
                    "Client rejected the freelancer's offer."
                )

                return self._build_result()

            # =================================================
            # TRY COMPROMISE
            # =================================================

            if self._try_compromise(
                current_offer,
                freelancer_counter,
                round_number,
            ):

                return self._build_result()

            # =================================================
            # CLIENT COUNTER
            # =================================================

            client_counter = (
                self.client_agent.make_counter_offer(
                    freelancer_price=freelancer_counter["price"],
                    freelancer_days=freelancer_counter["timeline_days"],
                    round_number=round_number,
                )
            )

            client_counter = self._clamp_offer(
                client_counter
            )

            # -------------------------------------------------
            # DUPLICATE PROTECTION
            # -------------------------------------------------

            if self._is_duplicate_offer(
                client_counter["price"],
                client_counter["timeline_days"],
            ):

                client_counter = (
                    self._calculate_compromise(
                        freelancer_counter,
                        {
                            "price":
                                self.client_target_budget,
                            "timeline_days":
                                self.client_desired_days,
                        },
                    )
                )

            client_counter = self._clamp_offer(
                client_counter
            )

            if self._is_duplicate_offer(
                client_counter["price"],
                client_counter["timeline_days"],
            ):

                self.failure_reason = (
                    "Client could not generate "
                    "a new offer."
                )

                return self._build_result()

            self._record_offer(
                round_number,
                "CLIENT",
                "COUNTER",
                client_counter,
            )

            current_offer = client_counter

        # =====================================================
        # FINAL SETTLEMENT ATTEMPT
        # =====================================================

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
                    freelancer_last,
                )
            )

            if self._is_feasible(
                final_compromise["price"],
                final_compromise["timeline_days"],
            ):

                # At the end of the maximum rounds, if the
                # compromise satisfies both hard reservation
                # values, settle the negotiation.
                if (
                    final_compromise["price"]
                    >= self.freelancer_min_price
                    and
                    final_compromise["price"]
                    <= self.client_budget
                    and
                    final_compromise["timeline_days"]
                    >= self.freelancer_min_days
                    and
                    final_compromise["timeline_days"]
                    <= self.client_maximum_days
                ):

                    self._record_offer(
                        self.max_rounds,
                        "SYSTEM",
                        "FINAL_COMPROMISE_ACCEPTED",
                        final_compromise,
                    )

                    self._set_agreement(
                        final_compromise["price"],
                        final_compromise["timeline_days"],
                    )

                    return self._build_result()

        # =====================================================
        # FAILURE
        # =====================================================

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
            "agreement": self.agreement,
            "final_price": self.final_price,
            "final_timeline_days":
                self.final_timeline_days,
            "rounds": self._calculate_rounds(),
            "failure_reason":
                self.failure_reason,
            "history":
                self.history.copy(),
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