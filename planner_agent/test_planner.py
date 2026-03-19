from __future__ import annotations

import json
import random

from budget_tool.budget import estimate_budget
from planner_agent.load_data import load_activities
from planner_agent.planner import PlannerAgent
from planner_agent.schemas import UserRequest


def build_stable_subset(all_activities, must_include_names, sample_size: int = 10):
    must_include_names = must_include_names or []
    selected = []
    selected_names = set()

    for activity in all_activities:
        lower_name = activity.name.lower()
        for need in must_include_names:
            if need.lower() in lower_name or lower_name in need.lower():
                if lower_name not in selected_names:
                    selected.append(activity)
                    selected_names.add(lower_name)

    remaining = [a for a in all_activities if a.name.lower() not in selected_names]
    extra_needed = max(0, sample_size - len(selected))

    if extra_needed > 0:
        selected.extend(random.sample(remaining, min(extra_needed, len(remaining))))

    return selected


def main() -> None:
    activities = load_activities("data/hk_activities.json")

    user_request = UserRequest(
        destination="Hong Kong",
        days=2,
        total_budget_hkd=6000,
        preferences=["sightseeing", "food", "budget", "harbour"],
        pace="moderate",
        must_include=["Star Ferry Tsim Sha Tsui to Central"],
        avoid=["hiking"],
        travelers=1,
        budget_style="standard",
    )

    activities_subset = build_stable_subset(
        all_activities=activities,
        must_include_names=user_request.must_include,
        sample_size=10,
    )

    planner = PlannerAgent(model_name="mistral:7b")
    planner_result = planner.plan(user_request, activities_subset)

    print("=== Planner Result ===")
    print(json.dumps(planner_result, ensure_ascii=False, indent=2))

    final_budget_result = estimate_budget(planner_result, user_request)
    print("\n=== Final Budget Check ===")
    print(json.dumps(final_budget_result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()