from __future__ import annotations

import json
from typing import Any, Dict, List

from planner_agent.load_data import load_activities
from planner_agent.ollama_client import OllamaLLMClient
from planner_agent.prompt_builder import build_planner_prompt
from planner_agent.schemas import Activity, UserRequest


class PlannerAgent:
    def __init__(self, model_name: str = "qwen3:4b") -> None:
        self.llm_client = OllamaLLMClient(model=model_name)

    def plan(self, user_request: UserRequest, activities: List[Activity]) -> Dict[str, Any]:
        prompt = build_planner_prompt(user_request, activities)
        raw_output = self.llm_client.generate(prompt)

        try:
            parsed = self._extract_json(raw_output)
            self._validate_output(parsed, user_request)
            return parsed
        except Exception as e:
            raise ValueError(
                f"Planner output is invalid.\nRaw output:\n{raw_output}\n\nError: {e}"
            ) from e

    def _extract_json(self, raw_output: str) -> Dict[str, Any]:
        raw_output = raw_output.strip()

        # 直接尝试解析
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

        # 如果模型多输出了文字，尝试截取最外层 JSON
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ValueError("No valid JSON object found in model output.")

        json_text = raw_output[start:end + 1]
        return json.loads(json_text)

    def _validate_output(self, output: Dict[str, Any], user_request: UserRequest) -> None:
        required_top_keys = {
            "destination",
            "days",
            "total_estimated_cost_hkd",
            "budget_limit_hkd",
            "within_budget",
            "itinerary",
            "planning_summary",
        }

        missing = required_top_keys - set(output.keys())
        if missing:
            raise ValueError(f"Missing top-level keys: {missing}")

        if output["days"] != user_request.days:
            raise ValueError("Output days do not match requested days.")

        itinerary = output["itinerary"]
        if not isinstance(itinerary, list):
            raise ValueError("Itinerary must be a list.")

        if len(itinerary) != user_request.days:
            raise ValueError("Itinerary length does not match requested days.")

        for day_plan in itinerary:
            if "day" not in day_plan:
                raise ValueError("Each day plan must include 'day'.")

            for slot in ["morning", "afternoon", "evening"]:
                if slot not in day_plan:
                    raise ValueError(f"Missing slot: {slot}")

                slot_obj = day_plan[slot]
                required_slot_keys = {
                    "activity_name",
                    "area",
                    "category",
                    "estimated_cost_hkd",
                    "duration_hours",
                    "reason",
                }
                slot_missing = required_slot_keys - set(slot_obj.keys())
                if slot_missing:
                    raise ValueError(f"Missing keys in {slot}: {slot_missing}")

            if "daily_cost_hkd" not in day_plan:
                raise ValueError("Missing daily_cost_hkd.")
            if "notes" not in day_plan:
                raise ValueError("Missing notes.")


if __name__ == "__main__":
    activities = load_activities("data/hk_activities.json")

    request = UserRequest(
        destination="Hong Kong",
        days=2,
        total_budget_hkd=500,
        preferences=["sightseeing", "budget", "local experience"],
        pace="moderate",
        must_include=["Victoria Peak Tram and Sky Terrace"],
        avoid=["museum"],
    )

    planner = PlannerAgent(model_name="qwen3:4b")
    result = planner.plan(request, activities)

    print(json.dumps(result, ensure_ascii=False, indent=2))