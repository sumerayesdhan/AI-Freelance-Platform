import os
import sys

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.callbacks import EvalCallback

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from environment.client_negotiation_env import (
    ClientNegotiationEnv
)


def main():

    print("=" * 70)
    print("IMPROVED CLIENT PPO TRAINING")
    print("=" * 70)

    # ---------------------------------------------------------
    # Training environment
    # ---------------------------------------------------------

    env = ClientNegotiationEnv(
        max_rounds=10
    )

    print("\nChecking environment...")

    check_env(
        env,
        warn=True
    )

    print("Environment check passed.")

    # ---------------------------------------------------------
    # Evaluation environment
    # ---------------------------------------------------------

    eval_env = ClientNegotiationEnv(
        max_rounds=10
    )

    # ---------------------------------------------------------
    # Evaluation callback
    # ---------------------------------------------------------

    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=os.path.join(
            PROJECT_ROOT,
            "models",
            "client_ppo_best"
        ),
        log_path=os.path.join(
            PROJECT_ROOT,
            "training",
            "client_eval"
        ),
        eval_freq=10000,
        deterministic=True,
        render=False
    )

    # ---------------------------------------------------------
    # PPO
    # ---------------------------------------------------------

    print("\nCreating PPO model...")

    model = PPO(
        policy="MlpPolicy",
        env=env,

        learning_rate=0.0001,

        n_steps=2048,

        batch_size=64,

        n_epochs=10,

        gamma=0.995,

        gae_lambda=0.95,

        clip_range=0.2,

        ent_coef=0.03,

        vf_coef=0.5,

        max_grad_norm=0.5,

        verbose=1,

        seed=42,

        tensorboard_log=os.path.join(
            PROJECT_ROOT,
            "training",
            "tensorboard_client"
        )
    )

    print("\nStarting improved training...")

    model.learn(
        total_timesteps=500_000,
        callback=eval_callback
    )

    # ---------------------------------------------------------
    # Save final model
    # ---------------------------------------------------------

    final_path = os.path.join(
        PROJECT_ROOT,
        "models",
        "client_ppo_v2"
    )

    model.save(final_path)

    print("\n" + "=" * 70)
    print("CLIENT PPO TRAINING COMPLETE")
    print("=" * 70)

    print("\nFinal model:")
    print("models/client_ppo_v2.zip")

    print("\nBest evaluation model:")
    print("models/client_ppo_best/best_model.zip")


if __name__ == "__main__":
    main()