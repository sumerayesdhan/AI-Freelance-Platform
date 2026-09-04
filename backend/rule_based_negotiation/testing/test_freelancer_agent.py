from rule_based_negotiation.agents.freelancer_agent import FreelancerAgent


def main():

    freelancer = FreelancerAgent(
        minimum_price=60000,
        preferred_price=90000,
        minimum_days=180,
        preferred_days=270,
        maximum_rounds=10
    )

    print("=" * 70)
    print("FREELANCER AGENT TEST")
    print("=" * 70)

    initial = freelancer.get_initial_offer()

    print("\nInitial Offer:")
    print(initial)

    test_offers = [
        (90000, 270),
        (85000, 250),
        (80000, 240),
        (70000, 210),
        (60000, 180),
        (50000, 180),
        (100000, 300),
        (80000, 100),
    ]

    print("\nOffer Evaluation:")

    for round_number, (price, days) in enumerate(
        test_offers,
        start=1
    ):

        decision = freelancer.evaluate_offer(
            price,
            days,
            round_number
        )

        utility = freelancer.calculate_utility(
            price,
            days
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

        counter = freelancer.make_counter_offer(
            client_price=75000,
            client_days=200,
            round_number=round_number
        )

        print(
            f"Round {round_number}: "
            f"{counter}"
        )

    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()