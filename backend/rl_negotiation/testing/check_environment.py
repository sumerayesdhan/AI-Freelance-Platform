from stable_baselines3.common.env_checker import check_env

from environment.negotiation_env import NegotiationEnv


def main():

    env = NegotiationEnv()

    check_env(
        env,
        warn=True
    )

    print(
        "Environment check completed successfully."
    )


if __name__ == "__main__":
    main()