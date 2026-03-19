from __future__ import annotations

import json
import random
from pathlib import Path

from budget_tool.budget import estimate_budget
from critic_agent.critic import CriticAgent
from planner_agent.load_data import load_activities
from planner_agent.planner import PlannerAgent
from planner_agent.schemas import UserRequest


def build_demo_user_request() -> UserRequest:
    return UserRequest(
        destination="Hong Kong",
        days=2,
        total_budget_hkd=6000,
        preferences=["sightseeing", "food", "culture", "harbour"],
        pace="moderate",
        must_include=["Star Ferry"],
        avoid=["hiking"],
        travelers=1,
        budget_style="standard",
    )


def build_stable_subset(all_activities, must_include_names, sample_size: int = 10):
    must_include_names = must_include_names or []
    selected = []
    selected_names = set()

    for activity in all_activities:
        lower_name = activity.name.lower()
        for need in must_include_names:
            need_lower = need.lower()
            if need_lower in lower_name or lower_name in need_lower:
                if lower_name not in selected_names:
                    selected.append(activity)
                    selected_names.add(lower_name)

    remaining = [a for a in all_activities if a.name.lower() not in selected_names]
    extra_needed = max(0, sample_size - len(selected))

    if extra_needed > 0:
        selected.extend(random.sample(remaining, min(extra_needed, len(remaining))))

    return selected


def save_json(data, path: str) -> None:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    activities = load_activities("data/hk_activities.json")
    user_request = build_demo_user_request()

    planner = PlannerAgent(model_name="mistral:7b")

    planner_result = None
    chosen_subset = None

    for sample_size in [10, 8, 6]:
        print(f"\n[Fallback] Trying candidate subset size = {sample_size}")
        for attempt in range(1, 4):
            print(f"[Attempt {attempt}]")
            try:
                subset = build_stable_subset(
                    all_activities=activities,
                    must_include_names=user_request.must_include,
                    sample_size=sample_size,
                )
                result = planner.plan(user_request, subset)
                planner_result = result
                chosen_subset = subset
                print("[Success] Planner output generated.")
                break
            except Exception as e:
                print(f"[Failed] {e}")

        if planner_result is not None:
            break

    if planner_result is None or chosen_subset is None:
        raise RuntimeError("Planner failed after all fallback attempts.")

    print("\n=== Planner Result ===")
    print(json.dumps(planner_result, ensure_ascii=False, indent=2))

    budget_result = estimate_budget(planner_result, user_request)
    print("\n=== Budget Result ===")
    print(json.dumps(budget_result, ensure_ascii=False, indent=2))

    critic = CriticAgent()
    critique_result = critic.critique(
        planner_output=planner_result,
        budget_output=budget_result,
        user_request=user_request,
        activities=chosen_subset,
    )

    print("\n=== Critic Result ===")
    print(json.dumps(critique_result, ensure_ascii=False, indent=2))

    combined = {
        "user_request": {
            "destination": user_request.destination,
            "days": user_request.days,
            "total_budget_hkd": user_request.total_budget_hkd,
            "preferences": user_request.preferences,
            "pace": user_request.pace,
            "must_include": user_request.must_include,
            "avoid": user_request.avoid,
            "travelers": user_request.travelers,
            "budget_style": user_request.budget_style,
        },
        "planner_result": planner_result,
        "budget_result": budget_result,
        "critic_result": critique_result,
    }

    save_json(combined, "outputs/critic_demo_result.json")
    save_json(combined, "outputs/critic_demo_pretty.json")

    print("\nSaved to:")
    print("- outputs/critic_demo_result.json")
    print("- outputs/critic_demo_pretty.json")


if __name__ == "__main__":
    main()