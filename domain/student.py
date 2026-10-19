from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    program: str = ""
    year_level: int = 1
    status: str = "Active"
