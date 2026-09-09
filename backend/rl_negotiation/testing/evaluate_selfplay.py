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


def get_observation(
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

    client_rejected = False
    freelancer_rejected = False

    for round_number in range(
        1,
        max_rounds + 1
    ):

        # ==========================================
        # CLIENT PPO
        # ==========================================

        client_obs = get_observation(
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

            if is_agreement_possible(
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
                    "client_rejected": False,
                    "freelancer_rejected": False,
                }

        elif client_action == 1:

            client_rejected = True

            return {
                "agreement": False,
                "price": current_price,
                "days": current_days,
                "rounds": round_number,
                "client_actions": client_actions,
                "freelancer_actions": freelancer_actions,
                "client_rejected": client_rejected,
                "freelancer_rejected": False,
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

        # ==========================================
        # FREELANCER PPO
        # ==========================================

        freelancer_obs = get_observation(
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

            if is_agreement_possible(
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
                    "client_rejected": False,
                    "freelancer_rejected": False,
                }

        elif freelancer_action == 1:

            freelancer_rejected = True

            return {
                "agreement": False,
                "price": current_price,
                "days": current_days,
                "rounds": round_number,
                "client_actions": client_actions,
                "freelancer_actions": freelancer_actions,
                "client_rejected": False,
                "freelancer_rejected": freelancer_rejected,
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
        "client_rejected": False,
        "freelancer_rejected": False,
    }


def print_actions(title, actions):

    print("\n" + title)
    print("-" * 60)

    total = sum(actions.values())

    for action in range(7):

        count = actions[action]

        percentage = (
            count / total * 100.0
            if total > 0
            else 0.0
        )

        print(
            f"{ACTION_NAMES[action]:<25}"
            f"{count:5d}"
            f" ({percentage:6.2f}%)"
        )


def main():

    print("=" * 70)
    print("FINAL SELF-PLAY PPO EVALUATION")
    print("=" * 70)

    client_path = os.path.join(
        PROJECT_ROOT,
        "models",
        "client_ppo_selfplay_v3",
    )

    freelancer_path = os.path.join(
        PROJECT_ROOT,
        "models",
        "freelancer_ppo_selfplay_v3",
    )

    print("\nLoading Client self-play PPO...")
    client_model = PPO.load(client_path)
    print("Client self-play PPO loaded.")

    print("\nLoading Freelancer self-play PPO...")
    freelancer_model = PPO.load(
        freelancer_path
    )
    print("Freelancer self-play PPO loaded.")

    episodes = 100

    agreements = 0
    no_agreements = 0

    total_price = 0.0
    total_days = 0.0
    total_rounds = 0

    client_actions = Counter()
    freelancer_actions = Counter()

    client_rejections = 0
    freelancer_rejections = 0

    print(
        f"\nRunning {episodes} negotiations..."
    )

    for episode in range(
        1,
        episodes + 1
    ):

        result = run_negotiation(
            client_model,
            freelancer_model,
            seed=episode,
        )

        if result["agreement"]:

            agreements += 1

            total_price += (
                result["price"]
            )

            total_days += (
                result["days"]
            )

        else:

            no_agreements += 1

        total_rounds += (
            result["rounds"]
        )

        client_actions.update(
            result["client_actions"]
        )

        freelancer_actions.update(
            result["freelancer_actions"]
        )

        if result["client_rejected"]:
            client_rejections += 1

        if result["freelancer_rejected"]:
            freelancer_rejections += 1

        if episode % 10 == 0:

            rate = (
                agreements
                / episode
                * 100.0
            )

            print(
                f"Episode {episode}/100 | "
                f"Agreement Rate: "
                f"{rate:.1f}%"
            )

    print("\n" + "=" * 70)
    print("FINAL SELF-PLAY RESULTS")
    print("=" * 70)

    agreement_rate = (
        agreements
        / episodes
        * 100.0
    )

    print(
        f"\nTotal Negotiations : "
        f"{episodes}"
    )

    print(
        f"Agreements         : "
        f"{agreements}"
    )

    print(
        f"No Agreements      : "
        f"{no_agreements}"
    )

    print(
        f"Agreement Rate     : "
        f"{agreement_rate:.2f}%"
    )

    if agreements > 0:

        print(
            f"\nAverage Final Price: "
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

    print_actions(
        "CLIENT SELF-PLAY PPO ACTIONS",
        client_actions,
    )

    print_actions(
        "FREELANCER SELF-PLAY PPO ACTIONS",
        freelancer_actions,
    )

    print("\n" + "-" * 60)
    print("REJECTION SUMMARY")
    print("-" * 60)

    print(
        f"Rejected by Client     : "
        f"{client_rejections}"
    )

    print(
        f"Rejected by Freelancer : "
        f"{freelancer_rejections}"
    )

    print("\n" + "=" * 70)
    print("SELF-PLAY EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()