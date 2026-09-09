import gymnasium as gym
from gymnasium import spaces
import numpy as np


class PPOvsPPOEnv(gym.Env):
    """
    Alternating PPO negotiation environment.

    The learning agent is controlled by Stable-Baselines3.
    The opponent is another already-trained PPO model.

    agent_role:
        "client"      -> Client PPO learns against Freelancer PPO
        "freelancer"  -> Freelancer PPO learns against Client PPO

    Actions:
        0 = ACCEPT
        1 = REJECT
        2 = DECREASE_PRICE_10
        3 = DECREASE_PRICE_5
        4 = INCREASE_PRICE_5
        5 = SHORTER_TIMELINE
        6 = BALANCED_COUNTER
    """

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        opponent_model=None,
        agent_role="client",
        max_rounds=10,
        render_mode=None,
    ):
        super().__init__()

        self.opponent_model = opponent_model
        self.agent_role = agent_role
        self.max_rounds = max_rounds
        self.render_mode = render_mode

        self.min_price = 400.0
        self.max_price = 2000.0

        self.min_days = 5.0
        self.max_days = 60.0

        self.action_space = spaces.Discrete(7)

        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(8,),
            dtype=np.float32,
        )

        self.round_number = 0

        self.client_budget = 0.0
        self.client_target_price = 0.0
        self.client_desired_days = 0.0

        self.freelancer_min_price = 0.0
        self.freelancer_preferred_price = 0.0
        self.freelancer_initial_price = 0.0
        self.freelancer_min_days = 0.0

        self.current_price = 0.0
        self.current_days = 0.0

    def reset(self, *, seed=None, options=None):

        super().reset(seed=seed)

        self.round_number = 0

        # ==============================
        # CLIENT PARAMETERS
        # ==============================

        self.client_budget = float(
            self.np_random.uniform(
                800.0,
                1200.0,
            )
        )

        self.client_target_price = (
            self.client_budget
            * float(
                self.np_random.uniform(
                    0.75,
                    0.90,
                )
            )
        )

        self.client_desired_days = float(
            self.np_random.uniform(
                12.0,
                20.0,
            )
        )

        # ==============================
        # FREELANCER PARAMETERS
        # ==============================

        self.freelancer_min_price = float(
            self.np_random.uniform(
                650.0,
                850.0,
            )
        )

        self.freelancer_preferred_price = (
            self.freelancer_min_price
            + float(
                self.np_random.uniform(
                    100.0,
                    300.0,
                )
            )
        )

        self.freelancer_initial_price = float(
            self.np_random.uniform(
                1000.0,
                1400.0,
            )
        )

        self.freelancer_min_days = float(
            self.np_random.uniform(
                10.0,
                25.0,
            )
        )

        # ==============================
        # INITIAL OFFER
        # ==============================

        self.current_price = (
            self.client_target_price
        )

        self.current_days = (
            self.client_desired_days
        )

        return self._get_observation(), {}

    def step(self, action):

        action = int(action)

        self.round_number += 1

        terminated = False
        truncated = False

        old_price = self.current_price
        old_days = self.current_days

        # ==========================================
        # LEARNING AGENT ACTION
        # ==========================================

        action_name = self._action_name(action)

        if action == 0:

            if self._is_agreement_possible():

                terminated = True

                reward = self._agreement_reward()

                reason = "Agreement reached"

            else:

                terminated = True

                reward = -30.0

                reason = "Invalid acceptance"

        elif action == 1:

            if self._is_agreement_possible():

                reward = -40.0

                reason = "Rejected acceptable offer"

            else:

                reward = -5.0

                reason = "Negotiation rejected"

            terminated = True

        else:

            self._apply_action(action)

            reward = -1.0

            price_change = abs(
                self.current_price
                - old_price
            )

            days_change = abs(
                self.current_days
                - old_days
            )

            if price_change > 0:
                reward += 1.0

            if days_change > 0:
                reward += 0.5

            if (
                self.current_price
                >= self.freelancer_min_price
                and
                self.current_price
                <= self.client_budget
            ):
                reward += 2.0
            else:
                reward -= 5.0

            if (
                self.current_days
                >= self.freelancer_min_days
                and
                self.current_days
                <= self.client_desired_days + 10.0
            ):
                reward += 2.0
            else:
                reward -= 5.0

            reason = "Counter offer"

        # ==========================================
        # OPPONENT RESPONSE
        # ==========================================

        opponent_action = None
        opponent_action_name = None

        if (
            not terminated
            and self.opponent_model is not None
        ):

            opponent_obs = self._get_observation()

            opponent_action, _ = (
                self.opponent_model.predict(
                    opponent_obs,
                    deterministic=True,
                )
            )

            opponent_action = int(
                opponent_action
            )

            opponent_action_name = (
                self._action_name(
                    opponent_action
                )
            )

            (
                opponent_reward,
                opponent_terminated,
            ) = self._apply_opponent_action(
                opponent_action
            )

            if opponent_terminated:

                terminated = True

                # From learning agent perspective:
                if opponent_action == 0:

                    if self._is_agreement_possible():

                        reward += 25.0
                        reason = (
                            "Opponent accepted"
                        )

                    else:

                        reward -= 20.0
                        reason = (
                            "Opponent invalid acceptance"
                        )

                elif opponent_action == 1:

                    reward -= 25.0

                    reason = (
                        "Opponent rejected"
                    )

        # ==========================================
        # MAX ROUNDS
        # ==========================================

        if (
            self.round_number
            >= self.max_rounds
            and not terminated
        ):

            terminated = True

            reward -= 20.0

            reason = (
                "Maximum rounds reached"
            )

        observation = self._get_observation()

        agreement = (
            terminated
            and self._is_agreement_possible()
        )

        info = {
            "agent_role": self.agent_role,
            "round": self.round_number,
            "action": action,
            "action_name": action_name,
            "opponent_action": opponent_action,
            "opponent_action_name": (
                opponent_action_name
            ),
            "client_budget": self.client_budget,
            "client_target_price": (
                self.client_target_price
            ),
            "freelancer_min_price": (
                self.freelancer_min_price
            ),
            "freelancer_preferred_price": (
                self.freelancer_preferred_price
            ),
            "freelancer_initial_price": (
                self.freelancer_initial_price
            ),
            "client_desired_days": (
                self.client_desired_days
            ),
            "freelancer_min_days": (
                self.freelancer_min_days
            ),
            "current_price": (
                self.current_price
            ),
            "current_days": (
                self.current_days
            ),
            "agreement": agreement,
            "reason": reason,
        }

        return (
            observation,
            float(reward),
            terminated,
            truncated,
            info,
        )

    def _apply_opponent_action(
        self,
        action,
    ):

        if action == 0:

            if self._is_agreement_possible():
                return 25.0, True

            return -20.0, True

        if action == 1:

            return -25.0, True

        self._apply_action(action)

        return 0.0, False

    def _apply_action(self, action):

        if action == 2:

            self.current_price *= 0.90

        elif action == 3:

            self.current_price *= 0.95

        elif action == 4:

            self.current_price *= 1.05

        elif action == 5:

            self.current_days -= 2.0

        elif action == 6:

            self.current_price = (
                self.current_price
                + self.client_target_price
            ) / 2.0

            self.current_days = (
                self.current_days
                + self.client_desired_days
            ) / 2.0

        self.current_price = float(
            np.clip(
                self.current_price,
                self.freelancer_min_price,
                self.client_budget,
            )
        )

        self.current_days = float(
            np.clip(
                self.current_days,
                self.freelancer_min_days,
                self.client_desired_days + 10.0,
            )
        )

    def _is_agreement_possible(self):

        return (
            self.current_price
            >= self.freelancer_min_price
            and
            self.current_price
            <= self.client_budget
            and
            self.current_days
            >= self.freelancer_min_days
            and
            self.current_days
            <= self.client_desired_days + 10.0
        )

    def _agreement_reward(self):

        price_margin = (
            self.current_price
            - self.freelancer_min_price
        )

        freelancer_score = (
            price_margin
            / self.client_budget
        ) * 50.0

        client_saving = (
            self.client_budget
            - self.current_price
        )

        client_score = (
            client_saving
            / self.client_budget
        ) * 50.0

        preferred_difference = abs(
            self.current_price
            - self.freelancer_preferred_price
        )

        preferred_score = max(
            0.0,
            25.0
            - preferred_difference / 10.0,
        )

        timeline_difference = abs(
            self.current_days
            - self.client_desired_days
        )

        timeline_score = max(
            0.0,
            25.0
            - timeline_difference * 2.0,
        )

        round_penalty = (
            self.round_number * 2.0
        )

        return float(
            50.0
            + freelancer_score
            + client_score
            + preferred_score
            + timeline_score
            - round_penalty
        )

    def _get_observation(self):

        observation = np.array(
            [
                self.round_number
                / self.max_rounds,

                self.client_budget
                / self.max_price,

                self.freelancer_min_price
                / self.max_price,

                self.current_price
                / self.max_price,

                self.client_desired_days
                / self.max_days,

                self.freelancer_min_days
                / self.max_days,

                self.current_days
                / self.max_days,

                self.freelancer_initial_price
                / self.max_price,
            ],
            dtype=np.float32,
        )

        return np.clip(
            observation,
            0.0,
            1.0,
        )

    def _action_name(self, action):

        names = {
            0: "ACCEPT",
            1: "REJECT",
            2: "DECREASE_PRICE_10",
            3: "DECREASE_PRICE_5",
            4: "INCREASE_PRICE_5",
            5: "SHORTER_TIMELINE",
            6: "BALANCED_COUNTER",
        }

        return names.get(
            int(action),
            "UNKNOWN",
        )

    def render(self):

        print(
            f"Round: {self.round_number} | "
            f"Role: {self.agent_role} | "
            f"Price: ${self.current_price:.2f} | "
            f"Days: {self.current_days:.2f}"
        )