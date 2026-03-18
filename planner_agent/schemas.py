from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class UserRequest:
    destination: str
    days: int
    total_budget_hkd: float
    preferences: List[str]
    pace: str = "moderate"  # slow / moderate / fast
    must_include: Optional[List[str]] = None
    avoid: Optional[List[str]] = None
    travelers: int = 1
    budget_style: Optional[str] = None  # economy / standard / premium


@dataclass
class Activity:
    name: str
    category: str
    area: str
    best_time: str
    duration_hours: float
    cost_hkd: float
    indoor: bool
    tags: List[str] = field(default_factory=list)


@dataclass
class BudgetAllocation:
    total_budget_hkd: float
    budget_style: str
    fixed_cost_estimate_hkd: float
    activity_budget_hkd: float
    fixed_cost_breakdown: Dict[str, float] = field(default_factory=dict)
    assumptions: List[str] = field(default_factory=list)