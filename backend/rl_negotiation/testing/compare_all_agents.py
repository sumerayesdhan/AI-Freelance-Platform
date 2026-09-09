import os
import sys
from collections import Counter

import numpy as np
from stable_baselines3 import PPO


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


ACTION_NAMES = {
    0: "ACCEPT",
    1: "REJECT",
    2: "DECREASE_PRICE_10",
    3: "DECREASE_PRICE_5",
    4: "INCREASE_PRICE_5",
    5: "SHORTER_TIMELINE",
    6: "BALANCED_COUNTER",
}


def agreement_possible(
    price,
    days,
    budget,
    freelancer_min_price,
    freelancer_min_days,
    client_desired_days,
):
    return (
        freelancer_min_price <= price <= budget
        and freelancer_min_days <= days <= client_desired_days + 10
    )


def apply_action(
    action,
    price,
    days,
    budget,
    freelancer_min_price,
    client_target_price,
    client_desired_days,
    freelancer_min_days,
):
    if action == 2:
        price *= 0.90

    elif action == 3:
        price *= 0.95

    elif action == 4:
        price *= 1.05

    elif action == 5:
        days -= 2.0

    elif action == 6:
        price = (
            price + client_target_price
        ) / 2.0

        days = (
            days + client_desired_days
        ) / 2.0

    price = np.clip(
        price,
        freelancer_min_price,
        budget,
    )

    days = max(
        freelancer_min_days,
        days,
    )

    return float(price), float(days)


def observation(
    round_number,
    max_rounds,
    budget,
    freelancer_min_price,
    current_price,
    client_desired_days,
    freelancer_min_days,
    current_days,
    freelancer_initial_price,
):
    return np.array(
        [
            round_number / max_rounds,
            budget / 2000.0,
            freelancer_min_price / 2000.0,
            current_price / 2000.0,
            client_desired_days / 60.0,
            freelancer_min_days / 60.0,
            current_days / 60.0,
            freelancer_initial_price / 2000.0,
        ],
        dtype=np.float32,
    )


def run_negotiation(
    client_model,
    freelancer_model,
    seed,
    max_rounds=10,
):
    rng = np.random.default_rng(seed)

    budget = float(
        rng.uniform(800.0, 1200.0)
    )

    client_target_price = (
        budget *
        float(rng.uniform(0.75, 0.90))
    )

    freelancer_min_price = float(
        rng.uniform(650.0, 850.0)
    )

    freelancer_initial_price = float(
        rng.uniform(1000.0, 1400.0)
    )

    client_desired_days = float(
        rng.uniform(12.0, 20.0)
    )

    freelancer_min_days = float(
        rng.uniform(10.0, 25.0)
    )

    current_price = client_target_price
    current_days = client_desired_days

    client_actions = Counter()
    freelancer_actions = Counter()

    for round_number in range(
        1,
        max_rounds + 1
    ):

        # ==============================
        # CLIENT PPO
        # ==============================

        client_obs = observation(
            round_number,
            max_rounds,
            budget,
            freelancer_min_price,
            current_price,
            client_desired_days,
            freelancer_min_days,
            current_days,
            freelancer_initial_price,
        )

        client_action, _ = client_model.predict(
            client_obs,
            deterministic=True,
        )

        client_action = int(client_action)

        client_actions[client_action] += 1

        if client_action == 0:

            if agreement_possible(
                current_price,
                current_days,
                budget,
                freelancer_min_price,
                freelancer_min_days,
                client_desired_days,
            ):
                return {
                    "agreement": True,
                    "price": current_price,
                    "days": current_days,
                    "rounds": round_number,
                    "client_actions": client_actions,
                    "freelancer_actions": freelancer_actions,
                }

        elif client_action == 1:

            return {
                "agreement": False,
                "price": current_price,
                "days": current_days,
                "rounds": round_number,
                "client_actions": client_actions,
                "freelancer_actions": freelancer_actions,
            }

        else:

            current_price, current_days = apply_action(
                client_action,
                current_price,
                current_days,
                budget,
                freelancer_min_price,
                client_target_price,
                client_desired_days,
                freelancer_min_days,
            )

        # ==============================
        # FREELANCER PPO
        # ==============================

        freelancer_obs = observation(
            round_number,
            max_rounds,
            budget,
            freelancer_min_price,
            current_price,
            client_desired_days,
            freelancer_min_days,
            current_days,
            freelancer_initial_price,
        )

        freelancer_action, _ = freelancer_model.predict(
            freelancer_obs,
            deterministic=True,
        )

        freelancer_action = int(freelancer_action)

        freelancer_actions[freelancer_action] += 1

        if freelancer_action == 0:

            if agreement_possible(
                current_price,
                current_days,
                budget,
                freelancer_min_price,
                freelancer_min_days,
                client_desired_days,
            ):
                return {
                    "agreement": True,
                    "price": current_price,
                    "days": current_days,
                    "rounds": round_number,
                    "client_actions": client_actions,
                    "freelancer_actions": freelancer_actions,
                }

        elif freelancer_action == 1:

            return {
                "agreement": False,
                "price": current_price,
                "days": current_days,
                "rounds": round_number,
                "client_actions": client_actions,
                "freelancer_actions": freelancer_actions,
            }

        else:

            current_price, current_days = apply_action(
                freelancer_action,
                current_price,
                current_days,
                budget,
                freelancer_min_price,
                client_target_price,
                client_desired_days,
                freelancer_min_days,
            )

    return {
        "agreement": False,
        "price": current_price,
        "days": current_days,
        "rounds": max_rounds,
        "client_actions": client_actions,
        "freelancer_actions": freelancer_actions,
    }


