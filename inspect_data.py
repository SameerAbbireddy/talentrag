from pathlib import Path

import pandas as pd

raw_folder = Path(__file__).resolve().parent / "data" / "raw"

for name in ("resumes", "jobs", "matches"):
    df = pd.read_parquet(raw_folder / f"{name}.parquet")

    print(f"\n--- {name.upper()} ---")
    print(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
    print(df.dtypes.to_string())