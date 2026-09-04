from environment.negotiation_env import NegotiationEnv
from agents.freelancer_ppo_agent import FreelancerPPOAgent


def get_action_name(action):
    actions = {
        0: "ACCEPT",
        1: "REJECT",
        2: "LOWER PRICE 10%",
        3: "LOWER PRICE 5%",
        4: "INCREASE PRICE 5%",
        5: "REQUEST SHORTER TIMELINE",
        6: "BALANCED COUNTER"
    }

    return actions.get(action, "UNKNOWN")


def main():

    print("=" * 60)
    print("RL FREELANCER NEGOTIATION DEMO")
    print("=" * 60)

    # -----------------------------------------------------
    # Create environment
    # -----------------------------------------------------

    env = NegotiationEnv()

    # -----------------------------------------------------
    # Load trained PPO freelancer
    # -----------------------------------------------------

    agent = FreelancerPPOAgent(
        "models/freelancer_ppo"
    )

    # -----------------------------------------------------
    # Start negotiation
    # -----------------------------------------------------

    observation, info = env.reset(seed=42)

    print("\nNEGOTIATION REQUIREMENTS")
    print("-" * 60)

    print(
        f"Client Budget: "
        f"${info['client_budget']:.2f}"
    )

    print(
        f"Freelancer Minimum Price: "
        f"${info['freelancer_min_price']:.2f}"
    )

    print(
        f"Freelancer Initial Price: "
        f"${info['freelancer_initial_price']:.2f}"
    )

    print(
        f"Client Desired Timeline: "
        f"{info['client_desired_days']:.2f} days"
    )

    print(
        f"Freelancer Minimum Timeline: "
        f"{info['freelancer_min_days']:.2f} days"
    )

    print("\n")
    print("=" * 60)
    print("NEGOTIATION STARTED")
    print("=" * 60)

    terminated = False
    truncated = False

    total_reward = 0.0

    while not terminated and not truncated:

        # -------------------------------------------------
        # PPO chooses freelancer action
        # -------------------------------------------------

        action = agent.get_action(observation)

        action_name = get_action_name(action)

        print(
            f"\nRound {env.round_number + 1}"
        )

        print(
            f"Current Price: "
            f"${env.current_price:.2f}"
        )

        print(
            f"Current Timeline: "
            f"{env.current_days:.2f} days"
        )

        print(
            f"Freelancer Action: "
            f"{action_name}"
        )

        # -------------------------------------------------
        # Apply action
        # -------------------------------------------------

        (
            observation,
            reward,
            terminated,
            truncated,
            step_info
        ) = env.step(action)

        total_reward += reward

        print(
            f"Reward: {reward:.2f}"
        )

    # =====================================================
    # FINAL RESULT
    # =====================================================

    print("\n")
    print("=" * 60)
    print("NEGOTIATION RESULT")
    print("=" * 60)

    agreement = step_info.get(
        "agreement",
        False
    )

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
        f"Total Rounds: "
        f"{env.round_number}"
    )

    print(
        f"Total Reward: "
        f"{total_reward:.2f}"
    )

    print("=" * 60)

    env.close()


if __name__ == "__main__":
    main()