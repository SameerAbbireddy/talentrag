import re

# Job description: "Looking for a junior backend developer
# with Python, SQL, and Flask experience."
required_skills = {"python", "sql", "flask"}

resumes = {
    "Candidate A": "Built a Flask app using Python and SQL.",
    "Candidate B": "Used Python and SQL to analyse sales data.",
    "Candidate C": "Used Python to automate file backups.",
}

results = []

for candidate, resume in resumes.items():
    words = set(re.findall(r"\b\w+\b", resume.lower()))
    matched_skills = required_skills & words
    results.append((candidate, matched_skills))

results.sort(key=lambda result: len(result[1]), reverse=True)

for rank, (candidate, matched) in enumerate(results, start=1):
    skills = ", ".join(sorted(matched)) or "None"
    print(f"{rank}. {candidate}: {len(matched)}/{len(required_skills)} — {skills}")