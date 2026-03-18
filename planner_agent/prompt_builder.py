from __future__ import annotations

import json
from dataclasses import asdict
from typing import List

from planner_agent.schemas import Activity, BudgetAllocation, UserRequest


def build_planner_prompt(
    user_request: UserRequest,
    activities: List[Activity],
    budget_allocation: BudgetAllocation,
) -> str:
    activity_data = [asdict(a) for a in activities]

    must_include_text = ", ".join(user_request.must_include) if user_request.must_include else "None"
    avoid_text = ", ".join(user_request.avoid) if user_request.avoid else "None"
    preferences_text = ", ".join(user_request.preferences) if user_request.preferences else "None"
    assumptions_text = "; ".join(budget_allocation.assumptions)

    prompt = f"""
You are a strict JSON travel planner.

Your task is to generate ONE travel itinerary JSON object.

Do NOT do any of the following:
- Do NOT list attractions
- Do NOT summarize the dataset
- Do NOT rewrite the activities
- Do NOT explain your answer
- Do NOT output markdown
- Do NOT output code fences
- Do NOT output any text before or after the JSON
- Do NOT output a top-level key named "activities"

You must use ONLY the activities in the dataset below.
You must NOT invent new places.
You must return valid JSON only.

Important budget logic:
- The user's budget is the TOTAL TRIP budget.
- Fixed costs have already been estimated by the system.
- You are ONLY responsible for planning activities within the remaining activity budget.
- Do NOT include accommodation, meals, transport, or misc costs in activity cost.
- Use only the activity costs from the dataset.

User request:
- destination: {user_request.destination}
- days: {user_request.days}
- total_budget_hkd: {user_request.total_budget_hkd}
- travelers: {user_request.travelers}
- preferences: {preferences_text}
- pace: {user_request.pace}
- must_include: {must_include_text}
- avoid: {avoid_text}

Budget allocation from system:
- budget_style: {budget_allocation.budget_style}
- fixed_cost_estimate_hkd: {budget_allocation.fixed_cost_estimate_hkd}
- activity_budget_hkd: {budget_allocation.activity_budget_hkd}
- assumptions: {assumptions_text}

Required top-level JSON format:
{{
  "destination": "{user_request.destination}",
  "days": {user_request.days},
  "activity_budget_hkd": {budget_allocation.activity_budget_hkd},
  "total_estimated_activity_cost_hkd": 0,
  "activities_within_budget": true,
  "itinerary": [
    {{
      "day": 1,
      "morning": {{
        "activity_name": "string",
        "area": "string",
        "category": "string",
        "estimated_cost_hkd": 0,
        "duration_hours": 0,
        "reason": "string"
      }},
      "afternoon": {{
        "activity_name": "string",
        "area": "string",
        "category": "string",
        "estimated_cost_hkd": 0,
        "duration_hours": 0,
        "reason": "string"
      }},
      "evening": {{
        "activity_name": "string",
        "area": "string",
        "category": "string",
        "estimated_cost_hkd": 0,
        "duration_hours": 0,
        "reason": "string"
      }},
      "daily_cost_hkd": 0,
      "notes": "string"
    }}
  ],
  "planning_summary": "string"
}}

Rules:
1. Each day must have exactly 3 slots: morning, afternoon, evening.
2. Use only activities from the dataset below.
3. Do not repeat the same activity.
4. The sum of activity costs should stay within activity_budget_hkd.
5. Match user preferences as much as possible.
6. Use best_time when reasonable.
7. Keep reasons short.
8. Output JSON only.

Activity dataset:
{json.dumps(activity_data, ensure_ascii=False, separators=(",", ":"))}
"""
    return prompt.strip()