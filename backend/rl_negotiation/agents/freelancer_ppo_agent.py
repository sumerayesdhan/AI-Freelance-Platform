from stable_baselines3 import PPO


class FreelancerPPOAgent:
    """
    PPO-based freelancer negotiation agent.

    Loads a trained PPO model and converts
    observations into negotiation actions.
    """

    def __init__(
        self,
        model_path="models/freelancer_ppo"
    ):
        print("Loading PPO freelancer agent...")

        self.model = PPO.load(model_path)

        print("PPO freelancer agent loaded successfully.")

    def get_action(self, observation):
        """
        Predict the freelancer's negotiation action.
        """

        action, _ = self.model.predict(
            observation,
            deterministic=True
        )

        return int(action)