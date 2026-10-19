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

    def _ensure_default_components(self, cursor):
        """Automatically seeds standard grading periods and component definitions if missing."""
        periods = [
            ('PRD001', 'Midterm', '2025-08-01', '2025-10-15', '2025-2026', '1st'),
            ('PRD002', 'Finals', '2025-10-16', '2025-12-15', '2025-2026', '1st'),
        ]
        for p in periods:
            cursor.execute("""
                INSERT INTO gradingperiod (period_id, name, start_date, end_date, school_year, semester)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (period_id) DO NOTHING;
            """, p)

        default_components = [
            ('1', 'Quiz', 'Quiz', 50.00, 'Midterm Quiz', 'PRD001'),
            ('2', 'Lab / Project', 'Laboratory', 100.00, 'Midterm Lab/Project', 'PRD001'),
            ('3', 'Examination', 'Exam', 100.00, 'Midterm Examination', 'PRD001'),
            ('4', 'Quiz', 'Quiz', 50.00, 'Finals Quiz', 'PRD002'),
            ('5', 'Lab / Project', 'Laboratory', 100.00, 'Finals Lab/Project', 'PRD002'),
            ('6', 'Examination', 'Exam', 100.00, 'Finals Examination', 'PRD002'),
        ]
        for comp in default_components:
            cursor.execute("""
                INSERT INTO gradecomponent (component_id, name, type, max_score, description, period_id)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (component_id) DO NOTHING;
            """, comp)

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

    def get_scores_for_grade(self, student_id: str, offering_id: str, period_id: str) -> list:
        """Fetches score, component max_score, and weight for component grade calculation using grade_id."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            self._ensure_default_components(cursor)
            conn.commit()

            cursor.execute("""
                SELECT gcs.score, gc.max_score, gp.percentage
                FROM gradecomponentscore gcs
                JOIN gradecomponent gc ON gcs.component_id = gc.component_id
                JOIN grade g ON gcs.grade_id = g.grade_id
                JOIN enrollment e ON g.enrollment_id = e.enrollment_id
                LEFT JOIN gradepercentage gp ON (gp.offering_id = e.offering_id AND gp.component_id = gc.component_id)
                WHERE e.student_id = %s AND e.offering_id = %s AND g.period_id = %s;
            """, (student_id, offering_id, period_id))
            rows = cursor.fetchall()

            scores = []
            for r in rows:
                scores.append({
                    "score": float(r[0]),
                    "max_score": float(r[1]) if r[1] is not None else 100.0,
                    "weight": float(r[2]) if r[2] is not None else 0.0
                })
            return scores
        except Exception as e:
            print(f"Error fetching scores for grade: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def save_component_score(self, enrollment_id: str, period_id: str, component_id: str, score: float, changed_by: str = "tester"):
        """Inserts or updates a raw component score linked via grade_id with audit logging."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            self._ensure_default_components(cursor)

            cursor.execute("""
                SELECT grade_id FROM grade WHERE enrollment_id = %s AND period_id = %s;
            """, (enrollment_id, period_id))
            row = cursor.fetchone()

            if row:
                grade_id = row[0]
            else:
                grade_id = f"GRD_{enrollment_id}_{period_id}"
                cursor.execute("""
                    INSERT INTO grade (grade_id, enrollment_id, period_id, date_encoded)
                    VALUES (%s, %s, %s, CURRENT_DATE)
                    ON CONFLICT (enrollment_id, period_id) DO NOTHING;
                """, (grade_id, enrollment_id, period_id))

                cursor.execute("""
                    SELECT grade_id FROM grade WHERE enrollment_id = %s AND period_id = %s;
                """, (enrollment_id, period_id))
                grade_id = cursor.fetchone()[0]

            cursor.execute("""
                SELECT score_id, score FROM gradecomponentscore 
                WHERE grade_id = %s AND component_id = %s;
            """, (grade_id, component_id))
            score_row = cursor.fetchone()

            if score_row:
                score_id, old_score = score_row[0], score_row[1]
                cursor.execute("""
                    UPDATE gradecomponentscore 
                    SET score = %s, date_recorded = CURRENT_DATE
                    WHERE score_id = %s;
                """, (score, score_id))
                self.log_audit_event("GRADE_COMPONENT_SCORE", str(score_id), "UPDATE", f"score {old_score}", f"score {score}", changed_by)
            else:
                score_id = f"SC_{enrollment_id}_{component_id}_{period_id}"
                cursor.execute("""
                    INSERT INTO gradecomponentscore (score_id, grade_id, component_id, score, date_recorded)
                    VALUES (%s, %s, %s, %s, CURRENT_DATE)
                    ON CONFLICT (score_id) DO UPDATE SET score = EXCLUDED.score;
                """, (score_id, grade_id, component_id, score))
                self.log_audit_event("GRADE_COMPONENT_SCORE", str(score_id), "INSERT", "None", f"score {score}", changed_by)

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def delete_component_score(self, enrollment_id: str, period_id: str, component_id: str, changed_by: str = "tester"):
        """Deletes a component score with audit logging."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            grade_id = f"GRD_{enrollment_id}_{period_id}"
            cursor.execute("""
                SELECT score_id, score FROM gradecomponentscore 
                WHERE grade_id = %s AND component_id = %s;
            """, (grade_id, component_id))
            row = cursor.fetchone()
            if row:
                score_id, old_score = row[0], row[1]
                cursor.execute("DELETE FROM gradecomponentscore WHERE score_id = %s;", (score_id,))
                self.log_audit_event("GRADE_COMPONENT_SCORE", str(score_id), "DELETE", f"score {old_score}", "None", changed_by)
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def save_or_update_grade(self, grade_id: str, enrollment_id: str, period_id: str, final_grade: float, remarks: str, final_equiv: float = None):
        """Directly inserts or updates a grade record from the GUI form."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO grade (grade_id, enrollment_id, period_id, final_grade, final_equiv, remarks, date_encoded)
                VALUES (%s, %s, %s, %s, %s, %s, CURRENT_DATE)
                ON CONFLICT (enrollment_id, period_id) 
                DO UPDATE SET 
                    final_grade = EXCLUDED.final_grade,
                    final_equiv = EXCLUDED.final_equiv,
                    remarks = EXCLUDED.remarks,
                    date_encoded = CURRENT_DATE;
            """, (grade_id, enrollment_id, period_id, final_grade, final_equiv, remarks))
            conn.commit()
            self.log_audit_event("GRADE", enrollment_id, "UPSERT", f"Grade: {final_grade}", f"Saved Grade: {final_grade}")
        finally:
            cursor.close()
            conn.close()

    def update_grade_record(self, enrollment_id: str, midterm_pct: float, finals_pct: float, overall_pct: float, midterm_equiv: float, final_equiv: float, remarks: str):
        """Persists percentages, grade point equivalents, and remarks into GRADE table."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
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

    def update_period_weights(self, offering_id: str, period_weights: dict):
        """Updates component weights for an offering period. Enforces 100% sum validation."""
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
                    SELECT percentage FROM gradepercentage WHERE offering_id = %s AND component_id = %s;
                """, (offering_id, comp_id))
                old_row = cursor.fetchone()
                old_weight = old_row[0] if old_row else 0.0

                cursor.execute("""
                    INSERT INTO gradepercentage (offering_id, component_id, percentage)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (offering_id, component_id)
                    DO UPDATE SET percentage = EXCLUDED.percentage;
                """, (offering_id, comp_id, weight))

                self.log_audit_event("GRADE_PERCENTAGE", f"{offering_id}_{comp_id}", "UPDATE", f"Weight: {old_weight}%", f"Weight: {weight}%")

            conn.commit()
        finally:
            cursor.close()
            conn.close()

    def get_all_audit_logs(self) -> list:
        """Fetches all audit trail records from AUDIT_LOG table."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT log_id, table_name, record_id, action, old_value, new_value, changed_by, changed_at
                FROM audit_log
                ORDER BY changed_at DESC;
            """)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()