from stable_baselines3 import PPO


class ClientPPOAgent:
    """
    PPO-based autonomous client negotiation agent.

    Loads a trained PPO model and converts
    observations into negotiation actions.
    """

    def __init__(self, model_path="models/client_ppo"):
        print("Loading PPO client agent...")

        self.model = PPO.load(model_path)

        print("PPO client agent loaded successfully.")

    def get_action(self, observation):
        action, _ = self.model.predict(
            observation,
            deterministic=True
        )

        return int(action)