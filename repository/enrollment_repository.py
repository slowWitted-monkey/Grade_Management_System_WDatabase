from config.database import get_db_connection

class EnrolmentRepository:
    def get_all_offering_ids(self) -> list:
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT offering_id FROM classoffering ORDER BY offering_id ASC;")
            rows = cursor.fetchall()
            return [row['offering_id'] if isinstance(row, dict) else row[0] for row in rows]
        except Exception as e:
            print(f"Error fetching offering IDs: {e}")
            return []
        finally:
            cursor.close()
            conn.close()

    def _get_valid_fallback_ids(self, cursor):
        """Helper to retrieve existing subject_id and teacher_id to prevent foreign key errors."""
        cursor.execute("SELECT subject_id FROM subject LIMIT 1;")
        subj_row = cursor.fetchone()
        valid_subj = subj_row['subject_id'] if isinstance(subj_row, dict) else (subj_row[0] if subj_row else None)

        cursor.execute("SELECT teacher_id FROM teacher LIMIT 1;")
        tch_row = cursor.fetchone()
        valid_tch = tch_row['teacher_id'] if isinstance(tch_row, dict) else (tch_row[0] if tch_row else None)

        return valid_subj, valid_tch

    def _ensure_default_subject(self, cursor, subject_code_or_id: str) -> str:
        """Finds an existing subject_id by ID or code, or safely inserts a unique record."""
        # 1. Search if subject already exists by subject_id or subject_code
        cursor.execute(
            "SELECT subject_id FROM subject WHERE subject_id = %s OR subject_code = %s LIMIT 1;",
            (subject_code_or_id, subject_code_or_id)
        )
        subj_row = cursor.fetchone()
        if subj_row:
            return subj_row['subject_id'] if isinstance(subj_row, dict) else subj_row[0]

        # 2. Check if any subject exists in the table to use as fallback
        fallback_subj, _ = self._get_valid_fallback_ids(cursor)
        if fallback_subj:
            return fallback_subj

        # 3. If subject table is completely empty, insert with ON CONFLICT resolution
        try:
            cursor.execute(
                """
                INSERT INTO subject (subject_id, subject_code, subject_name, units) 
                VALUES (%s, %s, 'General Subject', 3) 
                ON CONFLICT (subject_code) DO UPDATE SET subject_name = EXCLUDED.subject_name
                RETURNING subject_id;
                """,
                (f"SUB_{subject_code_or_id}", subject_code_or_id)
            )
            res = cursor.fetchone()
            return res['subject_id'] if isinstance(res, dict) else res[0]
        except Exception:
            # Fallback query to get any subject_id if insertion was bypassed
            cursor.execute("SELECT subject_id FROM subject LIMIT 1;")
            res = cursor.fetchone()
            return res['subject_id'] if isinstance(res, dict) else res[0]

    def save_offering(
            self,
            offering_id: str,
            teacher_id: str,
            subject_id: str = "CS101",
            class_code: str = None,
            schedule: str = "TBA",
            school_year: str = "2025-2026",
            semester: str = "1st"
    ) -> None:
        """Inserts or updates a class offering in classoffering safely."""
        conn = get_db_connection()
        cursor = conn.cursor()
        if not class_code:
            class_code = offering_id

        try:
            resolved_subject_id = self._ensure_default_subject(cursor, subject_id)

            query = """
                INSERT INTO classoffering (
                    offering_id, class_code, schedule, school_year, semester, teacher_id, subject_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (offering_id) DO UPDATE SET
                    class_code = EXCLUDED.class_code,
                    teacher_id = EXCLUDED.teacher_id,
                    subject_id = EXCLUDED.subject_id,
                    school_year = EXCLUDED.school_year,
                    semester = EXCLUDED.semester;
            """
            cursor.execute(query, (offering_id, class_code, schedule, school_year, semester, teacher_id, resolved_subject_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def enroll_student(self, enrollment_id: str, student_id: str, offering_id: str, status: str = "Enrolled"):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT offering_id FROM classoffering WHERE offering_id = %s;", (offering_id,))
            if not cursor.fetchone():
                valid_subj, valid_tch = self._get_valid_fallback_ids(cursor)

                if not valid_subj:
                    valid_subj = self._ensure_default_subject(cursor, "CS101")

                if not valid_tch:
                    cursor.execute(
                        "INSERT INTO teacher (teacher_id, first_name, last_name, email, department, status) "
                        "VALUES ('TCH001', 'Default', 'Teacher', 'teacher@ndmu.edu.ph', 'Computer Studies', 'Active') "
                        "ON CONFLICT (teacher_id) DO NOTHING;"
                    )
                    valid_tch = 'TCH001'

                cursor.execute("""
                    INSERT INTO classoffering (
                        offering_id, class_code, schedule, school_year, semester, teacher_id, subject_id
                    )
                    VALUES (%s, %s, 'TBA', '2025-2026', '1st', %s, %s)
                    ON CONFLICT (offering_id) DO NOTHING;
                """, (offering_id, offering_id, valid_tch, valid_subj))

            query = """
                INSERT INTO enrollment (enrollment_id, student_id, offering_id, status, enrollment_date)
                VALUES (%s, %s, %s, %s, CURRENT_DATE)
                ON CONFLICT (enrollment_id) DO UPDATE SET
                    student_id = EXCLUDED.student_id,
                    offering_id = EXCLUDED.offering_id,
                    status = EXCLUDED.status;
            """
            cursor.execute(query, (enrollment_id, student_id, offering_id, status))
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()