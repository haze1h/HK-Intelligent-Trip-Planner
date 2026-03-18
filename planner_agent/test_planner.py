from __future__ import annotations

import json
import random

from budget_tool.budget import estimate_budget
from planner_agent.load_data import load_activities
from planner_agent.planner import PlannerAgent
from planner_agent.schemas import UserRequest


def main() -> None:
    activities = load_activities("data/hk_activities.json")
    activities = random.sample(activities, 10)

    user_request = UserRequest(
        destination="Hong Kong",
        days=2,
        total_budget_hkd=6000,
        preferences=["sightseeing", "food", "budget", "harbour"],
        pace="moderate",
        must_include=["Star Ferry Tsim Sha Tsui to Central"],
        avoid=["hiking"],
        travelers=1,
        budget_style="standard",  # 可以显式填 economy / standard / premium,也可以留空让系统根据预算自动判断
    )

    planner = PlannerAgent(model_name="mistral:7b")
    planner_result = planner.plan(user_request, activities)

    print("=== Planner Result ===")
    print(json.dumps(planner_result, ensure_ascii=False, indent=2))

    final_budget_result = estimate_budget(planner_result, user_request)
    print("\n=== Final Budget Check ===")
    print(json.dumps(final_budget_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()