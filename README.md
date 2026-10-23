# Student Grade Management System

This Python and Tkinter project uses PostgreSQL for students, teachers, subjects, class offerings, enrollments, grading configuration, component scores, computed grades, and the audit trail.

## Local setup

1. Install PostgreSQL and Python 3.10 or later.
2. Create a fresh, empty PostgreSQL database for this project. The default name is `Almodiente_CSPC103`.
3. Create a local environment file by copying `.env.example` to `.env`, then enter the password for the local PostgreSQL account. Keep `.env` private; it is excluded by `.gitignore`.
4. Create a virtual environment and install the listed packages:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

5. Create the tables without inserting demonstration data:

   ```powershell
   python -m db.init_db
   ```

6. Start the application:

   ```powershell
   python main.py
   ```

`db/schema.sql` is idempotent and does not drop tables. Use a new empty database when switching from an older project schema, because `CREATE TABLE IF NOT EXISTS` does not convert existing tables. Do not run a destructive reset against a database containing records you need.

The instructor's live demonstration checklist requires a blank database before the test data is entered. `seed_db.py` now creates missing tables only and does not add sample records.

### Optional load-test data

To explore the GUI, reports, and grade calculations with synthetic records, first point `.env` to a development database such as `MockDataBase2`. Then run:

```powershell
python -m db.seed_load_test_data
```

This adds 30 clearly labeled synthetic students, teachers, courses, classes, enrollments, grade components, weights, and scores. It never deletes rows. To add a different-sized set, use `python -m db.seed_load_test_data --students 60` (1–100 students). Records use `LOAD-` IDs and sample emails under `example.test`. Re-running on the same date does not duplicate those records. Do not run this against the blank database you plan to use for the professor's checklist.

## Test calculations

The expected grading bands and the 40% Midterm / 60% Finals calculation are implemented in `strategy/standard_calculator.py`. Run the automated tests with:

```powershell
python -m pytest
```

The checklist's 52 GUI/database scenarios still need to be run against a configured local PostgreSQL database before the application can be considered ready for demonstration.

