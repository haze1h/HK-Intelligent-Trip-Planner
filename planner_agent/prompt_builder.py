from __future__ import annotations

import json
from dataclasses import asdict
from typing import List

from planner_agent.schemas import Activity, UserRequest


def build_planner_prompt(user_request: UserRequest, activities: List[Activity]) -> str:
    activity_data = [asdict(a) for a in activities]

    must_include_text = ", ".join(user_request.must_include) if user_request.must_include else "None"
    avoid_text = ", ".join(user_request.avoid) if user_request.avoid else "None"

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

User request:
- destination: {user_request.destination}
- days: {user_request.days}
- total_budget_hkd: {user_request.total_budget_hkd}
- preferences: {", ".join(user_request.preferences)}
- pace: {user_request.pace}
- must_include: {must_include_text}
- avoid: {avoid_text}

Required top-level JSON format:
{{
  "destination": "{user_request.destination}",
  "days": {user_request.days},
  "total_estimated_cost_hkd": 0,
  "budget_limit_hkd": {user_request.total_budget_hkd},
  "within_budget": true,
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
4. Try to stay within budget.
5. Match user preferences as much as possible.
6. Use best_time when reasonable.
7. Keep reasons short.
8. Output JSON only.

Activity dataset:
{json.dumps(activity_data, ensure_ascii=False, separators=(",", ":"))}
"""
    return prompt.strip()