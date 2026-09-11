# Educational Data Pipeline

Automated ETL pipeline for educational analytics, built with Python,
Pandas and PostgreSQL, using the OULAD (Open University Learning
Analytics Dataset).

## Project structure

```
educational-data-pipeline/
├── data/
│   ├── raw/                # place the OULAD CSVs here
│   └── processed/
├── src/
│   ├── config.py                        # shared DB config (single source of truth)
│   ├── extract.py                       # Source -> DataFrame
│   ├── transform.py                     # clean, standardize, reshape
│   ├── validate.py                      # data-quality checks, FK integrity
│   ├── load.py                          # DataFrame -> PostgreSQL
│   ├── pipeline.py                      # orchestrates all four steps
│   ├── test_database.py                 # standalone Python<->PostgreSQL connection check
│   ├── generate_data_analysis_doc.py    # auto-generates docs/data-analysis.md
│   └── generate_end_to_end_test_report.py  # auto-generates docs/end-to-end-test.md
├── scripts/
│   ├── run_pipeline.bat    # Windows Task Scheduler trigger
│   └── run_pipeline.sh     # Cron trigger (macOS/Linux)
├── sql/
│   ├── schema.sql          # table definitions (PK/FK/constraints/indexes)
│   └── analytics.sql       # analytical queries
├── tests/
│   ├── fixtures/            # small, fixed test dataset (NOT data/raw/)
│   ├── test_pipeline.py    # extraction/transformation/validation tests
│   └── test_load.py        # database insertion + FK-constraint tests
├── docs/
│   ├── requirements.md            # FR/NFR, Phase 1 Day 1
│   ├── data-analysis.md           # data profiling findings, Phase 1 Day 2 (auto-generated)
│   ├── architecture.png           # pipeline architecture diagram, Phase 1 Day 3
│   ├── database-design.md         # schema decisions and reasoning, Phase 2 Day 3
│   ├── automation.md              # scheduler setup, Phase 2 Day 4
│   ├── end-to-end-test.md         # Phase 2 Day 8 (auto-generated -- run the script to create it)
│   └── pipeline-documentation.md  # extraction/transformation/validation notes, Phase 1 Days 5-7
├── logs/                   # pipeline run logs (created automatically)
└── requirements.txt
```

**Note on `tests/fixtures/` vs `data/raw/`:** tests run against a
small, fixed sample dataset in `tests/fixtures/` — not whatever is
currently in `data/raw/` (which holds the full real OULAD download in
normal use). This keeps test assertions stable regardless of dataset
size or which real-world data-quality issues happen to be present.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install PostgreSQL locally and create the database (via pgAdmin,
   or `createdb educational_analytics` if `createdb` is on your PATH).

3. Set connection details via environment variables (defaults shown):
   ```bash
   export PGHOST=localhost
   export PGPORT=5432
   export PGDATABASE=educational_analytics
   export PGUSER=postgres
   export PGPASSWORD=postgres
   ```

## Getting the real data

Download OULAD from Kaggle:
https://www.kaggle.com/datasets/anlgrbz/student-demographics-online-education-dataoulad

Copy these five files into `data/raw/`, keeping their original names:
`courses.csv`, `studentInfo.csv`, `studentRegistration.csv`,
`assessments.csv`, `studentAssessment.csv`.
(`vle.csv` and `studentVle.csv` are not used — out of scope.)

## Running

Run the full pipeline (extract → transform → validate → load):
```bash
cd src
python pipeline.py
```

This applies `sql/schema.sql` (drops and recreates tables) and loads
the validated data. A summary of any data-quality issues found is
printed and logged to `logs/pipeline.log`.

Run individual stages for debugging:
```bash
python test_database.py   # confirm the DB connection works first
python extract.py
python transform.py
python validate.py
```

Run analytical queries:
```bash
psql -d educational_analytics -f ../sql/analytics.sql
```

Regenerate the data-analysis and end-to-end-test docs from the
current real data:
```bash
python generate_data_analysis_doc.py
python generate_end_to_end_test_report.py
```

## Testing

```bash
pytest tests/ -v
```

`test_load.py` runs against a dedicated `educational_analytics_test`
database (created and dropped automatically) — it never touches your
real data. It's skipped automatically if no PostgreSQL server is
reachable.

## Automation

See `docs/automation.md` for full setup. Quick version:
- **Windows:** Task Scheduler → Action → Start a program →
  `scripts/run_pipeline.bat`
- **macOS/Linux:** cron entry running `scripts/run_pipeline.sh`

Each run logs identically whether triggered manually or by a
scheduler, so scheduled runs are auditable via `logs/pipeline.log`.
