"""
load.py
Validated DataFrame -> Database connection -> PostgreSQL -> Tables.
Reports: successful connection, target table, records inserted, errors encountered.
"""

import logging
import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from config import DB_CONFIG, get_engine

log = logging.getLogger("pipeline.load")

# Load order matters: parents before children (FK dependencies)
LOAD_ORDER = ["courses", "students", "enrollments", "assessments", "results"]


def apply_schema(engine, schema_path: str):
    with open(schema_path) as f:
        schema_sql = f.read()
    with engine.begin() as conn:
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(text(statement))
    log.info(f"Schema applied from {schema_path}")


def load_all(validated: dict, engine=None, schema_path: str = None) -> dict:
    """
    Loads validated tables into PostgreSQL in FK-safe order.
    Raises a clear, actionable error (rather than a raw traceback)
    for the two expected failure modes: no DB connection, and an
    entirely empty validated dataset.
    """
    engine = engine or get_engine()

    try:
        with engine.connect():
            pass
        log.info(f"Database connection successful ({DB_CONFIG['dbname']} at "
                  f"{DB_CONFIG['host']}:{DB_CONFIG['port']})")
    except OperationalError as e:
        log.error(
            f"Database connection FAILED for {DB_CONFIG['dbname']} at "
            f"{DB_CONFIG['host']}:{DB_CONFIG['port']}. Is PostgreSQL running, "
            f"and are PGHOST/PGPORT/PGUSER/PGPASSWORD correct? Detail: {e}"
        )
        raise

    if all(len(df) == 0 for df in validated.values()):
        log.error(
            "All validated tables are empty -- nothing to load. This usually "
            "means every row was rejected during validation, or the source "
            "files in data/raw/ were empty. Refusing to load an empty dataset."
        )
        raise ValueError("Empty dataset: no valid records to load in any table.")

    if schema_path:
        apply_schema(engine, schema_path)

    results = {}
    for table in LOAD_ORDER:
        df = validated[table]
        try:
            df.to_sql(table, engine, if_exists="append", index=False)
            results[table] = {"status": "ok", "records_inserted": len(df)}
            log.info(f"Records loaded -- {table}: {len(df)} records")
        except Exception as e:
            # Broad except deliberately: pandas.to_sql wraps the underlying
            # SQLAlchemyError in its own pandas.errors.DatabaseError, which
            # does not inherit from SQLAlchemyError, so catching only that
            # type let real failures (e.g. FK violations) crash the whole
            # run instead of being recorded per-table as intended.
            results[table] = {"status": "error", "error": str(e)}
            log.error(f"Failed loading table '{table}': {e}")
    return results


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    from extract import extract_all
    from transform import transform_all
    from validate import validate_all

    raw = extract_all()
    clean = transform_all(raw)
    validated, report = validate_all(clean)
    print(report.summary())

    schema_path = str((__import__("pathlib").Path(__file__).resolve().parent.parent / "sql" / "schema.sql"))
    load_all(validated, schema_path=schema_path)
