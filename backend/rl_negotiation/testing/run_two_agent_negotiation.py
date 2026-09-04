from engine.negotiation_engine import NegotiationEngine


def main():

    engine = NegotiationEngine(
        client_budget=1100,
        client_desired_days=18,
        freelancer_min_price=750,
        freelancer_min_days=12,
        freelancer_initial_price=1200,
        max_rounds=10
    )

    result = engine.negotiate()

    print("\n")
    print("RESULT SENT TO CLIENT")
    print("------------------------------")
    print(
        f"Final Price: "
        f"${result['final_price']:.2f}"
    )
    print(
        f"Timeline: "
        f"{result['final_timeline_days']:.2f} days"
    )
    print(
        f"Status: "
        f"{'AGREEMENT' if result['agreement'] else 'NO AGREEMENT'}"
    )

    print("\n")
    print("RESULT SENT TO FREELANCER")
    print("------------------------------")
    print(
        f"Final Price: "
        f"${result['final_price']:.2f}"
    )
    print(
        f"Timeline: "
        f"{result['final_timeline_days']:.2f} days"
    )
    print(
        f"Status: "
        f"{'AGREEMENT' if result['agreement'] else 'NO AGREEMENT'}"
    )


if __name__ == "__main__":
    main()