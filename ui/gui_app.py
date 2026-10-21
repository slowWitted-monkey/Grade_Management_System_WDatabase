"""Modern dark dashboard for the student information and grading system."""

import tkinter as tk
from tkinter import messagebox, ttk

import customtkinter as ctk

from config.database import get_db_connection
from repository.grade_repository import GradeRepository
from service.grading_service import GradingService
from service.report_service import ReportService


class GradeManagementGUI(ctk.CTk):
    """A dark, developer-inspired desktop UI backed by the existing services."""

    BG = "#0b1020"
    PANEL = "#111a2e"
    CARD = "#151f35"
    CARD_HOVER = "#1b2944"
    BORDER = "#263550"
    TEXT = "#e7eefc"
    MUTED = "#8da0bf"
    BLUE = "#4f8cff"
    CYAN = "#39d6d0"
    GREEN = "#32d296"
    AMBER = "#f3b94f"
    RED = "#fa7185"

    TABLES = {
        "Students": ("student", "student_id", ["student_id", "first_name", "last_name", "program", "year_level", "email", "status"]),
        "Teachers": ("teacher", "teacher_id", ["teacher_id", "first_name", "last_name", "email", "department", "status"]),
        "Subjects": ("subject", "subject_id", ["subject_id", "subject_code", "subject_name", "description", "units"]),
        "Classes": ("class_offering", "class_id", ["class_id", "class_code", "subject_id", "teacher_id", "section", "school_year", "semester", "schedule", "room"]),
        "Enrollments": ("enrollment", "enrollment_id", ["enrollment_id", "student_id", "class_id", "status"]),
        "Grading Periods": ("grading_period", "period_id", ["period_id", "name", "period_order", "start_date", "end_date", "school_year", "semester"]),
        "Grade Components": ("grade_component", "component_id", ["component_id", "period_id", "name", "type", "max_score", "description"]),
    }

    NAV_ITEMS = [
        ("Overview", "overview"),
        ("Students", "Students"),
        ("Teachers", "Teachers"),
        ("Subjects", "Subjects"),
        ("Classes", "Classes"),
        ("Enrollments", "Enrollments"),
        ("Grading Periods", "Grading Periods"),
        ("Grade Components", "Grade Components"),
        ("Grade Weights", "weights"),
        ("Score Entry", "scores"),
        ("Compute & Reports", "reports"),
    ]

    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("Grade Management System  |  Academic Workspace")
        self.geometry("1450x900")
        self.minsize(1120, 720)
        self.configure(fg_color=self.BG)

        self.grade_repo = GradeRepository()
        self.grading_service = GradingService(self.grade_repo)
        self.report_service = ReportService()
        self.status = tk.StringVar(value="Checking database…")
        self._configure_tree_style()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_workspace()
        self.show_dashboard()
        self.after(250, self.check_database)

    def _configure_tree_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=self.PANEL, fieldbackground=self.PANEL,
                        foreground=self.TEXT, rowheight=34, borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=self.CARD, foreground=self.MUTED,
                        relief="flat", borderwidth=0, font=("Segoe UI Semibold", 9))
        style.map("Treeview", background=[("selected", "#254b7e")],
                  foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading", background=[("active", self.CARD_HOVER)])

    def _build_sidebar(self):
        side = ctk.CTkFrame(self, width=244, corner_radius=0, fg_color=self.PANEL,
                            border_width=0)
        side.grid(row=0, column=0, sticky="nsew")
        side.grid_propagate(False)
        side.grid_rowconfigure(2, weight=1)

        brand = ctk.CTkFrame(side, fg_color="transparent")
        brand.pack(fill="x", padx=20, pady=(25, 28))
        badge = ctk.CTkFrame(brand, width=42, height=42, corner_radius=12,
                             fg_color=self.BLUE)
        badge.pack(side="left", padx=(0, 12))
        badge.pack_propagate(False)
        ctk.CTkLabel(badge, text="SG", text_color="white",
                     font=ctk.CTkFont(family="Consolas", size=15, weight="bold")).pack(expand=True)
        brand_text = ctk.CTkFrame(brand, fg_color="transparent")
        brand_text.pack(side="left", fill="y")
        ctk.CTkLabel(brand_text, text="GRADE // SYSTEM", text_color=self.TEXT,
                     font=ctk.CTkFont(family="Consolas", size=13, weight="bold")).pack(anchor="w", pady=(2, 1))
        ctk.CTkLabel(brand_text, text="ACADEMIC WORKSPACE", text_color=self.MUTED,
                     font=ctk.CTkFont(size=9, weight="bold")).pack(anchor="w")

        ctk.CTkLabel(side, text="WORKSPACE", text_color="#607390",
                     font=ctk.CTkFont(family="Consolas", size=10, weight="bold"))\
            .pack(anchor="w", padx=22, pady=(0, 9))
        nav = ctk.CTkScrollableFrame(side, fg_color="transparent", corner_radius=0,
                                     scrollbar_button_color=self.BORDER,
                                     scrollbar_button_hover_color=self.MUTED)
        nav.pack(fill="both", expand=True, padx=10)
        self.nav_buttons = {}
        for label, key in self.NAV_ITEMS:
            button = ctk.CTkButton(
                nav, text=label, anchor="w", height=38, corner_radius=9,
                fg_color="transparent", hover_color=self.CARD_HOVER,
                text_color=self.MUTED, font=ctk.CTkFont(size=12, weight="normal"),
                command=lambda target=key: self.navigate(target),
            )
            button.pack(fill="x", pady=2)
            self.nav_buttons[key] = button

        footer = ctk.CTkFrame(side, fg_color="transparent")
        footer.pack(fill="x", padx=20, pady=17)
        ctk.CTkFrame(footer, height=1, fg_color=self.BORDER).pack(fill="x", pady=(0, 12))
        ctk.CTkLabel(footer, text="LOCAL POSTGRESQL", text_color=self.MUTED,
                     font=ctk.CTkFont(family="Consolas", size=9, weight="bold")).pack(anchor="w")
        self.side_status = ctk.CTkLabel(footer, textvariable=self.status,
                                        text_color=self.AMBER, font=ctk.CTkFont(size=10),
                                        wraplength=195, justify="left")
        self.side_status.pack(anchor="w", pady=(5, 0))

    def _build_workspace(self):
        workspace = ctk.CTkFrame(self, fg_color=self.BG, corner_radius=0)
        workspace.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(workspace, fg_color=self.BG, corner_radius=0,
                              height=88, border_width=0)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 12))
        header.grid_columnconfigure(0, weight=1)
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(title_box, text="ACADEMIC DATA / LOCAL INSTANCE", text_color=self.CYAN,
                     font=ctk.CTkFont(family="Consolas", size=10, weight="bold")).pack(anchor="w")
        self.page_title = ctk.CTkLabel(title_box, text="Overview", text_color=self.TEXT,
                                       font=ctk.CTkFont(size=25, weight="bold"))
        self.page_title.pack(anchor="w", pady=(4, 0))
        self.db_badge = ctk.CTkLabel(header, text="●  CHECKING", text_color=self.AMBER,
                                     fg_color=self.CARD, corner_radius=18, width=170, height=36,
                                     font=ctk.CTkFont(family="Consolas", size=10, weight="bold"))
        self.db_badge.grid(row=0, column=1, sticky="e", padx=(12, 9))
        ctk.CTkButton(header, text="↻", width=40, height=38, corner_radius=10,
                      fg_color=self.CARD, hover_color=self.CARD_HOVER,
                      text_color=self.CYAN, font=ctk.CTkFont(size=19, weight="bold"),
                      command=self.check_database).grid(row=0, column=2, sticky="e")

        self.content = ctk.CTkFrame(workspace, fg_color="transparent", corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 24))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    def navigate(self, target):
        if target == "overview":
            self.show_dashboard()
        elif target in self.TABLES:
            self.show_crud_page(target)
        elif target == "weights":
            self.show_weights_page()
        elif target == "scores":
            self.show_scores_page()
        elif target == "reports":
            self.show_reports_page()

    def _highlight_nav(self, key):
        for item, button in self.nav_buttons.items():
            active = item == key
            button.configure(fg_color="#1b3152" if active else "transparent",
                             text_color=self.CYAN if active else self.MUTED,
                             border_width=1 if active else 0,
                             border_color="#2f5b92")

    def _set_page(self, title, nav_key):
        for child in self.content.winfo_children():
            child.destroy()
        self.page_title.configure(text=title)
        self._highlight_nav(nav_key)
        self.content.grid_rowconfigure(0, weight=0)

    def _section_intro(self, parent, heading, detail):
        ctk.CTkLabel(parent, text=heading, text_color=self.TEXT,
                     font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(parent, text=detail, text_color=self.MUTED,
                     font=ctk.CTkFont(size=11), wraplength=900,
                     justify="left").pack(anchor="w", pady=(4, 14))

    def show_dashboard(self):
        self._set_page("Overview", "overview")
        page = ctk.CTkScrollableFrame(self.content, fg_color="transparent",
                                      scrollbar_button_color=self.BORDER)
        page.grid(row=0, column=0, sticky="nsew")
        for col in range(4):
            page.grid_columnconfigure(col, weight=1, uniform="metric")
        ctk.CTkLabel(page, text="Your grading workspace, at a glance.",
                     text_color=self.MUTED, font=ctk.CTkFont(size=13))\
            .grid(row=0, column=0, columnspan=4, sticky="w", pady=(5, 18))

        metrics = [("STUDENTS", "student", self.BLUE),
                   ("TEACHERS", "teacher", self.CYAN),
                   ("CLASSES", "class_offering", self.GREEN),
                   ("ENROLLMENTS", "enrollment", self.AMBER)]
        for col, (label, table, accent) in enumerate(metrics):
            card = ctk.CTkFrame(page, fg_color=self.CARD, corner_radius=14,
                                border_width=1, border_color=self.BORDER)
            card.grid(row=1, column=col, sticky="ew", padx=(0 if col == 0 else 8, 0), pady=(0, 17))
            ctk.CTkLabel(card, text="▰  " + label, text_color=self.MUTED,
                         font=ctk.CTkFont(family="Consolas", size=10, weight="bold"))\
                .pack(anchor="w", padx=16, pady=(15, 2))
            value = self._count(table)
            ctk.CTkLabel(card, text=value, text_color=accent,
                         font=ctk.CTkFont(family="Consolas", size=29, weight="bold"))\
                .pack(anchor="w", padx=16, pady=(2, 14))

        info = ctk.CTkFrame(page, fg_color=self.CARD, corner_radius=14,
                            border_width=1, border_color=self.BORDER)
        info.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(0, 8), pady=(0, 12))
        ctk.CTkLabel(info, text="// GET STARTED", text_color=self.CYAN,
                     font=ctk.CTkFont(family="Consolas", size=11, weight="bold"))\
            .pack(anchor="w", padx=20, pady=(18, 5))
        ctk.CTkLabel(info, text="Build your class data in a simple sequence:",
                     text_color=self.TEXT, font=ctk.CTkFont(size=15, weight="bold"))\
            .pack(anchor="w", padx=20, pady=(0, 12))
        steps = ["01   Add students, teachers, and subjects",
                 "02   Create class offerings, then enroll students",
                 "03   Set periods, components, and weights",
                 "04   Enter scores, compute grades, view reports"]
        for step in steps:
            ctk.CTkLabel(info, text=step, text_color=self.MUTED,
                         font=ctk.CTkFont(family="Consolas", size=11))\
                .pack(anchor="w", padx=22, pady=5)
        ctk.CTkFrame(info, fg_color="transparent", height=10).pack()

        quick = ctk.CTkFrame(page, fg_color=self.CARD, corner_radius=14,
                             border_width=1, border_color=self.BORDER)
        quick.grid(row=2, column=2, columnspan=2, sticky="nsew", padx=(8, 0), pady=(0, 12))
        ctk.CTkLabel(quick, text="// QUICK NAVIGATION", text_color=self.CYAN,
                     font=ctk.CTkFont(family="Consolas", size=11, weight="bold"))\
            .pack(anchor="w", padx=20, pady=(18, 12))
        for label, key in (("Open Students", "Students"), ("Open Classes", "Classes"),
                           ("Configure Grade Weights", "weights"), ("Compute & Reports", "reports")):
            ctk.CTkButton(quick, text=label + "   →", anchor="w", height=37,
                          fg_color="transparent", hover_color=self.CARD_HOVER,
                          text_color=self.TEXT, corner_radius=8,
                          command=lambda target=key: self.navigate(target))\
                .pack(fill="x", padx=12, pady=2)
        self.content.grid_rowconfigure(0, weight=1)

    def _count(self, table):
        try:
            rows = self._query(f"SELECT COUNT(*) FROM {table}")
            return str(rows[0][0])
        except Exception:
            return "—"

    def _db(self):
        return get_db_connection()

    def _query(self, sql, params=(), fetch=True):
        conn = self._db()
        try:
            with conn.cursor() as cur:
                cur.execute(sql, params)
                result = cur.fetchall() if fetch else None
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _reference_options(self, kind):
        """Return database-backed (stored value, display label) choices."""
        common_values = {
            "program": ["BSCS", "BSIT"],
            "department": ["Computer Studies Department", "Information Technology Department",
                           "Physical Education Department"],
        }
        if kind in common_values:
            table = "student" if kind == "program" else "teacher"
            try:
                rows = self._query(
                    f"SELECT DISTINCT {kind} FROM {table} WHERE {kind} IS NOT NULL "
                    f"AND btrim({kind}) <> '' ORDER BY {kind}"
                )
                values = {str(row[0]) for row in rows}
            except Exception:
                values = set()
            values.update(common_values[kind])
            return [(value, value) for value in sorted(values, key=str.casefold)]
        queries = {
            "student": """SELECT student_id, student_id || ' — ' || first_name || ' ' || last_name
                FROM student ORDER BY last_name, first_name""",
            "teacher": """SELECT teacher_id, teacher_id || ' — ' || first_name || ' ' || last_name
                FROM teacher ORDER BY last_name, first_name""",
            "subject": """SELECT subject_id, subject_code || ' — ' || subject_name
                FROM subject ORDER BY subject_code""",
            "class": """SELECT co.class_id, co.class_code || ' — ' || s.subject_code || ' / Section ' || co.section
                || ' / ' || co.school_year || ' ' || co.semester
                FROM class_offering co JOIN subject s USING(subject_id) ORDER BY co.class_code""",
            "period": """SELECT period_id, name || ' — ' || school_year || ' ' || semester
                FROM grading_period ORDER BY school_year, semester, period_order""",
            "component": """SELECT gc.component_id, gc.component_id::text || ' — ' || gc.name || ' / ' || gp.name || ' (' || gc.max_score || ' max)'
                FROM grade_component gc JOIN grading_period gp USING(period_id)
                ORDER BY gp.school_year, gp.semester, gp.period_order, gc.component_id""",
            "enrollment": """SELECT e.enrollment_id, e.enrollment_id::text || ' — ' || st.student_id || ' '
                || st.first_name || ' ' || st.last_name || ' / ' || co.class_code
                FROM enrollment e JOIN student st USING(student_id)
                JOIN class_offering co USING(class_id) ORDER BY st.last_name, st.first_name, co.class_code""",
        }
        if kind in {"active_class"}:
            query = queries["class"].replace("FROM class_offering co JOIN subject s USING(subject_id)",
                "FROM class_offering co JOIN subject s USING(subject_id) WHERE EXISTS "
                "(SELECT 1 FROM enrollment e WHERE e.class_id=co.class_id AND e.status='Enrolled')")
        else:
            query = queries.get(kind)
        if not query:
            return []
        try:
            return [(str(value), str(label)) for value, label in self._query(query)]
        except Exception:
            return []

    def _choice_definitions(self, table):
        """Map form fields to database choices or fixed, validated options."""
        foreign_keys = {
            ("class_offering", "subject_id"): "subject",
            ("class_offering", "teacher_id"): "teacher",
            ("enrollment", "student_id"): "student",
            ("enrollment", "class_id"): "class",
            ("grade_component", "period_id"): "period",
        }
        definitions = {}
        if table == "student":
            definitions["program"] = self._reference_options("program")
        elif table == "teacher":
            definitions["department"] = self._reference_options("department")
        for (owner, field), reference in foreign_keys.items():
            if owner == table:
                definitions[field] = self._reference_options(reference)
        if table in {"student", "teacher"}:
            definitions["status"] = [("Active", "Active"), ("Inactive", "Inactive")]
        elif table == "enrollment":
            definitions["status"] = [("Enrolled", "Enrolled"), ("Dropped", "Dropped"), ("Completed", "Completed")]
        elif table == "grade_component":
            definitions["type"] = [(value, value) for value in ("Quiz", "Assignment", "Laboratory", "Project", "Exam", "Other")]
        elif table == "class_offering":
            definitions["semester"] = [("1st", "1st Semester"), ("2nd", "2nd Semester"), ("Summer", "Summer")]
        if table == "student":
            definitions["year_level"] = [(str(n), f"{n} — {n}{'st' if n == 1 else 'nd' if n == 2 else 'rd' if n == 3 else 'th'} year") for n in range(1, 9)]
        return definitions

    def _make_combo(self, parent, options, *, default=None, width=None, height=35, editable=False):
        """Create a dropdown and a display-label-to-stored-value map."""
        label_to_value = {label: value for value, label in options}
        placeholder = "Choose an available record"
        values = [placeholder] + list(label_to_value)
        combo = ctk.CTkComboBox(
            parent, values=values, state="normal" if editable else "readonly", height=height,
            width=width or 220, fg_color="#0e1729", border_color=self.BORDER,
            button_color=self.BLUE, dropdown_fg_color=self.PANEL,
        )
        label_to_value[placeholder] = None
        chosen = next((label for value, label in options if str(value) == str(default)), placeholder)
        combo.set(chosen)
        return combo, label_to_value

    def check_database(self):
        try:
            conn = self._db()
            conn.close()
            self.status.set("Connected")
            self.side_status.configure(text_color=self.GREEN)
            self.db_badge.configure(text="●  DATABASE ONLINE", text_color=self.GREEN)
        except Exception as exc:
            self.status.set("Not connected — check .env")
            self.side_status.configure(text_color=self.AMBER)
            self.db_badge.configure(text="●  DATABASE OFFLINE", text_color=self.AMBER)

    def _show_error(self, error):
        sqlstate = getattr(error, "pgcode", None)
        if sqlstate == "23505":
            message = "A record with that ID or unique code already exists. Please use a different value."
        elif sqlstate == "23503":
            message = "This record is linked to other records and cannot be removed while they depend on it."
        else:
            message = str(error)
        messagebox.showerror("Unable to complete action", message, parent=self)

    def _guard(self, action):
        try:
            action()
        except Exception as exc:
            self._show_error(exc)

    def _card(self, parent, title):
        card = ctk.CTkFrame(parent, fg_color=self.CARD, corner_radius=13,
                            border_width=1, border_color=self.BORDER)
        ctk.CTkLabel(card, text=title, text_color=self.TEXT,
                     font=ctk.CTkFont(size=13, weight="bold"))\
            .pack(anchor="w", padx=16, pady=(14, 4))
        return card

    def _add_crud_page(self, title):
        table, key, fields = self.TABLES[title]
        self._set_page(title, title)
        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)
        subtitle = {
            "Students": "Maintain student identities and program information.",
            "Teachers": "Manage teaching staff and department records.",
            "Subjects": "Define the courses used by class offerings.",
            "Classes": "Connect a subject, teacher, section, and academic term.",
            "Enrollments": "Register students in a class offering.",
            "Grading Periods": "Set the academic periods used for grade calculations.",
            "Grade Components": "Add quizzes, assignments, exams, and other score categories.",
        }.get(title, "Manage project records.")
        self._section_intro(page, "Manage " + title.lower(), subtitle)

        form = self._card(page, "RECORD DETAILS  /  ADD OR UPDATE")
        form.pack(fill="x", pady=(0, 12))
        grid = ctk.CTkFrame(form, fg_color="transparent")
        grid.pack(fill="x", padx=13, pady=(6, 13))
        column_count = 4
        for col in range(column_count):
            grid.grid_columnconfigure(col, weight=1, uniform="fields")
        widgets = {}
        choice_maps = {}
        choice_definitions = self._choice_definitions(table)
        editable_choices = {"program", "department"}
        auto_keys = {"subject_id", "class_id", "enrollment_id", "period_id", "component_id"}
        field_defaults = {
            "student": {"status": "Active"},
            "teacher": {"status": "Active"},
            "enrollment": {"status": "Enrolled"},
        }.get(table, {})
        for index, field in enumerate(fields):
            row, col = divmod(index, column_count)
            cell = ctk.CTkFrame(grid, fg_color="transparent")
            cell.grid(row=row, column=col, sticky="ew", padx=5, pady=5)
            label = field.replace("_", " ").title()
            if field == key and field in auto_keys:
                label += "  /  AUTO"
            ctk.CTkLabel(cell, text=label, text_color=self.MUTED,
                         font=ctk.CTkFont(size=10, weight="bold"))\
                .pack(anchor="w", padx=2, pady=(0, 5))
            if field in choice_definitions:
                entry, choice_maps[field] = self._make_combo(
                    cell, choice_definitions[field], default=field_defaults.get(field), height=35,
                    editable=field in editable_choices)
            else:
                entry = ctk.CTkEntry(cell, height=35, corner_radius=8,
                                     fg_color="#0e1729", border_color=self.BORDER,
                                     text_color=self.TEXT, placeholder_text="Enter " + field.replace("_", " "))
            entry.pack(fill="x")
            if field in field_defaults and field not in choice_maps:
                entry.insert(0, field_defaults[field])
            if field == key and field in auto_keys:
                entry.configure(state="disabled", placeholder_text="Generated by database")
            widgets[field] = entry

        tree_card = self._card(page, "RECORDS  /  SELECT A ROW TO EDIT")
        tree_card.pack(fill="both", expand=True)
        search_row = ctk.CTkFrame(tree_card, fg_color="transparent")
        search_row.pack(fill="x", padx=12, pady=(6, 4))
        search_entry = ctk.CTkEntry(
            search_row, width=300, height=34, fg_color="#0e1729",
            border_color=self.BORDER, placeholder_text=f"Search {title.lower()}...",
        )
        search_entry.pack(side="left", padx=(0, 7))
        controls = ctk.CTkFrame(tree_card, fg_color="transparent")
        controls.pack(fill="x", padx=12, pady=(6, 10))
        columns = tuple(fields)
        tree_wrap = ctk.CTkFrame(tree_card, fg_color=self.PANEL, corner_radius=9)
        tree_wrap.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        tree = ttk.Treeview(tree_wrap, columns=columns, show="headings", height=11)
        for field in fields:
            tree.heading(field, text=field.replace("_", " ").upper())
            tree.column(field, width=max(105, min(185, 1120 // len(fields))), anchor="w")
        tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)
        ybar = ttk.Scrollbar(tree_wrap, orient="vertical", command=tree.yview)
        ybar.pack(side="right", fill="y", padx=(0, 5), pady=6)
        xbar = ttk.Scrollbar(tree_card, orient="horizontal", command=tree.xview)
        xbar.pack(fill="x", padx=16, pady=(0, 10))
        tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        state = {"selected": None}

        def set_field(field, value):
            widget = widgets[field]
            if field in choice_maps:
                display = next((label for label, raw in choice_maps[field].items()
                                if raw is not None and str(raw) == str(value)), None)
                if display is None and field in editable_choices and value:
                    display = str(value)
                display = display or "Choose an available record"
                widget.set(display)
                return
            disabled = str(widget.cget("state")) == "disabled"
            if disabled:
                widget.configure(state="normal")
            widget.delete(0, "end")
            widget.insert(0, "" if value is None else str(value))
            if disabled:
                widget.configure(state="disabled")

        def clear():
            for field in fields:
                set_field(field, field_defaults.get(field, ""))
            state["selected"] = None
            tree.selection_remove(tree.selection())

        def refresh():
            tree.delete(*tree.get_children())
            term = search_entry.get().strip()
            sql = f"SELECT {', '.join(fields)} FROM {table}"
            params = ()
            if term:
                predicates = [f"CAST({field} AS TEXT) ILIKE %s" for field in fields]
                sql += " WHERE " + " OR ".join(predicates)
                params = tuple(f"%{term}%" for _field in fields)
            rows = self._query(sql + f" ORDER BY {key}", params)
            for row in rows:
                tree.insert("", "end", values=["" if value is None else value for value in row])

        def search_records(_event=None):
            self._guard(refresh)

        def clear_search():
            search_entry.delete(0, "end")
            self._guard(refresh)

        def selected(_event=None):
            item = tree.focus()
            if not item:
                return
            row = tree.item(item, "values")
            for field, value in zip(fields, row):
                set_field(field, value)
            state["selected"] = row[fields.index(key)] if key in fields else None

        def collect():
            data = {}
            for field in fields:
                value = widgets[field].get().strip()
                if field == key and field in auto_keys:
                    continue
                if field in choice_maps:
                    if field in editable_choices:
                        data[field] = choice_maps[field].get(value, value) or None
                    else:
                        data[field] = choice_maps[field].get(value)
                    continue
                data[field] = value or None
            return data

        def add():
            data = collect()
            data = {field: value for field, value in data.items()
                    if field != key or field in {"student_id", "teacher_id"}}
            required = {
                "student": {"student_id", "first_name", "last_name", "program", "year_level"},
                "teacher": {"teacher_id", "first_name", "last_name", "department"},
                "subject": {"subject_code", "subject_name", "units"},
                "class_offering": {"class_code", "subject_id", "teacher_id", "section", "school_year", "semester"},
                "enrollment": {"student_id", "class_id"},
                "grading_period": {"name", "period_order", "school_year", "semester"},
                "grade_component": {"period_id", "name", "type", "max_score"},
            }.get(table, set())
            missing = sorted(field.replace("_", " ").title()
                             for field in required if not data.get(field))
            if missing:
                noun = "field" if len(missing) == 1 else "fields"
                raise ValueError(f"Complete these required {noun}: " + ", ".join(missing) + ".")
            names = list(data)
            marks = ", ".join(["%s"] * len(names))
            self._query(f"INSERT INTO {table} ({', '.join(names)}) VALUES ({marks})",
                        tuple(data[name] for name in names), fetch=False)
            refresh()
            clear()

        def update():
            if state["selected"] is None:
                raise ValueError("Select a row in the table before updating it.")
            data = collect()
            data.pop(key, None)
            if not data:
                raise ValueError("There are no fields to update.")
            assignments = ", ".join(f"{name}=%s" for name in data)
            self._query(f"UPDATE {table} SET {assignments} WHERE {key}=%s",
                        tuple(data.values()) + (state["selected"],), fetch=False)
            refresh()
            clear()

        def delete():
            if state["selected"] is None:
                raise ValueError("Select a row in the table before deleting it.")
            if not messagebox.askyesno("Confirm deletion", "Delete the selected record?", parent=self):
                return
            self._query(f"DELETE FROM {table} WHERE {key}=%s", (state["selected"],), fetch=False)
            refresh()
            clear()

        self._button(controls, "＋  Add record", add, self.BLUE).pack(side="left", padx=(0, 7))
        self._button(controls, "↻  Refresh", refresh, self.CARD_HOVER).pack(side="left", padx=4)
        self._button(controls, "Update selected", update, self.CARD_HOVER).pack(side="left", padx=4)
        self._button(controls, "Delete selected", delete, "#432638", self.RED).pack(side="left", padx=4)
        self._button(controls, "Clear form", clear, self.CARD_HOVER).pack(side="right")
        self._button(search_row, "Search", search_records, self.BLUE).pack(side="left", padx=(0, 6))
        self._button(search_row, "Clear search", clear_search, self.CARD_HOVER).pack(side="left")
        search_entry.bind("<Return>", search_records)
        tree.bind("<<TreeviewSelect>>", selected)
        self.after(100, lambda: self._guard(refresh))

    def _button(self, parent, text, command, color=None, text_color=None):
        return ctk.CTkButton(parent, text=text, command=lambda: self._guard(command),
                             height=34, corner_radius=8,
                             fg_color=color or self.BLUE,
                             hover_color=self.CARD_HOVER if color == self.BLUE else self.BORDER,
                             text_color=text_color or self.TEXT,
                             font=ctk.CTkFont(size=10, weight="bold"))

    def show_crud_page(self, title):
        self._add_crud_page(title)

    def show_weights_page(self):
        self._set_page("Grade Weights", "weights")
        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        self._section_intro(page, "Configure component weights",
                            "Weights are saved per class and grading period. Each period must total exactly 100%.")
        card = self._card(page, "CLASS CONFIGURATION")
        card.pack(fill="x", pady=(0, 12))
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(6, 14))
        ctk.CTkLabel(row, text="Class ID", text_color=self.MUTED).pack(side="left", padx=(0, 9))
        class_id, class_choices = self._make_combo(row, self._reference_options("class"), width=290, height=36)
        class_id.pack(side="left", padx=(0, 10))
        list_card = self._card(page, "COMPONENT WEIGHTS")
        list_card.pack(fill="both", expand=True)
        area = ctk.CTkScrollableFrame(list_card, fg_color="transparent")
        area.pack(fill="both", expand=True, padx=10, pady=(6, 12))
        entries = {}


        def load():
            for child in area.winfo_children():
                child.destroy()

            entries.clear()

            class_value = class_choices.get(class_id.get())
            if not class_value:
                raise ValueError("Choose a class first.")

            rows = self._query(
                """
                SELECT
                    gc.component_id,
                    gc.name,
                    gp.name,
                    gp.period_id,
                    gc.max_score,
                    COALESCE(w.percentage, 0)
                FROM grade_component gc
                JOIN grading_period gp USING (period_id)
                LEFT JOIN grade_percentage w
                    ON w.component_id = gc.component_id
                    AND w.class_id = %s
                WHERE gp.school_year = (
                    SELECT school_year
                    FROM class_offering
                    WHERE class_id = %s
                )
                AND gp.semester = (
                    SELECT semester
                    FROM class_offering
                    WHERE class_id = %s
                )
                ORDER BY gp.period_order, gc.component_id
                """,
                (class_value, class_value, class_value)
            )

            if not rows:
                raise ValueError(
                    "No grade components were found for this class term."
                )

            headers = (
                "PERIOD",
                "COMPONENT",
                "MAX SCORE",
                "WEIGHT (%)"
            )

            for column, label in enumerate(headers):
                area.grid_columnconfigure(
                    column,
                    weight=1 if column in (1, 3) else 0
                )

                ctk.CTkLabel(
                    area,
                    text=label,
                    text_color=self.CYAN,
                    font=ctk.CTkFont(
                        family="Consolas",
                        size=10,
                        weight="bold"
                    )
                ).grid(
                    row=0,
                    column=column,
                    sticky="w",
                    padx=12,
                    pady=(8, 12)
                )

            for i, (
                    cid,
                    name,
                    period,
                    _period_id,
                    max_score,
                    pct
            ) in enumerate(rows, 1):

                ctk.CTkLabel(
                    area,
                    text=period,
                    text_color=self.MUTED
                ).grid(
                    row=i, column=0, sticky="w", padx=12, pady=6
                )

                ctk.CTkLabel(
                    area,
                    text=name,
                    text_color=self.TEXT
                ).grid(
                    row=i, column=1, sticky="w", padx=12, pady=6
                )

                ctk.CTkLabel(
                    area,
                    text=str(max_score),
                    text_color=self.TEXT
                ).grid(
                    row=i, column=2, sticky="w", padx=12, pady=6
                )

                entry = ctk.CTkEntry(
                    area,
                    width=120,
                    height=34,
                    fg_color="#0e1729",
                    border_color=self.BORDER
                )
                entry.insert(0, str(pct))
                entry.grid(
                    row=i, column=3, sticky="w", padx=12, pady=5
                )

                entries[cid] = entry


        def save():
            if not entries:
                load()
            self.grading_service.update_grading_weights(
                str(class_choices[class_id.get()]), {cid: entry.get().strip() for cid, entry in entries.items()})
            messagebox.showinfo("Weights saved", "The grading weights have been saved.", parent=self)

        self._button(row, "Load components", load, self.BLUE).pack(side="left", padx=4)
        self._button(row, "Save weights", save, self.GREEN, "#071a16").pack(side="left", padx=4)

    def show_scores_page(self):
        self._set_page("Score Entry", "scores")
        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        self._section_intro(page, "Record student scores",
                            "Enter a score for a student’s enrollment and grade component. Saving the same pair updates it.")
        card = self._card(page, "SCORE RECORD")
        card.pack(fill="x")
        form = ctk.CTkFrame(card, fg_color="transparent")
        form.pack(fill="x", padx=15, pady=(6, 16))
        specs = [("enrollment_id", "Enrollment ID"), ("component_id", "Component ID"),
                 ("score", "Score earned"), ("remarks", "Remarks (optional)")]
        entries = {}
        score_choice_maps = {}
        for col, (field, label) in enumerate(specs):
            form.grid_columnconfigure(col, weight=1, uniform="score")
            ctk.CTkLabel(form, text=label, text_color=self.MUTED,
                         font=ctk.CTkFont(size=10, weight="bold")).grid(row=0, column=col, sticky="w", padx=6, pady=(3, 5))
            if field == "enrollment_id":
                entry, score_choice_maps[field] = self._make_combo(
                    form, self._reference_options("enrollment"), height=38)
            elif field == "component_id":
                entry, score_choice_maps[field] = self._make_combo(
                    form, self._reference_options("component"), height=38)
            else:
                entry = ctk.CTkEntry(form, height=38, fg_color="#0e1729", border_color=self.BORDER,
                                     placeholder_text="Enter " + label.lower())
            entry.grid(row=1, column=col, sticky="ew", padx=6)
            entries[field] = entry
        ctk.CTkLabel(card, text="Scores must be within the component’s maximum. The system checks enrollment, class, period, and weight.",
                     text_color=self.MUTED, font=ctk.CTkFont(size=10), wraplength=800)\
            .pack(anchor="w", padx=22, pady=(0, 12))

        def save():
            enrollment = score_choice_maps["enrollment_id"].get(entries["enrollment_id"].get())
            component = score_choice_maps["component_id"].get(entries["component_id"].get())
            score = entries["score"].get().strip()
            remarks = entries["remarks"].get().strip()
            if not enrollment or not component or not score:
                raise ValueError("Choose an enrollment and grade component, then enter a score.")
            rows = self._query("SELECT period_id FROM grade_component WHERE component_id=%s", (component,))
            if not rows:
                raise ValueError("Component ID was not found.")
            self.grade_repo.save_component_score(enrollment, rows[0][0], component, score)
            if remarks:
                self._query("UPDATE grade_component_score SET remarks=%s WHERE enrollment_id=%s AND component_id=%s",
                            (remarks, enrollment, component), fetch=False)
            messagebox.showinfo("Score saved", "The student score has been saved.", parent=self)

        def delete():
            enrollment = score_choice_maps["enrollment_id"].get(entries["enrollment_id"].get())
            component = score_choice_maps["component_id"].get(entries["component_id"].get())
            if not enrollment or not component:
                raise ValueError("Choose the enrollment and grade component for the score to remove.")
            found = self._query("SELECT period_id FROM grade_component WHERE component_id=%s", (component,))
            if not found:
                raise ValueError("Component ID was not found.")
            if not messagebox.askyesno("Confirm deletion", "Delete this component score?", parent=self):
                return
            if not self.grade_repo.delete_component_score(enrollment, found[0][0], component):
                raise ValueError("No score exists for that enrollment and component.")
            messagebox.showinfo("Score deleted", "The component score has been deleted.", parent=self)

        buttons = ctk.CTkFrame(card, fg_color="transparent")
        buttons.pack(anchor="w", padx=16, pady=(0, 16))
        self._button(buttons, "Save score", save, self.BLUE).pack(side="left", padx=5)
        self._button(buttons, "Delete score", delete, "#432638", self.RED).pack(side="left", padx=5)

    def show_reports_page(self):
        self._set_page("Compute & Reports", "reports")
        page = ctk.CTkFrame(self.content, fg_color="transparent")
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)
        self._section_intro(page, "Compute grades and build reports",
                            "Recalculate a student’s weighted grade or view class and student reports.")

        tools = ctk.CTkFrame(page, fg_color="transparent")
        tools.pack(fill="x", pady=(0, 12))
        compute = self._card(tools, "GRADE COMPUTATION")
        compute.pack(side="left", fill="both", expand=True, padx=(0, 6))
        compute_row = ctk.CTkFrame(compute, fg_color="transparent")
        compute_row.pack(fill="x", padx=13, pady=(6, 14))
        enrollment, enrollment_choices = self._small_combo(
            compute_row, "Enrollment", self._reference_options("enrollment"), 240)
        class_id, class_choices = self._small_combo(
            compute_row, "Class", self._reference_options("class"), 220)
        result_label = ctk.CTkLabel(compute, text="Grade results will appear here.",
                                    text_color=self.MUTED, font=ctk.CTkFont(size=11))
        result_label.pack(anchor="w", padx=18, pady=(0, 13))

        def calculate():
            enrollment_value = enrollment_choices.get(enrollment.get())
            class_value = class_choices.get(class_id.get())
            if not enrollment_value or not class_value:
                raise ValueError("Choose an enrollment and a class before computing.")
            result = self.grading_service.calculate_and_save_period_grade(
                enrollment_id=enrollment_value, class_id=class_value)
            result_label.configure(text="   •   ".join(f"{k.replace('_', ' ').title()}: {v}" for k, v in result.items()),
                                   text_color=self.GREEN)

        self._button(compute_row, "Compute & save", calculate, self.BLUE).pack(side="left", padx=5, pady=20)

        report = self._card(tools, "REPORT VIEWER")
        report.pack(side="left", fill="both", expand=True, padx=(6, 0))
        report_row = ctk.CTkFrame(report, fg_color="transparent")
        report_row.pack(fill="x", padx=13, pady=(6, 14))
        kind = ctk.CTkComboBox(report_row, values=["Class list", "Grade sheet", "Student grade report"],
                               width=180, height=36, fg_color="#0e1729", border_color=self.BORDER,
                               button_color=self.BLUE, dropdown_fg_color=self.PANEL)
        kind.set("Class list")
        kind.pack(side="left", padx=5, pady=20)
        report_id = ctk.CTkComboBox(report_row, values=["Choose a record"], state="readonly",
                                    width=260, height=36, fg_color="#0e1729",
                                    border_color=self.BORDER, button_color=self.BLUE,
                                    dropdown_fg_color=self.PANEL)
        report_id.set("Choose a record")
        report_choices = {"Choose a record": None}
        report_id.pack(side="left", padx=5, pady=20)
        def refresh_report_choices(_value=None):
            nonlocal report_choices
            reference = "student" if kind.get() == "Student grade report" else "class"
            options = self._reference_options(reference)
            report_choices = {label: value for value, label in options}
            labels = ["Choose a record"] + list(report_choices)
            report_choices["Choose a record"] = None
            report_id.configure(values=labels)
            report_id.set("Choose a record")
        kind.configure(command=refresh_report_choices)
        refresh_report_choices()
        self._button(report_row, "Show report", lambda: self._render_report(kind.get(), report_choices.get(report_id.get()), output), self.CYAN, "#081a1d")\
            .pack(side="left", padx=5, pady=20)

        output_card = self._card(page, "OUTPUT  /  REPORT DETAILS")
        output_card.pack(fill="both", expand=True)
        output = ctk.CTkTextbox(output_card, fg_color="#0e1729", text_color=self.TEXT,
                                border_color=self.BORDER, border_width=1, corner_radius=9,
                                font=ctk.CTkFont(family="Consolas", size=11), wrap="word")
        output.pack(fill="both", expand=True, padx=14, pady=(6, 14))
        self.content.grid_rowconfigure(0, weight=1)

    def _small_input(self, parent, label, width):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", padx=5, pady=3)
        ctk.CTkLabel(box, text=label, text_color=self.MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", pady=(0, 4))
        entry = ctk.CTkEntry(box, width=width, height=36, fg_color="#0e1729", border_color=self.BORDER)
        entry.pack()
        return entry

    def _small_combo(self, parent, label, options, width):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", padx=5, pady=3)
        ctk.CTkLabel(box, text=label, text_color=self.MUTED,
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", pady=(0, 4))
        combo, choices = self._make_combo(box, options, width=width, height=36)
        combo.pack()
        return combo, choices

    def _render_report(self, kind, ident, output):
        if not ident or ident == "Choose a record":
            raise ValueError("Choose a class or student for this report.")
        if kind == "Class list":
            data = self.report_service.get_class_list_report(ident)
        elif kind == "Grade sheet":
            data = self.report_service.get_grade_sheet_report(ident)
        else:
            data = self.report_service.get_student_grade_report(ident)
        output.delete("1.0", "end")
        output.insert("end", f"{kind}\n{'─' * 48}\n\n{data}")

