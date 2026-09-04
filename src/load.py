"""
load.py
Validated DataFrame -> Database connection -> PostgreSQL -> Tables.
Reports: successful connection, target table, records inserted, errors encountered.
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text

DB_CONFIG = {
    "host": os.environ.get("PGHOST", "localhost"),
    "port": os.environ.get("PGPORT", "5432"),
    "dbname": os.environ.get("PGDATABASE", "educational_analytics"),
    "user": os.environ.get("PGUSER", "postgres"),
    "password": os.environ.get("PGPASSWORD", "admin123"),
}

# Load order matters: parents before children (FK dependencies)
LOAD_ORDER = ["courses", "students", "enrollments", "assessments", "results"]


def get_engine():
    url = (f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
           f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    return create_engine(url)


def apply_schema(engine, schema_path: str):
    with open(schema_path) as f:
        schema_sql = f.read()
    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    print(f"[load] schema applied from {schema_path}")


def load_all(validated: dict, engine=None, schema_path: str = None) -> dict:
    engine = engine or get_engine()
    try:
        with engine.connect() as conn:
            pass
        print(f"[load] connected to {DB_CONFIG['dbname']} at {DB_CONFIG['host']}:{DB_CONFIG['port']}")
    except Exception as e:
        print(f"[load] connection FAILED: {e}")
        raise

    if schema_path:
        apply_schema(engine, schema_path)

    results = {}
    for table in LOAD_ORDER:
        df = validated[table]
        try:
            df.to_sql(table, engine, if_exists="append", index=False)
            results[table] = {"status": "ok", "records_inserted": len(df)}
            print(f"[load] {table}: {len(df)} records inserted")
        except Exception as e:
            results[table] = {"status": "error", "error": str(e)}
            print(f"[load] {table}: ERROR - {e}")
    return results


if __name__ == "__main__":
    from extract import extract_all
    from transform import transform_all
    from validate import validate_all

    raw = extract_all()
    clean = transform_all(raw)
    validated, report = validate_all(clean)
    print(report.summary())

    schema_path = str((__import__("pathlib").Path(__file__).resolve().parent.parent / "sql" / "schema.sql"))
    load_all(validated, schema_path=schema_path)
