from stable_baselines3 import PPO

from environment.negotiation_env import NegotiationEnv


def main():

    # ========================================================
    # CREATE ENVIRONMENT
    # ========================================================

    env = NegotiationEnv()


    # ========================================================
    # LOAD TRAINED MODEL
    # ========================================================

    print("Loading trained PPO model...")

    model = PPO.load(
        "models/freelancer_ppo"
    )


    print("\n==============================")
    print("TESTING TRAINED AGENT")
    print("==============================")


    # ========================================================
    # TEST 10 NEGOTIATIONS
    # ========================================================

    number_of_episodes = 100

    total_reward = 0.0

    agreements = 0


    for episode in range(number_of_episodes):

        observation, info = env.reset(
            seed=episode
        )

        done = False

        episode_reward = 0.0


        while not done:

            # ------------------------------------------------
            # Ask trained agent for an action
            # ------------------------------------------------

            action, _states = model.predict(

                observation,

                deterministic=True

            )


            # ------------------------------------------------
            # Execute action
            # ------------------------------------------------

            (
                observation,
                reward,
                terminated,
                truncated,
                info
            ) = env.step(
                int(action)
            )


            episode_reward += reward


            done = (
                terminated
                or
                truncated
            )


        total_reward += episode_reward


        if info.get(
            "agreement",
            False
        ):

            agreements += 1


        print(
            f"\nEpisode {episode + 1}"
        )

        print(
            f"Reward: {episode_reward:.2f}"
        )

        print(
            f"Agreement: "
            f"{info.get('agreement', False)}"
        )

        print(
            f"Final Price: "
            f"${info['price']:.2f}"
        )

        print(
            f"Timeline: "
            f"{info['timeline_days']:.1f} days"
        )

        print(
            f"Rounds: "
            f"{info['round']}"
        )


    # ========================================================
    # CALCULATE RESULTS
    # ========================================================

    average_reward = (
        total_reward
        /
        number_of_episodes
    )


    agreement_rate = (
        agreements
        /
        number_of_episodes
        *
        100
    )


    # ========================================================
    # FINAL RESULTS
    # ========================================================

    print("\n==============================")
    print("FINAL RL RESULTS")
    print("==============================")


    print(
        f"Average Reward: "
        f"{average_reward:.2f}"
    )


    print(
        f"Agreements: "
        f"{agreements}/{number_of_episodes}"
    )


    print(
        f"Agreement Rate: "
        f"{agreement_rate:.2f}%"
    )


    env.close()


if __name__ == "__main__":

    main()