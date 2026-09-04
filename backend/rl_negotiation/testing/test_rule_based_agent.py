from environment.negotiation_env import NegotiationEnv


def rule_based_action(env):
    """
    Simple rule-based freelancer negotiation strategy.

    Strategy:
    1. Accept if the current offer is acceptable.
    2. If price is below the freelancer's minimum,
       increase the price.
    3. Otherwise use a balanced counter-offer.
    """

    # -----------------------------------------------------
    # Accept a good offer
    # -----------------------------------------------------

    if env._is_offer_acceptable():
        return 0

    # -----------------------------------------------------
    # Price is too low
    # -----------------------------------------------------

    if env.current_price < env.freelancer_min_price:
        return 4

    # -----------------------------------------------------
    # Timeline is too short
    # -----------------------------------------------------

    if env.current_days < env.freelancer_min_days:
        return 5

    # -----------------------------------------------------
    # Otherwise use balanced negotiation
    # -----------------------------------------------------

    return 6


def main():

    print("==============================")
    print("TESTING RULE-BASED AGENT")
    print("==============================")

    env = NegotiationEnv()

    total_reward = 0.0
    agreements = 0
    episodes = 100

    for episode in range(episodes):

        observation, info = env.reset()

        terminated = False
        truncated = False

        episode_reward = 0.0

        while not terminated and not truncated:

            action = rule_based_action(env)

            (
                observation,
                reward,
                terminated,
                truncated,
                step_info
            ) = env.step(action)

            episode_reward += reward

        total_reward += episode_reward

        if step_info.get("agreement", False):
            agreements += 1

    average_reward = total_reward / episodes
    agreement_rate = (agreements / episodes) * 100

    print()
    print("==============================")
    print("FINAL RULE-BASED RESULTS")
    print("==============================")

    print(f"Average Reward: {average_reward:.2f}")
    print(f"Agreements: {agreements}/{episodes}")
    print(f"Agreement Rate: {agreement_rate:.2f}%")

    env.close()


if __name__ == "__main__":
    main()