"""
tests/test_pipeline.py
Unit tests for transform.py and validate.py, plus an integration test
that runs extract -> transform -> validate against the sample data
and checks the results are internally consistent.
"""

import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from extract import extract_all
from transform import transform_all
from validate import validate_all, ValidationReport


@pytest.fixture(scope="module")
def raw_data():
    return extract_all()


@pytest.fixture(scope="module")
def clean_data(raw_data):
    return transform_all(raw_data)


@pytest.fixture(scope="module")
def validated_data(clean_data):
    validated, report = validate_all(clean_data)
    return validated, report


# ---- Unit tests ----

def test_extract_returns_all_tables(raw_data):
    expected = {"courses", "studentInfo", "studentRegistration", "assessments", "studentAssessment"}
    assert set(raw_data.keys()) == expected
    for name, df in raw_data.items():
        assert len(df) > 0, f"{name} should not be empty"


def test_transform_students_has_no_duplicate_columns(clean_data):
    students = clean_data["students"]
    assert "id_student" in students.columns
    assert list(students.columns) == list(dict.fromkeys(students.columns))


def test_validation_report_logs_known_issues(validated_data):
    _, report = validated_data
    checks = {(i["table"], i["check"]) for i in report.issues}
    assert ("results", "score outside 0-100 range") in checks
    assert ("results", "missing score") in checks
    assert ("students", "duplicate id_student") in checks


# ---- Integration tests ----

def test_validated_students_have_no_nulls_or_dupes(validated_data):
    validated, _ = validated_data
    students = validated["students"]
    assert students["id_student"].isna().sum() == 0
    assert students.duplicated(subset=["id_student"]).sum() == 0


def test_validated_results_scores_in_range(validated_data):
    validated, _ = validated_data
    results = validated["results"]
    assert (results["score"] >= 0).all()
    assert (results["score"] <= 100).all()
    assert results["score"].isna().sum() == 0


def test_referential_integrity_enrollments(validated_data):
    validated, _ = validated_data
    valid_students = set(validated["students"]["id_student"])
    assert set(validated["enrollments"]["id_student"]).issubset(valid_students)


def test_referential_integrity_results(validated_data):
    validated, _ = validated_data
    valid_students = set(validated["students"]["id_student"])
    valid_assessments = set(validated["assessments"]["id_assessment"])
    assert set(validated["results"]["id_student"]).issubset(valid_students)
    assert set(validated["results"]["id_assessment"]).issubset(valid_assessments)
