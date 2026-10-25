from decimal import Decimal

import psycopg2

from config.database import get_db_connection


class GradeRepository:
    @staticmethod
    def _audit(cursor, table, record_id, action, old_value, new_value, changed_by="tester"):
        cursor.execute("""INSERT INTO audit_log
            (table_name, record_id, action, old_value, new_value, changed_by)
            VALUES (%s,%s,%s,%s,%s,%s)""",
            (table, str(record_id), action, str(old_value) if old_value is not None else None,
             str(new_value) if new_value is not None else None, changed_by))

    def log_audit_event(self, table_name, record_id, action, old_val, new_val, changed_by="tester"):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                self._audit(cursor, table_name, record_id, action, old_val, new_val, changed_by)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_component_score(self, enrollment_id, period_id, component_id, score,
                             changed_by="tester", remarks=None):
        score = Decimal(str(score))
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""SELECT gc.max_score, e.class_id FROM grade_component gc
                    JOIN enrollment e ON e.enrollment_id=%s
                    WHERE gc.component_id=%s AND gc.period_id=%s""",
                    (enrollment_id, component_id, period_id))
                meta = cursor.fetchone()
                if not meta:
                    raise ValueError("The student must be enrolled in the class and the component must belong to this grading period.")
                maximum, class_id = Decimal(meta[0]), meta[1]
                if score < 0 or score > maximum:
                    raise ValueError(f"Score must be between 0 and {maximum}.")
                cursor.execute("SELECT percentage FROM grade_percentage WHERE class_id=%s AND component_id=%s", (class_id, component_id))
                if not cursor.fetchone():
                    raise ValueError("Configure this component's class weight before entering scores.")
                cursor.execute("SELECT score_id, score, remarks FROM grade_component_score WHERE enrollment_id=%s AND component_id=%s", (enrollment_id, component_id))
                old = cursor.fetchone()
                cursor.execute("""INSERT INTO grade_component_score
                    (enrollment_id, component_id, score, remarks)
                    VALUES (%s,%s,%s,%s) ON CONFLICT (enrollment_id, component_id)
                    DO UPDATE SET score=EXCLUDED.score, remarks=EXCLUDED.remarks,
                    date_recorded=CURRENT_DATE
                    RETURNING score_id""", (enrollment_id, component_id, score, remarks))
                score_id = cursor.fetchone()[0]
                self._audit(cursor, "GRADE_COMPONENT_SCORE", score_id, "UPDATE" if old else "INSERT",
                            (old[1], old[2]) if old else None, (score, remarks), changed_by)
            conn.commit()
            return score_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def delete_component_score(self, enrollment_id, period_id, component_id, changed_by="tester"):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""DELETE FROM grade_component_score s USING grade_component c
                    WHERE s.component_id=c.component_id AND s.enrollment_id=%s AND s.component_id=%s
                    AND c.period_id=%s RETURNING s.score_id, s.score, s.remarks""", (enrollment_id, component_id, period_id))
                old = cursor.fetchone()
                if old:
                    self._audit(cursor, "GRADE_COMPONENT_SCORE", old[0], "DELETE",
                                (old[1], old[2]), None, changed_by)
            conn.commit()
            return bool(old)
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def update_period_weights(self, class_id, component_weights):
        weights = {int(k): Decimal(str(v)) for k, v in component_weights.items()}
        if not weights or any(v < 0 or v > 100 for v in weights.values()):
            raise ValueError("Each weight must be between 0 and 100%.")
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT component_id, period_id FROM grade_component WHERE component_id = ANY(%s)", (list(weights),))
                component_period = dict(cursor.fetchall())
                if len(component_period) != len(weights):
                    raise ValueError("One or more grade components do not exist.")
                changed_periods = set(component_period.values())
                for period_id in changed_periods:
                    cursor.execute("""SELECT gc.component_id, gp.percentage FROM grade_component gc
                        LEFT JOIN grade_percentage gp ON gp.component_id=gc.component_id AND gp.class_id=%s
                        WHERE gc.period_id=%s""", (class_id, period_id))
                    current = {cid: Decimal(str(pct or 0)) for cid, pct in cursor.fetchall()}
                    current.update({cid: wt for cid, wt in weights.items() if component_period[cid] == period_id})
                    if sum(current.values()) != Decimal("100"):
                        raise ValueError(f"Weights for grading period {period_id} must total exactly 100%.")
                for component_id, weight in weights.items():
                    cursor.execute("SELECT percentage_id, percentage FROM grade_percentage WHERE class_id=%s AND component_id=%s", (class_id, component_id))
                    old = cursor.fetchone()
                    cursor.execute("""INSERT INTO grade_percentage (class_id, component_id, percentage)
                        VALUES (%s,%s,%s) ON CONFLICT (class_id, component_id)
                        DO UPDATE SET percentage=EXCLUDED.percentage RETURNING percentage_id""",
                        (class_id, component_id, weight))
                    percentage_id = cursor.fetchone()[0]
                    self._audit(cursor, "GRADE_PERCENTAGE", percentage_id, "UPDATE" if old else "INSERT",
                                old[1] if old else None, weight)
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def save_computed_grade(self, enrollment_id, midterm, finals, overall, midterm_equiv, final_equiv, remarks):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT grade_id, midterm_grade, finals_grade, overall_grade FROM grade WHERE enrollment_id=%s", (enrollment_id,))
                old = cursor.fetchone()
                cursor.execute("""INSERT INTO grade
                    (enrollment_id, midterm_grade, finals_grade, overall_grade, midterm_equiv, final_equiv, remarks)
                    VALUES (%s,%s,%s,%s,%s,%s,%s) ON CONFLICT (enrollment_id)
                    DO UPDATE SET midterm_grade=EXCLUDED.midterm_grade, finals_grade=EXCLUDED.finals_grade,
                    overall_grade=EXCLUDED.overall_grade, midterm_equiv=EXCLUDED.midterm_equiv,
                    final_equiv=EXCLUDED.final_equiv, remarks=EXCLUDED.remarks,
                    date_encoded=CURRENT_DATE RETURNING grade_id""",
                    (enrollment_id, midterm, finals, overall, midterm_equiv, final_equiv, remarks))
                grade_id = cursor.fetchone()[0]
                new_values = (midterm, finals, overall, midterm_equiv, final_equiv, remarks)
                if old is None or tuple(old[1:]) != new_values:
                    self._audit(cursor, "GRADE", grade_id, "INSERT" if old is None else "UPDATE", old[1:] if old else None, new_values)
            conn.commit()
            return grade_id
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_all_audit_logs(self):
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT log_id, table_name, record_id, action, old_value, new_value, changed_by, changed_at FROM audit_log ORDER BY changed_at DESC, log_id DESC")
                return cursor.fetchall()
        finally:
            conn.close()

