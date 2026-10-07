# Student Grade Management System

A Python-based Object-Oriented Grade Management System with PostgreSQL database persistence and Tkinter GUI.

## Features
- Dynamic weighted grade calculations using the Strategy Pattern
- Parameterized SQL queries via the Repository Pattern (prevention of SQL injection)
- Integrated GUI supporting Grade Computation, Class Lists, Grade Sheets, and Student Grade Reports

## Setup & Running Instructions
1. Clone repository and set up virtual environment.
2. Install requirements: `pip install -r requirements.txt`
3. Execute SQL scripts in PostgreSQL (`db/schema.sql` and `db/seed_data.sql`).
4. Configure database credentials in `.env`.
5. Launch application: `python main.py`