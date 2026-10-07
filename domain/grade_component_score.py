from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class GradeComponentScore:
    score_id: str
    score: float
    grade_id: str
    component_id: str
    max_score: float = 100.0
    remarks: Optional[str] = None
    date_recorded: Optional[date] = None