"""
tests/test_load.py
Integration test for load.py: confirms data can actually be inserted
into a real PostgreSQL database -- the "Database: Can data be
inserted?" check from Phase 2 Day 7, which the extract/transform/
validate tests in test_pipeline.py don't cover.

Uses a dedicated test database (educational_analytics_test), never
the real development database, so running tests never touches real
data. Skips gracefully if no PostgreSQL server is reachable, so the
rest of the suite still runs in environments without a database.
"""

import os
import sys
from pathlib import Path
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

TEST_DB_NAME = "educational_analytics_test"
PG_HOST = os.environ.get("PGHOST", "localhost")
PG_PORT = os.environ.get("PGPORT", "5432")
PG_USER = os.environ.get("PGUSER", "postgres")
PG_PASSWORD = os.environ.get("PGPASSWORD", "postgres")

ADMIN_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/postgres"
TEST_URL = f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{TEST_DB_NAME}"


def _postgres_available() -> bool:
    try:
        engine = create_engine(ADMIN_URL)
        with engine.connect():
            pass
        return True
    except OperationalError:
        return False


requires_postgres = pytest.mark.skipif(
    not _postgres_available(),
    reason="No PostgreSQL server reachable -- skipping database integration test",
)


@pytest.fixture(scope="module")
def test_db_engine():
    admin_engine = create_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    engine = create_engine(TEST_URL)
    yield engine

    engine.dispose()
    with admin_engine.connect() as conn:
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))


@requires_postgres
def test_data_can_be_inserted(test_db_engine):
    """Phase 2 Day 7 'Database' check: can data actually be inserted?"""
    from load import load_all

    schema_path = str(Path(__file__).resolve().parent.parent / "sql" / "schema.sql")

    validated = {
        "courses": pd.DataFrame([{
            "code_module": "ZZZ", "code_presentation": "2099Z",
            "module_presentation_length": 100,
        }]),
        "students": pd.DataFrame([{
            "id_student": 999999, "gender": "F", "region": "Test Region",
            "highest_education": "HE Qualification", "imd_band": "50-60%",
            "age_band": "35-55", "disability": "N",
        }]),
        "enrollments": pd.DataFrame([{
            "id_student": 999999, "code_module": "ZZZ", "code_presentation": "2099Z",
            "date_registration": -10, "date_unregistration": None,
            "num_of_prev_attempts": 0, "studied_credits": 60, "final_result": "Pass",
        }]),
        "assessments": pd.DataFrame([{
            "id_assessment": 999999, "code_module": "ZZZ", "code_presentation": "2099Z",
            "assessment_type": "TMA", "date": 20, "weight": 100.0,
        }]),
        "results": pd.DataFrame([{
            "id_assessment": 999999, "id_student": 999999, "date_submitted": 18,
            "is_banked": False, "score": 85.0,
        }]),
    }

    load_all(validated, engine=test_db_engine, schema_path=schema_path)

    with test_db_engine.connect() as conn:
        student_count = conn.execute(
            text("SELECT COUNT(*) FROM students WHERE id_student = 999999")
        ).scalar()
        result_score = conn.execute(
            text("SELECT score FROM results WHERE id_student = 999999")
        ).scalar()

    assert student_count == 1
    assert float(result_score) == 85.0


@requires_postgres
def test_foreign_key_violation_is_rejected(test_db_engine):
    """The database itself should refuse an orphaned row, independent
    of validate.py -- proving the FK constraints in schema.sql are
    real, not just documentation."""
    from load import load_all

    schema_path = str(Path(__file__).resolve().parent.parent / "sql" / "schema.sql")

    # An enrollment referencing a student that was never inserted.
    validated = {
        "courses": pd.DataFrame([{
            "code_module": "YYY", "code_presentation": "2099Y",
            "module_presentation_length": 100,
        }]),
        "students": pd.DataFrame(columns=["id_student", "gender", "region",
                                           "highest_education", "imd_band",
                                           "age_band", "disability"]),
        "enrollments": pd.DataFrame([{
            "id_student": 888888, "code_module": "YYY", "code_presentation": "2099Y",
            "date_registration": -5, "date_unregistration": None,
            "num_of_prev_attempts": 0, "studied_credits": 60, "final_result": "Pass",
        }]),
        "assessments": pd.DataFrame(columns=["id_assessment", "code_module",
                                              "code_presentation", "assessment_type",
                                              "date", "weight"]),
        "results": pd.DataFrame(columns=["id_assessment", "id_student",
                                          "date_submitted", "is_banked", "score"]),
    }

    results = load_all(validated, engine=test_db_engine, schema_path=schema_path)
    assert results["enrollments"]["status"] == "error"
