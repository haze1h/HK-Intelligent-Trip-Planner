from __future__ import annotations

import json

from planner_agent.load_data import load_activities
from planner_agent.planner import PlannerAgent
from planner_agent.schemas import UserRequest


def main() -> None:
    activities = load_activities("data/hk_activities.json")

    user_request = UserRequest(
        destination="Hong Kong",
        days=3,
        total_budget_hkd=800,
        preferences=["sightseeing", "food", "budget", "harbour"],
        pace="moderate",
        must_include=["Star Ferry Tsim Sha Tsui to Central"],
        avoid=["hiking"],
    )

    planner = PlannerAgent(model_name="qwen3:4b")
    result = planner.plan(user_request, activities)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
