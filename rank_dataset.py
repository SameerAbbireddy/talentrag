from pathlib import Path

import pandas as pd

processed = Path(__file__).resolve().parent / "data" / "processed"

resumes = pd.read_parquet(processed / "resumes.parquet")
jobs = pd.read_parquet(processed / "jobs.parquet")
pairs = pd.read_csv(processed / "match_pairs.csv", dtype=str)

job_id = "J_000000"
job = jobs.loc[jobs["job_id"] == job_id].iloc[0]
required = {skill.casefold() for skill in job["must_have_skills"]}

results = []

for resume in resumes.itertuples(index=False):
    resume_skills = {skill.casefold() for skill in resume.skills}
    matched = required & resume_skills
    results.append((resume.resume_id, resume.role, matched))

# Rank by number of matched skills. Use resume ID to break ties.
results.sort(key=lambda row: (-len(row[2]), row[0]))

listed_ids = set(pairs.loc[pairs["job_id"] == job_id, "resume_id"])
top_five = results[:5]

print(f"Job: {job['job_title']} ({job_id})")
print("Required skills:", ", ".join(sorted(required)))
print(f"Resumes scored: {len(results):,}\n")

for rank, (resume_id, role, matched) in enumerate(top_five, start=1):
    print(f"{rank}. {resume_id} | {role} | {len(matched)}/{len(required)}")
    print(f"   Matched: {', '.join(sorted(matched)) or 'None'}")

listed_hits = sum(resume_id in listed_ids for resume_id, _, _ in top_five)
print(f"\nTop 5 also listed by the dataset: {listed_hits}/5")

from collections import Counter

all_scores = Counter(len(matched) for _, _, matched in results)
listed_scores = Counter(
    len(matched)
    for resume_id, _, matched in results
    if resume_id in listed_ids
)

print("\nSkill coverage | All candidates | Dataset-listed candidates")
for score in range(len(required), -1, -1):
    print(
        f"{score}/{len(required)}"
        f" | {all_scores[score]:,}"
        f" | {listed_scores[score]:,}"
    )
job_seniority = job["seniority"].strip().casefold()

resume_seniority = {
    row.resume_id: row.seniority.strip().casefold()
    for row in resumes.itertuples(index=False)
}


def same_seniority(resume_id):
    return resume_seniority[resume_id] == job_seniority


# Sort by skill coverage first, seniority match second, and ID last.
reranked = sorted(
    results,
    key=lambda row: (-len(row[2]), -int(same_seniority(row[0])), row[0]),
)

print(f"\nJob seniority: {job['seniority']}")
print("Top 5 with seniority as a tiebreaker:")

for rank, (resume_id, role, matched) in enumerate(reranked[:5], start=1):
    seniority = resume_seniority[resume_id]
    print(f"{rank}. {resume_id} | {role} | {len(matched)}/{len(required)} | {seniority}")

new_hits = sum(resume_id in listed_ids for resume_id, _, _ in reranked[:5])

print(f"\nSkill-only baseline: {listed_hits}/5 listed matches")
print(f"With seniority tiebreaker: {new_hits}/5 listed matches")

# Prepare each candidate's skill set once and reuse it across jobs.
candidate_skills = {
    row.resume_id: {skill.casefold() for skill in row.skills}
    for row in resumes.itertuples(index=False)
}

# Test on 20 other jobs. The seed gives us the same sample each run.
sample_jobs = jobs.loc[jobs["job_id"] != job_id].sample(n=20, random_state=42)
skill_only_hits = []
seniority_hits = []

for sample_job in sample_jobs.itertuples(index=False):
    needed = {skill.casefold() for skill in sample_job.must_have_skills}
    level = sample_job.seniority.strip().casefold()

    scores = [
        (resume_id, len(needed & skills))
        for resume_id, skills in candidate_skills.items()
    ]

    skill_only = sorted(scores, key=lambda row: (-row[1], row[0]))[:5]
    with_seniority = sorted(
        scores,
        key=lambda row: (
            -row[1],
            -int(resume_seniority[row[0]] == level),
            row[0],
        ),
    )[:5]

    listed = set(pairs.loc[pairs["job_id"] == sample_job.job_id, "resume_id"])
    skill_only_hits.append(sum(resume_id in listed for resume_id, _ in skill_only))
    seniority_hits.append(sum(resume_id in listed for resume_id, _ in with_seniority))

print("\n--- Comparison across 20 other jobs ---")
print(f"Skill only: {sum(skill_only_hits) / len(sample_jobs):.2f} listed matches per top 5")
print(f"With seniority: {sum(seniority_hits) / len(sample_jobs):.2f} listed matches per top 5")
print("Jobs improved:", sum(b > a for a, b in zip(skill_only_hits, seniority_hits)))
print("Jobs unchanged:", sum(b == a for a, b in zip(skill_only_hits, seniority_hits)))
print("Jobs worsened:", sum(b < a for a, b in zip(skill_only_hits, seniority_hits)))

preferred_hits = []

for sample_job in sample_jobs.itertuples(index=False):
    needed = {skill.casefold() for skill in sample_job.must_have_skills}
    preferred = {
        skill.casefold() for skill in sample_job.nice_to_have_skills
    } - needed  # Don't count a skill as both required and preferred.

    scores = []
    for resume_id, skills in candidate_skills.items():
        required_count = len(needed & skills)
        preferred_count = len(preferred & skills)
        total = 2 * required_count + preferred_count
        scores.append((resume_id, total, required_count))

    # Higher total first. If tied, prefer more required skills.
    top_five = sorted(
        scores, key=lambda row: (-row[1], -row[2], row[0])
    )[:5]

    listed = set(pairs.loc[pairs["job_id"] == sample_job.job_id, "resume_id"])
    preferred_hits.append(sum(resume_id in listed for resume_id, _, _ in top_five))

print("\n--- Preferred-skill experiment: same 20 jobs ---")
print(f"Skill-only baseline: {sum(skill_only_hits) / len(sample_jobs):.2f} listed matches per top 5")
print(f"Required + preferred: {sum(preferred_hits) / len(sample_jobs):.2f} listed matches per top 5")
print("Jobs improved:", sum(b > a for a, b in zip(skill_only_hits, preferred_hits)))
print("Jobs unchanged:", sum(b == a for a, b in zip(skill_only_hits, preferred_hits)))
print("Jobs worsened:", sum(b < a for a, b in zip(skill_only_hits, preferred_hits)))