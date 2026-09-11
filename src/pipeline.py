"""
pipeline.py
Orchestrates the complete ETL workflow:
Trigger -> pipeline.py -> Extract -> Transform -> Validate -> Load

Run directly, or trigger on a schedule (Windows Task Scheduler / Cron
-- see scripts/run_pipeline.bat and scripts/run_pipeline.sh).

Handles expected errors explicitly rather than letting a raw
traceback reach the person running it:
  - missing input file        (extract.py raises FileNotFoundError)
  - database connection failure (load.py raises OperationalError)
  - empty dataset             (load.py raises ValueError if every
                                 validated table is empty)
  - invalid data               (validate.py never raises -- it
                                 removes and reports bad rows instead,
                                 so the pipeline can still complete)
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

from extract import extract_all
from transform import transform_all
from validate import validate_all
from load import load_all

BASE_DIR = Path(__file__).resolve().parent.parent
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "pipeline.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("pipeline")


def run(apply_schema: bool = True) -> dict:
    started = datetime.now()
    log.info("Pipeline started")

    try:
        raw = extract_all()
    except FileNotFoundError as e:
        log.error(f"Pipeline stopped: missing input file. {e}")
        raise
    log.info("Data extracted")

    clean = transform_all(raw)
    log.info("Transformation completed")

    validated, report = validate_all(clean)
    log.info("Validation completed")
    log.info(report.summary())

    try:
        load_results = load_all(
            validated,
            schema_path=str(SCHEMA_PATH) if apply_schema else None,
        )
    except Exception as e:
        log.error(f"Pipeline stopped during load: {e}")
        raise

    duration = (datetime.now() - started).total_seconds()
    log.info(f"Pipeline completed in {duration:.2f}s")

    return {
        "validation_report": report,
        "load_results": load_results,
        "duration_seconds": duration,
    }


if __name__ == "__main__":
    try:
        run()
    except Exception:
        log.error("Pipeline run FAILED -- see error above for the cause.")
        sys.exit(1)
