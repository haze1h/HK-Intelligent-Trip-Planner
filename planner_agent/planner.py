from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List

from budget_tool.budget import estimate_fixed_costs
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

            self._validate_minimal_output(parsed, user_request)
            print("[6] Minimal output validated.")

            normalized = self._resolve_and_normalize(
                output=parsed,
                user_request=user_request,
                activities=activities,
                activity_budget_hkd=budget_allocation.activity_budget_hkd,
            )
            print("[7] Output resolved and normalized.")

            normalized["budget_context"] = asdict(budget_allocation)
            return normalized

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

    def _validate_minimal_output(self, output: Dict[str, Any], user_request: UserRequest) -> None:
        required_top_keys = {
            "destination",
            "days",
            "activity_budget_hkd",
            "itinerary",
            "planning_summary",
        }

        missing = required_top_keys - set(output.keys())
        if missing:
            raise ValueError(f"Missing top-level keys: {missing}")

        if output["destination"] != user_request.destination:
            raise ValueError("Output destination does not match requested destination.")

        if int(output["days"]) != int(user_request.days):
            raise ValueError("Output days do not match requested days.")

        itinerary = output["itinerary"]
        if not isinstance(itinerary, list):
            raise ValueError("Itinerary must be a list.")

        if len(itinerary) != user_request.days:
            raise ValueError("Itinerary length does not match requested days.")

        for expected_day, day_plan in enumerate(itinerary, start=1):
            if "day" not in day_plan:
                raise ValueError("Each day plan must include 'day'.")

            if int(day_plan["day"]) != expected_day:
                raise ValueError(f"Day numbering is invalid. Expected {expected_day}.")

            for slot in ["morning", "afternoon", "evening"]:
                if slot not in day_plan:
                    raise ValueError(f"Missing slot: {slot}")

                slot_obj = day_plan[slot]
                if not isinstance(slot_obj, dict):
                    raise ValueError(f"{slot} must be an object.")

                required_slot_keys = {"activity_name", "reason"}
                slot_missing = required_slot_keys - set(slot_obj.keys())
                if slot_missing:
                    raise ValueError(f"Missing keys in {slot}: {slot_missing}")

            if "notes" not in day_plan:
                raise ValueError("Missing notes.")

    def _resolve_and_normalize(
        self,
        output: Dict[str, Any],
        user_request: UserRequest,
        activities: List[Activity],
        activity_budget_hkd: float,
    ) -> Dict[str, Any]:
        activity_index = {a.name.strip().lower(): a for a in activities}
        itinerary = output["itinerary"]

        normalized_itinerary: List[Dict[str, Any]] = []
        used_activity_names = set()
        total_cost = 0.0
        selected_names: List[str] = []
        selected_categories: List[str] = []
        selected_areas: List[str] = []

        for day_plan in itinerary:
            normalized_day: Dict[str, Any] = {
                "day": int(day_plan["day"]),
                "notes": str(day_plan.get("notes", "")).strip(),
            }

            day_total = 0.0

            for slot in ["morning", "afternoon", "evening"]:
                raw_slot = day_plan[slot]
                raw_name = str(raw_slot.get("activity_name", "")).strip()
                reason = str(raw_slot.get("reason", "")).strip()

                if not raw_name:
                    raise ValueError(f"Empty activity_name in {slot}.")

                activity = self._find_activity(raw_name, activities, activity_index)
                if activity is None:
                    raise ValueError(f"Activity not found in dataset: {raw_name}")

                canonical_name = activity.name
                key = canonical_name.lower()

                if key in used_activity_names:
                    raise ValueError(f"Repeated activity found: {canonical_name}")
                used_activity_names.add(key)

                slot_obj = {
                    "activity_name": canonical_name,
                    "area": activity.area,
                    "category": activity.category,
                    "estimated_cost_hkd": round(float(activity.cost_hkd), 2),
                    "duration_hours": round(float(activity.duration_hours), 2),
                    "reason": reason if reason else "Fits the trip preferences and budget.",
                }

                normalized_day[slot] = slot_obj
                day_total += float(activity.cost_hkd)

                selected_names.append(canonical_name)
                selected_categories.append(activity.category)
                selected_areas.append(activity.area)

            normalized_day["daily_cost_hkd"] = round(day_total, 2)
            total_cost += day_total
            normalized_itinerary.append(normalized_day)

        self._validate_constraints(user_request, selected_names)

        final_summary = self._build_summary(
            user_request=user_request,
            total_cost=round(total_cost, 2),
            activity_budget_hkd=round(activity_budget_hkd, 2),
            selected_categories=selected_categories,
            selected_areas=selected_areas,
        )

        return {
            "destination": user_request.destination,
            "days": user_request.days,
            "activity_budget_hkd": round(activity_budget_hkd, 2),
            "total_estimated_activity_cost_hkd": round(total_cost, 2),
            "activities_within_budget": total_cost <= activity_budget_hkd,
            "itinerary": normalized_itinerary,
            "planning_summary": final_summary,
        }

    def _find_activity(
        self,
        raw_name: str,
        activities: List[Activity],
        activity_index: Dict[str, Activity],
    ) -> Activity | None:
        key = raw_name.strip().lower()

        if key in activity_index:
            return activity_index[key]

        for activity in activities:
            act_name = activity.name.lower()
            if key in act_name or act_name in key:
                return activity

        raw_tokens = set(key.replace("-", " ").split())
        for activity in activities:
            act_tokens = set(activity.name.lower().replace("-", " ").split())
            if raw_tokens and len(raw_tokens & act_tokens) >= max(1, min(2, len(raw_tokens))):
                return activity

        return None

    def _validate_constraints(self, user_request: UserRequest, selected_names: List[str]) -> None:
        joined = " | ".join(selected_names).lower()

        if user_request.must_include:
            for item in user_request.must_include:
                if not self._soft_match(item, joined):
                    raise ValueError(f"Must-include activity not found in itinerary: {item}")

        if user_request.avoid:
            for item in user_request.avoid:
                if self._soft_match(item, joined):
                    raise ValueError(f"Avoid preference violated by itinerary: {item}")

    def _soft_match(self, query: str, text: str) -> bool:
        q = query.strip().lower()
        t = text.strip().lower()

        if not q:
            return True
        if q in t:
            return True

        q_tokens = [tok for tok in q.replace("-", " ").split() if tok]
        if not q_tokens:
            return False

        hits = sum(1 for tok in q_tokens if tok in t)
        return hits >= max(1, len(q_tokens) // 2)

    def _build_summary(
        self,
        user_request: UserRequest,
        total_cost: float,
        activity_budget_hkd: float,
        selected_categories: List[str],
        selected_areas: List[str],
    ) -> str:
        unique_categories = []
        for c in selected_categories:
            if c not in unique_categories:
                unique_categories.append(c)

        unique_areas = []
        for a in selected_areas:
            if a not in unique_areas:
                unique_areas.append(a)

        cat_text = ", ".join(unique_categories[:3]) if unique_categories else "mixed activities"
        area_text = ", ".join(unique_areas[:3]) if unique_areas else user_request.destination

        return (
            f"A {user_request.days}-day {user_request.destination} itinerary focused on {cat_text}. "
            f"It covers {area_text} and keeps estimated activity spending at HKD {round(total_cost, 2)} "
            f"against an activity budget cap of HKD {round(activity_budget_hkd, 2)}."
        )