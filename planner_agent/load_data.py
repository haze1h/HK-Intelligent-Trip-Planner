from __future__ import annotations

import json
from typing import List

from planner_agent.schemas import Activity


def load_activities(json_path: str) -> List[Activity]:
    with open(json_path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    activities: List[Activity] = []
    for item in raw:
        activities.append(
            Activity(
                name=item["name"],
                category=item["category"],
                area=item["area"],
                best_time=item["best_time"],
                duration_hours=float(item["duration_hours"]),
                cost_hkd=float(item["cost_hkd"]),
                indoor=bool(item["indoor"]),
                tags=item.get("tags", []),
            )
        )

    return activities