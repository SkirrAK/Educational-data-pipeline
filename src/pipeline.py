"""
pipeline.py
Orchestrates the complete ETL workflow:
Extract -> Transform -> Validate -> Load

Run directly, or trigger on a schedule (Windows Task Scheduler / Cron).
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
    log.info("=== Pipeline run started ===")

    log.info("Step 1/4: Extract")
    raw = extract_all()

    log.info("Step 2/4: Transform")
    clean = transform_all(raw)

    log.info("Step 3/4: Validate")
    validated, report = validate_all(clean)
    log.info(report.summary())

    log.info("Step 4/4: Load")
    load_results = load_all(
        validated,
        schema_path=str(SCHEMA_PATH) if apply_schema else None,
    )

    duration = (datetime.now() - started).total_seconds()
    log.info(f"=== Pipeline run finished in {duration:.2f}s ===")

    return {
        "validation_report": report,
        "load_results": load_results,
        "duration_seconds": duration,
    }


if __name__ == "__main__":
    run()
