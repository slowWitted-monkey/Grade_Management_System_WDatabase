from service.report_service import ReportService

class ReportViews:
    def __init__(self):
        self.report_service = ReportService()

    def display_class_list(self, offering_id: str):
        data = self.report_service.get_class_list_report(offering_id)
        h = data["header"]
        roster = data["roster"]

        if not h:
            print(f"\n[!] Class Offering '{offering_id}' not found.")
            return

        print("\n" + "="*70)
        print("                     CLASS LIST REPORT")
        print("="*70)
        print(f"Subject    : {h['subject_code']} - {h['subject_name']}")
        print(f"Class Code : {h['class_code']} | Section: {h['section']} | Room: {h['room']}")
        print(f"Instructor : {h['teacher_first']} {h['teacher_last']}")
        print(f"Term       : {h['semester']} (SY {h['school_year']})")
        print("-" * 70)
        print(f"{'Student ID':<12} | {'Student Name':<25} | {'Program':<8} | {'Status':<10}")
        print("-" * 70)

        for s in roster:
            name = f"{s['last_name']}, {s['first_name']}"
            print(f"{s['student_id']:<12} | {name:<25} | {s['program']:<8} | {s['status']:<10}")
        print("="*70 + "\n")

    def display_grade_sheet(self, offering_id: str):
        data = self.report_service.get_grade_sheet_report(offering_id)
        grades = data["grades"]

        print("\n" + "="*70)
        print(f"               OFFICIAL GRADE SHEET ({offering_id})")
        print("="*70)
        print(f"{'Student ID':<12} | {'Student Name':<25} | {'Period':<10} | {'Grade':<8} | {'Remarks':<10}")
        print("-" * 70)

        for g in grades:
            name = f"{g['last_name']}, {g['first_name']}"
            grade_val = f"{g['final_grade']:.2f}" if g['final_grade'] is not None else "N/A"
            period = g['period_name'] if g['period_name'] else "N/A"
            remarks = g['remarks'] if g['remarks'] else "N/A"
            print(f"{g['student_id']:<12} | {name:<25} | {period:<10} | {grade_val:<8} | {remarks:<10}")
        print("="*70 + "\n")

    def display_student_grade_report(self, student_id: str):
        data = self.report_service.get_student_grade_report(student_id)
        s = data["student"]
        grades = data["grades"]

        if not s:
            print(f"\n[!] Student ID '{student_id}' not found.")
            return

        print("\n" + "="*70)
        print("                STUDENT ACADEMIC GRADE REPORT")
        print("="*70)
        print(f"Student ID : {s['student_id']}")
        print(f"Name       : {s['first_name']} {s['last_name']}")
        print(f"Program    : {s['program']} | Status: {s['status']}")
        print("-" * 70)
        print(f"{'Code':<10} | {'Subject Title':<30} | {'Units':<5} | {'Grade':<8} | {'Remarks':<10}")
        print("-" * 70)

        for g in grades:
            grade_val = f"{g['final_grade']:.2f}" if g['final_grade'] is not None else "N/A"
            remarks = g['remarks'] if g['remarks'] else "N/A"
            print(f"{g['subject_code']:<10} | {g['subject_name'][:30]:<30} | {g['units']:<5} | {grade_val:<8} | {remarks:<10}")
        print("="*70 + "\n")