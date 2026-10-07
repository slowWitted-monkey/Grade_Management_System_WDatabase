from typing import List
from strategy.grade_calculator import GradeCalculator
from domain.grade_component_score import GradeComponentScore
from domain.grade_percentage import GradePercentage

class StandardGradeCalculator(GradeCalculator):
    def compute_period_grade(
            self,
            scores: List[GradeComponentScore],
            percentages: List[GradePercentage]
    ) -> float:
        # Create map of component_id to percentage weight
        weight_map = {p.component_id: p.percentage for p in percentages}

        # Ensure total configured weights equal 100%
        total_weight = sum(weight_map.values())
        if abs(total_weight - 100.0) > 0.01:
            raise ValueError(f"Total percentage weights must equal 100%. Current total: {total_weight}%")

        weighted_total = 0.0
        for score_obj in scores:
            if score_obj.component_id in weight_map:
                weight = weight_map[score_obj.component_id]
                # Normalize raw score based on max score
                percentage_score = (score_obj.score / score_obj.max_score) * 100.0
                weighted_total += percentage_score * (weight / 100.0)

        return round(weighted_total, 2)

    def compute_overall_grade(self, midterm: float, finals: float) -> float:
        # Standard default strategy: 40% Midterm, 60% Finals
        return round((midterm * 0.40) + (finals * 0.60), 2)