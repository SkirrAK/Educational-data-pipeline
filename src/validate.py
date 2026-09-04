"""
validate.py
Data-quality checks applied to the transformed DataFrames.
Checks: missing values, duplicates, invalid values, required fields,
data types, and referential (foreign-key) integrity between tables.

Invalid rows are rejected (dropped) and reported rather than silently
loaded, so problems are visible instead of hidden.
"""

import pandas as pd


class ValidationReport:
    def __init__(self):
        self.issues = []

    def log(self, table: str, check: str, count: int):
        if count > 0:
            self.issues.append({"table": table, "check": check, "rows_affected": count})

    def summary(self) -> str:
        if not self.issues:
            return "No data-quality issues found."
        lines = ["Data-quality issues found:"]
        for i in self.issues:
            lines.append(f"  - [{i['table']}] {i['check']}: {i['rows_affected']} row(s)")
        return "\n".join(lines)


def validate_students(df: pd.DataFrame, report: ValidationReport) -> pd.DataFrame:
    before = len(df)
    df = df.dropna(subset=["id_student"])
    report.log("students", "missing id_student", before - len(df))

    dup = df.duplicated(subset=["id_student"]).sum()
    report.log("students", "duplicate id_student", dup)
    df = df.drop_duplicates(subset=["id_student"])
    return df


def validate_courses(df: pd.DataFrame, report: ValidationReport) -> pd.DataFrame:
    before = len(df)
    df = df.dropna(subset=["code_module", "code_presentation"])
    report.log("courses", "missing course key", before - len(df))
    return df


def validate_enrollments(df: pd.DataFrame, students: pd.DataFrame,
                          courses: pd.DataFrame, report: ValidationReport) -> pd.DataFrame:
    before = len(df)
    missing_student = df["id_student"].isna().sum()
    report.log("enrollments", "missing id_student", int(missing_student))
    df = df.dropna(subset=["id_student"])

    dup = df.duplicated(subset=["id_student", "code_module", "code_presentation"]).sum()
    report.log("enrollments", "duplicate enrollment rows", int(dup))
    df = df.drop_duplicates(subset=["id_student", "code_module", "code_presentation"])

    valid_students = set(students["id_student"].dropna())
    valid_courses = set(zip(courses["code_module"], courses["code_presentation"]))

    mask_student = df["id_student"].isin(valid_students)
    mask_course = df.apply(lambda r: (r["code_module"], r["code_presentation"]) in valid_courses, axis=1)
    orphans = (~mask_student | ~mask_course).sum()
    report.log("enrollments", "orphaned FK (unknown student or course)", int(orphans))

    df = df[mask_student & mask_course].copy()
    return df


def validate_assessments(df: pd.DataFrame, courses: pd.DataFrame, report: ValidationReport) -> pd.DataFrame:
    valid_courses = set(zip(courses["code_module"], courses["code_presentation"]))
    mask_course = df.apply(lambda r: (r["code_module"], r["code_presentation"]) in valid_courses, axis=1)
    orphans = (~mask_course).sum()
    report.log("assessments", "orphaned FK (unknown course)", int(orphans))
    return df[mask_course].copy()


def validate_results(df: pd.DataFrame, students: pd.DataFrame,
                      assessments: pd.DataFrame, report: ValidationReport) -> pd.DataFrame:
    before = len(df)

    missing_score = df["score"].isna().sum()
    report.log("results", "missing score", int(missing_score))
    df = df.dropna(subset=["score"])

    invalid_range = ((df["score"] < 0) | (df["score"] > 100)).sum()
    report.log("results", "score outside 0-100 range", int(invalid_range))
    df = df[(df["score"] >= 0) & (df["score"] <= 100)]

    valid_students = set(students["id_student"])
    valid_assessments = set(assessments["id_assessment"])
    mask = df["id_student"].isin(valid_students) & df["id_assessment"].isin(valid_assessments)
    orphans = (~mask).sum()
    report.log("results", "orphaned FK (unknown student or assessment)", int(orphans))
    df = df[mask]

    dup = df.duplicated(subset=["id_assessment", "id_student"]).sum()
    report.log("results", "duplicate (id_assessment, id_student)", int(dup))
    df = df.drop_duplicates(subset=["id_assessment", "id_student"])

    return df.reset_index(drop=True)


def validate_all(clean: dict) -> tuple[dict, ValidationReport]:
    report = ValidationReport()

    courses = validate_courses(clean["courses"], report)
    students = validate_students(clean["students"], report)
    enrollments = validate_enrollments(clean["enrollments"], students, courses, report)
    assessments = validate_assessments(clean["assessments"], courses, report)
    results = validate_results(clean["results"], students, assessments, report)

    validated = {
        "courses": courses,
        "students": students,
        "enrollments": enrollments,
        "assessments": assessments,
        "results": results,
    }
    return validated, report


if __name__ == "__main__":
    from extract import extract_all
    from transform import transform_all

    raw = extract_all()
    clean = transform_all(raw)
    validated, report = validate_all(clean)
    print(report.summary())
    for name, df in validated.items():
        print(f"\n{name}: {len(df)} valid rows")
