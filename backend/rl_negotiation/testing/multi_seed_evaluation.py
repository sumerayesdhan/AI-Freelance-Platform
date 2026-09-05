import numpy as np
from stable_baselines3 import PPO
from environment.negotiation_env import NegotiationEnv


NUM_EPISODES = 1000

SEEDS = [
    42,
    100,
    200,
    300,
    400
]


def rule_based_action(env):
    """
    Rule-based freelancer strategy.
    """

    if env._is_offer_acceptable():
        return 0

    if env.current_price < env.freelancer_min_price:
        return 4

    if env.current_days < env.freelancer_min_days:
        return 5

    return 6


def create_scenario(env, seed):

    env.reset(seed=seed)

    return {
        "client_budget": env.client_budget,
        "freelancer_min_price": env.freelancer_min_price,
        "freelancer_initial_price": env.freelancer_initial_price,
        "client_desired_days": env.client_desired_days,
        "freelancer_min_days": env.freelancer_min_days
    }


def apply_scenario(env, scenario):

    env.round_number = 0

    env.client_budget = scenario["client_budget"]

    env.freelancer_min_price = (
        scenario["freelancer_min_price"]
    )

    env.freelancer_initial_price = (
        scenario["freelancer_initial_price"]
    )

    env.client_desired_days = (
        scenario["client_desired_days"]
    )

    env.freelancer_min_days = (
        scenario["freelancer_min_days"]
    )

    env.current_price = (
        env.client_budget * 0.75
    )

    env.current_days = (
        env.client_desired_days
    )


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

    return (
        total_reward,
        final_info.get("agreement", False),
        rounds
    )


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

    return (
        total_reward,
        final_info.get("agreement", False),
        rounds
    )


def evaluate_seed(model, seed):

    rule_env = NegotiationEnv()
    ppo_env = NegotiationEnv()

    rule_rewards = []
    ppo_rewards = []

    rule_rounds = []
    ppo_rounds = []

    rule_agreements = 0
    ppo_agreements = 0

    for i in range(NUM_EPISODES):

        scenario_seed = seed + i

        scenario = create_scenario(
            rule_env,
            scenario_seed
        )

        (
            rule_reward,
            rule_agreement,
            rule_round
        ) = run_rule_based(
            rule_env,
            scenario
        )

        (
            ppo_reward,
            ppo_agreement,
            ppo_round
        ) = run_ppo(
            model,
            ppo_env,
            scenario
        )

        rule_rewards.append(rule_reward)
        ppo_rewards.append(ppo_reward)

        rule_rounds.append(rule_round)
        ppo_rounds.append(ppo_round)

        if rule_agreement:
            rule_agreements += 1

        if ppo_agreement:
            ppo_agreements += 1

    rule_rate = (
        rule_agreements
        / NUM_EPISODES
        * 100
    )

    ppo_rate = (
        ppo_agreements
        / NUM_EPISODES
        * 100
    )

    rule_env.close()
    ppo_env.close()

    return {
        "rule_rate": rule_rate,
        "ppo_rate": ppo_rate,
        "rule_reward": np.mean(rule_rewards),
        "ppo_reward": np.mean(ppo_rewards),
        "rule_rounds": np.mean(rule_rounds),
        "ppo_rounds": np.mean(ppo_rounds)
    }


def main():

    print("==============================")
    print("MULTI-SEED PPO EVALUATION")
    print("==============================")

    print("\nLoading PPO model...")

    model = PPO.load(
        "models/freelancer_ppo"
    )

    results = []

    for seed in SEEDS:

        print()
        print(
            f"Running seed {seed} "
            f"({NUM_EPISODES} scenarios)..."
        )

        result = evaluate_seed(
            model,
            seed
        )

        results.append(result)

        print(
            f"Rule-Based Agreement: "
            f"{result['rule_rate']:.2f}%"
        )

        print(
            f"PPO Agreement: "
            f"{result['ppo_rate']:.2f}%"
        )

        print(
            f"Rule-Based Reward: "
            f"{result['rule_reward']:.2f}"
        )

        print(
            f"PPO Reward: "
            f"{result['ppo_reward']:.2f}"
        )

        print(
            f"Rule-Based Rounds: "
            f"{result['rule_rounds']:.2f}"
        )

        print(
            f"PPO Rounds: "
            f"{result['ppo_rounds']:.2f}"
        )

    # =====================================================
    # OVERALL RESULTS
    # =====================================================

    rule_rates = [
        r["rule_rate"]
        for r in results
    ]

    ppo_rates = [
        r["ppo_rate"]
        for r in results
    ]

    rule_rewards = [
        r["rule_reward"]
        for r in results
    ]

    ppo_rewards = [
        r["ppo_reward"]
        for r in results
    ]

    rule_rounds = [
        r["rule_rounds"]
        for r in results
    ]

    ppo_rounds = [
        r["ppo_rounds"]
        for r in results
    ]

    print()
    print("==============================")
    print("OVERALL MULTI-SEED RESULTS")
    print("==============================")

    print("\nRULE-BASED AGENT")
    print("------------------------------")

    print(
        f"Mean Agreement Rate: "
        f"{np.mean(rule_rates):.2f}%"
    )

    print(
        f"Agreement Std Dev: "
        f"{np.std(rule_rates):.2f}%"
    )

    print(
        f"Mean Reward: "
        f"{np.mean(rule_rewards):.2f}"
    )

    print(
        f"Mean Rounds: "
        f"{np.mean(rule_rounds):.2f}"
    )

    print("\nPPO FREELANCER")
    print("------------------------------")

    print(
        f"Mean Agreement Rate: "
        f"{np.mean(ppo_rates):.2f}%"
    )

    print(
        f"Agreement Std Dev: "
        f"{np.std(ppo_rates):.2f}%"
    )

    print(
        f"Mean Reward: "
        f"{np.mean(ppo_rewards):.2f}"
    )

    print(
        f"Mean Rounds: "
        f"{np.mean(ppo_rounds):.2f}"
    )

    print("\n==============================")
    print("MULTI-SEED EVALUATION COMPLETE")
    print("==============================")


if __name__ == "__main__":
    main()