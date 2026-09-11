"""
config.py
Single source of truth for database configuration. Previously
DB_CONFIG and the connection URL were duplicated in load.py and
test_database.py -- consolidated here as part of Phase 2 Day 1
pipeline improvement.
"""

import os
from sqlalchemy import create_engine

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": os.environ.get("PGPORT", "5432"),
    "dbname": os.environ.get("PGDATABASE", "educational_analytics"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", "admin123"),
}


def get_database_url() -> str:
    return (f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
            f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")


def get_engine():
    return create_engine(get_database_url())
