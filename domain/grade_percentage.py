from dataclasses import dataclass
from typing import Optional


@dataclass
class GradePercentage:
    percentage_id: Optional[int]
    percentage: float
    class_id: int
    component_id: int
