from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Grade:
    grade_id: Optional[int]
    enrollment_id: int
    midterm_grade: Optional[float] = None
    finals_grade: Optional[float] = None
    overall_grade: Optional[float] = None
    midterm_equiv: Optional[float] = None
    final_equiv: Optional[float] = None
    remarks: Optional[str] = None
    date_encoded: Optional[date] = None
