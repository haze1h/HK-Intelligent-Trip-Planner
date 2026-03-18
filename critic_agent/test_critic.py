from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any, Dict, List, Tuple

from budget_tool.budget import estimate_budget
from critic_agent.critic import critic_agent
from planner_agent.load_data import load_activities
from planner_agent.planner import PlannerAgent
from planner_agent.schemas import UserRequest


OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


def print_section(title: str) -> None:
    line = "=" * 80
    print(f"\n{line}\n{title}\n{line}")


def save_json(data: Dict[str, Any], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_user_request(user_request: UserRequest) -> None:
    print_section("USER REQUEST")
    print(f"Destination     : {user_request.destination}")
    print(f"Days            : {user_request.days}")
    print(f"Total Budget    : HKD {user_request.total_budget_hkd}")
    print(f"Pace            : {user_request.pace}")
    print(f"Travelers       : {user_request.travelers}")
    print(f"Budget Style    : {user_request.budget_style}")
    print(f"Preferences     : {user_request.preferences}")
    print(f"Must Include    : {user_request.must_include}")
    print(f"Avoid           : {user_request.avoid}")


def print_planner_summary(planner_result: Dict[str, Any]) -> None:
    print_section("PLANNER SUMMARY")

    print(f"Destination              : {planner_result.get('destination')}")
    print(f"Days                     : {planner_result.get('days')}")
    print(f"Activity Budget          : HKD {planner_result.get('activity_budget_hkd')}")
    print(
        f"Estimated Activity Cost  : HKD {planner_result.get('total_estimated_activity_cost_hkd')}"
    )
    print(f"Within Activity Budget   : {planner_result.get('activities_within_budget')}")
    print(f"Planning Summary         : {planner_result.get('planning_summary')}")

    itinerary = planner_result.get("itinerary", [])
    for day_plan in itinerary:
        print(f"\nDay {day_plan.get('day')}:")
        for slot in ["morning", "afternoon", "evening"]:
            slot_obj = day_plan.get(slot, {})
            print(
                f"  {slot.capitalize():<10}"
                f"{slot_obj.get('activity_name', 'N/A')} "
                f"| {slot_obj.get('area', 'N/A')} "
                f"| {slot_obj.get('category', 'N/A')} "
                f"| HKD {slot_obj.get('estimated_cost_hkd', 'N/A')} "
                f"| {slot_obj.get('duration_hours', 'N/A')}h"
            )
        print(f"  Daily Cost  : HKD {day_plan.get('daily_cost_hkd', 'N/A')}")
        notes = day_plan.get("notes", "")
        print(f"  Notes       : {notes if notes else '(empty)'}")


def print_budget_summary(budget_result: Dict[str, Any]) -> None:
    print_section("BUDGET SUMMARY")

    print(f"Activity Budget                 : HKD {budget_result.get('activity_budget_hkd')}")
    print(
        f"Activity Estimated Total        : HKD {budget_result.get('activity_total_estimated_cost_hkd')}"
    )
    print(
        f"Activities Within Budget        : {budget_result.get('activities_within_budget')}"
    )
    print(
        f"Activity Over Budget By         : HKD {budget_result.get('activity_over_budget_by_hkd')}"
    )
    print(
        f"Total Trip Estimated Cost       : HKD {budget_result.get('total_trip_estimated_cost_hkd')}"
    )
    print(
        f"Total Trip Within Budget        : {budget_result.get('total_trip_within_budget')}"
    )
    print(
        f"Total Trip Over Budget By       : HKD {budget_result.get('total_over_budget_by_hkd')}"
    )

    breakdown = budget_result.get("breakdown", {})
    if breakdown:
        print("\nEstimated Cost Breakdown:")
        for key, value in breakdown.items():
            print(f"  {key:<20} HKD {value}")

    suggestions = budget_result.get("suggestions", [])
    if suggestions:
        print("\nBudget Suggestions:")
        for idx, suggestion in enumerate(suggestions, start=1):
            print(f"  {idx}. {suggestion}")


def print_critic_summary(critic_result: Dict[str, Any]) -> None:
    print_section("CRITIC SUMMARY")

    print(f"Overall Score    : {critic_result.get('overall_score')}/100")
    print(f"Is Feasible      : {critic_result.get('is_feasible')}")
    print(f"Summary          : {critic_result.get('summary')}")

    strengths = critic_result.get("strengths", [])
    if strengths:
        print("\nStrengths:")
        for idx, item in enumerate(strengths, start=1):
            print(f"  {idx}. {item}")

    issues = critic_result.get("issues", [])
    if issues:
        print("\nIssues:")
        for idx, issue in enumerate(issues, start=1):
            print(
                f"  {idx}. [{issue.get('severity', '').upper()}] "
                f"{issue.get('type', 'unknown')}: {issue.get('message', '')}"
            )

    suggestions = critic_result.get("suggestions", [])
    if suggestions:
        print("\nSuggestions:")
        for idx, item in enumerate(suggestions, start=1):
            print(f"  {idx}. {item}")


def build_full_result(
    user_request: UserRequest,
    planner_result: Dict[str, Any],
    budget_result: Dict[str, Any],
    critic_result: Dict[str, Any],
) -> Dict[str, Any]:
    return {
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
        "critic_result": critic_result,
    }


def build_pretty_result(
    user_request: UserRequest,
    planner_result: Dict[str, Any],
    budget_result: Dict[str, Any],
    critic_result: Dict[str, Any],
) -> Dict[str, Any]:
    itinerary_preview: List[Dict[str, Any]] = []

    for day in planner_result.get("itinerary", []):
        itinerary_preview.append(
            {
                "day": day.get("day"),
                "morning": day.get("morning", {}).get("activity_name"),
                "afternoon": day.get("afternoon", {}).get("activity_name"),
                "evening": day.get("evening", {}).get("activity_name"),
                "daily_cost_hkd": day.get("daily_cost_hkd"),
            }
        )

    top_issues = [issue.get("message", "") for issue in critic_result.get("issues", [])[:3]]
    top_suggestions = critic_result.get("suggestions", [])[:3]
    top_strengths = critic_result.get("strengths", [])[:3]

    return {
        "trip_overview": {
            "destination": user_request.destination,
            "days": user_request.days,
            "budget_hkd": user_request.total_budget_hkd,
            "preferences": user_request.preferences,
            "pace": user_request.pace,
            "must_include": user_request.must_include,
            "avoid": user_request.avoid,
        },
        "planner_summary": {
            "planning_summary": planner_result.get("planning_summary"),
            "itinerary_preview": itinerary_preview,
        },
        "budget_summary": {
            "activity_budget_hkd": budget_result.get("activity_budget_hkd"),
            "activity_total_estimated_cost_hkd": budget_result.get(
                "activity_total_estimated_cost_hkd"
            ),
            "total_trip_estimated_cost_hkd": budget_result.get("total_trip_estimated_cost_hkd"),
            "total_trip_within_budget": budget_result.get("total_trip_within_budget"),
        },
        "critic_summary": {
            "overall_score": critic_result.get("overall_score"),
            "is_feasible": critic_result.get("is_feasible"),
            "summary": critic_result.get("summary"),
            "top_strengths": top_strengths,
            "top_issues": top_issues,
            "top_suggestions": top_suggestions,
        },
    }


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


def run_planner_with_retry(
    planner: PlannerAgent,
    user_request: UserRequest,
    activities_subset: List[Any],
    max_retries: int = 3,
) -> Dict[str, Any]:
    last_error: Exception | None = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Planner attempt {attempt}/{max_retries} with {len(activities_subset)} activities...")
            return planner.plan(user_request, activities_subset)
        except Exception as e:
            last_error = e
            print(f"Planner failed on attempt {attempt}: {type(e).__name__}: {e}")

    raise RuntimeError(
        f"Planner failed after {max_retries} attempts with {len(activities_subset)} activities. "
        f"Last error: {last_error}"
    )


def run_planner_fallback(
    planner: PlannerAgent,
    user_request: UserRequest,
    all_activities: List[Any],
) -> Tuple[Dict[str, Any], List[Any]]:
    """
    Try the planner with gradually smaller activity subsets to reduce malformed JSON risk.
    """
    fallback_sizes = [10, 8, 6]

    for size in fallback_sizes:
        subset = random.sample(all_activities, min(size, len(all_activities)))
        try:
            print_section(f"RUNNING PLANNER (fallback size = {len(subset)})")
            result = run_planner_with_retry(
                planner=planner,
                user_request=user_request,
                activities_subset=subset,
                max_retries=3,
            )
            return result, subset
        except Exception as e:
            print(f"Planner failed for fallback size {size}: {type(e).__name__}: {e}")

    raise RuntimeError(
        "Planner failed for all fallback activity sizes (10, 8, 6). "
        "The local LLM output is too unstable to produce valid JSON right now."
    )


def main() -> None:
    try:
        print_section("LOADING DATA")
        activities = load_activities("data/hk_activities.json")
        print(f"Loaded {len(activities)} activities from data/hk_activities.json")

        random.seed(42)

        user_request = build_demo_user_request()
        print_user_request(user_request)

        planner = PlannerAgent(model_name="mistral:7b")

        planner_result, sampled_activities = run_planner_fallback(
            planner=planner,
            user_request=user_request,
            all_activities=activities,
        )

        print_planner_summary(planner_result)

        print_section("RUNNING BUDGET TOOL")
        budget_result = estimate_budget(planner_result, user_request)
        print_budget_summary(budget_result)

        print_section("RUNNING CRITIC AGENT")
        critic_result = critic_agent(
            planner_output=planner_result,
            budget_output=budget_result,
            user_request=user_request,
            activities=sampled_activities,
        )
        print_critic_summary(critic_result)

        full_result = build_full_result(
            user_request=user_request,
            planner_result=planner_result,
            budget_result=budget_result,
            critic_result=critic_result,
        )
        pretty_result = build_pretty_result(
            user_request=user_request,
            planner_result=planner_result,
            budget_result=budget_result,
            critic_result=critic_result,
        )

        full_path = OUTPUT_DIR / "critic_demo_result.json"
        pretty_path = OUTPUT_DIR / "critic_demo_pretty.json"

        save_json(full_result, full_path)
        save_json(pretty_result, pretty_path)

        print_section("RESULT FILES SAVED")
        print(f"Full result   : {full_path}")
        print(f"Pretty result : {pretty_path}")

    except FileNotFoundError as e:
        print_section("ERROR")
        print(f"Missing file: {e}")
        print("Please check whether data/hk_activities.json exists.")

    except ValueError as e:
        print_section("VALIDATION ERROR")
        print(str(e))

    except Exception as e:
        print_section("UNEXPECTED ERROR")
        print(f"{type(e).__name__}: {e}")


if __name__ == "__main__":
    main()