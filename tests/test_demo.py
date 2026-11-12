import io
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

import pandas as pd
import numpy as np

from talentrag.core import Matcher, coverage, load_data, load_pairs, mentions, passages
from talentrag.uploads import compare_upload, extract_text


class BackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resumes, cls.jobs = load_data()

    def test_alignment_and_ties(self):
        shuffled = self.resumes.sample(frac=1, random_state=4)
        matcher = Matcher(shuffled)
        job = self.jobs.iloc[0]
        for method in ['Skill-only', 'BM25']:
            ranking = matcher.rank(job, method)
            self.assertEqual(set(ranking.resume_id), set(shuffled.resume_id))
            self.assertEqual(len(ranking), len(shuffled))
            for _, group in ranking.groupby('score'):
                self.assertEqual(group.resume_id.tolist(), sorted(group.resume_id))
        expected = sorted(self.resumes.resume_id[self.resumes.skills.map(lambda values: len(set(value.casefold() for value in values) & set(value.casefold() for value in job.must_have_skills))) == matcher.rank(job, 'Skill-only').score.max()])
        self.assertEqual(matcher.rank(job, 'Skill-only').resume_id.iloc[0], expected[0])

    def test_empty_and_unknown_queries(self):
        matcher = Matcher(self.resumes.head(10))
        empty = dict(description='', must_have_skills=[], nice_to_have_skills=[])
        for method in ['Skill-only', 'BM25', 'Semantic']:
            with self.assertRaises(ValueError):
                matcher.rank(empty, method)

    def test_evidence_provenance(self):
        row = dict(skills=['Python'], summary='Engineer', experience_bullets=['Managed delivery.'])
        job = dict(description='Python', must_have_skills=[' python '], nice_to_have_skills=['PYTHON', 'SQL'])
        self.assertEqual(coverage(row, job)['required_matched'], ['python'])
        self.assertEqual(passages(row, job), [])
        self.assertFalse(mentions('JavaScript PostgreSQL', 'Java'))
        self.assertTrue(mentions('Built with C++.', 'c++'))
        self.assertFalse(mentions('C++', 'C'))

    def test_parsing_and_raw_mentions(self):
        self.assertEqual(extract_text('a.txt', b'Built Python APIs'), 'Built Python APIs')
        for name, data in [('a.txt', b''), ('a.docx', b'bad zip'), ('a.exe', b'test'), ('a.txt', b'\xff')]:
            with self.assertRaises(ValueError):
                extract_text(name, data)
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w') as archive:
            archive.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Python project</w:t></w:r></w:p></w:body></w:document>')
        self.assertIn('Python project', extract_text('a.docx', buffer.getvalue()))
        result = compare_upload('Built Python APIs\nPostgreSQL', dict(must_have_skills=['Python', 'SQL'], nice_to_have_skills=[]))
        self.assertEqual(result['required_matched'], ['python'])
        self.assertEqual(result['required_missing'], ['sql'])

    def test_files_and_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, 'Missing processed file'):
                load_data(directory)
        pairs = load_pairs(self.resumes, self.jobs)
        self.assertEqual(len(pairs), 75000)
        with tempfile.TemporaryDirectory() as directory:
            pd.DataFrame({'job_id': ['unknown'], 'resume_id': ['unknown']}).to_csv(directory + '/match_pairs.csv', index=False)
            with self.assertRaisesRegex(ValueError, 'align'):
                load_pairs(self.resumes, self.jobs, directory)

    def test_no_label_ranking_input(self):
        with patch('pandas.read_csv', side_effect=AssertionError('Ranking must not load labels')):
            matcher = Matcher(self.resumes.head(100))
            for method in ['Skill-only', 'BM25']:
                self.assertEqual(len(matcher.rank(self.jobs.iloc[0], method)), 100)

    def test_pdf_text_and_scanned(self):
        def pdf(content):
            objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
                       b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>',
                       b'<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>',
                       b'<< /Length ' + str(len(content)).encode() + b' >>\nstream\n' + content + b'\nendstream']
            data = b'%PDF-1.4\n'
            offsets = [0]
            for number, value in enumerate(objects, 1):
                offsets.append(len(data))
                data += f'{number} 0 obj\n'.encode() + value + b'\nendobj\n'
            start = len(data)
            data += b'xref\n0 6\n0000000000 65535 f \n' + b''.join(f'{offset:010d} 00000 n \n'.encode() for offset in offsets[1:])
            return data + f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF'.encode()
        self.assertIn('Python project', extract_text('test.pdf', pdf(b'BT /F1 12 Tf 72 700 Td (Python project) Tj ET')))
        with self.assertRaisesRegex(ValueError, 'No extractable text'):
            extract_text('scan.pdf', pdf(b''))


if __name__ == '__main__':
    unittest.main()
