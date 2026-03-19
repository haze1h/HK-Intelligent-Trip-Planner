from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List

from planner_agent.schemas import BudgetAllocation, UserRequest

BUDGET_STYLE_TABLE = {
    "economy": {
        "accommodation_per_person_per_night": 450,
        "meals_per_person_per_day": 140,
        "transport_per_person_per_day": 55,
        "misc_per_person_per_day": 50,
    },
    "standard": {
        "accommodation_per_person_per_night": 750,
        "meals_per_person_per_day": 220,
        "transport_per_person_per_day": 75,
        "misc_per_person_per_day": 80,
    },
    "premium": {
        "accommodation_per_person_per_night": 1300,
        "meals_per_person_per_day": 380,
        "transport_per_person_per_day": 110,
        "misc_per_person_per_day": 130,
    },
}


def infer_budget_style(user_request: UserRequest) -> str:
    if user_request.budget_style in {"economy", "standard", "premium"}:
        return user_request.budget_style

    pref_text = " ".join([p.lower() for p in user_request.preferences])

    if any(word in pref_text for word in ["luxury", "premium", "high-end"]):
        return "premium"
    if any(word in pref_text for word in ["budget", "cheap", "affordable"]):
        return "economy"

    travelers = max(1, user_request.travelers)
    days = max(1, user_request.days)
    per_person_per_day = user_request.total_budget_hkd / travelers / days

    if per_person_per_day < 700:
        return "economy"
    if per_person_per_day < 1600:
        return "standard"
    return "premium"


def _pace_transport_multiplier(pace: str) -> float:
    pace = (pace or "moderate").lower()
    if pace == "slow":
        return 0.9
    if pace == "fast":
        return 1.15
    return 1.0


def _pace_meal_multiplier(pace: str) -> float:
    pace = (pace or "moderate").lower()
    if pace == "slow":
        return 0.95
    if pace == "fast":
        return 1.08
    return 1.0


def estimate_fixed_costs(user_request: UserRequest) -> BudgetAllocation:
    style = infer_budget_style(user_request)
    base = BUDGET_STYLE_TABLE[style]

    travelers = max(1, user_request.travelers)
    days = max(1, user_request.days)

    accommodation = base["accommodation_per_person_per_night"] * travelers * days
    food = (
        base["meals_per_person_per_day"]
        * _pace_meal_multiplier(user_request.pace)
        * travelers
        * days
    )
    transport = (
        base["transport_per_person_per_day"]
        * _pace_transport_multiplier(user_request.pace)
        * travelers
        * days
    )
    misc = base["misc_per_person_per_day"] * travelers * days

    fixed_cost_breakdown = {
        "accommodation": round(accommodation, 2),
        "food": round(food, 2),
        "transport": round(transport, 2),
        "misc": round(misc, 2),
    }

    fixed_cost_total = round(sum(fixed_cost_breakdown.values()), 2)
    activity_budget = round(user_request.total_budget_hkd - fixed_cost_total, 2)

    assumptions = [
        f"Budget style inferred as '{style}' based on preferences and per-person daily budget.",
        "Accommodation, food, transport, and misc are heuristic estimates, not exact prices.",
        "Planner should only spend the remaining activity budget on attractions/experiences.",
    ]

    return BudgetAllocation(
        total_budget_hkd=round(user_request.total_budget_hkd, 2),
        budget_style=style,
        fixed_cost_estimate_hkd=fixed_cost_total,
        activity_budget_hkd=activity_budget,
        fixed_cost_breakdown=fixed_cost_breakdown,
        assumptions=assumptions,
    )


def estimate_budget(
    planner_output: Dict[str, Any],
    user_request: UserRequest,
) -> Dict[str, Any]:
    if not planner_output or "itinerary" not in planner_output:
        raise ValueError("planner_output must be a valid planner output dict")

    allocation = estimate_fixed_costs(user_request)

    activity_total = 0.0
    for day in planner_output.get("itinerary", []):
        day_total = 0.0
        for slot in ["morning", "afternoon", "evening"]:
            slot_obj = day.get(slot, {})
            day_total += float(slot_obj.get("estimated_cost_hkd", 0))
        activity_total += day_total

    activity_total = round(activity_total, 2)
    total_trip_cost = round(activity_total + allocation.fixed_cost_estimate_hkd, 2)

    activities_within_budget = activity_total <= allocation.activity_budget_hkd
    total_trip_within_budget = total_trip_cost <= allocation.total_budget_hkd

    activity_over_by = max(0.0, round(activity_total - allocation.activity_budget_hkd, 2))
    total_over_by = max(0.0, round(total_trip_cost - allocation.total_budget_hkd, 2))

    suggestions: List[str] = []
    if allocation.activity_budget_hkd <= 0:
        suggestions.append(
            "Estimated fixed costs already consume the full budget. Increase total budget or switch to economy style."
        )
    elif not activities_within_budget:
        suggestions.append(
            "Selected activities exceed the remaining activity budget. Replace expensive attractions with lower-cost options."
        )
    else:
        suggestions.append("Activities fit within the remaining activity budget.")

    if not total_trip_within_budget:
        suggestions.append(
            "Total trip cost exceeds the user's total budget. Consider cheaper accommodation, meals, or fewer paid activities."
        )
    else:
        suggestions.append("Total trip cost is within the user's total budget.")

    return {
        "total_budget_hkd": allocation.total_budget_hkd,
        "budget_style": allocation.budget_style,
        "fixed_cost_estimate_hkd": allocation.fixed_cost_estimate_hkd,
        "activity_budget_hkd": allocation.activity_budget_hkd,
        "activity_total_estimated_cost_hkd": activity_total,
        "total_trip_estimated_cost_hkd": total_trip_cost,
        "activities_within_budget": activities_within_budget,
        "total_trip_within_budget": total_trip_within_budget,
        "activity_over_budget_by_hkd": activity_over_by,
        "total_over_budget_by_hkd": total_over_by,
        "breakdown": {
            "activities": activity_total,
            **allocation.fixed_cost_breakdown,
        },
        "assumptions": allocation.assumptions,
        "suggestions": suggestions,
    }


if __name__ == "__main__":
    sample_request = UserRequest(
        destination="Hong Kong",
        days=2,
        total_budget_hkd=2500,
        preferences=["sightseeing", "budget", "local food"],
        pace="moderate",
    )

    sample_planner_output = {
        "destination": "Hong Kong",
        "days": 2,
        "activity_budget_hkd": 810,
        "total_estimated_activity_cost_hkd": 760,
        "activities_within_budget": True,
        "itinerary": [
            {
                "day": 1,
                "morning": {"estimated_cost_hkd": 120},
                "afternoon": {"estimated_cost_hkd": 80},
                "evening": {"estimated_cost_hkd": 120},
                "daily_cost_hkd": 320,
            },
            {
                "day": 2,
                "morning": {"estimated_cost_hkd": 140},
                "afternoon": {"estimated_cost_hkd": 150},
                "evening": {"estimated_cost_hkd": 150},
                "daily_cost_hkd": 440,
            },
        ],
        "planning_summary": "A 2-day Hong Kong itinerary focused on sightseeing and local food.",
    }

    allocation = estimate_fixed_costs(sample_request)
    print("=== Allocation ===")
    print(asdict(allocation))

    final_budget = estimate_budget(sample_planner_output, sample_request)
    print("=== Final Budget Check ===")
    print(final_budget)