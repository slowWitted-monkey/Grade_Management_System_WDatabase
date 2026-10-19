from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassOffering:
    class_id: Optional[int]
    class_code: str
    subject_id: int
    teacher_id: str
    section: str
    school_year: str
    semester: str
    schedule: Optional[str] = None
    room: Optional[str] = None
