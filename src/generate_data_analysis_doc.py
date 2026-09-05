"""
generate_data_analysis_doc.py

Automatically generates docs/data-analysis.md from whatever dataset
is currently in data/raw/, using real pandas profiling and the
actual pipeline's transform/validate logic. No numbers in the output
are hand-typed -- everything is computed directly from the data.

Covers every item the thesis guidelines ask for on Phase 1 Day 2:
rows, columns, data types, missing values, duplicate records, invalid
values (via the real validation checks), and relationships between
datasets.

Run this any time the dataset changes, to keep the documentation
in sync with reality:

    cd src
    python generate_data_analysis_doc.py
"""

from pathlib import Path
from datetime import datetime

from extract import extract_all, REQUIRED_FILES
from transform import transform_all
from validate import validate_all

BASE_DIR = Path(__file__).resolve().parent.parent
DOCS_PATH = BASE_DIR / "docs" / "data-analysis.md"

# Structural relationships between the source files. These describe
# how transform.py actually joins the data (fixed by design, not
# computed from the data itself).
RELATIONSHIPS = [
    ("studentInfo.csv", "studentRegistration.csv",
     "(id_student, code_module, code_presentation)"),
    ("assessments.csv", "courses.csv",
     "(code_module, code_presentation)"),
    ("studentAssessment.csv", "assessments.csv", "id_assessment"),
    ("studentAssessment.csv", "studentInfo.csv", "id_student"),
]


# Maps a raw source file to the pipeline table its rows end up in,
# so validation findings (logged per-table in validate.py) can be
# attributed back to the correct source document below.
SOURCE_TABLE = {
    "courses.csv": "courses",
    "studentInfo.csv": "students",
    "studentRegistration.csv": "enrollments",
    "assessments.csv": "assessments",
    "studentAssessment.csv": "results",
}


def profile_file(display_name: str, df, issues: list) -> str:
    """Item/Description summary card for one source document."""
    lines = [f"### Document: `{display_name}`", ""]
    lines.append("| Item | Description |")
    lines.append("|---|---|")
    lines.append("| Source | OULAD (Open University Learning Analytics Dataset) |")
    lines.append("| Format | CSV |")
    lines.append(f"| Rows | {len(df):,} |")
    lines.append(f"| Columns | {len(df.columns)} |")

    missing = df.isna().sum()
    missing_cols = [(col, int(c)) for col, c in missing.items() if c > 0]
    if missing_cols:
        missing_str = "; ".join(f"`{col}`: {c:,}" for col, c in missing_cols)
    else:
        missing_str = "None"
    lines.append(f"| Missing values | {missing_str} |")

    dup = int(df.duplicated().sum())
    dup_str = f"{dup:,} fully duplicate row(s)" if dup else "None found"
    lines.append(f"| Duplicates | {dup_str} |")

    table = SOURCE_TABLE.get(display_name)
    file_issues = [i for i in issues if i["table"] == table]
    if file_issues:
        problems_str = "; ".join(
            f"{i['check']} ({i['rows_affected']:,})" for i in file_issues
        )
    else:
        problems_str = "None found by the pipeline's validation checks."
    lines.append(f"| Problems | {problems_str} |")
    lines.append("")
    return "\n".join(lines)


def main():
    raw = extract_all()
    total_rows = sum(len(df) for df in raw.values())

    out = []
    out.append("# Data analysis\n")
    out.append(
        "All figures in this document were generated automatically by "
        "`src/generate_data_analysis_doc.py` from the data actually "
        f"present in `data/raw/` at generation time "
        f"({datetime.now():%Y-%m-%d %H:%M}). Nothing here is hand-typed. "
        "Re-run the script any time the dataset changes.\n"
    )
    out.append("**Source:** OULAD (Open University Learning Analytics Dataset)  ")
    out.append(f"**Format:** CSV, {len(REQUIRED_FILES)} files\n")

    # Run the real transform + validate steps first so each per-file
    # card below can show its actual "Problems" findings (invalid
    # values, duplicate business keys, orphaned FKs) rather than just
    # full-row duplicates.
    clean = transform_all(raw)
    validated, report = validate_all(clean)

    out.append("## Source documents\n")
    for key, filename in REQUIRED_FILES.items():
        out.append(profile_file(filename, raw[key], report.issues))

    out.append("## Relationships between datasets\n")
    for left, right, key in RELATIONSHIPS:
        out.append(f"- `{left}` ↔ `{right}` on **{key}**")
    out.append("")

    out.append("## Validation findings (from the actual pipeline)\n")
    if report.issues:
        out.append("| Table | Check | Rows affected |")
        out.append("|---|---|---|")
        for issue in report.issues:
            out.append(f"| {issue['table']} | {issue['check']} | {issue['rows_affected']:,} |")
    else:
        out.append("No data-quality issues found by any check.")
    out.append("")
    out.append(
        "*Checks run: required ID present, duplicate records, score "
        "range (0–100), and referential integrity between all tables. "
        "A check not listed above found zero issues — it still ran, "
        "it simply found nothing wrong.*\n"
    )

    out.append("## Load summary (valid records after validation)\n")
    out.append("| Table | Records |")
    out.append("|---|---|")
    for name, df in validated.items():
        out.append(f"| {name} | {len(df):,} |")
    out.append("")

    out.append(
        f"## Summary\n\nTotal raw rows across all {len(REQUIRED_FILES)} "
        f"source files: {total_rows:,}. See "
        "`docs/pipeline-documentation.md` for extraction, transformation "
        "and validation methodology, and `logs/pipeline.log` for the "
        "full pipeline run log.\n"
    )

    DOCS_PATH.parent.mkdir(exist_ok=True)
    DOCS_PATH.write_text("\n".join(out), encoding="utf-8")
    print(f"Wrote {DOCS_PATH} ({DOCS_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()