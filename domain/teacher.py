from dataclasses import dataclass
from typing import Optional

@dataclass
class Teacher:
    teacher_id: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    department: Optional[str] = None
    status: Optional[str] = None