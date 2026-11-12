import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import pandas as pd
from talentrag.core import Matcher, load_data, load_pairs


def evaluate(output='results/development.csv'):
    resumes, jobs = load_data()
    pairs = load_pairs(resumes, jobs)
    sample = jobs.loc[jobs.job_id != 'J_000000'].sample(n=20, random_state=42)
    matcher = Matcher(resumes)
    rows = []
    for method in ['Skill-only', 'BM25']:
        for _, job in sample.iterrows():
            start = perf_counter()
            top = matcher.rank(job, method).head(5).resume_id.tolist()
            elapsed = perf_counter() - start
            listed = set(pairs.loc[pairs.job_id == job.job_id, 'resume_id'])
            hits = len(set(top) & listed)
            rows.append(dict(method=method, engine=matcher.bm25_engine if method == 'BM25' else 'exact required skills; ID ties', job_id=job.job_id,
                             candidate_count=len(resumes), listed_positives=len(listed), listed_positive_overlap_at_5=hits,
                             listed_positive_recall_at_5=hits / len(listed) if listed else None,
                             seconds=elapsed, top_5_ids=';'.join(top)))
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(output, index=False)
    output.with_suffix('.json').write_text(json.dumps({'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'sample_job_ids': sample.job_id.tolist(), 'seed': 42, 'candidate_count': len(resumes),
        'overlap_definition': 'Count of top five IDs also in source-listed positives (0..5)',
        'recall_definition': 'Listed-positive overlap / number of distinct source positives for that job',
        'labels': 'Synthetic/incomplete source positives; unlisted pairs are unlabeled. Development sample, not held-out accuracy.'}, indent=2))
    print(frame.groupby('method')[['listed_positive_overlap_at_5', 'listed_positive_recall_at_5', 'seconds']].mean().to_string())
    return frame


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='results/development.csv')
    evaluate(parser.parse_args().output)
