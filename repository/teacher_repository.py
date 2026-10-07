from typing import List, Optional, Union
from config.database import get_db_connection
from domain.teacher import Teacher


class TeacherRepository:
    def find_all(self) -> List[Teacher]:
        """Fetches all teachers from the database sorted by last name, first name."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT teacher_id, first_name, last_name, email, department, status "
            "FROM teacher ORDER BY last_name, first_name;"
        )
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        teachers = []
        for r in rows:
            if isinstance(r, dict):
                teachers.append(Teacher(
                    teacher_id=r.get("teacher_id"),
                    first_name=r.get("first_name"),
                    last_name=r.get("last_name"),
                    email=r.get("email"),
                    department=r.get("department"),
                    status=r.get("status", "Active")
                ))
            else:
                teachers.append(Teacher(
                    teacher_id=r[0],
                    first_name=r[1],
                    last_name=r[2],
                    email=r[3],
                    department=r[4],
                    status=r[5] if len(r) > 5 else "Active"
                ))
        return teachers

    def save(
            self,
            teacher_or_id: Union[Teacher, str],
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            email: Optional[str] = None,
            department: Optional[str] = None,
            status: str = "Active"
    ) -> None:
        """Inserts or updates a teacher record using either a Teacher object or positional values."""
        if isinstance(teacher_or_id, Teacher):
            t_id = teacher_or_id.teacher_id
            f_name = teacher_or_id.first_name
            l_name = teacher_or_id.last_name
            e_mail = teacher_or_id.email
            dept = teacher_or_id.department
            stat = getattr(teacher_or_id, 'status', 'Active')
        else:
            t_id = teacher_or_id
            f_name = first_name
            l_name = last_name
            e_mail = email
            dept = department
            stat = status

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            INSERT INTO teacher (teacher_id, first_name, last_name, email, department, status)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (teacher_id) DO UPDATE SET
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                email = EXCLUDED.email,
                department = EXCLUDED.department,
                status = EXCLUDED.status;
        """
        cursor.execute(query, (t_id, f_name, l_name, e_mail, dept, stat))
        conn.commit()
        cursor.close()
        conn.close()

    def delete_by_id(self, teacher_id: str) -> None:
        """Deletes a teacher record by ID."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM teacher WHERE teacher_id = %s;", (teacher_id,))
        conn.commit()
        cursor.close()
        conn.close()