from dataclasses import dataclass
from typing import Optional

@dataclass
class Student:
    student_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    program: Optional[str] = None
    status: Optional[str] = None