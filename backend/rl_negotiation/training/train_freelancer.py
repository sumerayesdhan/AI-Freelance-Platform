from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env

from environment.negotiation_env import NegotiationEnv


def main():

    print("==============================")
    print("CREATING NEGOTIATION ENVIRONMENT")
    print("==============================")

    env = NegotiationEnv()


    # ========================================================
    # VERIFY ENVIRONMENT BEFORE TRAINING
    # ========================================================

    print("\nChecking environment...")

    check_env(
        env,
        warn=True
    )

    print("Environment check passed.")


    # ========================================================
    # CREATE PPO MODEL
    # ========================================================

    print("\nCreating PPO model...")

    model = PPO(

        policy="MlpPolicy",

        env=env,

        learning_rate=0.0003,

        n_steps=2048,

        batch_size=64,

        gamma=0.99,

        gae_lambda=0.95,

        ent_coef=0.01,

        verbose=1,

        seed=42
    )


    # ========================================================
    # TRAIN MODEL
    # ========================================================

    print("\n==============================")
    print("STARTING PPO TRAINING")
    print("==============================")

    model.learn(
        total_timesteps=100_000
    )


    # ========================================================
    # SAVE MODEL
    # ========================================================

    model.save(
        "models/freelancer_ppo_v2"
    )


    print("\n==============================")
    print("TRAINING COMPLETED")
    print("==============================")

    print(
        "Model saved as:"
    )

    print(
        "models/freelancer_ppo_v2.zip"
    )


    # ========================================================
    # CLOSE ENVIRONMENT
    # ========================================================

    env.close()


if __name__ == "__main__":

    main()