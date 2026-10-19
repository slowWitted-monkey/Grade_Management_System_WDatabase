"""Simple database-backed desktop interface for the grade management system."""

import tkinter as tk
from tkinter import messagebox, ttk

from config.database import get_db_connection
from repository.grade_repository import GradeRepository
from service.grading_service import GradingService
from service.report_service import ReportService


class GradeManagementGUI(tk.Tk):
    """Tabbed CRUD interface. SQL identifiers are fixed in this file; values are bound."""

    TABLES = [
        ("Students", "student", "student_id", ["student_id", "first_name", "last_name", "program", "year_level", "email", "status"]),
        ("Teachers", "teacher", "teacher_id", ["teacher_id", "first_name", "last_name", "email", "department", "status"]),
        ("Subjects", "subject", "subject_id", ["subject_id", "subject_code", "subject_name", "description", "units"]),
        ("Classes", "class_offering", "class_id", ["class_id", "class_code", "subject_id", "teacher_id", "section", "school_year", "semester", "schedule", "room"]),
        ("Enrollments", "enrollment", "enrollment_id", ["enrollment_id", "student_id", "class_id", "status"]),
        ("Grading Periods", "grading_period", "period_id", ["period_id", "name", "period_order", "start_date", "end_date", "school_year", "semester"]),
        ("Grade Components", "grade_component", "component_id", ["component_id", "period_id", "name", "type", "max_score", "description"]),
    ]

    def __init__(self):
        super().__init__()
        self.title("Student Information and Grading System")
        self.geometry("1180x760")
        self.minsize(950, 620)
        self.configure(padx=12, pady=10)
        self.grade_repo = GradeRepository()
        self.grading_service = GradingService(self.grade_repo)
        self.report_service = ReportService()
        self.status = tk.StringVar(value="Starting�")

        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 8))
        ttk.Label(header, text="Student Information and Grading System", font=("Segoe UI", 17, "bold")).pack(side="left")
        ttk.Button(header, text="Check database", command=self.check_database).pack(side="right")
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        for title, table, key, fields in self.TABLES:
            self._add_crud_tab(title, table, key, fields)
        self._add_weights_tab()
        self._add_scores_tab()
        self._add_grades_reports_tab()
        ttk.Label(self, textvariable=self.status, anchor="w").pack(fill="x", pady=(7, 0))
        self.after(150, self.check_database)

    def _db(self):
        return get_db_connection()

    def _show_error(self, error):
        messagebox.showerror("Unable to complete action", str(error), parent=self)

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

    def check_database(self):
        try:
            conn = self._db()
            conn.close()
            self.status.set("Database connected. Use the tabs to manage records.")
        except Exception as exc:
            self.status.set(f"Database not connected: {exc}")

    def _add_crud_tab(self, title, table, key, fields):
        frame = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(frame, text=title)
        form = ttk.LabelFrame(frame, text="Record details", padding=8)
        form.pack(fill="x", pady=(0, 8))
        widgets = {}
        for i, field in enumerate(fields):
            row, col = divmod(i, 4)
            cell = ttk.Frame(form)
            cell.grid(row=row, column=col, sticky="ew", padx=5, pady=4)
            ttk.Label(cell, text=field.replace("_", " ").title()).pack(anchor="w")
            entry = ttk.Entry(cell, width=22)
            entry.pack(fill="x")
            widgets[field] = entry
            form.columnconfigure(col, weight=1)
        if key in widgets and key in {"subject_id", "class_id", "enrollment_id", "period_id", "component_id"}:
            widgets[key].configure(state="readonly")
        controls = ttk.Frame(frame)
        controls.pack(fill="x", pady=(0, 8))
        tree = ttk.Treeview(frame, columns=fields, show="headings", height=15)
        for field in fields:
            tree.heading(field, text=field.replace("_", " ").title())
            tree.column(field, width=max(100, min(180, 1300 // len(fields))), anchor="w")
        tree.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        state = {"selected": None}

        def set_field(field, value):
            widget = widgets[field]
            readonly = str(widget.cget("state")) == "readonly"
            if readonly:
                widget.configure(state="normal")
            widget.delete(0, "end")
            widget.insert(0, "" if value is None else str(value))
            if readonly:
                widget.configure(state="readonly")

        def clear():
            for field in fields:
                set_field(field, "")
            state["selected"] = None
            tree.selection_remove(tree.selection())

        def refresh():
            tree.delete(*tree.get_children())
            rows = self._query(f"SELECT {', '.join(fields)} FROM {table} ORDER BY {key}")
            for row in rows:
                tree.insert("", "end", values=["" if x is None else x for x in row])

        def selected(_event=None):
            item = tree.focus()
            if not item:
                return
            values = tree.item(item, "values")
            for field, value in zip(fields, values):
                set_field(field, value)
            state["selected"] = values[fields.index(key)] if key in fields else None

        def values():
            result = {}
            for field in fields:
                value = widgets[field].get().strip()
                if field == key and key not in {"student_id", "teacher_id"}:
                    continue
                if value == "":
                    result[field] = None
                else:
                    result[field] = value
            return result

        def add():
            data = values()
            data = {f: v for f, v in data.items() if f != key or key in {"student_id", "teacher_id"}}
            required = set()
            if table == "student": required |= {"first_name", "last_name", "program", "year_level"}
            if table == "teacher": required |= {"first_name", "last_name", "department"}
            if table == "subject": required |= {"subject_code", "subject_name", "units"}
            if table == "class_offering": required |= {"class_code", "subject_id", "teacher_id", "section", "school_year", "semester"}
            if table == "enrollment": required |= {"student_id", "class_id"}
            if table == "grading_period": required |= {"name", "period_order", "school_year", "semester"}
            if table == "grade_component": required |= {"period_id", "name", "type", "max_score"}
            missing = [f for f in required if not data.get(f)]
            if missing:
                raise ValueError("Please complete required fields: " + ", ".join(missing))
            cols = list(data)
            placeholders = ", ".join(["%s"] * len(cols))
            self._query(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", tuple(data[c] for c in cols), fetch=False)
            refresh(); clear()

        def update():
            if state["selected"] is None:
                raise ValueError("Select a record in the list before choosing Update.")
            data = values()
            data.pop(key, None)
            if not data:
                raise ValueError("There are no fields to update.")
            sets = ", ".join(f"{column}=%s" for column in data)
            self._query(f"UPDATE {table} SET {sets} WHERE {key}=%s", tuple(data.values()) + (state["selected"],), fetch=False)
            refresh(); clear()

        def delete():
            if state["selected"] is None:
                raise ValueError("Select a record in the list before choosing Delete.")
            if not messagebox.askyesno("Confirm deletion", "Delete the selected record?", parent=self):
                return
            self._query(f"DELETE FROM {table} WHERE {key}=%s", (state["selected"],), fetch=False)
            refresh(); clear()

        for label, command in (("Add new", add), ("Update selected", update), ("Delete selected", delete), ("Clear", clear), ("Refresh", refresh)):
            ttk.Button(controls, text=label, command=lambda fn=command: self._guard(fn)).pack(side="left", padx=(0, 6))
        tree.bind("<<TreeviewSelect>>", selected)
        frame.refresh = refresh
        self.after(250, lambda: self._guard(refresh))

    def _guard(self, action):
        try:
            action()
        except Exception as exc:
            self._show_error(exc)

    def _add_weights_tab(self):
        frame = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(frame, text="Grade Weights")
        ttk.Label(frame, text="Class ID").grid(row=0, column=0, sticky="w", padx=4, pady=5)
        class_id = ttk.Entry(frame, width=20); class_id.grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(frame, text="Set each component weight. Weights for each grading period must total 100%.", wraplength=800).grid(row=1, column=0, columnspan=3, sticky="w", pady=8)
        area = ttk.Frame(frame); area.grid(row=2, column=0, columnspan=3, sticky="nsew")
        entries = {}
        def load():
            for child in area.winfo_children(): child.destroy()
            entries.clear()
            rows = self._query("""SELECT gc.component_id,gc.name,gp.name,gp.period_id,COALESCE(w.percentage,0)
                FROM grade_component gc JOIN grading_period gp USING(period_id)
                LEFT JOIN grade_percentage w ON w.component_id=gc.component_id AND w.class_id=%s
                WHERE gp.school_year=(SELECT school_year FROM class_offering WHERE class_id=%s)
                AND gp.semester=(SELECT semester FROM class_offering WHERE class_id=%s)
                ORDER BY gp.period_order,gc.component_id""", (class_id.get().strip(), class_id.get().strip(), class_id.get().strip()))
            if not rows: raise ValueError("No grade components found for this class's school year and semester.")
            ttk.Label(area, text="Period").grid(row=0,column=0,sticky="w"); ttk.Label(area,text="Component").grid(row=0,column=1,sticky="w"); ttk.Label(area,text="Weight (%)").grid(row=0,column=2,sticky="w")
            for i,(cid,name,period,pid,pct) in enumerate(rows,1):
                ttk.Label(area,text=period).grid(row=i,column=0,sticky="w",padx=4,pady=3)
                ttk.Label(area,text=name).grid(row=i,column=1,sticky="w",padx=4,pady=3)
                ent=ttk.Entry(area,width=12);ent.insert(0,str(pct));ent.grid(row=i,column=2,sticky="w",padx=4,pady=3);entries[cid]=ent
        def save():
            if not entries: load()
            self.grading_service.update_grading_weights(class_id.get().strip(), {cid: ent.get().strip() for cid,ent in entries.items()})
            messagebox.showinfo("Saved", "Grade weights saved.", parent=self)
        ttk.Button(frame,text="Load components",command=lambda:self._guard(load)).grid(row=0,column=2,padx=5)
        ttk.Button(frame,text="Save weights",command=lambda:self._guard(save)).grid(row=3,column=0,pady=12,sticky="w")
        frame.rowconfigure(2,weight=1);frame.columnconfigure(1,weight=1)

    def _add_scores_tab(self):
        frame=ttk.Frame(self.tabs,padding=12);self.tabs.add(frame,text="Scores")
        entries={}
        for row,(field,label) in enumerate((("enrollment_id","Enrollment ID"),("component_id","Component ID"),("score","Score"),("remarks","Remarks (optional)"))):
            ttk.Label(frame,text=label).grid(row=row,column=0,sticky="w",pady=5)
            ent=ttk.Entry(frame,width=38);ent.grid(row=row,column=1,sticky="w",pady=5);entries[field]=ent
        ttk.Label(frame,text="Saving an existing enrollment/component pair updates its score.",wraplength=600).grid(row=4,column=0,columnspan=2,sticky="w",pady=8)
        def save():
            enrollment=entries["enrollment_id"].get().strip();component=entries["component_id"].get().strip();score=entries["score"].get().strip();remarks=entries["remarks"].get().strip()
            if not enrollment or not component or not score: raise ValueError("Enrollment ID, component ID, and score are required.")
            rows=self._query("SELECT gc.period_id FROM grade_component gc WHERE gc.component_id=%s",(component,))
            if not rows: raise ValueError("Component ID was not found.")
            self.grade_repo.save_component_score(enrollment,rows[0][0],component,score)
            if remarks:
                self._query("UPDATE grade_component_score SET remarks=%s WHERE enrollment_id=%s AND component_id=%s",(remarks,enrollment,component),fetch=False)
            messagebox.showinfo("Saved","Score saved.",parent=self)
        def delete():
            enrollment=entries["enrollment_id"].get().strip();component=entries["component_id"].get().strip()
            if not enrollment or not component: raise ValueError("Enter the enrollment and component IDs for the score to remove.")
            found=self._query("SELECT period_id FROM grade_component WHERE component_id=%s",(component,))
            if not found: raise ValueError("Component ID was not found.")
            if not messagebox.askyesno("Confirm deletion","Delete this component score?",parent=self): return
            if not self.grade_repo.delete_component_score(enrollment,found[0][0],component):
                raise ValueError("No score exists for that enrollment and component.")
            messagebox.showinfo("Deleted","Component score deleted.",parent=self)
        ttk.Button(frame,text="Save score",command=lambda:self._guard(save)).grid(row=5,column=0,sticky="w",pady=8)
        ttk.Button(frame,text="Delete score",command=lambda:self._guard(delete)).grid(row=5,column=1,sticky="w",pady=8)

    def _add_grades_reports_tab(self):
        frame=ttk.Frame(self.tabs,padding=12);self.tabs.add(frame,text="Compute & Reports")
        ttk.Label(frame,text="Enrollment ID").grid(row=0,column=0,sticky="w")
        enrollment=ttk.Entry(frame,width=18);enrollment.grid(row=0,column=1,sticky="w",padx=5,pady=5)
        ttk.Label(frame,text="Class ID").grid(row=0,column=2,sticky="w")
        class_id=ttk.Entry(frame,width=18);class_id.grid(row=0,column=3,sticky="w",padx=5,pady=5)
        output=tk.Text(frame,height=23,wrap="word");output.grid(row=2,column=0,columnspan=5,sticky="nsew",pady=8)
        def compute():
            result=self.grading_service.calculate_and_save_period_grade(enrollment_id=enrollment.get().strip(),class_id=class_id.get().strip())
            output.delete("1.0","end");output.insert("end", "Computed grade\n\n"+"\n".join(f"{k.replace('_',' ').title()}: {v}" for k,v in result.items()))
        ttk.Button(frame,text="Compute and save grade",command=lambda:self._guard(compute)).grid(row=1,column=0,sticky="w",pady=5)
        ttk.Label(frame,text="Report type").grid(row=1,column=1,sticky="e")
        report_type=ttk.Combobox(frame,values=("Class list","Grade sheet","Student grade report"),state="readonly",width=23);report_type.current(0);report_type.grid(row=1,column=2,sticky="w",padx=5)
        report_id=ttk.Entry(frame,width=18);report_id.grid(row=1,column=3,sticky="w",padx=5)
        ttk.Label(frame,text="Class ID or student ID").grid(row=1,column=4,sticky="w")
        def report():
            kind=report_type.get();ident=report_id.get().strip()
            if not ident: raise ValueError("Enter a class ID or student ID for the report.")
            if kind=="Class list": data=self.report_service.get_class_list_report(ident)
            elif kind=="Grade sheet": data=self.report_service.get_grade_sheet_report(ident)
            else: data=self.report_service.get_student_grade_report(ident)
            output.delete("1.0","end");output.insert("end",f"{kind}\n\n{data}")
        ttk.Button(frame,text="Show report",command=lambda:self._guard(report)).grid(row=1,column=5,sticky="w",padx=5)
        frame.rowconfigure(2,weight=1);frame.columnconfigure(4,weight=1)
