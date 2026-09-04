"""
test_database.py
A small standalone check that Python can connect to PostgreSQL.
Run this before src/load.py to confirm the database is reachable.
"""

import os
from sqlalchemy import create_engine, text

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": os.environ.get("PGPORT", "5432"),
    "dbname": os.environ.get("PGDATABASE", "educational_analytics"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", "admin123"),
}


def main():
    url = (f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
           f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    engine = create_engine(url)
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
