"""Compatibility entry point: the professor's checklist requires a blank test database."""
from db.init_db import initialize_schema


def reset_and_seed_database():
    """Create missing tables only; never truncate user data or add demo rows."""
    initialize_schema()
    print("Schema is ready. No sample rows were inserted; enter the checklist data in the application.")


if __name__ == "__main__":
    reset_and_seed_database()
