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

    prompt = f"""
You are a travel planner that must return ONE valid JSON object only.

Rules:
- Use ONLY activities from the dataset.
- Do NOT invent activities, places, or names.
- If a preference cannot be matched by the dataset, ignore that preference instead of inventing.
- Respect must_include if possible using dataset activities only.
- Respect avoid.
- Do NOT repeat activities.
- Keep same-day activities geographically coherent when possible.
- Consider activity cost_hkd so the plan stays within the activity budget cap.
- Do NOT output any cost totals.
- Keep reasons short.
- Keep planning_summary short and generic.
- Do NOT output markdown, code fences, or explanations.
- Output valid JSON only.

User request:
- destination: {user_request.destination}
- days: {user_request.days}
- total_budget_hkd: {user_request.total_budget_hkd}
- travelers: {user_request.travelers}
- preferences: {preferences_text}
- pace: {user_request.pace}
- must_include: {must_include_text}
- avoid: {avoid_text}

Budget context:
- budget_style: {budget_allocation.budget_style}
- activity_budget_cap_hkd: {budget_allocation.activity_budget_hkd}

Goal:
Create a good-quality itinerary that matches the user's preferences, uses reasonable-value activities, and is not overly conservative if suitable dataset options exist.

Return exactly this JSON shape:
{{
  "destination": "{user_request.destination}",
  "days": {user_request.days},
  "activity_budget_hkd": {budget_allocation.activity_budget_hkd},
  "itinerary": [
    {{
      "day": 1,
      "morning": {{
        "activity_name": "string",
        "reason": "string"
      }},
      "afternoon": {{
        "activity_name": "string",
        "reason": "string"
      }},
      "evening": {{
        "activity_name": "string",
        "reason": "string"
      }},
      "notes": "string"
    }}
  ],
  "planning_summary": "string"
}}

Dataset:
{json.dumps(activity_data, ensure_ascii=False, separators=(",", ":"))}
"""
    return prompt.strip()