from rule_based_negotiation.engine.negotiation_engine import (
    NegotiationEngine,
)


def run_test(
    name,
    client_budget,
    client_target_budget,
    client_desired_days,
    client_maximum_days,
    freelancer_min_price,
    freelancer_preferred_price,
    freelancer_min_days,
    freelancer_preferred_days,
    max_rounds=10,
):

    print("\n")
    print("#" * 70)
    print(f"TEST: {name}")
    print("#" * 70)

    engine = NegotiationEngine(
        client_budget=client_budget,
        client_target_budget=client_target_budget,
        client_desired_days=client_desired_days,
        client_maximum_days=client_maximum_days,
        freelancer_min_price=freelancer_min_price,
        freelancer_preferred_price=freelancer_preferred_price,
        freelancer_min_days=freelancer_min_days,
        freelancer_preferred_days=freelancer_preferred_days,
        max_rounds=max_rounds,
    )

    result = engine.negotiate()

    print("\nNEGOTIATION HISTORY")
    print("-" * 70)

    for record in result["history"]:
        print(record)

    print("\nTEST RESULT")
    print("-" * 70)

    print(
        f"Agreement: "
        f"{result['agreement']}"
    )

    print(
        f"Final Price: "
        f"{result['final_price']}"
    )

    print(
        f"Final Timeline: "
        f"{result['final_timeline_days']}"
    )

    print(
        f"Rounds: "
        f"{result['rounds']}"
    )

    print(
        f"Failure Reason: "
        f"{result['failure_reason']}"
    )

    return result


def main():

    # =========================================================
    # TEST 1
    # NORMAL NEGOTIATION
    # =========================================================

    run_test(
        name="Normal Negotiation",

        client_budget=1200,
        client_target_budget=900,
        client_desired_days=18,
        client_maximum_days=30,

        freelancer_min_price=750,
        freelancer_preferred_price=1100,
        freelancer_min_days=14,
        freelancer_preferred_days=24,

        max_rounds=10,
    )

    # =========================================================
    # TEST 2
    # LOW CLIENT BUDGET
    # =========================================================

    run_test(
        name="Low Client Budget",

        client_budget=800,
        client_target_budget=700,
        client_desired_days=18,
        client_maximum_days=30,

        freelancer_min_price=750,
        freelancer_preferred_price=1100,
        freelancer_min_days=14,
        freelancer_preferred_days=24,

        max_rounds=10,
    )

    # =========================================================
    # TEST 3
    # IMPOSSIBLE PRICE
    # =========================================================

    run_test(
        name="Impossible Price",

        client_budget=600,
        client_target_budget=500,
        client_desired_days=18,
        client_maximum_days=30,

        freelancer_min_price=900,
        freelancer_preferred_price=1200,
        freelancer_min_days=14,
        freelancer_preferred_days=24,

        max_rounds=10,
    )

    # =========================================================
    # TEST 4
    # IMPOSSIBLE TIMELINE
    # =========================================================

    run_test(
        name="Impossible Timeline",

        client_budget=1500,
        client_target_budget=1000,
        client_desired_days=10,
        client_maximum_days=12,

        freelancer_min_price=800,
        freelancer_preferred_price=1200,
        freelancer_min_days=20,
        freelancer_preferred_days=30,

        max_rounds=10,
    )

    # =========================================================
    # TEST 5
    # HIGH CLIENT BUDGET
    # =========================================================

    run_test(
        name="High Budget",

        client_budget=2000,
        client_target_budget=1600,
        client_desired_days=30,
        client_maximum_days=45,

        freelancer_min_price=900,
        freelancer_preferred_price=1600,
        freelancer_min_days=20,
        freelancer_preferred_days=30,

        max_rounds=10,
    )

    # =========================================================
    # TEST 6
    # BOUNDARY FEASIBLE
    # =========================================================

    run_test(
        name="Boundary Feasible",

        client_budget=800,
        client_target_budget=750,
        client_desired_days=20,
        client_maximum_days=25,

        freelancer_min_price=800,
        freelancer_preferred_price=1000,
        freelancer_min_days=20,
        freelancer_preferred_days=25,

        max_rounds=10,
    )

    # =========================================================
    # TEST 7
    # FLEXIBLE NEGOTIATION
    # =========================================================

    run_test(
        name="Flexible Negotiation",

        client_budget=1500,
        client_target_budget=1000,
        client_desired_days=20,
        client_maximum_days=40,

        freelancer_min_price=800,
        freelancer_preferred_price=1300,
        freelancer_min_days=15,
        freelancer_preferred_days=30,

        max_rounds=10,
    )


if __name__ == "__main__":
    main()