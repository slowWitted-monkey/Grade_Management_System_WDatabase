import re
import tkinter as tk
from tkinter import ttk, messagebox

# Absolute imports from the project root
from domain.student import Student
from repository.student_repository import StudentRepository
from repository.teacher_repository import TeacherRepository
from repository.enrollment_repository import EnrolmentRepository
from repository.grade_repository import GradeRepository
from service.report_service import ReportService
from service.grading_service import GradingService


class GradeManagementGUI(tk.Tk):
    # Modern Dark Theme Color Palette
    BG_DARK = "#1E1E2E"
    CARD_BG = "#2A2A3C"
    ACCENT_BLUE = "#3B82F6"
    ACCENT_HOVER = "#2563EB"
    DANGER_RED = "#EF4444"
    DANGER_HOVER = "#DC2626"
    TEXT_LIGHT = "#F3F4F6"
    TEXT_MUTED = "#9CA3AF"
    ENTRY_BG = "#181825"
    BORDER_COLOR = "#313244"

    def __init__(self):
        super().__init__()

        # Instantiate grade_repository so self.grade_repository exists
        self.grade_repository = GradeRepository()

        self.title("Student Grade Management System - NDMU CSPC 103")
        self.geometry("1120x760")
        self.minsize(920, 670)
        self.configure(bg=self.BG_DARK)

        # Initialize Repositories and Services
        self.student_repo = StudentRepository()
        self.teacher_repo = TeacherRepository()
        self.enrolment_repo = EnrolmentRepository()
        self.grade_repo = GradeRepository()
        self.report_service = ReportService()
        self.grading_service = GradingService()

        # Configure Global Modern TTK Styles
        self._setup_modern_styles()

        # Build Header Container
        self._build_header()

        # Navigation Tabs Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Tab Frames
        self.tab_student_mgmt = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_teacher_mgmt = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_enrollment = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_grade_entry = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_class_list = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_grade_sheet = ttk.Frame(self.notebook, style="Card.TFrame")
        self.tab_student_report = ttk.Frame(self.notebook, style="Card.TFrame")

        # Register Notebook Tabs
        self.notebook.add(self.tab_student_mgmt, text="  Student Records  ")
        self.notebook.add(self.tab_teacher_mgmt, text="  Teacher Records  ")
        self.notebook.add(self.tab_enrollment, text="  Course Enrollment  ")
        self.notebook.add(self.tab_grade_entry, text="  Grade Computation  ")
        self.notebook.add(self.tab_class_list, text="  Class List Report  ")
        self.notebook.add(self.tab_grade_sheet, text="  Class Grade Sheet  ")
        self.notebook.add(self.tab_student_report, text="  Student Grade Report  ")

        # Initialize Tab Layouts
        self._setup_student_mgmt_tab()
        self._setup_teacher_mgmt_tab()
        self._setup_enrollment_tab()
        self._setup_grade_entry_tab()
        self._setup_class_list_tab()
        self._setup_grade_sheet_tab()
        self._setup_student_report_tab()

        # Initial loading & sync across dropdowns
        self.refresh_student_dropdowns()
        self.refresh_teacher_dropdowns()
        self.refresh_offering_comboboxes()

    # ------------------------------------------------------------------
    # STYLING & THEMING SETUP
    # ------------------------------------------------------------------
    def _setup_modern_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=self.BG_DARK)
        style.configure("Card.TFrame", background=self.CARD_BG, relief="flat")
        style.configure("Card.TLabelframe", background=self.CARD_BG, bordercolor=self.BORDER_COLOR, relief="solid")
        style.configure("Card.TLabelframe.Label", background=self.CARD_BG, foreground=self.TEXT_LIGHT, font=("Segoe UI", 10, "bold"))

        style.configure("TLabel", background=self.CARD_BG, foreground=self.TEXT_LIGHT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=self.BG_DARK, foreground=self.TEXT_LIGHT, font=("Segoe UI", 16, "bold"))
        style.configure("SubHeader.TLabel", background=self.BG_DARK, foreground=self.TEXT_MUTED, font=("Segoe UI", 10))

        style.configure("TEntry", fieldbackground=self.ENTRY_BG, foreground=self.TEXT_LIGHT, insertcolor=self.TEXT_LIGHT, borderwidth=1, relief="solid")
        style.configure("TCombobox", fieldbackground=self.ENTRY_BG, background=self.CARD_BG, foreground=self.TEXT_LIGHT, insertcolor=self.TEXT_LIGHT, borderwidth=1)
        style.map("TCombobox", fieldbackground=[("readonly", self.ENTRY_BG)], selectbackground=[("readonly", self.ACCENT_BLUE)])

        style.configure("Primary.TButton", background=self.ACCENT_BLUE, foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=(12, 6))
        style.map("Primary.TButton", background=[("active", self.ACCENT_HOVER)])

        style.configure("Danger.TButton", background=self.DANGER_RED, foreground="#FFFFFF", font=("Segoe UI", 10, "bold"), borderwidth=0, padding=(12, 6))
        style.map("Danger.TButton", background=[("active", self.DANGER_HOVER)])

        style.configure("TNotebook", background=self.BG_DARK, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.CARD_BG, foreground=self.TEXT_MUTED, padding=(14, 8), font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map("TNotebook.Tab", background=[("selected", self.ACCENT_BLUE)], foreground=[("selected", "#FFFFFF")])

        style.configure("Treeview", background=self.ENTRY_BG, foreground=self.TEXT_LIGHT, fieldbackground=self.ENTRY_BG, rowheight=30, font=("Segoe UI", 10), borderwidth=0)
        style.configure("Treeview.Heading", background=self.CARD_BG, foreground=self.TEXT_LIGHT, font=("Segoe UI", 10, "bold"), borderwidth=0, padding=6)
        style.map("Treeview", background=[("selected", self.ACCENT_BLUE)], foreground=[("selected", "#FFFFFF")])

    def _build_header(self):
        header_frame = ttk.Frame(self)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        ttk.Label(header_frame, text="Student Grade Management System", style="Header.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="NDMU CSPC 103 Academic Administration Portal", style="SubHeader.TLabel").pack(anchor="w")

    # ------------------------------------------------------------------
    # DROPDOWN REFRESH HELPERS
    # ------------------------------------------------------------------
    def refresh_student_dropdowns(self):
        try:
            students = self.student_repo.find_all()
            student_ids = [s.student_id for s in students] if students else []

            self.cmb_enr_student['values'] = student_ids
            self.cmb_man_student_id['values'] = student_ids
            self.cmb_report_student_id['values'] = student_ids

            if student_ids:
                if not self.cmb_enr_student.get():
                    self.cmb_enr_student.set(student_ids[0])
                if not self.cmb_man_student_id.get():
                    self.cmb_man_student_id.set(student_ids[0])
                if not self.cmb_report_student_id.get():
                    self.cmb_report_student_id.set(student_ids[0])
            else:
                self.cmb_enr_student.set("")
                self.cmb_man_student_id.set("")
                self.cmb_report_student_id.set("")
        except Exception as e:
            print(f"Error refreshing student dropdowns: {e}")

    def refresh_teacher_dropdowns(self):
        try:
            if hasattr(self.teacher_repo, 'find_all'):
                teachers = self.teacher_repo.find_all()
                formatted_list = [f"{t.teacher_id} - {t.first_name} {t.last_name}" for t in teachers] if teachers else []
            else:
                formatted_list = []

            if hasattr(self, 'cmb_offering_teacher'):
                self.cmb_offering_teacher['values'] = formatted_list
                if formatted_list and not self.cmb_offering_teacher.get():
                    self.cmb_offering_teacher.set(formatted_list[0])
        except Exception as e:
            print(f"Error refreshing teacher dropdowns: {e}")

    def refresh_offering_comboboxes(self):
        try:
            if hasattr(self.enrolment_repo, 'get_all_offering_ids'):
                offering_ids = self.enrolment_repo.get_all_offering_ids()
            else:
                offering_ids = ["OFF001", "OFF002", "OFF003", "OFF004"]

            if not offering_ids:
                offering_ids = ["OFF001", "OFF002", "OFF003", "OFF004"]

            if hasattr(self, 'cmb_enr_offering'):
                self.cmb_enr_offering['values'] = offering_ids
            if hasattr(self, 'cmb_man_offering_id'):
                self.cmb_man_offering_id['values'] = offering_ids
            if hasattr(self, 'cmb_offering_id_calc'):
                self.cmb_offering_id_calc['values'] = offering_ids
            if hasattr(self, 'cmb_offering_class'):
                self.cmb_offering_class['values'] = offering_ids
            if hasattr(self, 'cmb_offering_sheet'):
                self.cmb_offering_sheet['values'] = offering_ids
        except Exception as e:
            print(f"Error refreshing offering comboboxes: {e}")

    # ------------------------------------------------------------------
    # TAB 1: STUDENT RECORDS MANAGEMENT
    # ------------------------------------------------------------------
    def _setup_student_mgmt_tab(self):
        form_frame = ttk.LabelFrame(self.tab_student_mgmt, text=" Add / Update / Delete Student ", style="Card.TLabelframe")
        form_frame.pack(fill="x", padx=15, pady=15)

        form_grid = ttk.Frame(form_frame, style="Card.TFrame")
        form_grid.pack(padx=15, pady=15, fill="x")

        ttk.Label(form_grid, text="Student ID:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.ent_std_id = ttk.Entry(form_grid, width=15)
        self.ent_std_id.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(form_grid, text="Program:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.cmb_std_prog = ttk.Combobox(form_grid, width=13, values=["BSCS", "BSIT", "BSEMC", "BSIS"])
        self.cmb_std_prog.set("BSCS")
        self.cmb_std_prog.grid(row=1, column=1, padx=8, pady=8)

        ttk.Label(form_grid, text="First Name:").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.ent_std_first = ttk.Entry(form_grid, width=18)
        self.ent_std_first.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(form_grid, text="Email:").grid(row=1, column=2, padx=8, pady=8, sticky="w")
        self.ent_std_email = ttk.Entry(form_grid, width=18)
        self.ent_std_email.grid(row=1, column=3, padx=8, pady=8)

        ttk.Label(form_grid, text="Last Name:").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        self.ent_std_last = ttk.Entry(form_grid, width=18)
        self.ent_std_last.grid(row=0, column=5, padx=8, pady=8)

        ttk.Label(form_grid, text="Status:").grid(row=1, column=4, padx=8, pady=8, sticky="w")
        self.cmb_std_status = ttk.Combobox(form_grid, width=16, values=["Enrolled", "Dropped", "Graduated", "Inactive"], state="readonly")
        self.cmb_std_status.set("Enrolled")
        self.cmb_std_status.grid(row=1, column=5, padx=8, pady=8)

        btn_box = ttk.Frame(form_grid, style="Card.TFrame")
        btn_box.grid(row=0, column=6, rowspan=2, padx=12, pady=8, sticky="e")

        btn_save = ttk.Button(btn_box, text="Save Student", style="Primary.TButton", command=self._save_student)
        btn_save.pack(side="top", pady=2, fill="x")

        btn_delete = ttk.Button(btn_box, text="Delete Student", style="Danger.TButton", command=self._delete_student)
        btn_delete.pack(side="top", pady=2, fill="x")

        table_frame = ttk.Frame(self.tab_student_mgmt, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("student_id", "first_name", "last_name", "program", "email", "status")
        self.tree_students = ttk.Treeview(table_frame, columns=columns, show="headings")

        headers = {
            "student_id": "Student ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "program": "Program",
            "email": "Email Address",
            "status": "Status"
        }

        for col_id, col_name in headers.items():
            self.tree_students.heading(col_id, text=col_name)
            self.tree_students.column(col_id, anchor="center" if col_id in ["student_id", "status", "program"] else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_students.yview)
        self.tree_students.configure(yscrollcommand=scrollbar.set)

        self.tree_students.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree_students.bind("<<TreeviewSelect>>", self._on_student_select)
        self._load_students_table()

    def _on_student_select(self, event):
        selected_item = self.tree_students.selection()
        if selected_item:
            item = self.tree_students.item(selected_item[0])
            vals = item['values']
            self.ent_std_id.delete(0, tk.END)
            self.ent_std_id.insert(0, vals[0])
            self.ent_std_first.delete(0, tk.END)
            self.ent_std_first.insert(0, vals[1])
            self.ent_std_last.delete(0, tk.END)
            self.ent_std_last.insert(0, vals[2])
            self.cmb_std_prog.set(vals[3])
            self.ent_std_email.delete(0, tk.END)
            self.ent_std_email.insert(0, vals[4])
            self.cmb_std_status.set(vals[5])

    def _save_student(self):
        s_id = self.ent_std_id.get().strip()
        f_name = self.ent_std_first.get().strip()
        l_name = self.ent_std_last.get().strip()
        prog = self.cmb_std_prog.get().strip()
        email = self.ent_std_email.get().strip()
        status = self.cmb_std_status.get().strip()

        if not s_id or not f_name or not l_name:
            messagebox.showwarning("Missing Data", "Student ID, First Name, and Last Name are required.")
            return

        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            messagebox.showwarning("Invalid Email", "Please enter a valid email address.")
            return

        try:
            new_student = Student(
                student_id=s_id,
                first_name=f_name,
                last_name=l_name,
                email=email,
                program=prog,
                status=status
            )
            self.student_repo.save(new_student)
            messagebox.showinfo("Success", f"Student '{s_id}' saved successfully!")
            self._load_students_table()
            self.refresh_student_dropdowns()

            self.ent_std_id.delete(0, tk.END)
            self.ent_std_first.delete(0, tk.END)
            self.ent_std_last.delete(0, tk.END)
            self.ent_std_email.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _delete_student(self):
        s_id = self.ent_std_id.get().strip()
        if not s_id:
            messagebox.showwarning("Missing ID", "Please select or enter a Student ID to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete student '{s_id}'?\nThis action cannot be undone.")
        if not confirm:
            return

        try:
            if hasattr(self.student_repo, 'delete'):
                self.student_repo.delete(s_id)
            else:
                from config.database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM student WHERE student_id = %s;", (s_id,))
                conn.commit()
                cursor.close()
                conn.close()

            messagebox.showinfo("Success", f"Student '{s_id}' deleted successfully!")
            self._load_students_table()
            self.refresh_student_dropdowns()

            self.ent_std_id.delete(0, tk.END)
            self.ent_std_first.delete(0, tk.END)
            self.ent_std_last.delete(0, tk.END)
            self.ent_std_email.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Delete Error", str(e))

    def _load_students_table(self):
        for row in self.tree_students.get_children():
            self.tree_students.delete(row)

        students = self.student_repo.find_all()
        for s in students:
            self.tree_students.insert("", "end", values=(s.student_id, s.first_name, s.last_name, s.program, s.email, s.status))

    # ------------------------------------------------------------------
    # TAB 2: TEACHER RECORDS MANAGEMENT
    # ------------------------------------------------------------------
    def _setup_teacher_mgmt_tab(self):
        form_frame = ttk.LabelFrame(self.tab_teacher_mgmt, text=" Add / Update Teacher Record ", style="Card.TLabelframe")
        form_frame.pack(fill="x", padx=15, pady=15)

        form_grid = ttk.Frame(form_frame, style="Card.TFrame")
        form_grid.pack(padx=15, pady=15, fill="x")

        ttk.Label(form_grid, text="Teacher ID:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.ent_tch_id = ttk.Entry(form_grid, width=15)
        self.ent_tch_id.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(form_grid, text="First Name:").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.ent_tch_first = ttk.Entry(form_grid, width=18)
        self.ent_tch_first.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(form_grid, text="Last Name:").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        self.ent_tch_last = ttk.Entry(form_grid, width=18)
        self.ent_tch_last.grid(row=0, column=5, padx=8, pady=8)

        ttk.Label(form_grid, text="Email:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.ent_tch_email = ttk.Entry(form_grid, width=18)
        self.ent_tch_email.grid(row=1, column=1, padx=8, pady=8)

        ttk.Label(form_grid, text="Department:").grid(row=1, column=2, padx=8, pady=8, sticky="w")
        self.ent_tch_dept = ttk.Entry(form_grid, width=18)
        self.ent_tch_dept.insert(0, "Computer Studies")
        self.ent_tch_dept.grid(row=1, column=3, padx=8, pady=8)

        btn_save_tch = ttk.Button(form_grid, text="Save Teacher", style="Primary.TButton", command=self._save_teacher)
        btn_save_tch.grid(row=1, column=5, padx=12, pady=8, sticky="e")

        table_frame = ttk.Frame(self.tab_teacher_mgmt, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("teacher_id", "first_name", "last_name", "email", "department")
        self.tree_teachers = ttk.Treeview(table_frame, columns=columns, show="headings")

        headers = {
            "teacher_id": "Teacher ID",
            "first_name": "First Name",
            "last_name": "Last Name",
            "email": "Email Address",
            "department": "Department"
        }

        for col_id, col_name in headers.items():
            self.tree_teachers.heading(col_id, text=col_name)
            self.tree_teachers.column(col_id, anchor="center" if col_id in ["teacher_id", "department"] else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_teachers.yview)
        self.tree_teachers.configure(yscrollcommand=scrollbar.set)

        self.tree_teachers.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree_teachers.bind("<<TreeviewSelect>>", self._on_teacher_select)
        self._load_teachers_table()

    def _on_teacher_select(self, event):
        selected_item = self.tree_teachers.selection()
        if selected_item:
            item = self.tree_teachers.item(selected_item[0])
            vals = item['values']
            self.ent_tch_id.delete(0, tk.END)
            self.ent_tch_id.insert(0, vals[0])
            self.ent_tch_first.delete(0, tk.END)
            self.ent_tch_first.insert(0, vals[1])
            self.ent_tch_last.delete(0, tk.END)
            self.ent_tch_last.insert(0, vals[2])
            self.ent_tch_email.delete(0, tk.END)
            self.ent_tch_email.insert(0, vals[3])
            self.ent_tch_dept.delete(0, tk.END)
            self.ent_tch_dept.insert(0, vals[4])

    def _save_teacher(self):
        t_id = self.ent_tch_id.get().strip()
        f_name = self.ent_tch_first.get().strip()
        l_name = self.ent_tch_last.get().strip()
        email = self.ent_tch_email.get().strip()
        dept = self.ent_tch_dept.get().strip()

        if not t_id or not f_name or not l_name:
            messagebox.showwarning("Missing Data", "Teacher ID, First Name, and Last Name are required.")
            return

        try:
            self.teacher_repo.save(t_id, f_name, l_name, email, dept)
            messagebox.showinfo("Success", f"Teacher '{t_id}' saved successfully!")
            self._load_teachers_table()
            self.refresh_teacher_dropdowns()

            self.ent_tch_id.delete(0, tk.END)
            self.ent_tch_first.delete(0, tk.END)
            self.ent_tch_last.delete(0, tk.END)
            self.ent_tch_email.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _load_teachers_table(self):
        for row in self.tree_teachers.get_children():
            self.tree_teachers.delete(row)

        try:
            if hasattr(self.teacher_repo, 'find_all'):
                teachers = self.teacher_repo.find_all()
                for t in teachers:
                    self.tree_teachers.insert("", "end", values=(t.teacher_id, t.first_name, t.last_name, t.email, t.department))
        except Exception as e:
            print("Error loading teachers table:", e)

    # ------------------------------------------------------------------
    # TAB 3: COURSE ENROLLMENT & DIRECT GRADE ENTRY
    # ------------------------------------------------------------------
    def _setup_enrollment_tab(self):
        offering_options = ["OFF001", "OFF002", "OFF003", "OFF004"]

        # Section A: Assign Teacher & Create Class Offering
        offering_frame = ttk.LabelFrame(self.tab_enrollment, text=" Assign Teacher to Class Offering ", style="Card.TLabelframe")
        offering_frame.pack(fill="x", padx=15, pady=10)

        grid_o = ttk.Frame(offering_frame, style="Card.TFrame")
        grid_o.pack(padx=15, pady=10, fill="x")

        ttk.Label(grid_o, text="Offering ID:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.ent_offering_id = ttk.Entry(grid_o, width=15)
        self.ent_offering_id.insert(0, "OFF001")
        self.ent_offering_id.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(grid_o, text="Assigned Teacher:").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.cmb_offering_teacher = ttk.Combobox(grid_o, width=25, state="readonly")
        self.cmb_offering_teacher.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(grid_o, text="Subject Code:").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        self.ent_offering_subject = ttk.Entry(grid_o, width=15)
        self.ent_offering_subject.insert(0, "CS101")
        self.ent_offering_subject.grid(row=0, column=5, padx=8, pady=8)

        btn_save_offering = ttk.Button(grid_o, text="Save Offering", style="Primary.TButton", command=self._save_offering_action)
        btn_save_offering.grid(row=0, column=6, padx=12, pady=8)

        # Section B: Enroll Student
        enroll_frame = ttk.LabelFrame(self.tab_enrollment, text=" Enroll Student in Course Offering ", style="Card.TLabelframe")
        enroll_frame.pack(fill="x", padx=15, pady=10)

        grid_e = ttk.Frame(enroll_frame, style="Card.TFrame")
        grid_e.pack(padx=15, pady=10, fill="x")

        ttk.Label(grid_e, text="Enrollment ID:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.ent_enr_id = ttk.Entry(grid_e, width=15)
        self.ent_enr_id.insert(0, "ENR003")
        self.ent_enr_id.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(grid_e, text="Student ID:").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.cmb_enr_student = ttk.Combobox(grid_e, width=13)
        self.cmb_enr_student.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(grid_e, text="Offering ID:").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        self.cmb_enr_offering = ttk.Combobox(grid_e, width=13, values=offering_options)
        self.cmb_enr_offering.set("OFF001")
        self.cmb_enr_offering.grid(row=0, column=5, padx=8, pady=8)

        btn_enroll = ttk.Button(grid_e, text="Enroll Student", style="Primary.TButton", command=self._enroll_student_action)
        btn_enroll.grid(row=0, column=6, padx=12, pady=8)

        # Section C: Direct Grade Update
        grade_frame = ttk.LabelFrame(self.tab_enrollment, text=" Directly Add / Update Student Grade ", style="Card.TLabelframe")
        grade_frame.pack(fill="x", padx=15, pady=10)

        grid_g = ttk.Frame(grade_frame, style="Card.TFrame")
        grid_g.pack(padx=15, pady=10, fill="x")

        ttk.Label(grid_g, text="Grade Record ID:").grid(row=0, column=0, padx=8, pady=8, sticky="w")
        self.ent_man_grade_id = ttk.Entry(grid_g, width=15)
        self.ent_man_grade_id.insert(0, "GRD003")
        self.ent_man_grade_id.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(grid_g, text="Student ID:").grid(row=0, column=2, padx=8, pady=8, sticky="w")
        self.cmb_man_student_id = ttk.Combobox(grid_g, width=13)
        self.cmb_man_student_id.grid(row=0, column=3, padx=8, pady=8)

        ttk.Label(grid_g, text="Offering ID:").grid(row=0, column=4, padx=8, pady=8, sticky="w")
        self.cmb_man_offering_id = ttk.Combobox(grid_g, width=13, values=offering_options)
        self.cmb_man_offering_id.set("OFF001")
        self.cmb_man_offering_id.grid(row=0, column=5, padx=8, pady=8)

        ttk.Label(grid_g, text="Period Name:").grid(row=1, column=0, padx=8, pady=8, sticky="w")
        self.cmb_man_period = ttk.Combobox(grid_g, width=13, values=["Midterm", "Finals", "Prelim", "Semi-Final"])
        self.cmb_man_period.set("Finals")
        self.cmb_man_period.grid(row=1, column=1, padx=8, pady=8)

        ttk.Label(grid_g, text="Final Grade (%):").grid(row=1, column=2, padx=8, pady=8, sticky="w")
        self.ent_man_score = ttk.Entry(grid_g, width=15)
        self.ent_man_score.insert(0, "92.5")
        self.ent_man_score.grid(row=1, column=3, padx=8, pady=8)

        ttk.Label(grid_g, text="Remarks:").grid(row=1, column=4, padx=8, pady=8, sticky="w")
        self.cmb_man_remarks = ttk.Combobox(grid_g, width=13, values=["Passed", "Failed", "Incomplete", "Dropped"])
        self.cmb_man_remarks.set("Passed")
        self.cmb_man_remarks.grid(row=1, column=5, padx=8, pady=8)

        btn_save_grade = ttk.Button(grid_g, text="Save Grade", style="Primary.TButton", command=self._save_direct_grade_action)
        btn_save_grade.grid(row=1, column=6, padx=12, pady=8)

    def _save_offering_action(self):
        off_id = self.ent_offering_id.get().strip()
        teacher_str = self.cmb_offering_teacher.get().strip()
        subject_id = self.ent_offering_subject.get().strip()

        if not off_id or not teacher_str or not subject_id:
            messagebox.showwarning("Missing Information", "Offering ID, Assigned Teacher, and Subject Code are required.")
            return

        teacher_id = teacher_str.split(" - ")[0] if " - " in teacher_str else teacher_str

        try:
            if hasattr(self.enrolment_repo, 'save_offering'):
                self.enrolment_repo.save_offering(
                    offering_id=off_id,
                    teacher_id=teacher_id,
                    subject_id=subject_id
                )
            else:
                from config.database import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO classoffering (
                        offering_id, class_code, schedule, school_year, semester, teacher_id, subject_id
                    )
                    VALUES (%s, %s, 'TBA', '2025-2026', '1st', %s, %s)
                    ON CONFLICT (offering_id) DO UPDATE SET
                        teacher_id = EXCLUDED.teacher_id,
                        subject_id = EXCLUDED.subject_id;
                """, (off_id, off_id, teacher_id, subject_id))
                conn.commit()
                cursor.close()
                conn.close()

            self.refresh_offering_comboboxes()
            messagebox.showinfo("Success", f"Class Offering '{off_id}' saved successfully!")
        except Exception as e:
            messagebox.showerror("Offering Error", str(e))

    def _enroll_student_action(self):
        enr_id = self.ent_enr_id.get().strip()
        std_id = self.cmb_enr_student.get().strip()
        off_id = self.cmb_enr_offering.get().strip()

        if not enr_id or not std_id or not off_id:
            messagebox.showwarning("Missing Information", "Enrollment ID, Student ID, and Offering ID are required.")
            return

        try:
            self.enrolment_repo.enroll_student(enr_id, std_id, off_id)
            self.refresh_offering_comboboxes()
            messagebox.showinfo("Success", f"Student '{std_id}' enrolled into '{off_id}' successfully!")
        except Exception as e:
            messagebox.showerror("Enrollment Error", str(e))

    def _save_direct_grade_action(self):
        grade_id = self.ent_man_grade_id.get().strip()
        std_id = self.cmb_man_student_id.get().strip()
        off_id = self.cmb_man_offering_id.get().strip()
        period = self.cmb_man_period.get().strip()

        try:
            score = float(self.ent_man_score.get().strip())
        except ValueError:
            messagebox.showwarning("Invalid Score", "Please enter a valid numeric grade percentage.")
            return

        remarks = self.cmb_man_remarks.get().strip()

        try:
            from config.database import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Find the enrollment_id linking this student to the course offering
            cursor.execute("SELECT enrollment_id FROM enrollment WHERE student_id = %s AND offering_id = %s;", (std_id, off_id))
            row = cursor.fetchone()

            # Map period name to period_id
            period_id = 'PRD002' if period.lower() in ['finals', 'final'] else 'PRD001'

            if not row:
                raise ValueError(f"No active enrollment found for Student '{std_id}' in Offering '{off_id}'. Please enroll them first.")

            enrollment_id = row[0]
            cursor.close()
            conn.close()

            # Save via grade repository
            self.grade_repo.save_or_update_grade(grade_id, enrollment_id, period_id, score, remarks)
            messagebox.showinfo("Success", f"Grade record '{grade_id}' updated successfully for student '{std_id}'!")
        except Exception as e:
            messagebox.showerror("Grade Error", str(e))

    # ------------------------------------------------------------------
    # TAB 4: GRADE COMPUTATION
    # ------------------------------------------------------------------
    def _setup_grade_entry_tab(self):
        frame = ttk.LabelFrame(self.tab_grade_entry, text=" Compute & Save Period Grade ", style="Card.TLabelframe")
        frame.pack(padx=30, pady=30, fill="x")

        inner_frame = ttk.Frame(frame, style="Card.TFrame")
        inner_frame.pack(padx=20, pady=20)

        ttk.Label(inner_frame, text="Grade ID (e.g., GRD001):").grid(row=0, column=0, padx=12, pady=12, sticky="e")
        self.ent_grade_id = ttk.Entry(inner_frame, width=20)
        self.ent_grade_id.insert(0, "GRD001")
        self.ent_grade_id.grid(row=0, column=1, padx=12, pady=12)

        ttk.Label(inner_frame, text="Offering ID:").grid(row=1, column=0, padx=12, pady=12, sticky="e")
        self.cmb_offering_id_calc = ttk.Combobox(inner_frame, width=18, values=["OFF001", "OFF002", "OFF003", "OFF004"])
        self.cmb_offering_id_calc.set("OFF001")
        self.cmb_offering_id_calc.grid(row=1, column=1, padx=12, pady=12)

        btn_calc = ttk.Button(inner_frame, text="Calculate & Save Grade", style="Primary.TButton", command=self._handle_grade_calculation)
        btn_calc.grid(row=2, column=0, columnspan=2, pady=20)

        self.lbl_calc_result = ttk.Label(inner_frame, text="", font=("Segoe UI", 11, "bold"))
        self.lbl_calc_result.grid(row=3, column=0, columnspan=2, pady=5)

    def _handle_grade_calculation(self):
        grade_id = self.ent_grade_id.get().strip()
        offering_id = self.cmb_offering_id_calc.get().strip()

        try:
            # Fetch student_id associated with this grade_id first
            student_id = self.grade_repository.get_student_id_by_grade_id(grade_id)

            # Pass all 3 arguments: grade_id, student_id, offering_id
            res = self.grading_service.calculate_and_save_period_grade(grade_id, student_id, offering_id)

            self.lbl_calc_result.config(text=f"Success! Calculated Final Grade: {res:.2f}%", foreground="#10B981")
            messagebox.showinfo(title="Success", message=f"Grade updated successfully!\nComputed Grade: {res:.2f}%")
        except Exception as e:
            self.lbl_calc_result.config(text=f"Error: {str(e)}", foreground="#EF4444")
            messagebox.showerror(title="Calculation Error", message=str(e))

    # ------------------------------------------------------------------
    # TAB 5: CLASS LIST REPORT
    # ------------------------------------------------------------------
    def _setup_class_list_tab(self):
        filter_frame = ttk.Frame(self.tab_class_list, style="Card.TFrame")
        filter_frame.pack(fill="x", padx=15, pady=15)

        ttk.Label(filter_frame, text="Select Offering ID:").pack(side="left", padx=8)
        self.cmb_offering_class = ttk.Combobox(filter_frame, width=15)
        self.cmb_offering_class.pack(side="left", padx=8)

        btn_fetch = ttk.Button(filter_frame, text="Generate Class List", style="Primary.TButton", command=self._generate_class_list)
        btn_fetch.pack(side="left", padx=12)

        table_frame = ttk.Frame(self.tab_class_list, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("student_id", "name", "program", "email", "status")
        self.tree_class_list = ttk.Treeview(table_frame, columns=columns, show="headings")

        headers = {
            "student_id": "Student ID",
            "name": "Student Name",
            "program": "Program",
            "email": "Email Address",
            "status": "Status"
        }

        for col_id, col_name in headers.items():
            self.tree_class_list.heading(col_id, text=col_name)
            self.tree_class_list.column(col_id, anchor="center" if col_id in ["student_id", "program", "status"] else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_class_list.yview)
        self.tree_class_list.configure(yscrollcommand=scrollbar.set)

        self.tree_class_list.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _generate_class_list(self):
        offering_id = self.cmb_offering_class.get().strip()
        if not offering_id:
            messagebox.showwarning("Missing Offering ID", "Please select an Offering ID.")
            return

        for row in self.tree_class_list.get_children():
            self.tree_class_list.delete(row)

        try:
            students = self.report_service.get_class_list(offering_id)
            for s in students:
                name = f"{s.get('first_name', '')} {s.get('last_name', '')}".strip()
                self.tree_class_list.insert("", "end", values=(
                    s.get("student_id", ""),
                    name,
                    s.get("program", ""),
                    s.get("email", ""),
                    s.get("status", "")
                ))
        except Exception as e:
            messagebox.showerror("Report Error", str(e))

    # ------------------------------------------------------------------
    # TAB 6: CLASS GRADE SHEET
    # ------------------------------------------------------------------
    def _setup_grade_sheet_tab(self):
        filter_frame = ttk.Frame(self.tab_grade_sheet, style="Card.TFrame")
        filter_frame.pack(fill="x", padx=15, pady=15)

        ttk.Label(filter_frame, text="Select Offering ID:").pack(side="left", padx=8)
        self.cmb_offering_sheet = ttk.Combobox(filter_frame, width=15)
        self.cmb_offering_sheet.pack(side="left", padx=8)

        btn_fetch = ttk.Button(filter_frame, text="Generate Grade Sheet", style="Primary.TButton", command=self._generate_grade_sheet)
        btn_fetch.pack(side="left", padx=12)

        table_frame = ttk.Frame(self.tab_grade_sheet, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("student_id", "name", "period", "final_grade", "remarks")
        self.tree_grade_sheet = ttk.Treeview(table_frame, columns=columns, show="headings")

        headers = {
            "student_id": "Student ID",
            "name": "Student Name",
            "period": "Period",
            "final_grade": "Final Grade (%)",
            "remarks": "Remarks"
        }

        for col_id, col_name in headers.items():
            self.tree_grade_sheet.heading(col_id, text=col_name)
            self.tree_grade_sheet.column(col_id, anchor="center" if col_id in ["student_id", "period", "final_grade", "remarks"] else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_grade_sheet.yview)
        self.tree_grade_sheet.configure(yscrollcommand=scrollbar.set)

        self.tree_grade_sheet.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _generate_grade_sheet(self):
        offering_id = self.cmb_offering_sheet.get().strip()
        if not offering_id:
            messagebox.showwarning("Missing Offering ID", "Please select an Offering ID.")
            return

        for row in self.tree_grade_sheet.get_children():
            self.tree_grade_sheet.delete(row)

        try:
            grades = self.report_service.get_class_grade_sheet(offering_id)
            for g in grades:
                name = f"{g.get('first_name', '')} {g.get('last_name', '')}".strip()
                score = g.get("final_grade")
                score_str = f"{float(score):.2f}%" if score is not None else "N/A"

                self.tree_grade_sheet.insert("", "end", values=(
                    g.get("student_id", ""),
                    name,
                    g.get("period_name", "N/A"),
                    score_str,
                    g.get("remarks", "N/A")
                ))
        except Exception as e:
            messagebox.showerror("Report Error", str(e))

    # ------------------------------------------------------------------
    # TAB 7: STUDENT GRADE REPORT
    # ------------------------------------------------------------------
    def _setup_student_report_tab(self):
        filter_frame = ttk.Frame(self.tab_student_report, style="Card.TFrame")
        filter_frame.pack(fill="x", padx=15, pady=15)

        ttk.Label(filter_frame, text="Select Student ID:").pack(side="left", padx=8)
        self.cmb_report_student_id = ttk.Combobox(filter_frame, width=15)
        self.cmb_report_student_id.pack(side="left", padx=8)

        btn_fetch = ttk.Button(filter_frame, text="Generate Student Report", style="Primary.TButton", command=self._generate_student_report)
        btn_fetch.pack(side="left", padx=12)

        table_frame = ttk.Frame(self.tab_student_report, style="Card.TFrame")
        table_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        columns = ("offering_id", "subject_code", "period", "final_grade", "remarks")
        self.tree_student_report = ttk.Treeview(table_frame, columns=columns, show="headings")

        headers = {
            "offering_id": "Offering ID",
            "subject_code": "Subject Code",
            "period": "Period",
            "final_grade": "Final Grade (%)",
            "remarks": "Remarks"
        }

        for col_id, col_name in headers.items():
            self.tree_student_report.heading(col_id, text=col_name)
            self.tree_student_report.column(col_id, anchor="center" if col_id in ["offering_id", "subject_code", "period", "final_grade", "remarks"] else "w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_student_report.yview)
        self.tree_student_report.configure(yscrollcommand=scrollbar.set)

        self.tree_student_report.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _generate_student_report(self):
        student_id = self.cmb_report_student_id.get().strip()
        if not student_id:
            messagebox.showwarning("Missing Student ID", "Please select a Student ID.")
            return

        for row in self.tree_student_report.get_children():
            self.tree_student_report.delete(row)

        try:
            records = self.report_service.get_student_grade_report(student_id)
            for r in records:
                score = r.get("final_grade")
                score_str = f"{float(score):.2f}%" if score is not None else "N/A"

                self.tree_student_report.insert("", "end", values=(
                    r.get("offering_id", ""),
                    r.get("subject_code", "N/A"),
                    r.get("period_name", "N/A"),
                    score_str,
                    r.get("remarks", "N/A")
                ))
        except Exception as e:
            messagebox.showerror("Report Error", str(e))


if __name__ == "__main__":
    app = GradeManagementGUI()
    app.mainloop()