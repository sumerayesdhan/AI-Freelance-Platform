import gymnasium as gym
from gymnasium import spaces
import numpy as np


class NegotiationEnv(gym.Env):
    """
    Negotiation environment.

    The RL agent represents the freelancer.
    The client uses a simple rule-based strategy.

    The freelancer learns how to negotiate:
        - price
        - timeline
        - accept/reject/counter
    """

    metadata = {"render_modes": ["human"]}

    def __init__(self, render_mode=None):

        super().__init__()

        self.render_mode = render_mode

        # =====================================================
        # NEGOTIATION LIMITS
        # =====================================================

        self.max_rounds = 10

        self.min_price = 400.0
        self.max_price = 2000.0

        self.min_days = 5.0
        self.max_days = 60.0

        # =====================================================
        # ACTION SPACE
        # =====================================================
        #
        # 0 -> Accept
        # 1 -> Reject
        # 2 -> Lower price by 10%
        # 3 -> Lower price by 5%
        # 4 -> Increase price by 5%
        # 5 -> Request shorter timeline
        # 6 -> Balanced counter-offer
        #
        # =====================================================

        self.action_space = spaces.Discrete(7)

        # =====================================================
        # OBSERVATION SPACE
        # =====================================================
        #
        # 0 -> current round
        # 1 -> client budget
        # 2 -> freelancer minimum price
        # 3 -> current offer price
        # 4 -> client desired timeline
        # 5 -> freelancer minimum timeline
        # 6 -> current timeline
        # 7 -> freelancer initial asking price
        #
        # All values are normalized between 0 and 1.
        #
        # =====================================================

        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(8,),
            dtype=np.float32
        )

        # =====================================================
        # STATE VARIABLES
        # =====================================================

        self.round_number = 0

        self.client_budget = 0.0

        self.freelancer_min_price = 0.0

        self.current_price = 0.0

        self.client_desired_days = 0.0

        self.freelancer_min_days = 0.0

        self.current_days = 0.0

        self.freelancer_initial_price = 0.0

    # =========================================================
    # RESET
    # =========================================================

    def reset(self, *, seed=None, options=None):

        super().reset(seed=seed)

        self.round_number = 0

        # -----------------------------------------------------
        # Generate client budget
        # -----------------------------------------------------

        self.client_budget = float(
            self.np_random.uniform(
                800.0,
                1200.0
            )
        )

        # -----------------------------------------------------
        # Generate freelancer minimum acceptable price
        # -----------------------------------------------------

        self.freelancer_min_price = float(
            self.np_random.uniform(
                650.0,
                850.0
            )
        )

        # -----------------------------------------------------
        # Generate freelancer initial asking price
        # -----------------------------------------------------

        self.freelancer_initial_price = float(
            self.np_random.uniform(
                1000.0,
                1400.0
            )
        )

        # -----------------------------------------------------
        # Generate timeline requirements
        # -----------------------------------------------------

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
            self.client_budget * 0.75
        )

        self.current_days = (
            self.client_desired_days
        )

        observation = self._get_observation()

        info = {

            "client_budget":
                self.client_budget,

            "freelancer_min_price":
                self.freelancer_min_price,

            "freelancer_initial_price":
                self.freelancer_initial_price,

            "client_desired_days":
                self.client_desired_days,

            "freelancer_min_days":
                self.freelancer_min_days

        }

        return observation, info

    # =========================================================
    # STEP
    # =========================================================

    def step(self, action):

        self.round_number += 1

        terminated = False

        truncated = False

        # Small penalty for continuing negotiation.
        reward = -2.0

        # =====================================================
        # ACTION 0 — ACCEPT
        # =====================================================

        if action == 0:

            if self._is_offer_acceptable():

                reward = self._agreement_reward()

            else:

                reward = -40.0

            terminated = True

        # =====================================================
        # ACTION 1 — REJECT
        # =====================================================

        elif action == 1:

            reward = -50.0

            terminated = True

        # =====================================================
        # ACTION 2 — LOWER PRICE BY 10%
        # =====================================================

        elif action == 2:

            self.current_price *= 0.90

            self._client_response()

        # =====================================================
        # ACTION 3 — LOWER PRICE BY 5%
        # =====================================================

        elif action == 3:

            self.current_price *= 0.95

            self._client_response()

        # =====================================================
        # ACTION 4 — INCREASE PRICE BY 5%
        # =====================================================

        elif action == 4:

            self.current_price *= 1.05

            self.current_price = min(
                self.current_price,
                self.max_price
            )

            self._client_response()

        # =====================================================
        # ACTION 5 — SHORTER TIMELINE
        # =====================================================

        elif action == 5:

            self.current_days -= 2.0

            self.current_days = max(
                self.current_days,
                self.min_days
            )

            self._client_response()

        # =====================================================
        # ACTION 6 — BALANCED COUNTER
        # =====================================================

        elif action == 6:

            self.current_price *= 0.95

            self.current_days -= 1.0

            self.current_price = max(
                self.current_price,
                self.min_price
            )

            self.current_days = max(
                self.current_days,
                self.min_days
            )

            self._client_response()

        # =====================================================
        # MAXIMUM ROUNDS
        # =====================================================

        if self.round_number >= self.max_rounds:

            terminated = True

            if self._is_offer_acceptable():

                reward += self._agreement_reward()

            else:

                reward -= 30.0

        # =====================================================
        # CREATE NEXT OBSERVATION
        # =====================================================

        observation = self._get_observation()

        info = {

            "round":
                self.round_number,

            "price":
                self.current_price,

            "timeline_days":
                self.current_days,

            "agreement":
                (
                    terminated
                    and self._is_offer_acceptable()
                    and action == 0
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
    # CLIENT RESPONSE
    # =========================================================

    def _client_response(self):

        """
        Rule-based client response.

        The client tries to move the offer toward
        the client's budget.
        """

        if self.current_price <= self.client_budget:

            self.current_price = min(
                self.current_price,
                self.client_budget
            )

        else:

            self.current_price = (
                self.current_price
                + self.client_budget
            ) / 2.0

        # -----------------------------------------------------
        # Timeline response
        # -----------------------------------------------------

        if (
            self.current_days
            >
            self.client_desired_days
        ):

            self.current_days -= 1.0

        elif (
            self.current_days
            <
            self.client_desired_days
        ):

            self.current_days += 1.0

        self.current_days = min(
            max(
                self.current_days,
                self.min_days
            ),
            self.max_days
        )

    # =========================================================
    # CHECK WHETHER OFFER IS ACCEPTABLE
    # =========================================================

    def _is_offer_acceptable(self):

        price_ok = (
            self.current_price
            >=
            self.freelancer_min_price
        )

        budget_ok = (
            self.current_price
            <=
            self.client_budget
        )

        timeline_ok = (
            self.current_days
            >=
            self.freelancer_min_days
        )

        return (
            price_ok
            and budget_ok
            and timeline_ok
        )

    # =========================================================
    # AGREEMENT REWARD
    # =========================================================

    def _agreement_reward(self):

        price_margin = (
            self.current_price
            -
            self.freelancer_min_price
        )

        price_reward = (
            price_margin / 10.0
        )

        timeline_difference = abs(
            self.current_days
            -
            self.client_desired_days
        )

        timeline_reward = max(
            0.0,
            20.0 - timeline_difference
        )

        reward = (
            100.0
            +
            price_reward
            +
            timeline_reward
        )

        return reward

    # =========================================================
    # CREATE NORMALIZED OBSERVATION
    # =========================================================

    def _get_observation(self):

        observation = np.array(
            [

                self.round_number
                /
                self.max_rounds,

                self.client_budget
                /
                self.max_price,

                self.freelancer_min_price
                /
                self.max_price,

                self.current_price
                /
                self.max_price,

                self.client_desired_days
                /
                self.max_days,

                self.freelancer_min_days
                /
                self.max_days,

                self.current_days
                /
                self.max_days,

                self.freelancer_initial_price
                /
                self.max_price

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
            f"Client Budget: ${self.client_budget:.2f}"
        )