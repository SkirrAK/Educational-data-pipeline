"""
test_database.py
A small standalone check that Python can connect to PostgreSQL.
Run this before src/load.py to confirm the database is reachable.
"""

from sqlalchemy import text
from config import DB_CONFIG, get_engine


def main():
    engine = get_engine()
    try:
        with engine.connect() as conn:
            version = conn.execute(text("SELECT version();")).scalar()
        print("Connection successful.")
        print(f"Connected to: {DB_CONFIG['dbname']} at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"Server version: {version}")
    except Exception as e:
        print(f"Connection FAILED: {e}")
        raise


if __name__ == "__main__":
    main()
