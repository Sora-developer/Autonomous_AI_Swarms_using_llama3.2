# schemas.py
"""
Pydantic response models used to enforce real JSON-Schema compliance on the
Planner and Critic agents (instead of relying on generic format='json' mode,
which only guarantees valid JSON — not the right fields).
"""

from typing import List
from pydantic import BaseModel


class PlannerOutput(BaseModel):
    feature_name: str
    core_components: List[str]
    implementation_steps: List[str]


class CriticOutput(BaseModel):
    identified_flaws: List[str]
    severity_level: str
    suggested_fixes: List[str]
