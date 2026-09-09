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


def is_agreement_possible(
    price,
    days,
    client_budget,
    freelancer_min_price,
    freelancer_min_days,
    client_desired_days,
):
    return (
        price >= freelancer_min_price
        and price <= client_budget
        and days >= freelancer_min_days
        and days <= client_desired_days + 10
    )


def apply_action(
    action,
    price,
    days,
    client_budget,
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
        price = (price + client_target_price) / 2.0
        days = (days + client_desired_days) / 2.0

    price = np.clip(
        price,
        freelancer_min_price,
        client_budget,
    )

    days = max(
        freelancer_min_days,
        days,
    )

    return float(price), float(days)


def get_client_observation(
    round_number,
    max_rounds,
    client_budget,
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
            client_budget / 2000.0,
            freelancer_min_price / 2000.0,
            current_price / 2000.0,
            client_desired_days / 60.0,
            freelancer_min_days / 60.0,
            current_days / 60.0,
            freelancer_initial_price / 2000.0,
        ],
        dtype=np.float32,
    )


def get_freelancer_observation(
    round_number,
    max_rounds,
    client_budget,
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
            client_budget / 2000.0,
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

    client_budget = float(
        rng.uniform(800.0, 1200.0)
    )

    client_target_price = (
        client_budget
        * float(rng.uniform(0.75, 0.90))
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

    client_rejections = 0
    freelancer_rejections = 0

    agreement = False
    final_reason = "Maximum rounds reached"

    for round_number in range(1, max_rounds + 1):

        # --------------------------------------------------
        # CLIENT PPO TURN
        # --------------------------------------------------

        client_obs = get_client_observation(
            round_number,
            max_rounds,
            client_budget,
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
            if is_agreement_possible(
                current_price,
                current_days,
                client_budget,
                freelancer_min_price,
                freelancer_min_days,
                client_desired_days,
            ):
                agreement = True
                final_reason = "Client PPO accepted"
                break

        elif client_action == 1:
            client_rejections += 1
            final_reason = "Client PPO rejected"
            break

        else:
            current_price, current_days = apply_action(
                client_action,
                current_price,
                current_days,
                client_budget,
                freelancer_min_price,
                client_target_price,
                client_desired_days,
                freelancer_min_days,
            )

        # --------------------------------------------------
        # FREELANCER PPO TURN
        # --------------------------------------------------

        freelancer_obs = get_freelancer_observation(
            round_number,
            max_rounds,
            client_budget,
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
            if is_agreement_possible(
                current_price,
                current_days,
                client_budget,
                freelancer_min_price,
                freelancer_min_days,
                client_desired_days,
            ):
                agreement = True
                final_reason = "Freelancer PPO accepted"
                break

        elif freelancer_action == 1:
            freelancer_rejections += 1
            final_reason = "Freelancer PPO rejected"
            break

        else:
            current_price, current_days = apply_action(
                freelancer_action,
                current_price,
                current_days,
                client_budget,
                freelancer_min_price,
                client_target_price,
                client_desired_days,
                freelancer_min_days,
            )

    return {
        "agreement": agreement,
        "final_price": current_price,
        "final_days": current_days,
        "rounds": round_number,
        "client_actions": client_actions,
        "freelancer_actions": freelancer_actions,
        "client_rejections": client_rejections,
        "freelancer_rejections": freelancer_rejections,
        "reason": final_reason,
    }


def main():

    print("=" * 70)
    print("IMPROVED TWO-PPO NEGOTIATION EVALUATION")
    print("=" * 70)

    client_path = os.path.join(
        PROJECT_ROOT,
        "models",
        "client_ppo_v2",
    )

    freelancer_path = os.path.join(
        PROJECT_ROOT,
        "models",
        "freelancer_ppo_v3",
    )

    print("\nLoading improved Client PPO...")
    client_model = PPO.load(client_path)
    print("Client PPO loaded.")

    print("\nLoading improved Freelancer PPO...")
    freelancer_model = PPO.load(freelancer_path)
    print("Freelancer PPO loaded.")

    total_episodes = 100

    agreements = 0
    no_agreements = 0

    total_price = 0.0
    total_days = 0.0
    total_rounds = 0

    client_action_counts = Counter()
    freelancer_action_counts = Counter()

    client_rejections = 0
    freelancer_rejections = 0

    print(
        f"\nRunning {total_episodes} negotiations..."
    )

    for episode in range(1, total_episodes + 1):

        result = run_negotiation(
            client_model,
            freelancer_model,
            seed=episode,
        )

        if result["agreement"]:
            agreements += 1
            total_price += result["final_price"]
            total_days += result["final_days"]

        else:
            no_agreements += 1

        total_rounds += result["rounds"]

        client_action_counts.update(
            result["client_actions"]
        )

        freelancer_action_counts.update(
            result["freelancer_actions"]
        )

        client_rejections += result[
            "client_rejections"
        ]

        freelancer_rejections += result[
            "freelancer_rejections"
        ]

        if episode % 10 == 0:
            agreement_rate = (
                agreements / episode
            ) * 100.0

            print(
                f"Episode {episode}/100 | "
                f"Agreement Rate: "
                f"{agreement_rate:.1f}%"
            )

    print("\n" + "=" * 70)
    print("FINAL EVALUATION RESULTS")
    print("=" * 70)

    agreement_rate = (
        agreements / total_episodes
    ) * 100.0

    no_agreement_rate = (
        no_agreements / total_episodes
    ) * 100.0

    print(
        f"\nTotal Negotiations: "
        f"{total_episodes}"
    )

    print(
        f"Agreements: "
        f"{agreements}"
    )

    print(
        f"No Agreements: "
        f"{no_agreements}"
    )

    print(
        f"\nAgreement Rate: "
        f"{agreement_rate:.2f}%"
    )

    print(
        f"No-Agreement Rate: "
        f"{no_agreement_rate:.2f}%"
    )

    if agreements > 0:

        print(
            f"\nAverage Final Price: "
            f"${total_price / agreements:.2f}"
        )

        print(
            f"Average Timeline: "
            f"{total_days / agreements:.2f} days"
        )

    print(
        f"Average Negotiation Rounds: "
        f"{total_rounds / total_episodes:.2f}"
    )

    print("\n" + "-" * 70)
    print("CLIENT PPO ACTION DISTRIBUTION")
    print("-" * 70)

    total_client_actions = sum(
        client_action_counts.values()
    )

    for action in range(7):
        count = client_action_counts[action]

        percentage = (
            count / total_client_actions * 100.0
            if total_client_actions
            else 0.0
        )

        print(
            f"{ACTION_NAMES[action]:<25}: "
            f"{count:5d} "
            f"({percentage:6.2f}%)"
        )

    print("\n" + "-" * 70)
    print("FREELANCER PPO ACTION DISTRIBUTION")
    print("-" * 70)

    total_freelancer_actions = sum(
        freelancer_action_counts.values()
    )

    for action in range(7):
        count = freelancer_action_counts[action]

        percentage = (
            count
            / total_freelancer_actions
            * 100.0
            if total_freelancer_actions
            else 0.0
        )

        print(
            f"{ACTION_NAMES[action]:<25}: "
            f"{count:5d} "
            f"({percentage:6.2f}%)"
        )

    print("\n" + "-" * 70)
    print("REJECTION SUMMARY")
    print("-" * 70)

    print(
        f"Rejected by Client: "
        f"{client_rejections}"
    )

    print(
        f"Rejected by Freelancer: "
        f"{freelancer_rejections}"
    )

    print("\n" + "=" * 70)
    print("EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()