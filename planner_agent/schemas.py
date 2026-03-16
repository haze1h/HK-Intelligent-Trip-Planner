from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserRequest:
    destination: str
    days: int
    total_budget_hkd: float
    preferences: List[str]
    pace: str = "moderate"  # slow / moderate / fast
    must_include: Optional[List[str]] = None
    avoid: Optional[List[str]] = None


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