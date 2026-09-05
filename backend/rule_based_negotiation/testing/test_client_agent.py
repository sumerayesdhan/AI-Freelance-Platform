from rule_based_negotiation.agents.client_agent import ClientAgent


def main():

    client = ClientAgent(
        maximum_budget=115000,
        target_budget=98000,
        desired_days=180,
        maximum_days=360,
        max_rounds=10
    )

    print("=" * 70)
    print("CLIENT AGENT TEST")
    print("=" * 70)

    initial = client.get_initial_offer()

    print("\nInitial Offer:")
    print(initial)

    test_offers = [
        (98000, 180),
        (100000, 200),
        (105000, 240),
        (110000, 300),
        (114000, 350),
        (130000, 180),
        (50000, 180),
        (100000, 500),
    ]

    print("\nOffer Evaluation:")

    for round_number, (price, days) in enumerate(
        test_offers,
        start=1
    ):

        decision = client.evaluate_offer(
            price,
            days,
            round_number=round_number
        )

        utility = client.calculate_utility(
            min(price, client.maximum_budget),
            min(days, client.maximum_days)
        )

        print(
            f"Round {round_number}: "
            f"${price:,.2f}, "
            f"{days} days "
            f"-> {decision} "
            f"(utility={utility:.3f})"
        )

    print("\nCounter Offers:")

    for round_number in range(1, 6):

        counter = client.make_counter_offer(
            freelancer_price=115000,
            freelancer_days=300,
            round_number=round_number,
            freelancer_min_price=60000,
            freelancer_min_days=180
        )

        print(
            f"Round {round_number}: "
            f"{counter}"
        )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()