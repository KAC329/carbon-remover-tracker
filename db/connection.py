"""
db/connection.py
Centralized database connection using SQLAlchemy.
All pipeline modules import get_engine() from here.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    """Return a SQLAlchemy engine using environment variables."""
    url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}"
        f"/{os.getenv('DB_NAME')}"
    )
    return create_engine(url, pool_pre_ping=True)


def test_connection():
    engine = get_engine()
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM technology_categories"))
        count = result.scalar()
        print(f"✓ Connected. {count} technology categories loaded.")


if __name__ == "__main__":
    test_connection()
