from dataclasses import dataclass
from typing import Optional


@dataclass
class GradeComponent:
    component_id: Optional[int]
    period_id: int
    name: str
    type: str
    max_score: float
    description: Optional[str] = None
