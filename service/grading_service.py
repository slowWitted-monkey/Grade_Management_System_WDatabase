from config.database import get_db_connection
from repository.grade_repository import GradeRepository
from strategy.standard_calculator import StandardGradeCalculator


class GradingService:
    def __init__(self, grade_repo=None, calculator=None):
        self.grade_repo = grade_repo or GradeRepository()
        self.calculator = calculator or StandardGradeCalculator()

    def calculate_and_save_period_grade(self, grade_id=None, student_id=None, offering_id=None,
                                        enrollment_id=None, class_id=None):
        """Recompute a saved grade from persisted scores and class weights."""
        enrollment_id = enrollment_id or (str(grade_id).removeprefix("GRD_") if grade_id else None)
        class_id = class_id or offering_id
        if enrollment_id is None or class_id is None:
            raise ValueError("An enrollment and class are required to compute grades.")

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT class_id FROM class_offering WHERE class_id::text=%s OR class_code=%s", (str(class_id), str(class_id)))
                class_row = cursor.fetchone()
                if not class_row:
                    raise ValueError(f"Class offering '{class_id}' was not found.")
                class_id = class_row[0]
                cursor.execute("SELECT school_year, semester FROM class_offering WHERE class_id=%s", (class_id,))
                school_year, semester = cursor.fetchone()
                cursor.execute("""SELECT period_id, name FROM grading_period
                                 WHERE school_year=%s AND semester=%s ORDER BY period_order""",
                               (school_year, semester))
                periods = cursor.fetchall()
                computed = {}
                for period_id, period_name in periods:
                    cursor.execute("""SELECT gc.component_id, gc.max_score, gp.percentage, gcs.score
                        FROM grade_component gc
                        LEFT JOIN grade_percentage gp ON gp.component_id=gc.component_id AND gp.class_id=%s
                        LEFT JOIN grade_component_score gcs ON gcs.component_id=gc.component_id AND gcs.enrollment_id=%s
                        WHERE gc.period_id=%s ORDER BY gc.component_id""", (class_id, enrollment_id, period_id))
                    rows = cursor.fetchall()
                    if not rows or any(r[2] is None for r in rows):
                        continue
                    scores = [{"component_id": r[0], "score": r[3], "max_score": r[1]} for r in rows if r[3] is not None]
                    weights = [{"component_id": r[0], "percentage": r[2]} for r in rows]
                    if len(scores) != len(rows):
                        continue
                    computed[str(period_name).lower()] = self.calculator.compute_period_grade(scores, weights)

            midterm = computed.get("midterm")
            finals = computed.get("finals")
            overall, final_equiv, remarks = self.calculator.compute_overall_grade(midterm, finals)
            midterm_equiv = self.calculator.get_grade_point(midterm)[0] if midterm is not None else None
            self.grade_repo.save_computed_grade(enrollment_id, midterm, finals, overall,
                                                midterm_equiv, final_equiv, remarks)
            return {"midterm_pct": midterm, "finals_pct": finals, "overall_pct": overall,
                    "midterm_equiv": midterm_equiv, "final_equiv": final_equiv,
                    "remarks": remarks}
        finally:
            conn.close()

    def update_grading_weights(self, class_id: str, component_weights: dict):
        self.grade_repo.update_period_weights(class_id, component_weights)
