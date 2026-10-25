from dataclasses import dataclass
from typing import Optional


@dataclass
class Subject:
    subject_id: Optional[int]
    subject_code: str
    subject_name: str
    description: Optional[str] = None
    units: int = 3
