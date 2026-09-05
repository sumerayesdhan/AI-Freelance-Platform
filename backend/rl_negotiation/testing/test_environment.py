from environment.negotiation_env import NegotiationEnv


def main():

    env = NegotiationEnv()

    observation, info = env.reset(seed=42)

    print("\n==============================")
    print("INITIAL NEGOTIATION")
    print("==============================")

    print("Observation:")
    print(observation)

    print("\nScenario:")
    print(info)

    done = False

    while not done:

        # Random action.
        # This is ONLY for testing the environment.
        action = env.action_space.sample()

        (
            observation,
            reward,
            terminated,
            truncated,
            info
        ) = env.step(action)

        env.render()

        print(
            f"Action: {action} | "
            f"Reward: {reward:.2f}"
        )

        done = (
            terminated
            or
            truncated
        )

    print("\n==============================")
    print("NEGOTIATION FINISHED")
    print("==============================")

    print(info)


if __name__ == "__main__":
    main()