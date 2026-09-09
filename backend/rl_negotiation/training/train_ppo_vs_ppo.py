import os
import sys

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from environment.ppo_vs_ppo_env import PPOvsPPOEnv


CLIENT_MODEL = os.path.join(
    PROJECT_ROOT,
    "models",
    "client_ppo_v2",
)

FREELANCER_MODEL = os.path.join(
    PROJECT_ROOT,
    "models",
    "freelancer_ppo_v3",
)


def train_client_against_freelancer(
    client_model_path,
    freelancer_model_path,
    output_path,
    timesteps=100_000,
):

    print("\n" + "=" * 70)
    print("TRAINING CLIENT PPO AGAINST FREELANCER PPO")
    print("=" * 70)

    print("\nLoading frozen Freelancer PPO...")
    freelancer_model = PPO.load(
        freelancer_model_path
    )
    print("Freelancer PPO loaded.")

    env = PPOvsPPOEnv(
        opponent_model=freelancer_model,
        agent_role="client",
        max_rounds=10,
    )

    print("\nLoading Client PPO...")
    client_model = PPO.load(
        client_model_path,
        env=env,
    )

    print("Client PPO loaded.")

    print(
        f"\nTraining Client PPO for "
        f"{timesteps:,} timesteps..."
    )

    client_model.learn(
        total_timesteps=timesteps,
        reset_num_timesteps=False,
    )

    client_model.save(output_path)

    print("\nClient training complete.")

    return output_path


def train_freelancer_against_client(
    freelancer_model_path,
    client_model_path,
    output_path,
    timesteps=100_000,
):

    print("\n" + "=" * 70)
    print("TRAINING FREELANCER PPO AGAINST CLIENT PPO")
    print("=" * 70)

    print("\nLoading frozen Client PPO...")
    client_model = PPO.load(
        client_model_path
    )
    print("Client PPO loaded.")

    env = PPOvsPPOEnv(
        opponent_model=client_model,
        agent_role="freelancer",
        max_rounds=10,
    )

    print("\nLoading Freelancer PPO...")

    freelancer_model = PPO.load(
        freelancer_model_path,
        env=env,
    )

    print("Freelancer PPO loaded.")

    print(
        f"\nTraining Freelancer PPO for "
        f"{timesteps:,} timesteps..."
    )

    freelancer_model.learn(
        total_timesteps=timesteps,
        reset_num_timesteps=False,
    )

    freelancer_model.save(output_path)

    print("\nFreelancer training complete.")

    return output_path


def main():

    print("=" * 70)
    print("ALTERNATING PPO VS PPO TRAINING")
    print("=" * 70)

    print("\nExisting models will NOT be overwritten.")

    # --------------------------------------------------
    # CYCLE 1
    # --------------------------------------------------

    client_v1 = os.path.join(
        PROJECT_ROOT,
        "models",
        "client_ppo_selfplay_v1",
    )

    freelancer_v1 = os.path.join(
        PROJECT_ROOT,
        "models",
        "freelancer_ppo_selfplay_v1",
    )

    train_client_against_freelancer(
        CLIENT_MODEL,
        FREELANCER_MODEL,
        client_v1,
        timesteps=100_000,
    )

    train_freelancer_against_client(
        FREELANCER_MODEL,
        client_v1,
        freelancer_v1,
        timesteps=100_000,
    )

    # --------------------------------------------------
    # CYCLE 2
    # --------------------------------------------------

    client_v2 = os.path.join(
        PROJECT_ROOT,
        "models",
        "client_ppo_selfplay_v2",
    )

    freelancer_v2 = os.path.join(
        PROJECT_ROOT,
        "models",
        "freelancer_ppo_selfplay_v2",
    )

    train_client_against_freelancer(
        client_v1,
        freelancer_v1,
        client_v2,
        timesteps=100_000,
    )

    train_freelancer_against_client(
        freelancer_v1,
        client_v2,
        freelancer_v2,
        timesteps=100_000,
    )

    # --------------------------------------------------
    # CYCLE 3
    # --------------------------------------------------

    client_v3 = os.path.join(
        PROJECT_ROOT,
        "models",
        "client_ppo_selfplay_v3",
    )

    freelancer_v3 = os.path.join(
        PROJECT_ROOT,
        "models",
        "freelancer_ppo_selfplay_v3",
    )

    train_client_against_freelancer(
        client_v2,
        freelancer_v2,
        client_v3,
        timesteps=100_000,
    )

    train_freelancer_against_client(
        freelancer_v2,
        client_v2,
        freelancer_v3,
        timesteps=100_000,
    )

    print("\n" + "=" * 70)
    print("PPO VS PPO TRAINING COMPLETE")
    print("=" * 70)

    print("\nFinal Client model:")
    print(
        "models/client_ppo_selfplay_v3.zip"
    )

    print("\nFinal Freelancer model:")
    print(
        "models/freelancer_ppo_selfplay_v3.zip"
    )


if __name__ == "__main__":
    main()