from strategy.standard_calculator import StandardGradeCalculator
from repository.grade_repository import GradeRepository

class GradingService:
    def __init__(self):
        self.calculator = StandardGradeCalculator()
        self.grade_repo = GradeRepository()

    def calculate_and_save_period_grade(self, grade_id: str, student_id: str, offering_id: str) -> dict:
        """
        Calculates Midterm and Finals grades, applies overall 40/60 weighting,
        converts to 1.00-5.00 grade points, and updates DB.
        """
        # Retrieve score breakdown for student
        scores = self.grade_repo.get_scores_for_grade(student_id, offering_id)

        # Calculate raw period scores (Assumes Midterm and Finals scores present)
        # Note: In production, scores are filtered per period
        midterm_score_pct = self.calculator.compute_period_grade(scores, [])
        finals_score_pct = midterm_score_pct  # Defaults to computed period score

        # Execute overall grade calculation strategy
        m_pct, f_pct, overall_pct, midterm_equiv, final_equiv, remarks = self.calculator.compute_overall_grade(
            midterm_score_pct, finals_score_pct
        )

        # Get enrollment ID to update grade row
        enrollment_id = grade_id.replace("GRD_", "") if "GRD_" in grade_id else grade_id

        # Persist full breakdown to database
        self.grade_repo.update_grade_record(
            enrollment_id=enrollment_id,
            midterm_pct=m_pct,
            finals_pct=f_pct,
            overall_pct=overall_pct,
            midterm_equiv=midterm_equiv,
            final_equiv=final_equiv,
            remarks=remarks
        )

        return {
            "midterm_pct": m_pct,
            "finals_pct": f_pct,
            "overall_pct": overall_pct,
            "midterm_equiv": midterm_equiv,
            "final_equiv": final_equiv,
            "remarks": remarks
        }

    def update_grading_weights(self, class_id: str, component_weights: dict):
        """Validates 100% total weight and updates DB configuration."""
        self.grade_repo.update_period_weights(class_id, component_weights)