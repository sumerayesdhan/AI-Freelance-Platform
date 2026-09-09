import gymnasium as gym
from gymnasium import spaces
import numpy as np


class ClientNegotiationEnv(gym.Env):
    """
    PPO training environment for the client.

    The client learns to:
        - protect its budget
        - negotiate price
        - negotiate timeline
        - accept reasonable offers
        - reject unacceptable offers
        - reach agreement efficiently

    The environment uses a simulated freelancer response.
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, max_rounds=10, render_mode=None):
        super().__init__()

        self.max_rounds = max_rounds
        self.render_mode = render_mode

        # -----------------------------------------------------
        # Negotiation limits
        # -----------------------------------------------------

        self.min_price = 400.0
        self.max_price = 2000.0

        self.min_days = 5.0
        self.max_days = 60.0

        # -----------------------------------------------------
        # Actions
        # -----------------------------------------------------

        self.action_space = spaces.Discrete(7)

        # 0 -> Accept
        # 1 -> Reject
        # 2 -> Decrease price 10%
        # 3 -> Decrease price 5%
        # 4 -> Increase price 5%
        # 5 -> Request shorter timeline
        # 6 -> Balanced counter

        # -----------------------------------------------------
        # Observation
        # -----------------------------------------------------

        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(8,),
            dtype=np.float32
        )

        # -----------------------------------------------------
        # State
        # -----------------------------------------------------

        self.round_number = 0

        self.client_budget = 0.0
        self.client_target_price = 0.0

        self.freelancer_min_price = 0.0
        self.freelancer_initial_price = 0.0

        self.client_desired_days = 0.0
        self.freelancer_min_days = 0.0

        self.current_price = 0.0
        self.current_days = 0.0

    # =========================================================
    # RESET
    # =========================================================

    def reset(self, *, seed=None, options=None):

        super().reset(seed=seed)

        self.round_number = 0

        # -----------------------------------------------------
        # Generate scenario
        # -----------------------------------------------------

        self.client_budget = float(
            self.np_random.uniform(
                800.0,
                1200.0
            )
        )

        # Client has an internal target below its maximum budget.
        self.client_target_price = (
            self.client_budget
            * self.np_random.uniform(0.75, 0.90)
        )

        self.freelancer_min_price = float(
            self.np_random.uniform(
                650.0,
                850.0
            )
        )

        self.freelancer_initial_price = float(
            self.np_random.uniform(
                1000.0,
                1400.0
            )
        )

        self.client_desired_days = float(
            self.np_random.uniform(
                12.0,
                20.0
            )
        )

        self.freelancer_min_days = float(
            self.np_random.uniform(
                10.0,
                25.0
            )
        )

        # -----------------------------------------------------
        # Initial client offer
        # -----------------------------------------------------

        self.current_price = (
            self.client_target_price
        )

        self.current_days = (
            self.client_desired_days
        )

        return self._get_observation(), {}

    # =========================================================
    # STEP
    # =========================================================

    def step(self, action):

        action = int(action)

        self.round_number += 1

        reward = -1.0

        terminated = False
        truncated = False

        # -----------------------------------------------------
        # Apply client action
        # -----------------------------------------------------

        old_price = self.current_price
        old_days = self.current_days

        self._apply_action(action)

        # -----------------------------------------------------
        # ACCEPT
        # -----------------------------------------------------

        if action == 0:

            if self._is_offer_acceptable():

                terminated = True

                reward = self._calculate_agreement_reward()

            else:

                # Invalid acceptance
                terminated = False

                reward = -25.0

        # -----------------------------------------------------
        # REJECT
        # -----------------------------------------------------

        elif action == 1:

            # Rejecting a feasible negotiation is undesirable.
            if self._is_offer_acceptable():

                reward = -35.0

            else:

                reward = -10.0

            terminated = True

        # -----------------------------------------------------
        # COUNTER OFFER
        # -----------------------------------------------------

        else:

            # Reward useful movement toward target.
            old_distance = abs(
                old_price -
                self.client_target_price
            )

            new_distance = abs(
                self.current_price -
                self.client_target_price
            )

            improvement = (
                old_distance -
                new_distance
            )

            reward += improvement / 20.0

            # Penalize moving outside budget.
            if self.current_price > self.client_budget:
                reward -= 20.0

            # Reward staying within acceptable timeline.
            if (
                self.current_days
                <= self.client_desired_days + 5
            ):
                reward += 2.0

        # -----------------------------------------------------
        # Maximum rounds
        # -----------------------------------------------------

        if self.round_number >= self.max_rounds:

            if not terminated:

                terminated = True

                reward -= 20.0

        # -----------------------------------------------------
        # Observation
        # -----------------------------------------------------

        observation = self._get_observation()

        info = {
            "client_budget": self.client_budget,
            "client_target_price": self.client_target_price,
            "freelancer_min_price": self.freelancer_min_price,
            "freelancer_initial_price":
                self.freelancer_initial_price,
            "client_desired_days":
                self.client_desired_days,
            "freelancer_min_days":
                self.freelancer_min_days,
            "current_price": self.current_price,
            "current_days": self.current_days,
            "agreement": (
                terminated
                and action == 0
                and self._is_offer_acceptable()
            )
        }

        return (
            observation,
            float(reward),
            terminated,
            truncated,
            info
        )

    # =========================================================
    # APPLY ACTION
    # =========================================================

    def _apply_action(self, action):

        # ACCEPT
        if action == 0:
            return

        # REJECT
        if action == 1:
            return

        # DECREASE PRICE 10%
        if action == 2:

            self.current_price *= 0.90

        # DECREASE PRICE 5%
        elif action == 3:

            self.current_price *= 0.95

        # INCREASE PRICE 5%
        elif action == 4:

            self.current_price *= 1.05

        # SHORTER TIMELINE
        elif action == 5:

            self.current_days -= 2.0

        # BALANCED COUNTER
        elif action == 6:

            self.current_price = (
                self.current_price
                + self.client_target_price
            ) / 2.0

            self.current_days = (
                self.current_days
                + self.client_desired_days
            ) / 2.0

        # -----------------------------------------------------
        # Safety limits
        # -----------------------------------------------------

        self.current_price = np.clip(
            self.current_price,
            self.freelancer_min_price,
            self.client_budget
        )

        self.current_days = np.clip(
            self.current_days,
            self.freelancer_min_days,
            self.client_desired_days + 10.0
        )

    # =========================================================
    # ACCEPTANCE CHECK
    # =========================================================

    def _is_offer_acceptable(self):

        price_ok = (
            self.current_price
            >= self.freelancer_min_price
        )

        budget_ok = (
            self.current_price
            <= self.client_budget
        )

        timeline_ok = (
            self.current_days
            >= self.freelancer_min_days
        )

        return (
            price_ok
            and budget_ok
            and timeline_ok
        )

    # =========================================================
    # AGREEMENT REWARD
    # =========================================================

    def _calculate_agreement_reward(self):

        # -----------------------------------------------------
        # Price efficiency
        # -----------------------------------------------------

        price_saving = (
            self.client_budget
            - self.current_price
        )

        price_score = (
            price_saving
            / self.client_budget
        ) * 50.0

        # -----------------------------------------------------
        # Timeline quality
        # -----------------------------------------------------

        timeline_difference = abs(
            self.current_days
            - self.client_desired_days
        )

        timeline_score = max(
            0.0,
            30.0
            - (timeline_difference * 3.0)
        )

        # -----------------------------------------------------
        # Efficiency
        # -----------------------------------------------------

        round_penalty = (
            self.round_number * 2.0
        )

        # -----------------------------------------------------
        # Final reward
        # -----------------------------------------------------

        reward = (
            50.0
            + price_score
            + timeline_score
            - round_penalty
        )

        return reward

    # =========================================================
    # OBSERVATION
    # =========================================================

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
                / self.max_price
            ],
            dtype=np.float32
        )

        return np.clip(
            observation,
            0.0,
            1.0
        )

    # =========================================================
    # RENDER
    # =========================================================

    def render(self):

        print(
            f"Round: {self.round_number} | "
            f"Price: ${self.current_price:.2f} | "
            f"Timeline: {self.current_days:.1f} days | "
            f"Budget: ${self.client_budget:.2f}"
        )