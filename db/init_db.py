# init_db.py
import os
from config.database import get_db_connection

def initialize_schema():
    schema_path = os.path.join(os.path.dirname(__file__), 'db', 'schema.sql')

    if not os.path.exists(schema_path):
        print(f"Error: Could not find schema file at {schema_path}")
        return

    print("Connecting to PostgreSQL to initialize schema...")
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        with open(schema_path, 'r') as file:
            sql_script = file.read()
            cursor.execute(sql_script)
            conn.commit()
            print("Database schema created successfully!")
    except Exception as e:
        print(f"Error initializing database schema: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    initialize_schema()