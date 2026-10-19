from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Enrollment:
    enrollment_id: Optional[int]
    student_id: str
    class_id: int
    enroll_date: Optional[date] = None
    status: str = "Enrolled"
