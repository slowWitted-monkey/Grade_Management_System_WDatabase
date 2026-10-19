"""Create the project schema in the database configured in the local .env."""
from pathlib import Path

from config.database import get_db_connection


def initialize_schema() -> None:
    schema_path = Path(__file__).with_name("schema.sql")
    if not schema_path.is_file():
        raise FileNotFoundError(f"Could not find schema file: {schema_path}")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(schema_path.read_text(encoding="utf-8"))
        conn.commit()
        print("Database schema created successfully.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    initialize_schema()
