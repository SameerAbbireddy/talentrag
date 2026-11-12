from pathlib import Path

import pandas as pd

processed = Path(__file__).resolve().parent / "data" / "processed"

resumes = pd.read_parquet(processed / "resumes.parquet")
jobs = pd.read_parquet(processed / "jobs.parquet")
pairs = pd.read_csv(processed / "match_pairs.csv", dtype=str)

job_id = pairs["job_id"].iloc[0]
job = jobs.loc[jobs["job_id"] == job_id].iloc[0]

job_pairs = pairs.loc[pairs["job_id"] == job_id]
linked_resumes = job_pairs.merge(
    resumes[["resume_id", "role", "skills"]],
    on="resume_id",
    how="left",
    validate="many_to_one",
    indicator=True,
)

print(f"Job: {job['job_title']} ({job_id})")
print("Required skills:", ", ".join(job["must_have_skills"]))
print("Listed matches:", len(job_pairs))
print("Resume IDs found:", linked_resumes["_merge"].eq("both").sum())

print("\nFirst three linked resumes:")
for row in linked_resumes.head(3).itertuples(index=False):
    print(f"- {row.resume_id}: {row.role} | {', '.join(row.skills)}")
    