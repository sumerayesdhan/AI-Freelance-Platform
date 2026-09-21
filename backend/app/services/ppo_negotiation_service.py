from pathlib import Path

import numpy as np


ACTION_NAMES = {
    0: "ACCEPT",
    1: "REJECT",
    2: "DECREASE_PRICE_10",
    3: "DECREASE_PRICE_5",
    4: "INCREASE_PRICE_5",
    5: "SHORTER_TIMELINE",
    6: "BALANCED_COUNTER",
}


def _observation(parameters, round_number, price, timeline_days, max_rounds):
    price_scale = max(
        2000.0,
        parameters["client_budget"],
        parameters["freelancer_initial_price"],
    )
    days_scale = max(
        60.0,
        parameters["client_maximum_days"],
    )

    values = np.array(
        [
            round_number / max_rounds,
            parameters["client_budget"] / price_scale,
            parameters["freelancer_min_price"] / price_scale,
            price / price_scale,
            parameters["client_desired_days"] / days_scale,
            parameters["freelancer_min_days"] / days_scale,
            timeline_days / days_scale,
            parameters["freelancer_initial_price"] / price_scale,
        ],
        dtype=np.float32,
    )
    return np.clip(values, 0.0, 1.0)


def _apply_action(action, price, timeline_days, parameters, role):
    action = int(action)
    target_price = (
        parameters["client_target_budget"]
        if role == "client"
        else parameters["freelancer_preferred_price"]
    )
    target_days = (
        parameters["client_desired_days"]
        if role == "client"
        else parameters["freelancer_preferred_days"]
    )

    if action == 2:
        price *= 0.90
    elif action == 3:
        price *= 0.95
    elif action == 4:
        price *= 1.05
    elif action == 5:
        timeline_days -= 2.0
    elif action == 6:
        price = (price + target_price) / 2.0
        timeline_days = (timeline_days + target_days) / 2.0

    return (
        float(np.clip(
            price,
            parameters["freelancer_min_price"],
            parameters["client_budget"],
        )),
        float(np.clip(
            timeline_days,
            parameters["freelancer_min_days"],
            parameters["client_maximum_days"],
        )),
    )


def _is_agreement_possible(price, timeline_days, parameters):
    return (
        parameters["freelancer_min_price"] <= price <= parameters["client_budget"]
        and parameters["freelancer_min_days"]
        <= timeline_days
        <= parameters["client_maximum_days"]
    )


def run_ppo_negotiation(parameters, max_rounds=10):
    """Run the production client and freelancer PPO models alternately."""
    from stable_baselines3 import PPO

    backend_root = Path(__file__).resolve().parents[2]
    model_root = backend_root / "rl_negotiation" / "models"
    client_model = PPO.load(str(model_root / "client_ppo_v2.zip"))
    freelancer_model = PPO.load(str(model_root / "freelancer_ppo_v3.zip"))

    price = float(parameters["client_target_budget"])
    timeline_days = float(parameters["client_desired_days"])
    history = []

    for round_number in range(1, max_rounds + 1):
        for agent, model, role in (
            ("CLIENT_PPO", client_model, "client"),
            ("FREELANCER_PPO", freelancer_model, "freelancer"),
        ):
            observation = _observation(
                parameters,
                round_number,
                price,
                timeline_days,
                max_rounds,
            )
            action = int(model.predict(observation, deterministic=True)[0])
            action_name = ACTION_NAMES.get(action, "UNKNOWN")

            if action in (0, 1):
                history.append({
                    "round": round_number,
                    "agent": agent,
                    "action_number": action,
                    "action": action_name,
                    "price": round(price, 2),
                    "timeline_days": round(timeline_days, 2),
                })
                return {
                    "agreement": action == 0 and _is_agreement_possible(
                        price, timeline_days, parameters
                    ),
                    "final_price": round(price, 2),
                    "final_timeline_days": round(timeline_days, 2),
                    "rounds": round_number,
                    "history": history,
                    "failure_reason": (
                        None if action == 0 else f"{agent} rejected the offer"
                    ),
                }

            price, timeline_days = _apply_action(
                action,
                price,
                timeline_days,
                parameters,
                role,
            )
            history.append({
                "round": round_number,
                "agent": agent,
                "action_number": action,
                "action": action_name,
                "price": round(price, 2),
                "timeline_days": round(timeline_days, 2),
            })

    return {
        "agreement": False,
        "final_price": round(price, 2),
        "final_timeline_days": round(timeline_days, 2),
        "rounds": max_rounds,
        "history": history,
        "failure_reason": "Maximum negotiation rounds reached",
    }
