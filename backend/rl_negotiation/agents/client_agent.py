class ClientAgent:
    """
    Autonomous rule/utility-based client negotiation agent.

    The client agent negotiates automatically with the
    PPO freelancer agent.

    The human client does NOT participate during negotiation.
    """

    def __init__(
        self,
        budget,
        desired_days,
        minimum_price=None,
        minimum_days=None
    ):
        self.budget = float(budget)
        self.desired_days = float(desired_days)

        # Minimum acceptable price for the client.
        # If not provided, use 60% of budget.
        self.minimum_price = (
            float(minimum_price)
            if minimum_price is not None
            else self.budget * 0.60
        )

        # Maximum timeline client can tolerate.
        # If not provided, use desired timeline + 5 days.
        self.maximum_days = (
            float(minimum_days)
            if minimum_days is not None
            else self.desired_days + 5.0
        )

    def evaluate_offer(self, price, timeline_days):
        """
        Evaluate a freelancer proposal.

        Returns:
            ACCEPT
            COUNTER
            REJECT
        """

        price = float(price)
        timeline_days = float(timeline_days)

        # -------------------------------------------------
        # ACCEPT
        # -------------------------------------------------

        if (
            price <= self.budget
            and
            timeline_days <= self.maximum_days
        ):
            return "ACCEPT"

        # -------------------------------------------------
        # REJECT
        # -------------------------------------------------

        if (
            price > self.budget * 1.20
            or
            timeline_days > self.maximum_days + 10
        ):
            return "REJECT"

        # -------------------------------------------------
        # COUNTER
        # -------------------------------------------------

        return "COUNTER"

    def make_counter_offer(self, price, timeline_days):
        """
        Generate an autonomous client counter-offer.

        The client moves the freelancer proposal toward
        the client's preferred budget and timeline.
        """

        price = float(price)
        timeline_days = float(timeline_days)

        # -------------------------------------------------
        # PRICE COUNTER
        # -------------------------------------------------

        if price > self.budget:
            new_price = (
                price + self.budget
            ) / 2.0

        else:
            # If price is already within budget,
            # client tries to improve the deal slightly.
            new_price = max(
                self.minimum_price,
                price * 0.97
            )

        # Never exceed client budget.
        new_price = min(
            new_price,
            self.budget
        )

        # -------------------------------------------------
        # TIMELINE COUNTER
        # -------------------------------------------------

        if timeline_days > self.desired_days:

            new_timeline = (
                timeline_days
                + self.desired_days
            ) / 2.0

        else:

            new_timeline = timeline_days

        new_timeline = max(
            self.desired_days,
            new_timeline
        )

        return {
            "price": round(new_price, 2),
            "timeline_days": round(
                new_timeline,
                2
            )
        }

    def get_initial_offer(self):
        """
        Generate the client's initial offer.
        """

        return {
            "price": round(
                self.budget * 0.75,
                2
            ),
            "timeline_days": round(
                self.desired_days,
                2
            )
        }