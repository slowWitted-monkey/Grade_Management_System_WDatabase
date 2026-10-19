import psycopg2
from config.database import get_db_connection

class GradeRepository:

    def log_audit_event(self, table_name: str, record_id: str, action: str, old_val: str, new_val: str, changed_by: str = "tester"):
        """Records structural and grade modifications into AUDIT_LOG table."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO audit_log (table_name, record_id, action, old_value, new_value, changed_by)
                VALUES (%s, %s, %s, %s, %s, %s);
            """, (table_name, str(record_id), action, str(old_val), str(new_val), changed_by))
            conn.commit()
        except Exception as e:
            print(f"Error writing audit log: {e}")
            conn.rollback()
        finally:
            cursor.close()
            conn.close()

    def get_student_id_by_grade_id(self, grade_id: str) -> str:
        """Retrieves student_id linked to a specific grade record."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT e.student_id
                FROM grade g
                JOIN enrollment e ON g.enrollment_id = e.enrollment_id
                WHERE g.grade_id = %s;
            """, (grade_id,))
            row = cursor.fetchone()
            if row:
                return row[0]
            raise ValueError(f"No student record found for Grade ID: {grade_id}")
        finally:
            cursor.close()
            conn.close()

    def get_scores_for_grade(self, student_id: str, offering_id: str) -> list:
        """Fetches score, max_score, and weight for component grade calculation."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT cs.score, a.max_score, gp.percentage
                FROM componentscore cs
                JOIN assessment a ON cs.assessment_id = a.assessment_id
                JOIN enrollment e ON cs.enrollment_id = e.enrollment_id
                LEFT JOIN grade_percentage gp ON (gp.class_id = e.offering_id AND gp.component_id = a.component_id)
                WHERE e.student_id = %s AND e.offering_id = %s;
            """, (student_id, offering_id))
            rows = cursor.fetchall()

            scores = []
            for r in rows:
                scores.append({
                    "score": r[0],
                    "max_score": r[1],
                    "weight": float(r[2]) if r[2] is not None else 0.0
                })
            return scores
        except Exception as e:
            print(f"Error fetching scores for grade: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def update_grade_record(self, enrollment_id: str, midterm_pct: float, finals_pct: float, overall_pct: float, midterm_equiv: float, final_equiv: float, remarks: str):
        """Persists percentages, grade point equivalents, and remarks into GRADE table."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check old grade state for audit logging
            cursor.execute("""
                SELECT midterm_grade, overall_grade FROM grade WHERE enrollment_id = %s;
            """, (enrollment_id,))
            old_row = cursor.fetchone()
            old_val_str = f"Midterm: {old_row[0]}, Overall: {old_row[1]}" if old_row else "None"

            cursor.execute("""
                INSERT INTO grade (grade_id, enrollment_id, period_id, midterm_grade, finals_grade, overall_grade, midterm_equiv, final_equiv, remarks, date_encoded)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_DATE)
                ON CONFLICT (enrollment_id, period_id) 
                DO UPDATE SET 
                    midterm_grade = EXCLUDED.midterm_grade,
                    finals_grade = EXCLUDED.finals_grade,
                    overall_grade = EXCLUDED.overall_grade,
                    midterm_equiv = EXCLUDED.midterm_equiv,
                    final_equiv = EXCLUDED.final_equiv,
                    remarks = EXCLUDED.remarks,
                    date_encoded = CURRENT_DATE;
            """, (f"GRD_{enrollment_id}", enrollment_id, 'PRD002', midterm_pct, finals_pct, overall_pct, midterm_equiv, final_equiv, remarks))

            conn.commit()

            new_val_str = f"Midterm: {midterm_pct}, Overall: {overall_pct} ({final_equiv})"
            self.log_audit_event("GRADE", enrollment_id, "UPDATE", old_val_str, new_val_str)
        finally:
            cursor.close()
            conn.close()

    def update_period_weights(self, class_id: str, period_weights: dict):
        """
        Updates component weights for a class period. Enforces 100% sum validation.
        period_weights format: {component_id: weight_percentage}
        """
        total_weight = sum(period_weights.values())
        if round(total_weight, 2) != 100.0:
            raise ValueError(f"Weight validation failed! Period weights sum to {total_weight}%, but must equal exactly 100.0%.")

        for w in period_weights.values():
            if w < 0:
                raise ValueError("Weight validation failed! Weights cannot be negative.")

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for comp_id, weight in period_weights.items():
                cursor.execute("""
                    SELECT percentage FROM grade_percentage WHERE class_id = %s AND component_id = %s;
                """, (class_id, comp_id))
                old_row = cursor.fetchone()
                old_weight = old_row[0] if old_row else 0.0

                cursor.execute("""
                    INSERT INTO grade_percentage (class_id, component_id, percentage)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (class_id, component_id)
                    DO UPDATE SET percentage = EXCLUDED.percentage;
                """, (class_id, comp_id, weight))

                self.log_audit_event("GRADE_PERCENTAGE", f"{class_id}_{comp_id}", "UPDATE", f"Weight: {old_weight}%", f"Weight: {weight}%")

            conn.commit()
        finally:
            cursor.close()
            conn.close()