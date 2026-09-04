"""
extract.py
Reads the raw OULAD source CSV files into pandas DataFrames.
Responsibility: Source -> DataFrame. No cleaning or transformation here.
"""

import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

REQUIRED_FILES = {
    "courses": "courses.csv",
    "studentInfo": "studentInfo.csv",
    "studentRegistration": "studentRegistration.csv",
    "assessments": "assessments.csv",
    "studentAssessment": "studentAssessment.csv",
}


def extract_all(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    """
    Locate and read all required source files.
    Returns a dict of {table_name: DataFrame}.
    Raises FileNotFoundError with a clear message if a source file is missing.
    """
    frames = {}
    for name, filename in REQUIRED_FILES.items():
        path = raw_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Required source file not found: {path}. "
                f"Place the OULAD CSV files in {raw_dir}."
            )
        df = pd.read_csv(path)
        frames[name] = df
        print(f"[extract] {filename}: {len(df)} records, columns={list(df.columns)}")
    return frames


if __name__ == "__main__":
    data = extract_all()
    for name, df in data.items():
        print(f"\n{name} preview:")
        print(df.head())
