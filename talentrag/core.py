from pathlib import Path
import re
from collections import Counter
import math

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def normalize(text):
    return ' '.join(str(text).casefold().split())


def skills(values):
    return {normalize(value) for value in values if normalize(value)}


def tokenize(text):
    return re.findall(r'[\w]+(?:[+#]+)?', normalize(text))


def mentions(text, skill):
    return bool(re.search(r'(?<![\w+#])' + re.escape(normalize(skill)) + r'(?![\w+#])', normalize(text)))


def load_data(directory=ROOT / 'data' / 'processed'):
    directory = Path(directory)
    required = {'resumes.parquet': ['resume_id', 'role', 'summary', 'skills', 'experience_bullets', 'seniority', 'years_experience', 'industry'],
                'jobs.parquet': ['job_id', 'job_title', 'description', 'must_have_skills', 'nice_to_have_skills']}
    frames = []
    for filename, columns in required.items():
        path = directory / filename
        if not path.exists():
            raise ValueError(f'Missing processed file: {path}. Run the original preprocessing scripts.')
        frame = pd.read_parquet(path)
        if frame.empty or not set(columns).issubset(frame.columns):
            raise ValueError(f'Empty or invalid schema: {filename}')
        identifier = columns[0]
        if frame[identifier].isna().any() or frame[identifier].duplicated().any():
            raise ValueError(f'Missing or duplicate IDs in {filename}')
        frames.append(frame)
    return tuple(frames)


def load_pairs(resumes, jobs, directory=ROOT / 'data' / 'processed'):
    path = Path(directory) / 'match_pairs.csv'
    if not path.exists():
        raise ValueError(f'Missing label file: {path}')
    pairs = pd.read_csv(path, dtype=str)
    if not {'job_id', 'resume_id'}.issubset(pairs.columns):
        raise ValueError('Invalid match-pair columns')
    if not set(pairs.job_id).issubset(set(jobs.job_id)) or not set(pairs.resume_id).issubset(set(resumes.resume_id)):
        raise ValueError('Label IDs do not align with processed data')
    return pairs.drop_duplicates()


def candidate_text(row):
    return f"Role: {row['role']}\nSummary: {row['summary']}\nSkills list: {', '.join(row['skills'])}\nExperience: " + '\n'.join(row['experience_bullets'])


def query_text(job):
    return str(job['description']) + '\nRequired skills: ' + ', '.join(job['must_have_skills']) + '\nPreferred skills: ' + ', '.join(job['nice_to_have_skills'])


def coverage(row, job):
    available = skills(row['skills'])
    required = skills(job['must_have_skills'])
    preferred = skills(job['nice_to_have_skills']) - required
    return {'required_matched': sorted(required & available), 'required_missing': sorted(required - available),
            'preferred_matched': sorted(preferred & available), 'preferred_missing': sorted(preferred - available)}


def passages(row, job):
    terms = skills(job['must_have_skills']) | skills(job['nice_to_have_skills'])
    if not terms:
        terms = set(tokenize(job['description'])) - {'a', 'the', 'and', 'in', 'to', 'of', 'with', 'for', 'we', 'are', 'hiring'}
    sections = [('summary', str(row['summary']))] + [('experience', str(bullet)) for bullet in row['experience_bullets']]
    return [(section, text) for section, text in sections if any(mentions(text, term) for term in terms)]


class LocalBM25:
    """Offline Okapi implementation, used only when rank-bm25 is absent."""

    def __init__(self, corpus):
        self.frequencies = [Counter(document) for document in corpus]
        self.lengths = np.array([len(document) for document in corpus])
        self.average = float(self.lengths.mean()) or 1
        counts = Counter(term for document in self.frequencies for term in document)
        self.idf = {term: math.log(len(corpus) - count + .5) - math.log(count + .5) for term, count in counts.items()}
        floor = .25 * sum(self.idf.values()) / max(1, len(self.idf))
        self.idf = {term: max(value, floor) if value < 0 else value for term, value in self.idf.items()}

    def get_scores(self, query):
        scores = np.zeros(len(self.frequencies))
        for term in query:
            frequency = np.array([document.get(term, 0) for document in self.frequencies])
            scores += self.idf.get(term, 0) * frequency * 2.5 / (frequency + 1.5 * (.25 + .75 * self.lengths / self.average))
        return scores


class Matcher:
    def __init__(self, resumes):
        self.resumes = resumes.reset_index(drop=True).copy()
        self.ids = self.resumes.resume_id.tolist()
        self.skill_sets = [skills(value) for value in self.resumes.skills]
        self.index = None
        try:
            from rank_bm25 import BM25Okapi
            self.index_class = BM25Okapi
            self.bm25_engine = 'rank-bm25 0.2.2 / BM25Okapi'
        except ImportError:
            self.index_class = LocalBM25
            self.bm25_engine = 'Local Okapi fallback (rank-bm25 unavailable)'

    def rank(self, job, method):
        if method not in ('Skill-only', 'BM25'):
            raise ValueError('Method unavailable')
        if not tokenize(str(job['description'])) and not skills(job['must_have_skills']) and not skills(job['nice_to_have_skills']):
            raise ValueError('Enter a job description or at least one skill.')
        if method == 'Skill-only':
            required = skills(job['must_have_skills'])
            if not required:
                raise ValueError('Skill-only ranking requires at least one required skill.')
            scores = [len(required & available) for available in self.skill_sets]
        else:
            if self.index is None:
                self.index = self.index_class([tokenize(candidate_text(row)) for _, row in self.resumes.iterrows()])
            scores = self.index.get_scores(tokenize(query_text(job)))
        results = pd.DataFrame({'resume_id': self.ids, 'score': scores})
        return results.sort_values(['score', 'resume_id'], ascending=[False, True], kind='stable').reset_index(drop=True)
