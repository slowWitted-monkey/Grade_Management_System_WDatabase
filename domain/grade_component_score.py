from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class GradeComponentScore:
    score_id: Optional[int]
    score: float
    enrollment_id: int
    component_id: int
    max_score: Optional[float] = None
    remarks: Optional[str] = None
    date_recorded: Optional[date] = None
