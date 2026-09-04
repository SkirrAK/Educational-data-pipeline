# Data analysis

All figures in this document were generated automatically by `src/generate_data_analysis_doc.py` from the data actually present in `data/raw/` at generation time (2026-09-04 17:47). Nothing here is hand-typed. Re-run the script any time the dataset changes.

**Source:** OULAD (Open University Learning Analytics Dataset)  
**Format:** CSV, 5 files

## courses.csv

- **Rows:** 22
- **Columns:** 3
- **Data types:** 2 str, 1 int64
- **Fully duplicate rows:** 0

| Column | Type | Missing values |
|---|---|---|
| `code_module` | str | — |
| `code_presentation` | str | — |
| `module_presentation_length` | int64 | — |

## studentInfo.csv

- **Rows:** 32,593
- **Columns:** 12
- **Data types:** 9 str, 3 int64
- **Fully duplicate rows:** 0

| Column | Type | Missing values |
|---|---|---|
| `code_module` | str | — |
| `code_presentation` | str | — |
| `id_student` | int64 | — |
| `gender` | str | — |
| `region` | str | — |
| `highest_education` | str | — |
| `imd_band` | str | 1,111 |
| `age_band` | str | — |
| `num_of_prev_attempts` | int64 | — |
| `studied_credits` | int64 | — |
| `disability` | str | — |
| `final_result` | str | — |

## studentRegistration.csv

- **Rows:** 32,593
- **Columns:** 5
- **Data types:** 2 str, 2 float64, 1 int64
- **Fully duplicate rows:** 0

| Column | Type | Missing values |
|---|---|---|
| `code_module` | str | — |
| `code_presentation` | str | — |
| `id_student` | int64 | — |
| `date_registration` | float64 | 45 |
| `date_unregistration` | float64 | 22,521 |

## assessments.csv

- **Rows:** 206
- **Columns:** 6
- **Data types:** 3 str, 2 float64, 1 int64
- **Fully duplicate rows:** 0

| Column | Type | Missing values |
|---|---|---|
| `code_module` | str | — |
| `code_presentation` | str | — |
| `id_assessment` | int64 | — |
| `assessment_type` | str | — |
| `date` | float64 | 11 |
| `weight` | float64 | — |

## studentAssessment.csv

- **Rows:** 173,912
- **Columns:** 5
- **Data types:** 4 int64, 1 float64
- **Fully duplicate rows:** 0

| Column | Type | Missing values |
|---|---|---|
| `id_assessment` | int64 | — |
| `id_student` | int64 | — |
| `date_submitted` | int64 | — |
| `is_banked` | int64 | — |
| `score` | float64 | 173 |

## Relationships between datasets

- `studentInfo.csv` ↔ `studentRegistration.csv` on **(id_student, code_module, code_presentation)**
- `assessments.csv` ↔ `courses.csv` on **(code_module, code_presentation)**
- `studentAssessment.csv` ↔ `assessments.csv` on **id_assessment**
- `studentAssessment.csv` ↔ `studentInfo.csv` on **id_student**

## Validation findings (from the actual pipeline)

| Table | Check | Rows affected |
|---|---|---|
| students | duplicate id_student | 3,808 |
| results | missing score | 173 |

*Checks run: required ID present, duplicate records, score range (0–100), and referential integrity between all tables. A check not listed above found zero issues — it still ran, it simply found nothing wrong.*

## Load summary (valid records after validation)

| Table | Records |
|---|---|
| courses | 22 |
| students | 28,785 |
| enrollments | 32,593 |
| assessments | 206 |
| results | 173,739 |

## Summary

Total raw rows across all 5 source files: 239,326. See `docs/pipeline-documentation.md` for extraction, transformation and validation methodology, and `logs/pipeline.log` for the full pipeline run log.
