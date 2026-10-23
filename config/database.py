import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def get_db_connection():
    """Open the local PostgreSQL database using the project's .env settings."""
    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError(
            "DB_PASSWORD is not set. Copy .env.example to .env and enter your "
            "local PostgreSQL password. Never commit .env."
        )

    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "Almodiente_CSPC103"),
        user=os.getenv("DB_USER", "postgres"),
        password=password,
    )
