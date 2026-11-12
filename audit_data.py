from pathlib import Path

import pandas as pd

raw = Path(__file__).resolve().parent / "data" / "raw"

resumes = pd.read_parquet(raw / "resumes.parquet")
jobs = pd.read_parquet(raw / "jobs.parquet")
matches = pd.read_parquet(raw / "matches.parquet")

for name, df, id_column in [
    ("Resumes", resumes, "resume_id"),
    ("Jobs", jobs, "job_id"),
    ("Matches", matches, "job_id"),
]:
    missing = df.isna().sum()
    print(f"\n--- {name} ---")
    print("Missing values by column:", missing[missing > 0].to_dict() or "None")
    print(f"Repeated {id_column}:", df[id_column].duplicated().sum())

print("\n--- Match links ---")

# Turn each list of resume IDs into one row per job–resume pair.
pairs = matches.explode("relevant_resume_ids").rename(
    columns={"relevant_resume_ids": "resume_id"}
)

print("Rows with no resume ID:", pairs["resume_id"].isna().sum())
pairs = pairs.dropna(subset=["resume_id"])

print(f"Job–resume pairs: {len(pairs):,}")
print("Repeated pairs:", pairs.duplicated(["job_id", "resume_id"]).sum())
print("Match rows with unknown job IDs:", (~matches["job_id"].isin(jobs["job_id"])).sum())
print("Pairs with unknown resume IDs:", (~pairs["resume_id"].isin(resumes["resume_id"])).sum())
