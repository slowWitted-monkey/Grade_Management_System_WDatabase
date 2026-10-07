from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class Grade:
    grade_id: str
    enrollment_id: str
    period_id: str
    final_grade: Optional[float] = None
    remarks: Optional[str] = None
    date_encoded: Optional[date] = None