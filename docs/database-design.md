# Database design decisions

This document explains *why* `sql/schema.sql` is designed the way it
is — per Phase 2 Day 3's requirement to document the reasoning behind
primary keys, foreign keys, constraints, indexes, and data types, not
just the schema itself.

## Table structure

Five tables map directly onto OULAD's five source files, normalised
into the relational shape the pipeline was built to produce:
`courses`, `students`, `enrollments`, `assessments`, `results`.

`students` is deliberately separate from `enrollments`: OULAD's
`studentInfo.csv` holds one row per student *per course presentation*
(the source of the 3,808 "duplicate" rows found during validation).
Splitting demographic data (`students`, one row per person) from
enrollment data (`enrollments`, one row per person-per-course) avoids
repeating the same demographic values once per course a student took.

## Primary keys

| Table | Primary key | Reasoning |
|---|---|---|
| `courses` | `(code_module, code_presentation)` composite | Neither column alone is unique — the same module (e.g. `BBB`) runs across multiple presentations — but the pair uniquely identifies one course offering |
| `students` | `id_student` | Already a unique identifier in the source data once demographic rows are deduplicated |
| `enrollments` | surrogate `SERIAL` (`enrollment_id`) | No single source column is a natural key; a surrogate key is simpler to reference from other tables than a 3-column composite. The real business key — one enrollment per student per course — is enforced separately via a `UNIQUE` constraint, not the primary key |
| `assessments` | `id_assessment` | Already unique in the source data |
| `results` | surrogate `SERIAL` (`result_id`) | Same reasoning as `enrollments`: business uniqueness (one result per student per assessment) is enforced via `UNIQUE`, not the primary key |

## Foreign keys

Every table that references another has an explicit `FOREIGN KEY`
constraint: `enrollments` and `assessments` reference `courses`;
`enrollments` and `results` reference `students`; `results`
references `assessments`. This was a deliberate choice over leaving
referential integrity to application code (`validate.py`) alone —
`validate.py` catches problems *before* loading, but the foreign keys
mean the database itself refuses to accept an orphaned row even if a
future version of the pipeline (or a different tool entirely) tries
to insert one directly. Two layers of defence, not one.

## Constraints

- `UNIQUE (id_student, code_module, code_presentation)` on
  `enrollments`, and `UNIQUE (id_assessment, id_student)` on
  `results`: enforce the real-world business rule (one enrollment per
  student per course; one result per student per assessment) at the
  database level, independent of whether `validate.py` catches it
  first.
- `CHECK (score >= 0 AND score <= 100)` on `results.score`: the same
  reasoning as the foreign keys above — `validate.py` already
  rejects out-of-range scores before loading, but the `CHECK`
  constraint means the database enforces this rule regardless of
  which code path inserts data.

## Indexes

Indexes were added only on columns actually used in `WHERE` or `JOIN`
clauses in `sql/analytics.sql` — not on every column, since indexes
speed up reads at the cost of slower writes and extra storage, which
isn't worthwhile for columns nothing queries by.

| Index | Justified by |
|---|---|
| `idx_enrollments_student` | `results`/`enrollments` joins to `students` in most analytics queries |
| `idx_enrollments_course` | joins to `courses` (e.g. completion breakdown by course) |
| `idx_results_student` | per-student average score queries |
| `idx_results_assessment` | joins to `assessments` |
| `idx_assessments_course` | `assessments` joins to `courses` in almost every analytics query (added during this Phase 2 Day 3 review — it was missing initially despite being one of the most-used join paths) |

Columns like `students.region` or `enrollments.final_result` are not
indexed: nothing in `sql/analytics.sql` currently filters or joins on
them, so an index there would add write overhead with no read benefit
yet.

## Data types

- `VARCHAR(10)` for `code_module`/`code_presentation`: actual OULAD
  values are short (e.g. `BBB`, `2013J`), sized with headroom rather
  than the exact minimum.
- `INTEGER` for day-offset columns (`date_registration`,
  `date_unregistration`, `date`, `date_submitted`): these are signed
  day counts relative to course start (negative values are valid —
  e.g. registering before the course begins), so an unsigned type
  would be wrong.
- `NUMERIC(5,2)` for `score` and `weight`: both are percentages that
  can carry a fractional component; `NUMERIC` avoids the rounding
  behaviour of floating-point types, which matters when scores feed
  directly into averages reported in the thesis.
- `BOOLEAN` for `is_banked`: the raw source value is a 0/1 flag;
  `transform.py` converts it to a proper boolean before loading, so
  the column type matches what's actually stored, not the raw
  source encoding.
