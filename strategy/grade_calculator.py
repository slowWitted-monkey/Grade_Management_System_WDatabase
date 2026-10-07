from abc import ABC, abstractmethod
from typing import List
from domain.grade_component_score import GradeComponentScore
from domain.grade_percentage import GradePercentage

class GradeCalculator(ABC):
    @abstractmethod
    def compute_period_grade(
            self,
            scores: List[GradeComponentScore],
            percentages: List[GradePercentage]
    ) -> float:
        pass

    @abstractmethod
    def compute_overall_grade(self, midterm: float, finals: float) -> float:
        pass