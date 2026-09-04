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


def profile_file(display_name: str, df) -> str:
    lines = [f"## {display_name}", ""]
    lines.append(f"- **Rows:** {len(df):,}")
    lines.append(f"- **Columns:** {len(df.columns)}")

    dtype_counts = df.dtypes.astype(str).value_counts().to_dict()
    dtype_str = ", ".join(f"{count} {dtype}" for dtype, count in dtype_counts.items())
    lines.append(f"- **Data types:** {dtype_str}")

    dup = df.duplicated().sum()
    lines.append(f"- **Fully duplicate rows:** {dup:,}")
    lines.append("")

    lines.append("| Column | Type | Missing values |")
    lines.append("|---|---|---|")
    missing = df.isna().sum()
    for col in df.columns:
        miss = missing[col]
        miss_str = f"{miss:,}" if miss > 0 else "—"
        lines.append(f"| `{col}` | {df[col].dtype} | {miss_str} |")
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

    for key, filename in REQUIRED_FILES.items():
        out.append(profile_file(filename, raw[key]))

    out.append("## Relationships between datasets\n")
    for left, right, key in RELATIONSHIPS:
        out.append(f"- `{left}` ↔ `{right}` on **{key}**")
    out.append("")

    # Run the real transform + validate steps to get the pipeline's
    # actual data-quality findings (this covers "invalid values" and
    # "duplicate records" in the guideline's sense -- e.g. repeated
    # business keys and out-of-range values, not just full-row dupes).
    clean = transform_all(raw)
    validated, report = validate_all(clean)

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