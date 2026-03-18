from __future__ import annotations

from typing import Any, Dict, List, Optional, Set, Tuple

from planner_agent.schemas import Activity, UserRequest


class CriticAgent:
    """
    Rule-based Critic Agent for HK Intelligent Trip Planner.

    Responsibilities:
    - Evaluate itinerary quality
    - Read planner_output + budget_output + user_request
    - Return issues, strengths, suggestions, and an overall score

    Design principles:
    - Do NOT regenerate itinerary
    - Do NOT replace Budget Tool as budget authority
    - Prefer deterministic, explainable checks
    """

    PREFERENCE_HINTS: Dict[str, List[str]] = {
        "food": ["food", "restaurant", "cafe", "dessert", "snack", "street food", "tea"],
        "shopping": ["shopping", "market", "mall", "souvenir", "retail"],
        "sightseeing": ["sightseeing", "landmark", "viewpoint", "scenic", "harbour", "skyline"],
        "culture": ["culture", "museum", "temple", "heritage", "art", "history"],
        "budget": ["budget", "cheap", "free", "affordable", "public", "market"],
        "nightlife": ["night", "bar", "evening", "nightlife", "rooftop"],
        "nature": ["nature", "park", "garden", "hiking", "trail", "outdoor"],
        "family": ["family", "kids", "children", "theme park", "zoo"],
        "romantic": ["romantic", "harbour", "sunset", "view", "cruise"],
    }

    def __init__(self) -> None:
        self.slot_names = ["morning", "afternoon", "evening"]

    def critique(
        self,
        planner_output: Dict[str, Any],
        budget_output: Dict[str, Any],
        user_request: UserRequest,
        activities: Optional[List[Activity]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(planner_output, dict):
            raise ValueError("planner_output must be a dict")
        if not isinstance(budget_output, dict):
            raise ValueError("budget_output must be a dict")

        activity_index = self._build_activity_index(activities or [])

        issues: List[Dict[str, str]] = []
        strengths: List[str] = []
        suggestions: List[str] = []

        if not activity_index:
            suggestions.append(
                "Provide the full activity catalog to enable stronger preference, weather, and time-fit checks."
            )

        # 1. Structure / consistency checks
        structure_issues, structure_strengths, structure_suggestions = self._check_structure(
            planner_output, user_request
        )
        issues.extend(structure_issues)
        strengths.extend(structure_strengths)
        suggestions.extend(structure_suggestions)

        # 2. Budget checks
        budget_issues, budget_strengths, budget_suggestions = self._check_budget(
            planner_output, budget_output
        )
        issues.extend(budget_issues)
        strengths.extend(budget_strengths)
        suggestions.extend(budget_suggestions)

        # 3. Pace / travel checks
        pace_issues, pace_strengths, pace_suggestions = self._check_pace_and_travel(
            planner_output, user_request
        )
        issues.extend(pace_issues)
        strengths.extend(pace_strengths)
        suggestions.extend(pace_suggestions)

        # 4. Preference alignment checks
        pref_issues, pref_strengths, pref_suggestions = self._check_preference_match(
            planner_output, user_request, activity_index
        )
        issues.extend(pref_issues)
        strengths.extend(pref_strengths)
        suggestions.extend(pref_suggestions)

        # 5. Weather / time-slot checks
        weather_issues, weather_strengths, weather_suggestions = self._check_weather_and_time(
            planner_output, activity_index
        )
        issues.extend(weather_issues)
        strengths.extend(weather_strengths)
        suggestions.extend(weather_suggestions)

        # 6. Diversity / quality checks
        quality_issues, quality_strengths, quality_suggestions = self._check_plan_quality(
            planner_output
        )
        issues.extend(quality_issues)
        strengths.extend(quality_strengths)
        suggestions.extend(quality_suggestions)

        strengths = self._dedupe_strings(strengths)
        suggestions = self._dedupe_strings(suggestions)

        overall_score = self._calculate_score(issues)
        is_feasible = self._determine_feasibility(issues)

        summary = self._build_summary(
            overall_score=overall_score,
            is_feasible=is_feasible,
            issues=issues,
            strengths=strengths,
        )

        return {
            "overall_score": overall_score,
            "is_feasible": is_feasible,
            "issues": issues,
            "strengths": strengths,
            "suggestions": suggestions,
            "summary": summary,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_activity_index(self, activities: List[Activity]) -> Dict[str, Activity]:
        index: Dict[str, Activity] = {}
        for activity in activities:
            index[activity.name.strip().lower()] = activity
        return index

    def _lookup_activity(
        self,
        activity_name: str,
        activity_index: Dict[str, Activity],
    ) -> Optional[Activity]:
        return activity_index.get((activity_name or "").strip().lower())

    def _issue(
        self,
        issue_type: str,
        severity: str,
        message: str,
    ) -> Dict[str, str]:
        return {
            "type": issue_type,
            "severity": severity,
            "message": message,
        }

    def _dedupe_strings(self, items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items:
            key = item.strip()
            if key and key not in seen:
                seen.add(key)
                result.append(item)
        return result

    def _collect_day_slots(self, day_plan: Dict[str, Any]) -> List[Tuple[str, Dict[str, Any]]]:
        slots: List[Tuple[str, Dict[str, Any]]] = []
        for slot in self.slot_names:
            slot_obj = day_plan.get(slot, {})
            if isinstance(slot_obj, dict):
                slots.append((slot, slot_obj))
        return slots

    def _safe_float(self, value: Any, default: float = 0.0) -> float:
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def _normalize_text(self, text: str) -> str:
        return " ".join((text or "").lower().strip().split())

    def _tokenize_for_soft_match(self, text: str) -> List[str]:
        raw = self._normalize_text(text).replace("/", " ").replace("-", " ")
        words = [w.strip(".,:;()[]{}'\"") for w in raw.split()]
        return [w for w in words if len(w) > 2]

    def _soft_match(self, query: str, text: str) -> bool:
        query_norm = self._normalize_text(query)
        text_norm = self._normalize_text(text)

        if not query_norm:
            return False

        if query_norm in text_norm:
            return True

        query_words = self._tokenize_for_soft_match(query_norm)
        if not query_words:
            return False

        matched = sum(1 for w in query_words if w in text_norm)
        threshold = max(1, len(query_words) // 2)
        return matched >= threshold

    def _best_time_matches_slot(self, best_time: str, slot: str) -> bool:
        best_time = best_time.lower().strip()
        slot = slot.lower().strip()

        if not best_time or best_time in {"any", "flexible", "all day"}:
            return True

        morning_terms = {"morning", "daytime"}
        afternoon_terms = {"afternoon", "late afternoon", "daytime", "sunset"}
        evening_terms = {"evening", "night", "sunset", "late afternoon"}

        if slot == "morning":
            return any(term in best_time for term in morning_terms)
        if slot == "afternoon":
            return any(term in best_time for term in afternoon_terms)
        if slot == "evening":
            return any(term in best_time for term in evening_terms)
        return True

    def _activity_text_fields(self, activity: Activity) -> str:
        tag_text = " ".join(activity.tags)
        return " ".join(
            [
                activity.name.lower(),
                activity.category.lower(),
                activity.area.lower(),
                activity.best_time.lower(),
                tag_text.lower(),
            ]
        )

    def _get_preference_keywords(self, pref: str) -> List[str]:
        pref_norm = self._normalize_text(pref)
        keywords = [pref_norm]

        if pref_norm in self.PREFERENCE_HINTS:
            keywords.extend(self.PREFERENCE_HINTS[pref_norm])

        return self._dedupe_strings(keywords)

    def _preference_matches_text(self, pref: str, text: str) -> bool:
        keywords = self._get_preference_keywords(pref)
        return any(self._soft_match(keyword, text) for keyword in keywords)

    def _suggest_activities_for_pref(
        self,
        pref: str,
        activity_index: Dict[str, Activity],
        used_names: Set[str],
        limit: int = 3,
    ) -> List[str]:
        matches: List[Tuple[int, float, str]] = []
        keywords = self._get_preference_keywords(pref)

        for name_lower, activity in activity_index.items():
            if name_lower in used_names:
                continue

            score = 0
            name_text = activity.name.lower()
            category_text = activity.category.lower()
            area_text = activity.area.lower()
            tag_text = " ".join(activity.tags).lower()
            best_time_text = activity.best_time.lower()

            for keyword in keywords:
                if self._soft_match(keyword, name_text):
                    score += 4
                if self._soft_match(keyword, category_text):
                    score += 3
                if self._soft_match(keyword, tag_text):
                    score += 3
                if self._soft_match(keyword, area_text):
                    score += 1
                if self._soft_match(keyword, best_time_text):
                    score += 1

            if score > 0:
                matches.append((-score, float(activity.cost_hkd), activity.name))

        matches.sort()
        return [name for _, _, name in matches[:limit]]

    # ------------------------------------------------------------------
    # Checks
    # ------------------------------------------------------------------

    def _check_structure(
        self,
        planner_output: Dict[str, Any],
        user_request: UserRequest,
    ) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        issues: List[Dict[str, str]] = []
        strengths: List[str] = []
        suggestions: List[str] = []

        required_top_keys = {
            "destination",
            "days",
            "activity_budget_hkd",
            "total_estimated_activity_cost_hkd",
            "activities_within_budget",
            "itinerary",
            "planning_summary",
        }

        missing_top = required_top_keys - set(planner_output.keys())
        if missing_top:
            issues.append(
                self._issue(
                    "structure",
                    "high",
                    f"Planner output is missing top-level keys: {sorted(missing_top)}.",
                )
            )

        if planner_output.get("destination") == user_request.destination:
            strengths.append("Destination matches the user request.")
        else:
            issues.append(
                self._issue(
                    "structure",
                    "high",
                    "Destination in planner output does not match the user request.",
                )
            )

        if planner_output.get("days") == user_request.days:
            strengths.append("The itinerary length matches the requested number of days.")
        else:
            issues.append(
                self._issue(
                    "structure",
                    "high",
                    "The planner output days value does not match the user request.",
                )
            )

        itinerary = planner_output.get("itinerary")
        if not isinstance(itinerary, list):
            issues.append(
                self._issue(
                    "structure",
                    "high",
                    "Itinerary is not a valid list.",
                )
            )
            return issues, strengths, suggestions

        if len(itinerary) != user_request.days:
            issues.append(
                self._issue(
                    "structure",
                    "high",
                    "The number of day plans does not equal the requested trip length.",
                )
            )

        seen_names = set()
        repeated_names = set()

        for idx, day_plan in enumerate(itinerary, start=1):
            if day_plan.get("day") != idx:
                issues.append(
                    self._issue(
                        "structure",
                        "medium",
                        f"Day numbering is inconsistent around Day {idx}.",
                    )
                )

            for slot in self.slot_names:
                if slot not in day_plan:
                    issues.append(
                        self._issue(
                            "structure",
                            "high",
                            f"Day {idx} is missing the '{slot}' slot.",
                        )
                    )
                    continue

                slot_obj = day_plan.get(slot, {})
                if not isinstance(slot_obj, dict):
                    issues.append(
                        self._issue(
                            "structure",
                            "high",
                            f"Day {idx} {slot} is not a valid object.",
                        )
                    )
                    continue

                required_slot_keys = {
                    "activity_name",
                    "area",
                    "category",
                    "estimated_cost_hkd",
                    "duration_hours",
                    "reason",
                }
                missing_slot = required_slot_keys - set(slot_obj.keys())
                if missing_slot:
                    issues.append(
                        self._issue(
                            "structure",
                            "high",
                            f"Day {idx} {slot} is missing keys: {sorted(missing_slot)}.",
                        )
                    )

                activity_name = str(slot_obj.get("activity_name", "")).strip()
                if activity_name:
                    if activity_name in seen_names:
                        repeated_names.add(activity_name)
                    seen_names.add(activity_name)

            if "daily_cost_hkd" not in day_plan:
                issues.append(
                    self._issue(
                        "structure",
                        "medium",
                        f"Day {idx} is missing daily_cost_hkd.",
                    )
                )

            if "notes" not in day_plan:
                issues.append(
                    self._issue(
                        "structure",
                        "low",
                        f"Day {idx} is missing notes.",
                    )
                )

        if repeated_names:
            issues.append(
                self._issue(
                    "structure",
                    "high",
                    f"Repeated activities found: {sorted(repeated_names)}.",
                )
            )
        else:
            strengths.append("No repeated activities were found in the itinerary.")

        return issues, strengths, suggestions

    def _check_budget(
        self,
        planner_output: Dict[str, Any],
        budget_output: Dict[str, Any],
    ) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        issues: List[Dict[str, str]] = []
        strengths: List[str] = []
        suggestions: List[str] = []

        activities_within_budget = bool(budget_output.get("activities_within_budget", False))
        total_trip_within_budget = bool(budget_output.get("total_trip_within_budget", False))
        activity_over_by = self._safe_float(budget_output.get("activity_over_budget_by_hkd", 0))
        total_over_by = self._safe_float(budget_output.get("total_over_budget_by_hkd", 0))
        activity_total = self._safe_float(
            budget_output.get("activity_total_estimated_cost_hkd", 0)
        )
        activity_budget = self._safe_float(budget_output.get("activity_budget_hkd", 0))

        if activities_within_budget:
            strengths.append("Selected activities stay within the allocated activity budget.")
        else:
            issues.append(
                self._issue(
                    "budget",
                    "high",
                    f"Activities exceed the activity budget by HKD {activity_over_by:.2f}.",
                )
            )
            suggestions.append(
                "Replace one or two expensive attractions with lower-cost alternatives."
            )

        if total_trip_within_budget:
            strengths.append("The overall trip stays within the user's total budget.")
        else:
            issues.append(
                self._issue(
                    "budget",
                    "high",
                    f"Total trip cost exceeds the user's total budget by HKD {total_over_by:.2f}.",
                )
            )
            suggestions.append(
                "Reduce accommodation or food level, or remove paid activities to fit the full trip budget."
            )

        if activity_budget > 0:
            usage_ratio = activity_total / activity_budget
            if usage_ratio < 0.35:
                issues.append(
                    self._issue(
                        "budget",
                        "low",
                        "The itinerary uses only a small portion of the available activity budget and may be overly conservative.",
                    )
                )
                suggestions.append(
                    "Consider adding one higher-value activity if the user wants a richer experience."
                )
            elif usage_ratio <= 1.0:
                strengths.append("Activity spending is reasonably aligned with the available budget.")

        planner_flag = bool(planner_output.get("activities_within_budget", False))
        if planner_flag != activities_within_budget:
            issues.append(
                self._issue(
                    "budget",
                    "medium",
                    "Planner budget flag is inconsistent with the final Budget Tool result.",
                )
            )

        return issues, strengths, suggestions

    def _check_pace_and_travel(
        self,
        planner_output: Dict[str, Any],
        user_request: UserRequest,
    ) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        issues: List[Dict[str, str]] = []
        strengths: List[str] = []
        suggestions: List[str] = []

        itinerary = planner_output.get("itinerary", [])
        pace = (user_request.pace or "moderate").lower()

        if pace == "slow":
            max_hours = 6.0
        elif pace == "fast":
            max_hours = 10.0
        else:
            max_hours = 8.0

        travel_heavy_days = 0

        for day_plan in itinerary:
            day_num = day_plan.get("day", "?")
            total_hours = 0.0
            unique_areas = set()

            for _, slot_obj in self._collect_day_slots(day_plan):
                total_hours += self._safe_float(slot_obj.get("duration_hours", 0))
                area = str(slot_obj.get("area", "")).strip()
                if area:
                    unique_areas.add(area)

            if total_hours > max_hours:
                severity = "medium" if total_hours <= max_hours + 1.5 else "high"
                issues.append(
                    self._issue(
                        "pace",
                        severity,
                        f"Day {day_num} may be too packed for a '{pace}' trip pace ({total_hours:.1f} planned hours).",
                    )
                )
                suggestions.append(
                    f"Reduce activity time on Day {day_num} or swap one slot for a lighter option."
                )

            if len(unique_areas) >= 3:
                travel_heavy_days += 1
                issues.append(
                    self._issue(
                        "travel",
                        "medium",
                        f"Day {day_num} spans {len(unique_areas)} different areas and may involve too much travel.",
                    )
                )
                suggestions.append(
                    f"Cluster Day {day_num} activities into fewer areas to reduce commuting time."
                )

            if total_hours <= max_hours and len(unique_areas) <= 2:
                strengths.append(f"Day {day_num} looks reasonably paced with manageable travel.")

        if travel_heavy_days == 0 and itinerary:
            strengths.append("The itinerary is geographically fairly coherent day by day.")

        return issues, strengths, suggestions

    def _check_preference_match(
        self,
        planner_output: Dict[str, Any],
        user_request: UserRequest,
        activity_index: Dict[str, Activity],
    ) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        issues: List[Dict[str, str]] = []
        strengths: List[str] = []
        suggestions: List[str] = []

        itinerary = planner_output.get("itinerary", [])
        selected_names: List[str] = []
        selected_categories: List[str] = []
        selected_tags: List[str] = []

        for day_plan in itinerary:
            for _, slot_obj in self._collect_day_slots(day_plan):
                name = str(slot_obj.get("activity_name", "")).strip()
                category = str(slot_obj.get("category", "")).strip().lower()

                if name:
                    selected_names.append(name)
                if category:
                    selected_categories.append(category)

                matched = self._lookup_activity(name, activity_index)
                if matched:
                    selected_tags.extend([tag.lower() for tag in matched.tags])

        joined_text = " ".join(
            [s.lower() for s in selected_names + selected_categories + selected_tags]
        )

        must_include = user_request.must_include or []
        avoid = user_request.avoid or []
        preferences = user_request.preferences or []

        missing_required = []
        for item in must_include:
            if not self._soft_match(item, joined_text):
                missing_required.append(item)

        if missing_required:
            issues.append(
                self._issue(
                    "preference",
                    "high",
                    f"Required preferences or must-include items were not satisfied: {missing_required}.",
                )
            )
            suggestions.append(
                "Ensure all must-include items appear explicitly in the itinerary."
            )
        elif must_include:
            strengths.append("The itinerary appears to cover the must-include requests.")

        violated_avoid = []
        for item in avoid:
            if self._soft_match(item, joined_text):
                violated_avoid.append(item)

        if violated_avoid:
            issues.append(
                self._issue(
                    "preference",
                    "high",
                    f"The itinerary includes items the user wanted to avoid: {violated_avoid}.",
                )
            )
            suggestions.append(
                "Remove or replace activities that conflict with the user's avoid list."
            )
        elif avoid:
            strengths.append("The itinerary respects the user's avoid list.")

        matched_preferences = []
        unmatched_preferences = []

        for pref in preferences:
            if self._preference_matches_text(pref, joined_text):
                matched_preferences.append(pref)
            else:
                unmatched_preferences.append(pref)

        if matched_preferences:
            strengths.append(
                f"The itinerary reflects user preferences such as: {matched_preferences}."
            )

        if preferences and len(matched_preferences) == 0:
            issues.append(
                self._issue(
                    "preference",
                    "medium",
                    "The itinerary does not clearly reflect the user's stated preferences.",
                )
            )
            suggestions.append(
                "Add activities whose categories or tags better match the user's interests."
            )
        elif unmatched_preferences:
            issues.append(
                self._issue(
                    "preference",
                    "low",
                    f"Some preferences are not strongly represented: {unmatched_preferences}.",
                )
            )

            used_set = {n.strip().lower() for n in selected_names if n.strip()}
            for pref in unmatched_preferences:
                candidates = self._suggest_activities_for_pref(pref, activity_index, used_set)
                if candidates:
                    suggestions.append(
                        f"Consider adding a '{pref}' activity: {', '.join(candidates)}."
                    )

        return issues, strengths, suggestions

    def _check_weather_and_time(
        self,
        planner_output: Dict[str, Any],
        activity_index: Dict[str, Activity],
    ) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        issues: List[Dict[str, str]] = []
        strengths: List[str] = []
        suggestions: List[str] = []

        itinerary = planner_output.get("itinerary", [])

        for day_plan in itinerary:
            day_num = day_plan.get("day", "?")
            outdoor_count = 0
            checked_count = 0

            for slot, slot_obj in self._collect_day_slots(day_plan):
                name = str(slot_obj.get("activity_name", "")).strip()
                matched = self._lookup_activity(name, activity_index)
                if not matched:
                    continue

                checked_count += 1
                if not matched.indoor:
                    outdoor_count += 1

                best_time = (matched.best_time or "").strip().lower()
                if best_time and best_time not in {"any", "flexible", "all day"}:
                    if not self._best_time_matches_slot(best_time, slot):
                        issues.append(
                            self._issue(
                                "time_fit",
                                "low",
                                f"Day {day_num} {slot} may not match the activity's best_time ('{best_time}') for '{matched.name}'.",
                            )
                        )

            if checked_count > 0:
                if outdoor_count == 3:
                    issues.append(
                        self._issue(
                            "weather",
                            "medium",
                            f"Day {day_num} is heavily weather-sensitive because all scheduled activities are outdoor.",
                        )
                    )
                    suggestions.append(
                        f"Prepare an indoor backup for Day {day_num} in case of rain."
                    )
                elif outdoor_count == 2:
                    issues.append(
                        self._issue(
                            "weather",
                            "low",
                            f"Day {day_num} has moderate weather risk because most activities are outdoor.",
                        )
                    )
                else:
                    strengths.append(f"Day {day_num} has a reasonable indoor/outdoor balance.")

        return issues, strengths, suggestions

    def _check_plan_quality(
        self,
        planner_output: Dict[str, Any],
    ) -> Tuple[List[Dict[str, str]], List[str], List[str]]:
        issues: List[Dict[str, str]] = []
        strengths: List[str] = []
        suggestions: List[str] = []

        itinerary = planner_output.get("itinerary", [])
        summary = str(planner_output.get("planning_summary", "")).strip()

        if len(summary) < 20:
            issues.append(
                self._issue(
                    "quality",
                    "low",
                    "Planning summary is too short to explain the overall trip logic clearly.",
                )
            )
            suggestions.append(
                "Expand the planning summary so the user can understand the route and planning rationale."
            )
        else:
            strengths.append("The planner output includes a usable trip summary.")

        for day_plan in itinerary:
            day_num = day_plan.get("day", "?")
            categories = []
            reasons_missing = 0

            for _, slot_obj in self._collect_day_slots(day_plan):
                category = str(slot_obj.get("category", "")).strip().lower()
                if category:
                    categories.append(category)

                reason = str(slot_obj.get("reason", "")).strip()
                if len(reason) < 8:
                    reasons_missing += 1

            if len(categories) == 3 and len(set(categories)) == 1:
                issues.append(
                    self._issue(
                        "quality",
                        "low",
                        f"Day {day_num} may feel repetitive because all three slots use the same category.",
                    )
                )

            if reasons_missing >= 2:
                issues.append(
                    self._issue(
                        "quality",
                        "low",
                        f"Day {day_num} contains weak or overly short recommendation reasons.",
                    )
                )

        if not any(i["type"] == "quality" for i in issues):
            strengths.append("The itinerary shows reasonable variety and explanation quality.")

        return issues, strengths, suggestions

    # ------------------------------------------------------------------
    # Scoring and summary
    # ------------------------------------------------------------------

    def _calculate_score(self, issues: List[Dict[str, str]]) -> int:
        score = 100
        for issue in issues:
            severity = issue.get("severity", "low")
            issue_type = issue.get("type", "")

            if severity == "high":
                score -= 18 if issue_type in {"structure", "budget"} else 15
            elif severity == "medium":
                score -= 8
            else:
                score -= 3

        return max(0, min(100, score))

    def _determine_feasibility(self, issues: List[Dict[str, str]]) -> bool:
        blocking_types = {"structure", "budget"}
        return not any(
            issue.get("severity") == "high" and issue.get("type") in blocking_types
            for issue in issues
        )
    def _build_summary(
        self,
        overall_score: int,
        is_feasible: bool,
        issues: List[Dict[str, str]],
        strengths: List[str],
    ) -> str:
        high_issues = [i for i in issues if i["severity"] == "high"]
        medium_issues = [i for i in issues if i["severity"] == "medium"]
        low_issues = [i for i in issues if i["severity"] == "low"]

        major_messages = [i["message"] for i in high_issues[:1] + medium_issues[:1]]
        top_strengths = strengths[:2]

        if is_feasible:
            opening = "The itinerary is generally feasible"
        else:
            opening = "The itinerary needs revision before it can be considered fully feasible"

        summary_parts = [
            f"{opening}.",
            (
                f"Overall score: {overall_score}/100 "
                f"({len(high_issues)} high, {len(medium_issues)} medium, {len(low_issues)} low issues)."
            ),
        ]

        if major_messages:
            summary_parts.append("Main concerns: " + " ".join(major_messages))

        if top_strengths:
            clean_strengths = [s.rstrip(". ") for s in top_strengths]
            summary_parts.append("Strengths: " + "; ".join(clean_strengths) + ".")

        return " ".join(summary_parts)
    
        

def critic_agent(
    planner_output: Dict[str, Any],
    budget_output: Dict[str, Any],
    user_request: UserRequest,
    activities: Optional[List[Activity]] = None,
) -> Dict[str, Any]:
    """
    Functional wrapper for easier pipeline integration.
    """
    return CriticAgent().critique(
        planner_output=planner_output,
        budget_output=budget_output,
        user_request=user_request,
        activities=activities,
    )