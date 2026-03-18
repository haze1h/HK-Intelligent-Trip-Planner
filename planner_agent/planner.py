from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List

from budget_tool.budget import estimate_fixed_costs
from planner_agent.load_data import load_activities
from planner_agent.ollama_client import OllamaLLMClient
from planner_agent.prompt_builder import build_planner_prompt
from planner_agent.schemas import Activity, UserRequest


class PlannerAgent:
    def __init__(self, model_name: str = "mistral:7b") -> None:
        self.llm_client = OllamaLLMClient(model=model_name)

    def plan(self, user_request: UserRequest, activities: List[Activity]) -> Dict[str, Any]:
        print("[1] Estimating fixed costs and activity budget...")
        budget_allocation = estimate_fixed_costs(user_request)

        if budget_allocation.activity_budget_hkd <= 0:
            raise ValueError(
                "The estimated fixed costs already consume the full budget. "
                "Please increase the total budget or choose a cheaper budget style."
            )

        print("[2] Building prompt...")
        prompt = build_planner_prompt(user_request, activities, budget_allocation)

        print("[3] Sending prompt to Ollama...")
        raw_output = self.llm_client.generate(prompt)

        print("[4] Raw output received:")
        print(raw_output[:1000])

        try:
            parsed = self._extract_json(raw_output)
            print("[5] JSON extracted.")

            self._validate_output(parsed, user_request)
            print("[6] Output structure validated.")

            parsed = self._normalize_budget_fields(parsed, budget_allocation.activity_budget_hkd)
            print("[7] Output totals normalized.")

            parsed["budget_context"] = asdict(budget_allocation)
            return parsed
        except Exception as e:
            raise ValueError(
                f"Planner output is invalid.\nRaw output:\n{raw_output}\n\nError: {e}"
            ) from e

    def _extract_json(self, raw_output: str) -> Dict[str, Any]:
        raw_output = raw_output.strip()

        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            pass

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
            "activity_budget_hkd",
            "total_estimated_activity_cost_hkd",
            "activities_within_budget",
            "itinerary",
            "planning_summary",
        }

        missing = required_top_keys - set(output.keys())
        if missing:
            raise ValueError(f"Missing top-level keys: {missing}")

        if output["destination"] != user_request.destination:
            raise ValueError("Output destination does not match requested destination.")

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

    def _normalize_budget_fields(
        self,
        output: Dict[str, Any],
        activity_budget_hkd: float,
    ) -> Dict[str, Any]:
        itinerary = output["itinerary"]

        calculated_total = 0.0
        used_activity_names = set()

        for day_plan in itinerary:
            day_total = 0.0

            for slot in ["morning", "afternoon", "evening"]:
                slot_obj = day_plan[slot]
                activity_name = slot_obj["activity_name"]

                if activity_name in used_activity_names:
                    raise ValueError(f"Repeated activity found: {activity_name}")
                used_activity_names.add(activity_name)

                cost = float(slot_obj.get("estimated_cost_hkd", 0))
                duration = float(slot_obj.get("duration_hours", 0))

                if cost < 0:
                    raise ValueError(f"Negative cost found in activity: {activity_name}")
                if duration <= 0:
                    raise ValueError(f"Invalid duration found in activity: {activity_name}")

                day_total += cost

            day_plan["daily_cost_hkd"] = round(day_total, 2)
            calculated_total += day_total

        output["activity_budget_hkd"] = round(activity_budget_hkd, 2)
        output["total_estimated_activity_cost_hkd"] = round(calculated_total, 2)
        output["activities_within_budget"] = calculated_total <= activity_budget_hkd

        return output


if __name__ == "__main__":
    activities = load_activities("data/hk_activities.json")

    request = UserRequest(
        destination="Hong Kong",
        days=2,
        total_budget_hkd=2500,
        preferences=["sightseeing", "budget", "local experience"],
        pace="moderate",
        must_include=["Victoria Peak Tram and Sky Terrace"],
        avoid=["museum"],
        travelers=1,
    )

    planner = PlannerAgent(model_name="mistral:7b")
    result = planner.plan(request, activities)

    print(json.dumps(result, ensure_ascii=False, indent=2))