from rl_negotiation.agents.client_agent import ClientAgent
from rl_negotiation.agents.freelancer_ppo_agent import FreelancerPPOAgent

class NegotiationEngine:
    """
    Coordinates autonomous negotiation between:

        Client Agent
              ↕
        Freelancer PPO Agent

    No human input is required during negotiation.
    """

    def __init__(
        self,
        client_budget,
        client_desired_days,
        freelancer_min_price,
        freelancer_min_days,
        freelancer_initial_price,
        max_rounds=10
    ):

        self.client_budget = float(client_budget)
        self.client_desired_days = float(
            client_desired_days
        )

        self.freelancer_min_price = float(
            freelancer_min_price
        )

        self.freelancer_min_days = float(
            freelancer_min_days
        )

        self.freelancer_initial_price = float(
            freelancer_initial_price
        )

        self.max_rounds = max_rounds

        # -------------------------------------------------
        # Create Client Agent
        # -------------------------------------------------

        self.client_agent = ClientAgent(
            budget=self.client_budget,
            desired_days=self.client_desired_days
        )

        # -------------------------------------------------
        # Create PPO Freelancer Agent
        # -------------------------------------------------

        self.freelancer_agent = FreelancerPPOAgent(
            "models/freelancer_ppo"
        )

        # -------------------------------------------------
        # Negotiation history
        # -------------------------------------------------

        self.history = []

    # =====================================================
    # CONVERT NEGOTIATION STATE TO PPO OBSERVATION
    # =====================================================

    def _get_freelancer_observation(
        self,
        round_number,
        current_price,
        current_days
    ):

        observation = [

            # Current round
            round_number / self.max_rounds,

            # Client budget
            self.client_budget / 2000.0,

            # Freelancer minimum price
            self.freelancer_min_price / 2000.0,

            # Current price
            current_price / 2000.0,

            # Client desired timeline
            self.client_desired_days / 60.0,

            # Freelancer minimum timeline
            self.freelancer_min_days / 60.0,

            # Current timeline
            current_days / 60.0,

            # Freelancer initial asking price
            self.freelancer_initial_price / 2000.0
        ]

        return observation

    # =====================================================
    # TRANSLATE PPO ACTION
    # =====================================================

    def _apply_freelancer_action(
        self,
        action,
        current_price,
        current_days
    ):

        # -------------------------------------------------
        # ACCEPT
        # -------------------------------------------------

        if action == 0:

            return (
                current_price,
                current_days,
                "ACCEPT"
            )

        # -------------------------------------------------
        # REJECT
        # -------------------------------------------------

        if action == 1:

            return (
                current_price,
                current_days,
                "REJECT"
            )

        # -------------------------------------------------
        # LOWER PRICE 10%
        # -------------------------------------------------

        if action == 2:

            current_price *= 0.90

            return (
                current_price,
                current_days,
                "LOWER_PRICE_10"
            )

        # -------------------------------------------------
        # LOWER PRICE 5%
        # -------------------------------------------------

        if action == 3:

            current_price *= 0.95

            return (
                current_price,
                current_days,
                "LOWER_PRICE_5"
            )

        # -------------------------------------------------
        # INCREASE PRICE 5%
        # -------------------------------------------------

        if action == 4:

            current_price *= 1.05

            current_price = min(
                current_price,
                self.client_budget
            )

            return (
                current_price,
                current_days,
                "INCREASE_PRICE_5"
            )

        # -------------------------------------------------
        # SHORTER TIMELINE
        # -------------------------------------------------

        if action == 5:

            current_days -= 2.0

            current_days = max(
                current_days,
                self.freelancer_min_days
            )

            return (
                current_price,
                current_days,
                "REQUEST_SHORTER_TIMELINE"
            )

        # -------------------------------------------------
        # BALANCED COUNTER
        # -------------------------------------------------

        if action == 6:

            current_price *= 0.95
            current_days -= 1.0

            current_price = max(
                current_price,
                self.freelancer_min_price
            )

            current_price = min(
                current_price,
                self.client_budget
            )

            current_days = max(
                current_days,
                self.freelancer_min_days
            )

            return (
                current_price,
                current_days,
                "BALANCED_COUNTER"
            )

        return (
            current_price,
            current_days,
            "UNKNOWN"
        )

    # =====================================================
    # RUN NEGOTIATION
    # =====================================================

    def negotiate(self):

        # -------------------------------------------------
        # Initial client offer
        # -------------------------------------------------

        initial_offer = (
            self.client_agent.get_initial_offer()
        )

        current_price = initial_offer["price"]

        current_days = initial_offer[
            "timeline_days"
        ]

        self.history = []

        print("\n")
        print("=" * 60)
        print("AUTONOMOUS TWO-AGENT NEGOTIATION")
        print("=" * 60)

        print(
            f"\nClient Initial Offer:"
            f" ${current_price:.2f}"
            f" / {current_days:.2f} days"
        )

        # =================================================
        # NEGOTIATION LOOP
        # =================================================

        for round_number in range(
            1,
            self.max_rounds + 1
        ):

            # ---------------------------------------------
            # FREELANCER TURN
            # ---------------------------------------------

            observation = (
                self._get_freelancer_observation(
                    round_number,
                    current_price,
                    current_days
                )
            )

            action = (
                self.freelancer_agent.get_action(
                    observation
                )
            )

            (
                current_price,
                current_days,
                action_name
            ) = self._apply_freelancer_action(
                action,
                current_price,
                current_days
            )

            freelancer_event = {
                "round": round_number,
                "agent": "FREELANCER",
                "action": action_name,
                "price": round(
                    current_price,
                    2
                ),
                "timeline_days": round(
                    current_days,
                    2
                )
            }

            self.history.append(
                freelancer_event
            )

            print(
                f"\nRound {round_number}"
            )

            print(
                f"FREELANCER AGENT:"
                f" {action_name}"
            )

            print(
                f"Proposal:"
                f" ${current_price:.2f}"
                f" / {current_days:.2f} days"
            )

            # ---------------------------------------------
            # FREELANCER ACCEPT
            # ---------------------------------------------

            if action == 0:

                if (
                    current_price <=
                    self.client_budget
                    and
                    current_days <=
                    self.client_agent.maximum_days
                ):

                    return self._result(
                        True,
                        current_price,
                        current_days,
                        round_number
                    )

                # Freelancer incorrectly accepted
                return self._result(
                    False,
                    current_price,
                    current_days,
                    round_number
                )

            # ---------------------------------------------
            # FREELANCER REJECT
            # ---------------------------------------------

            if action == 1:

                return self._result(
                    False,
                    current_price,
                    current_days,
                    round_number
                )

            # ---------------------------------------------
            # CLIENT EVALUATES
            # ---------------------------------------------

            client_decision = (
                self.client_agent.evaluate_offer(
                    current_price,
                    current_days
                )
            )

            print(
                f"CLIENT AGENT:"
                f" {client_decision}"
            )

            # ---------------------------------------------
            # CLIENT ACCEPTS
            # ---------------------------------------------

            if client_decision == "ACCEPT":

                return self._result(
                    True,
                    current_price,
                    current_days,
                    round_number
                )

            # ---------------------------------------------
            # CLIENT REJECTS
            # ---------------------------------------------

            if client_decision == "REJECT":

                return self._result(
                    False,
                    current_price,
                    current_days,
                    round_number
                )

            # ---------------------------------------------
            # CLIENT COUNTER
            # ---------------------------------------------

            counter = (
                self.client_agent.make_counter_offer(
                    current_price,
                    current_days
                )
            )

            current_price = counter["price"]

            current_days = counter[
                "timeline_days"
            ]

            client_event = {
                "round": round_number,
                "agent": "CLIENT",
                "action": "COUNTER",
                "price": current_price,
                "timeline_days": current_days
            }

            self.history.append(
                client_event
            )

            print(
                f"CLIENT COUNTER:"
                f" ${current_price:.2f}"
                f" / {current_days:.2f} days"
            )

        # -------------------------------------------------
        # Maximum rounds reached
        # -------------------------------------------------

        return self._result(
            False,
            current_price,
            current_days,
            self.max_rounds
        )

    # =====================================================
    # RESULT
    # =====================================================

    def _result(
        self,
        agreement,
        price,
        timeline_days,
        rounds
    ):

        result = {
            "agreement": bool(agreement),
            "final_price": round(
                price,
                2
            ),
            "final_timeline_days": round(
                timeline_days,
                2
            ),
            "rounds": rounds,
            "client_budget": round(
                self.client_budget,
                2
            ),
            "freelancer_min_price": round(
                self.freelancer_min_price,
                2
            ),
            "history": self.history
        }

        print("\n")
        print("=" * 60)
        print("FINAL NEGOTIATION RESULT")
        print("=" * 60)

        print(
            f"Agreement: "
            f"{'YES' if agreement else 'NO'}"
        )

        print(
            f"Final Price: "
            f"${price:.2f}"
        )

        print(
            f"Final Timeline: "
            f"{timeline_days:.2f} days"
        )

        print(
            f"Rounds: "
            f"{rounds}"
        )

        print("=" * 60)

        return result