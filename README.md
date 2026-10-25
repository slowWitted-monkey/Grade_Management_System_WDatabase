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

The application opens maximized to use the available display area. Restore it with the title-bar button to resize it normally. PostgreSQL connection attempts stop after five seconds by default; set `DB_CONNECT_TIMEOUT` in `.env` to change that limit.

`db/schema.sql` is idempotent and does not drop tables. Use a new empty database when switching from an older project schema, because `CREATE TABLE IF NOT EXISTS` does not convert existing tables. Do not run a destructive reset against a database containing records you need.

The instructor's live demonstration checklist requires a blank database before the test data is entered. `seed_db.py` now creates missing tables only and does not add sample records.

### Optional CRUD checklist fixture

To explore the GUI, reports, and grade calculations with the professor's exact data, point `.env` to a development database such as `MockDataBase2`, then run:

```powershell
python -m db.seed_load_test_data
```

This inserts or refreshes the named checklist records: Juan, Pedro, Ana, Carlo, Kevin, Maria, Jose, CSPC 103, PATHFIT 3, both classes, the six grading components, all checklist scores, final weights, and computed grades. It matches the checklist's final report-ready state, including updates such as Ana's BSCS program, Maria's department, CSPC 103's room/schedule, Juan's corrected score, and the 30/30/40 Midterm weights. Scores are saved through the application's repository and grades are calculated by the application's grading service, creating audit entries. It never deletes rows, but it does reset those specific checklist fixture records to their listed values each time it runs. Add optional un-enrolled list/search records with `python -m db.seed_load_test_data --extra-students 30` (1–100). These extra students use `LOAD-` IDs. Do not use this seeded final state to score the live checklist's create/update scenarios; keep the required blank database for that demonstration.

## Test calculations

The expected grading bands and the 40% Midterm / 60% Finals calculation are implemented in `strategy/standard_calculator.py`. Run the automated tests with:

```powershell
python -m pytest
```

The checklist's 52 GUI/database scenarios still need to be run against a configured local PostgreSQL database before the application can be considered ready for demonstration.

