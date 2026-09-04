# Educational Data Pipeline — Phase 1

Python + PostgreSQL pipeline: extract → transform → validate → load,
built for the OULAD dataset.

## Setup

```bash
pip install -r requirements.txt
```

Install PostgreSQL locally, then:

```bash
createdb educational_analytics
```

Set connection details via environment variables (defaults shown):

```bash
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=educational_analytics
export PGUSER=postgres
export PGPASSWORD=admin123
```

## Add your data

Put your downloaded OULAD files into `data/raw/`, unmodified,
with their original names:

```
data/raw/courses.csv
data/raw/studentInfo.csv
data/raw/studentRegistration.csv
data/raw/assessments.csv
data/raw/studentAssessment.csv
```

(`vle.csv` and `studentVle.csv` are not used.)

## Run

Check the DB connection first:
```bash
cd src
python test_database.py
```

Run the full pipeline (applies `sql/schema.sql`, then extract → transform → validate → load):
```bash
python pipeline.py
```

This prints and logs (`logs/pipeline.log`) a validation summary —
how many records were rejected and why — before loading the clean
records into PostgreSQL.

Run stages individually for debugging:
```bash
python extract.py
python transform.py
python validate.py
```

## Test

```bash
cd ..
pytest tests/ -v
```
