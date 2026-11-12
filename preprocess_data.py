from pathlib import Path

import pandas as pd

data = Path(__file__).resolve().parent / "data"
raw = data / "raw"
processed = data / "processed"
processed.mkdir(exist_ok=True)

resumes = pd.read_parquet(raw / "resumes.parquet")
jobs = pd.read_parquet(raw / "jobs.parquet")
matches = pd.read_parquet(raw / "matches.parquet")


def clean_text(text):
    return " ".join(text.split())


def clean_skills(skills):
    result = []
    seen = set()

    for skill in skills:
        skill = clean_text(skill)
        key = skill.casefold()
        if skill and key not in seen:
            result.append(skill)
            seen.add(key)

    return result


for column in ["role", "seniority", "industry", "education", "summary"]:
    resumes[column] = resumes[column].map(clean_text)

for column in ["job_title", "seniority", "industry", "description"]:
    jobs[column] = jobs[column].map(clean_text)

resumes["skills"] = resumes["skills"].map(clean_skills)

for column in ["must_have_skills", "nice_to_have_skills"]:
    jobs[column] = jobs[column].map(clean_skills)

pairs = matches.explode("relevant_resume_ids", ignore_index=True).rename(
    columns={"relevant_resume_ids": "resume_id"}
)

resumes.to_parquet(processed / "resumes.parquet", index=False)
jobs.to_parquet(processed / "jobs.parquet", index=False)
pairs[["job_id", "resume_id"]].to_csv(processed / "match_pairs.csv", index=False)

print(f"Saved {len(resumes):,} resumes")
print(f"Saved {len(jobs):,} jobs")
print(f"Saved {len(pairs):,} match pairs")