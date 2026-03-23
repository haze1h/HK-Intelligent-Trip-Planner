from __future__ import annotations

import os
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from budget_tool.budget import estimate_budget
from critic_agent.critic import CriticAgent
from planner_agent.load_data import load_activities
from planner_agent.planner import PlannerAgent
from planner_agent.schemas import UserRequest

BASE_DIR = Path(__file__).resolve().parent
MODEL_NAME = os.getenv("OLLAMA_MODEL", "mistral:7b")
DATA_PATH = Path(os.getenv("HK_ACTIVITIES_PATH", str(BASE_DIR / "data" / "hk_activities.json"))).resolve()
SAMPLE_SIZE = int(os.getenv("PLANNER_SAMPLE_SIZE", "12"))

PACE_MAP = {
    "relaxed": "slow",
    "slow": "slow",
    "moderate": "moderate",
    "packed": "fast",
    "fast": "fast",
}

BUDGET_STYLE_MAP = {
    "budget": "economy",
    "economy": "economy",
    "standard": "standard",
    "premium": "premium",
    "luxury": "premium",
}


class TravelPlanRequest(BaseModel):
    destination: str = Field(default="Hong Kong")
    days: int = Field(ge=1, le=30)
    total_budget_hkd: float = Field(gt=0)
    preferences: List[str] = Field(default_factory=list)
    pace: str = Field(default="moderate")
    must_include: List[str] = Field(default_factory=list)
    avoid: List[str] = Field(default_factory=list)
    travelers: int = Field(default=1, ge=1, le=20)
    budget_style: str = Field(default="standard")


app = FastAPI(title="HK Intelligent Trip Planner API", version="1.0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@lru_cache(maxsize=1)
def get_activities():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Activity dataset not found: {DATA_PATH}")
    return load_activities(str(DATA_PATH))


@lru_cache(maxsize=1)
def get_planner() -> PlannerAgent:
    return PlannerAgent(model_name=MODEL_NAME)


@lru_cache(maxsize=1)
def get_critic() -> CriticAgent:
    return CriticAgent()


def build_stable_subset(all_activities, must_include_names: List[str], sample_size: int = SAMPLE_SIZE):
    must_include_names = must_include_names or []
    selected = []
    selected_names = set()

    for activity in all_activities:
        lower_name = activity.name.lower()
        for need in must_include_names:
            need_lower = need.lower().strip()
            if need_lower and (need_lower in lower_name or lower_name in need_lower):
                if lower_name not in selected_names:
                    selected.append(activity)
                    selected_names.add(lower_name)

    remaining = [a for a in all_activities if a.name.lower() not in selected_names]
    extra_needed = max(0, sample_size - len(selected))

    if extra_needed > 0 and remaining:
        selected.extend(random.sample(remaining, min(extra_needed, len(remaining))))

    return selected


def normalize_request(payload: TravelPlanRequest) -> UserRequest:
    normalized_pace = PACE_MAP.get(payload.pace.lower().strip(), "moderate")
    normalized_budget_style = BUDGET_STYLE_MAP.get(payload.budget_style.lower().strip(), "standard")

    return UserRequest(
        destination=payload.destination.strip() or "Hong Kong",
        days=payload.days,
        total_budget_hkd=payload.total_budget_hkd,
        preferences=[p.strip() for p in payload.preferences if p and p.strip()],
        pace=normalized_pace,
        must_include=[m.strip() for m in payload.must_include if m and m.strip()],
        avoid=[a.strip() for a in payload.avoid if a and a.strip()],
        travelers=payload.travelers,
        budget_style=normalized_budget_style,
    )


def _is_service_error(detail: str) -> bool:
    text = (detail or "").lower()
    keywords = [
        "ollama",
        "connect",
        "connection",
        "refused",
        "timed out",
        "timeout",
        "model",
        "failed to generate itinerary",
    ]
    return any(k in text for k in keywords)


@app.get("/api/health")
def health_check() -> Dict[str, Any]:
    try:
        activities_loaded = len(get_activities())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {
        "ok": True,
        "model": MODEL_NAME,
        "data_path": str(DATA_PATH),
        "activities_loaded": activities_loaded,
    }


@app.post("/api/travel-plan")
def create_travel_plan(payload: TravelPlanRequest) -> Dict[str, Any]:
    try:
        user_request = normalize_request(payload)
        activities = get_activities()
        subset = build_stable_subset(activities, user_request.must_include, SAMPLE_SIZE)

        planner_output = get_planner().plan(user_request, subset)
        budget_summary = estimate_budget(planner_output, user_request)
        critic_report = get_critic().critique(
            planner_output=planner_output,
            budget_output=budget_summary,
            user_request=user_request,
            activities=activities,
        )
    except Exception as exc:
        detail = str(exc)
        if _is_service_error(detail):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Failed to generate itinerary. Check that Ollama is running, the model "
                    f"'{MODEL_NAME}' is installed, and the backend can access it. Original error: {detail}"
                ),
            ) from exc
        raise HTTPException(status_code=500, detail=detail) from exc

    return {
        "itinerary": planner_output,
        "budget_summary": budget_summary,
        "critic_report": critic_report,
    }
