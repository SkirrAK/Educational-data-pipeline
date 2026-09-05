# Data analysis

All figures in this document were generated automatically by `src/generate_data_analysis_doc.py` from the data actually present in `data/raw/` at generation time (2026-09-04 18:23). Nothing here is hand-typed. Re-run the script any time the dataset changes.

**Source:** OULAD (Open University Learning Analytics Dataset)  
**Format:** CSV, 5 files

## Source documents

### Document: `courses.csv`

| Item | Description |
|---|---|
| Source | OULAD (Open University Learning Analytics Dataset) |
| Format | CSV |
| Rows | 22 |
| Columns | 3 |
| Missing values | None |
| Duplicates | None found |
| Problems | None found by the pipeline's validation checks. |

### Document: `studentInfo.csv`

| Item | Description |
|---|---|
| Source | OULAD (Open University Learning Analytics Dataset) |
| Format | CSV |
| Rows | 32,593 |
| Columns | 12 |
| Missing values | `imd_band`: 1,111 |
| Duplicates | None found |
| Problems | duplicate id_student (3,808) |

### Document: `studentRegistration.csv`

| Item | Description |
|---|---|
| Source | OULAD (Open University Learning Analytics Dataset) |
| Format | CSV |
| Rows | 32,593 |
| Columns | 5 |
| Missing values | `date_registration`: 45; `date_unregistration`: 22,521 |
| Duplicates | None found |
| Problems | None found by the pipeline's validation checks. |

### Document: `assessments.csv`

| Item | Description |
|---|---|
| Source | OULAD (Open University Learning Analytics Dataset) |
| Format | CSV |
| Rows | 206 |
| Columns | 6 |
| Missing values | `date`: 11 |
| Duplicates | None found |
| Problems | None found by the pipeline's validation checks. |

### Document: `studentAssessment.csv`

| Item | Description |
|---|---|
| Source | OULAD (Open University Learning Analytics Dataset) |
| Format | CSV |
| Rows | 173,912 |
| Columns | 5 |
| Missing values | `score`: 173 |
| Duplicates | None found |
| Problems | missing score (173) |

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
