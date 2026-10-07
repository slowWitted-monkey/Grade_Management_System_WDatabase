import sys
from ui.report_views import ReportViews
from service.grading_service import GradingService

class MainMenu:
    def __init__(self):
        self.report_views = ReportViews()
        self.grading_service = GradingService()

    def start(self):
        while True:
            print("\n==================================================")
            print("  STUDENT GRADE MANAGEMENT SYSTEM (CSPC 103)")
            print("==================================================")
            print("1. Compute & Persist Period Grades")
            print("2. Display Class List Report")
            print("3. Display Class Grade Sheet")
            print("4. Display Individual Student Grade Report")
            print("5. Exit Application")
            print("--------------------------------------------------")

            choice = input("Enter choice (1-5): ").strip()

            if choice == "1":
                grade_id = input("Enter Grade ID (e.g., GRD001): ").strip()
                offering_id = input("Enter Offering ID (e.g., OFF001): ").strip()
                try:
                    result = self.grading_service.calculate_and_save_period_grade(grade_id, offering_id)
                    print(f"\n[SUCCESS] Grade calculated and saved: {result:.2f}%")
                except Exception as e:
                    print(f"\n[ERROR] Calculation failed: {e}")

            elif choice == "2":
                offering_id = input("Enter Offering ID (e.g., OFF001): ").strip()
                self.report_views.display_class_list(offering_id)

            elif choice == "3":
                offering_id = input("Enter Offering ID (e.g., OFF001): ").strip()
                self.report_views.display_grade_sheet(offering_id)

            elif choice == "4":
                student_id = input("Enter Student ID (e.g., STD001): ").strip()
                self.report_views.display_student_grade_report(student_id)

            elif choice == "5":
                print("\nThank you for using Student Grade Management System!")
                sys.exit(0)

            else:
                print("\n[!] Invalid option. Please try again.")