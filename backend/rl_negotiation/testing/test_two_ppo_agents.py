from stable_baselines3 import PPO
from environment.client_negotiation_env import ClientNegotiationEnv


ACTION_NAMES = {
    0: "ACCEPT",
    1: "REJECT",
    2: "DECREASE_PRICE_10",
    3: "DECREASE_PRICE_5",
    4: "INCREASE_PRICE_5",
    5: "SHORTER_TIMELINE",
    6: "BALANCED_COUNTER",
}


def is_agreement_possible(env):
    return (
        env.current_price >= env.freelancer_min_price
        and env.current_price <= env.client_budget
        and env.current_days >= env.freelancer_min_days
        and env.current_days <= env.client_desired_days + 10
    )


def apply_action(env, action, agent):

    action = int(action)

    if action == 0:
        return

    if action == 1:
        return

    if action == 2:
        env.current_price *= 0.90

    elif action == 3:
        env.current_price *= 0.95

    elif action == 4:
        env.current_price *= 1.05

    elif action == 5:
        env.current_days = max(
            env.freelancer_min_days,
            env.current_days - 2.0
        )

    elif action == 6:

        env.current_price = (
            env.current_price +
            env.client_budget
        ) / 2.0

        env.current_days = (
            env.current_days +
            env.client_desired_days
        ) / 2.0

    # Keep price within valid negotiation boundaries.
    env.current_price = max(
        env.current_price,
        env.freelancer_min_price
    )

    env.current_price = min(
        env.current_price,
        env.client_budget
    )

    # Keep timeline within reasonable limits.
    env.current_days = max(
        env.current_days,
        env.freelancer_min_days
    )


def get_client_observation(env):
    return env._get_observation()


def get_freelancer_observation(env, round_number):

    observation = [
        round_number / env.max_rounds,
        env.client_budget / env.max_price,
        env.freelancer_min_price / env.max_price,
        env.current_price / env.max_price,
        env.client_desired_days / env.max_days,
        env.freelancer_min_days / env.max_days,
        env.current_days / env.max_days,
        env.freelancer_initial_price / env.max_price,
    ]

    return observation


def main():

    print("=" * 70)
    print("TRUE TWO-PPO NEGOTIATION")
    print("=" * 70)

    print("\nLoading Client PPO...")
    client_model = PPO.load("models/client_ppo")
    print("Client PPO loaded successfully.")

    print("\nLoading Freelancer PPO...")
    freelancer_model = PPO.load("models/freelancer_ppo")
    print("Freelancer PPO loaded successfully.")

    env = ClientNegotiationEnv(max_rounds=10)

    observation, info = env.reset(seed=42)

    print("\n" + "=" * 70)
    print("NEGOTIATION SCENARIO")
    print("=" * 70)

    print(f"Client Budget:            ${env.client_budget:.2f}")
    print(f"Freelancer Minimum Price: ${env.freelancer_min_price:.2f}")
    print(
        f"Freelancer Initial Price: "
        f"${env.freelancer_initial_price:.2f}"
    )
    print(
        f"Client Desired Days:      "
        f"{env.client_desired_days:.2f}"
    )
    print(
        f"Freelancer Minimum Days:   "
        f"{env.freelancer_min_days:.2f}"
    )

    # Client makes the initial offer.
    env.current_price = env.client_budget * 0.75
    env.current_days = env.client_desired_days

    print("\n" + "=" * 70)
    print("CLIENT PPO ↔ FREELANCER PPO")
    print("=" * 70)

    print(
        f"\nInitial Client Offer:"
        f" ${env.current_price:.2f}"
        f" / {env.current_days:.2f} days"
    )

    agreement = False
    rejection_agent = None
    final_reason = "Maximum negotiation rounds reached"

    for round_number in range(1, env.max_rounds + 1):

        print("\n" + "-" * 70)
        print(f"ROUND {round_number}")
        print("-" * 70)

        # =========================================================
        # CLIENT PPO TURN
        # =========================================================

        client_observation = get_client_observation(env)

        client_action, _ = client_model.predict(
            client_observation,
            deterministic=True
        )

        client_action = int(client_action)

        print(
            f"CLIENT PPO:"
            f" {ACTION_NAMES[client_action]}"
        )

        if client_action == 0:

            if is_agreement_possible(env):

                agreement = True
                final_reason = "Client PPO accepted the current terms"

                print("→ Client accepted.")
                break

            print(
                "→ Client attempted to accept, "
                "but terms are not valid."
            )

            rejection_agent = "CLIENT"
            final_reason = "Invalid client acceptance"
            break

        if client_action == 1:

            print("→ Client rejected the negotiation.")

            rejection_agent = "CLIENT"
            final_reason = "Client PPO rejected"
            break

        apply_action(
            env,
            client_action,
            "CLIENT"
        )

        print(
            f"Client Counter:"
            f" ${env.current_price:.2f}"
            f" / {env.current_days:.2f} days"
        )

        # =========================================================
        # FREELANCER PPO TURN
        # =========================================================

        freelancer_observation = get_freelancer_observation(
            env,
            round_number
        )

        freelancer_action, _ = freelancer_model.predict(
            freelancer_observation,
            deterministic=True
        )

        freelancer_action = int(freelancer_action)

        print(
            f"FREELANCER PPO:"
            f" {ACTION_NAMES[freelancer_action]}"
        )

        if freelancer_action == 0:

            if is_agreement_possible(env):

                agreement = True
                final_reason = (
                    "Freelancer PPO accepted the current terms"
                )

                print("→ Freelancer accepted.")
                break

            print(
                "→ Freelancer attempted to accept, "
                "but terms are not valid."
            )

            rejection_agent = "FREELANCER"
            final_reason = "Invalid freelancer acceptance"
            break

        if freelancer_action == 1:

            print("→ Freelancer rejected the negotiation.")

            rejection_agent = "FREELANCER"
            final_reason = "Freelancer PPO rejected"
            break

        apply_action(
            env,
            freelancer_action,
            "FREELANCER"
        )

        print(
            f"Freelancer Counter:"
            f" ${env.current_price:.2f}"
            f" / {env.current_days:.2f} days"
        )

        # Do NOT automatically declare agreement here.
        # The Client PPO must get the next decision.

        if is_agreement_possible(env):

            print(
                "→ Terms are currently mutually acceptable."
            )

    # =============================================================
    # FINAL RESULT
    # =============================================================

    print("\n" + "=" * 70)
    print("FINAL TWO-PPO NEGOTIATION RESULT")
    print("=" * 70)

    print(
        f"Agreement: "
        f"{'YES' if agreement else 'NO'}"
    )

    print(
        f"Final Price: "
        f"${env.current_price:.2f}"
    )

    print(
        f"Final Timeline: "
        f"{env.current_days:.2f} days"
    )

    print(
        f"Rounds: "
        f"{round_number}"
    )

    print(
        f"Reason: "
        f"{final_reason}"
    )

    if rejection_agent:
        print(
            f"Rejected By: "
            f"{rejection_agent}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()