from __future__ import annotations

import json
from dataclasses import asdict
from typing import List

from planner_agent.schemas import Activity, UserRequest


def build_planner_prompt(user_request: UserRequest, activities: List[Activity]) -> str:
    activity_data = [asdict(a) for a in activities]

    must_include_text = (
        ", ".join(user_request.must_include)
        if user_request.must_include
        else "None"
    )
    avoid_text = (
        ", ".join(user_request.avoid)
        if user_request.avoid
        else "None"
    )

    prompt = f"""
You are a professional travel planner agent.

Your task:
Create a {user_request.days}-day travel itinerary for {user_request.destination}.

User requirements:
- Destination: {user_request.destination}
- Number of days: {user_request.days}
- Total budget (HKD): {user_request.total_budget_hkd}
- Preferences: {", ".join(user_request.preferences)}
- Pace: {user_request.pace}
- Must include: {must_include_text}
- Avoid: {avoid_text}

Rules:
1. Output STRICTLY in valid JSON only.
2. Plan each day with exactly 3 slots: morning, afternoon, evening.
3. Use only activities from the provided activity dataset.
4. Match the user's preferences as much as possible.
5. Keep the total estimated cost within budget when possible.
6. Avoid overly tight schedules across distant areas in the same day.
7. Avoid repeating the same activity.
8. Use best_time when selecting activities if possible.
9. If budget is tight, prioritize cheaper activities.
10. Reasons should be concise and practical.

Return a JSON object with exactly this structure:
{{
  "destination": "Hong Kong",
  "days": 2,
  "total_estimated_cost_hkd": 300,
  "budget_limit_hkd": 500,
  "within_budget": true,
  "itinerary": [
    {{
      "day": 1,
      "morning": {{
        "activity_name": "Example Activity",
        "area": "Central",
        "category": "sightseeing",
        "estimated_cost_hkd": 100,
        "duration_hours": 2.0,
        "reason": "Matches sightseeing preference."
      }},
      "afternoon": {{
        "activity_name": "Example Activity 2",
        "area": "Central",
        "category": "food",
        "estimated_cost_hkd": 80,
        "duration_hours": 1.5,
        "reason": "Good match for food preference."
      }},
      "evening": {{
        "activity_name": "Example Activity 3",
        "area": "Tsim Sha Tsui",
        "category": "local experience",
        "estimated_cost_hkd": 50,
        "duration_hours": 1.0,
        "reason": "Suitable evening activity."
      }},
      "daily_cost_hkd": 230,
      "notes": "Reasonable grouping by area and time."
    }}
  ],
  "planning_summary": "A balanced itinerary within budget."
}}

Important:
- Do not output markdown.
- Do not output code fences.
- Do not output explanations before or after the JSON.
- Output JSON only.

Available activity dataset:
{json.dumps(activity_data, ensure_ascii=False, indent=2)}
"""
    return prompt.strip()