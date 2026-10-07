from strategy.standard_calculator import StandardGradeCalculator
from repository.grade_repository import GradeRepository

class GradingService:
    def __init__(self):
        self.calculator = StandardGradeCalculator()
        self.grade_repo = GradeRepository()

    def calculate_and_save_period_grade(self, grade_id: str, student_id: str, offering_id: str) -> float:
        # Pass student_id and offering_id as required by GradeRepository
        scores = self.grade_repo.get_scores_for_grade(student_id, offering_id)
        percentages = self.grade_repo.get_percentages_for_offering(offering_id)

        # Calculate grade using strategy
        calculated_grade = self.calculator.compute_period_grade(scores, percentages)

        # Derive remarks
        remarks = "Passed" if calculated_grade >= 75.0 else "Failed"

        # Persist result
        self.grade_repo.update_final_grade(grade_id, calculated_grade, remarks)
        return calculated_grade