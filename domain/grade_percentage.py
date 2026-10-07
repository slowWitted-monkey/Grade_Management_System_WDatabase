from dataclasses import dataclass

@dataclass
class GradePercentage:
    percentage_id: str
    percentage: float
    offering_id: str
    component_id: str