def evaluate_pair(
    client_path,
    freelancer_path,
    label,
    episodes=100,
):

    print("\n" + "=" * 70)
    print(label)
    print("=" * 70)

    client_model = PPO.load(client_path)
    freelancer_model = PPO.load(freelancer_path)

    agreements = 0
    total_price = 0.0
    total_days = 0.0
    total_rounds = 0

    client_actions = Counter()
    freelancer_actions = Counter()

    for seed in range(
        1,
        episodes + 1
    ):

        result = run_negotiation(
            client_model,
            freelancer_model,
            seed,
        )

        if result["agreement"]:
            agreements += 1
            total_price += result["price"]
            total_days += result["days"]

        total_rounds += result["rounds"]

        client_actions.update(
            result["client_actions"]
        )

        freelancer_actions.update(
            result["freelancer_actions"]
        )

    agreement_rate = (
        agreements / episodes
    ) * 100.0

    print(
        f"Negotiations       : {episodes}"
    )

    print(
        f"Agreements         : {agreements}"
    )

    print(
        f"No Agreements      : "
        f"{episodes - agreements}"
    )

    print(
        f"Agreement Rate     : "
        f"{agreement_rate:.2f}%"
    )

    if agreements > 0:

        print(
            f"Average Price      : "
            f"${total_price / agreements:.2f}"
        )

        print(
            f"Average Timeline   : "
            f"{total_days / agreements:.2f} days"
        )

    print(
        f"Average Rounds     : "
        f"{total_rounds / episodes:.2f}"
    )

    print("\nClient Actions:")

    total_client = sum(
        client_actions.values()
    )

    for action in range(7):

        count = client_actions[action]

        percentage = (
            count / total_client * 100
            if total_client
            else 0
        )

        print(
            f"  {ACTION_NAMES[action]:<22}"
            f"{count:5d} "
            f"({percentage:6.2f}%)"
        )

    print("\nFreelancer Actions:")

    total_freelancer = sum(
        freelancer_actions.values()
    )

    for action in range(7):

        count = freelancer_actions[action]

        percentage = (
            count / total_freelancer * 100
            if total_freelancer
            else 0
        )

        print(
            f"  {ACTION_NAMES[action]:<22}"
            f"{count:5d} "
            f"({percentage:6.2f}%)"
        )

    return {
        "label": label,
        "agreement_rate": agreement_rate,
        "average_price": (
            total_price / agreements
            if agreements
            else 0
        ),
        "average_days": (
            total_days / agreements
            if agreements
            else 0
        ),
        "average_rounds": (
            total_rounds / episodes
        ),
    }


def main():

    print("\n")
    print("#" * 70)
    print("PPO MODEL COMPARISON EXPERIMENT")
    print("#" * 70)

    old_result = evaluate_pair(
        os.path.join(
            PROJECT_ROOT,
            "models",
            "client_ppo",
        ),
        os.path.join(
            PROJECT_ROOT,
            "models",
            "freelancer_ppo",
        ),
        "OLD PPO MODELS",
    )

    improved_result = evaluate_pair(
        os.path.join(
            PROJECT_ROOT,
            "models",
            "client_ppo_v2",
        ),
        os.path.join(
            PROJECT_ROOT,
            "models",
            "freelancer_ppo_v3",
        ),
        "IMPROVED PPO MODELS",
    )

    print("\n")
    print("#" * 70)
    print("FINAL COMPARISON")
    print("#" * 70)

    print(
        f"\n{'Metric':<25}"
        f"{'Old PPO':>15}"
        f"{'Improved PPO':>18}"
    )

    print("-" * 60)

    print(
        f"{'Agreement Rate':<25}"
        f"{old_result['agreement_rate']:>14.2f}%"
        f"{improved_result['agreement_rate']:>17.2f}%"
    )

    print(
        f"{'Average Price':<25}"
        f"${old_result['average_price']:>13.2f}"
        f"${improved_result['average_price']:>16.2f}"
    )

    print(
        f"{'Average Timeline':<25}"
        f"{old_result['average_days']:>13.2f}"
        f"{improved_result['average_days']:>16.2f}"
    )

    print(
        f"{'Average Rounds':<25}"
        f"{old_result['average_rounds']:>14.2f}"
        f"{improved_result['average_rounds']:>17.2f}"
    )

    print("\nComparison complete.")


if __name__ == "__main__":
    main()