"""
transform.py
Raw DataFrames -> clean -> standardize -> transform into the target
relational shape (students, courses, enrollments, assessments, results).
"""

import pandas as pd


def transform_courses(courses_raw: pd.DataFrame) -> pd.DataFrame:
    df = courses_raw.copy()
    df["code_module"] = df["code_module"].str.strip()
    df["code_presentation"] = df["code_presentation"].str.strip()
    df = df.drop_duplicates(subset=["code_module", "code_presentation"])
    return df


def transform_students(student_info_raw: pd.DataFrame) -> pd.DataFrame:
    """
    studentInfo.csv has one row per student per course presentation.
    Demographic fields are the same across a student's rows, so this
    narrows to demographic columns and standardizes id_student's type.
    Rows with a missing id_student, and duplicate id_student rows, are
    intentionally NOT dropped here -- that is validate.py's job, so
    those issues are counted and reported rather than silently lost.
    """
    df = student_info_raw.copy()
    df["id_student"] = pd.to_numeric(df["id_student"], errors="coerce").astype("Int64")

    demo_cols = ["id_student", "gender", "region", "highest_education",
                 "imd_band", "age_band", "disability"]
    return df[demo_cols].reset_index(drop=True)


def transform_enrollments(student_info_raw: pd.DataFrame,
                           registration_raw: pd.DataFrame) -> pd.DataFrame:
    df = student_info_raw.copy()
    df["id_student"] = pd.to_numeric(df["id_student"], errors="coerce").astype("Int64")

    reg = registration_raw.copy()
    reg["id_student"] = pd.to_numeric(reg["id_student"], errors="coerce").astype("Int64")

    enroll_cols = ["id_student", "code_module", "code_presentation",
                   "num_of_prev_attempts", "studied_credits", "final_result"]
    enrollments = df[enroll_cols].merge(
        reg[["id_student", "code_module", "code_presentation",
             "date_registration", "date_unregistration"]],
        on=["id_student", "code_module", "code_presentation"],
        how="left",
    )
    # Deliberately not deduplicated here -- validate.py counts and
    # removes exact-duplicate enrollment rows so it shows up in the report.
    return enrollments.reset_index(drop=True)


def transform_assessments(assessments_raw: pd.DataFrame) -> pd.DataFrame:
    df = assessments_raw.copy()
    df = df.dropna(subset=["id_assessment"])
    df["id_assessment"] = df["id_assessment"].astype(int)
    df["weight"] = pd.to_numeric(df["weight"], errors="coerce")
    df = df.drop_duplicates(subset=["id_assessment"])
    return df.reset_index(drop=True)


def transform_results(student_assessment_raw: pd.DataFrame) -> pd.DataFrame:
    df = student_assessment_raw.copy()
    df = df.dropna(subset=["id_assessment", "id_student"])
    df["id_assessment"] = df["id_assessment"].astype(int)
    df["id_student"] = df["id_student"].astype(int)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df["is_banked"] = df["is_banked"].fillna(0).astype(int).astype(bool)
    df = df.drop_duplicates(subset=["id_assessment", "id_student"], keep="first")
    return df.reset_index(drop=True)


def transform_all(raw: dict) -> dict:
    return {
        "courses": transform_courses(raw["courses"]),
        "students": transform_students(raw["studentInfo"]),
        "enrollments": transform_enrollments(raw["studentInfo"], raw["studentRegistration"]),
        "assessments": transform_assessments(raw["assessments"]),
        "results": transform_results(raw["studentAssessment"]),
    }


if __name__ == "__main__":
    from extract import extract_all
    raw = extract_all()
    clean = transform_all(raw)
    for name, df in clean.items():
        print(f"\n{name}: {len(df)} rows")
        print(df.head())
