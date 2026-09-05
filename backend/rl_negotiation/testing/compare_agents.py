import numpy as np
from stable_baselines3 import PPO
from environment.negotiation_env import NegotiationEnv


NUM_EPISODES = 1000
SEED = 42


def rule_based_action(env):
    """
    Rule-based freelancer strategy.
    """

    # Accept if the offer satisfies freelancer constraints
    if env._is_offer_acceptable():
        return 0

    # Price is below minimum
    if env.current_price < env.freelancer_min_price:
        return 4

    # Timeline is too short
    if env.current_days < env.freelancer_min_days:
        return 5

    # Balanced counter
    return 6


def create_scenario(env, seed):
    """
    Generate one fixed negotiation scenario.
    """

    env.reset(seed=seed)

    return {
        "client_budget": env.client_budget,
        "freelancer_min_price": env.freelancer_min_price,
        "freelancer_initial_price": env.freelancer_initial_price,
        "client_desired_days": env.client_desired_days,
        "freelancer_min_days": env.freelancer_min_days,
    }


def apply_scenario(env, scenario):
    """
    Put the exact same scenario into the environment.
    """

    env.round_number = 0

    env.client_budget = scenario["client_budget"]
    env.freelancer_min_price = scenario["freelancer_min_price"]
    env.freelancer_initial_price = scenario["freelancer_initial_price"]
    env.client_desired_days = scenario["client_desired_days"]
    env.freelancer_min_days = scenario["freelancer_min_days"]

    env.current_price = env.client_budget * 0.75
    env.current_days = env.client_desired_days


def run_rule_based(env, scenario):

    apply_scenario(env, scenario)

    observation = env._get_observation()

    terminated = False
    truncated = False

    total_reward = 0.0
    rounds = 0
    final_info = {}

    while not terminated and not truncated:

        action = rule_based_action(env)

        (
            observation,
            reward,
            terminated,
            truncated,
            final_info
        ) = env.step(action)

        total_reward += reward
        rounds += 1

    return {
        "reward": total_reward,
        "agreement": final_info.get("agreement", False),
        "rounds": rounds,
        "price": final_info.get("price", env.current_price),
        "timeline": final_info.get(
            "timeline_days",
            env.current_days
        ),
    }


def run_ppo(model, env, scenario):

    apply_scenario(env, scenario)

    observation = env._get_observation()

    terminated = False
    truncated = False

    total_reward = 0.0
    rounds = 0
    final_info = {}

    while not terminated and not truncated:

        action, _ = model.predict(
            observation,
            deterministic=True
        )

        (
            observation,
            reward,
            terminated,
            truncated,
            final_info
        ) = env.step(int(action))

        total_reward += reward
        rounds += 1

    return {
        "reward": total_reward,
        "agreement": final_info.get("agreement", False),
        "rounds": rounds,
        "price": final_info.get("price", env.current_price),
        "timeline": final_info.get(
            "timeline_days",
            env.current_days
        ),
    }


def main():

    print("==============================")
    print("CONTROLLED AGENT COMPARISON")
    print("==============================")

    print("\nLoading PPO model...")

    model = PPO.load(
        "models/freelancer_ppo"
    )

    rule_env = NegotiationEnv()
    ppo_env = NegotiationEnv()

    rule_rewards = []
    ppo_rewards = []

    rule_agreements = 0
    ppo_agreements = 0

    rule_rounds = []
    ppo_rounds = []

    rule_prices = []
    ppo_prices = []

    rule_timelines = []
    ppo_timelines = []

    print(
        f"\nRunning {NUM_EPISODES} identical scenarios..."
    )

    for i in range(NUM_EPISODES):

        scenario_seed = SEED + i

        scenario = create_scenario(
            rule_env,
            scenario_seed
        )

        rule_result = run_rule_based(
            rule_env,
            scenario
        )

        ppo_result = run_ppo(
            model,
            ppo_env,
            scenario
        )

        rule_rewards.append(
            rule_result["reward"]
        )

        ppo_rewards.append(
            ppo_result["reward"]
        )

        rule_rounds.append(
            rule_result["rounds"]
        )

        ppo_rounds.append(
            ppo_result["rounds"]
        )

        rule_prices.append(
            rule_result["price"]
        )

        ppo_prices.append(
            ppo_result["price"]
        )

        rule_timelines.append(
            rule_result["timeline"]
        )

        ppo_timelines.append(
            ppo_result["timeline"]
        )

        if rule_result["agreement"]:
            rule_agreements += 1

        if ppo_result["agreement"]:
            ppo_agreements += 1

    # =====================================================
    # FINAL RESULTS
    # =====================================================

    rule_agreement_rate = (
        rule_agreements
        / NUM_EPISODES
        * 100
    )

    ppo_agreement_rate = (
        ppo_agreements
        / NUM_EPISODES
        * 100
    )

    print("\n==============================")
    print("FINAL COMPARISON")
    print("==============================")

    print("\nRULE-BASED AGENT")
    print("------------------------------")

    print(
        f"Agreements: "
        f"{rule_agreements}/{NUM_EPISODES}"
    )

    print(
        f"Agreement Rate: "
        f"{rule_agreement_rate:.2f}%"
    )

    print(
        f"Average Reward: "
        f"{np.mean(rule_rewards):.2f}"
    )

    print(
        f"Average Rounds: "
        f"{np.mean(rule_rounds):.2f}"
    )

    print(
        f"Average Final Price: "
        f"${np.mean(rule_prices):.2f}"
    )

    print(
        f"Average Timeline: "
        f"{np.mean(rule_timelines):.2f} days"
    )

    print("\nPPO FREELANCER")
    print("------------------------------")

    print(
        f"Agreements: "
        f"{ppo_agreements}/{NUM_EPISODES}"
    )

    print(
        f"Agreement Rate: "
        f"{ppo_agreement_rate:.2f}%"
    )

    print(
        f"Average Reward: "
        f"{np.mean(ppo_rewards):.2f}"
    )

    print(
        f"Average Rounds: "
        f"{np.mean(ppo_rounds):.2f}"
    )

    print(
        f"Average Final Price: "
        f"${np.mean(ppo_prices):.2f}"
    )

    print(
        f"Average Timeline: "
        f"{np.mean(ppo_timelines):.2f} days"
    )

    print("\n==============================")
    print("COMPARISON COMPLETED")
    print("==============================")


if __name__ == "__main__":
    main()