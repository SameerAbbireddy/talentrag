import pandas as pd

from talentrag.runtime import streamlit_module

st = streamlit_module()

from talentrag.core import ROOT, Matcher, coverage, load_data, load_pairs, passages
from talentrag.uploads import compare_upload, extract_text

st.set_page_config(page_title='TalentRAG', page_icon='🔎', layout='wide')
st.markdown('<style>.block-container{max-width:1200px;padding-top:2rem} h1{color:#16394a} div[data-testid="stMetric"]{background:#f0f5f7;padding:14px;border-radius:8px}</style>', unsafe_allow_html=True)
st.title('TalentRAG — Evidence-Based Resume Matching')
st.caption('Interim prototype • retrieval, ranking and source-text inspection • synthetic dataset')


@st.cache_resource
def resources(signature):
    resumes, jobs = load_data()
    return resumes, jobs, Matcher(resumes)


try:
    signature = tuple((ROOT / 'data' / 'processed' / name).stat().st_mtime_ns for name in ['resumes.parquet', 'jobs.parquet'])
    resumes, jobs, matcher = resources(signature)
except Exception as error:
    st.error(f'Cannot load processed data: {error}')
    st.stop()

try:
    pairs = load_pairs(resumes, jobs)
    pair_count = len(pairs)
except Exception as error:
    pairs = None
    pair_count = None
    st.warning(f'Matching is available, but source-label evaluation is unavailable: {error}')

for column, label, count in zip(st.columns(3), ['Candidate profiles', 'Dataset jobs', 'Source-listed positive pairs'], [len(resumes), len(jobs), pair_count]):
    column.metric(label, f'{count:,}' if count is not None else 'Unavailable')

match_tab, evaluation_tab, status_tab = st.tabs(['Match Candidates', 'Data & Evaluation', 'Project Status'])


def show_coverage(details):
    for label in ['required', 'preferred']:
        matched = details[label + '_matched']
        missing = details[label + '_missing']
        st.write(f'**{label.title()} coverage:** {len(matched)}/{len(matched) + len(missing)}')
        st.write('Matched mentions: ' + (', '.join(matched) or 'None'))
        st.write('Missing mentions: ' + (', '.join(missing) or 'None'))


def candidate_details(identifier, job):
    row = resumes.loc[resumes.resume_id == identifier].iloc[0]
    st.subheader(f"{identifier} · {row['role']}")
    st.caption(f"{row['seniority']} · {row['years_experience']} years · {row['industry']}")
    show_coverage(coverage(row, job))
    st.caption('Coverage checks normalized exact skills-list entries. Missing mentions do not establish a lack of ability.')
    st.write('**Skills list:** ' + ', '.join(row['skills']))
    relevant = passages(row, job)
    st.write('**Relevant retrieved passages**')
    st.caption('Verbatim retrieved text; these passages are not verified proof of expertise.')
    for section, text in relevant:
        st.caption(f'{identifier} · source section: {section}')
        st.text(text)
    if not any(section == 'experience' for section, _ in relevant):
        st.info('No relevant experience passage found. Skill-list mentions are displayed separately.')
    with st.expander('All source summary and experience text'):
        st.text(str(row['summary']))
        for bullet in row['experience_bullets']:
            st.text(str(bullet))


with match_tab:
    source = st.radio('Job source', ['Dataset job', 'Custom job'], horizontal=True)
    if source == 'Dataset job':
        identifier = st.selectbox('Select a job', jobs.job_id.tolist(), format_func=lambda value: f"{jobs.loc[jobs.job_id == value, 'job_title'].iloc[0]} · {value}")
        job = jobs.loc[jobs.job_id == identifier].iloc[0].to_dict()
        st.write(job['description'])
        st.write('**Required skills:** ' + ', '.join(job['must_have_skills']))
        st.write('**Preferred skills:** ' + ', '.join(job['nice_to_have_skills']))
    else:
        description = st.text_area('Job description', placeholder='Describe the role and responsibilities…')
        required = st.text_input('Required skills (comma separated)', 'Python, SQL, Flask')
        preferred = st.text_input('Preferred skills (comma separated)', 'Docker, Git')
        job = {'job_id': 'CUSTOM', 'description': description,
               'must_have_skills': [value.strip() for value in required.split(',') if value.strip()],
               'nice_to_have_skills': [value.strip() for value in preferred.split(',') if value.strip()]}
    method = st.selectbox('Ranking method', ['Skill-only', 'BM25'])
    st.caption('Skill-only: required-skill count, then resume ID. BM25: text relevance score, then resume ID. Scores are not hiring probabilities.')
    st.caption('BM25 engine: ' + matcher.bm25_engine)
    st.caption('Semantic / hybrid retrieval: unavailable in this interim build; no model is downloaded.')
    fingerprint = (str(job), method)
    if st.button('Rank candidates', type='primary'):
        try:
            with st.spinner('Ranking the full candidate collection…'):
                ranking = matcher.rank(job, method)
            st.session_state['ranking'] = ranking
            st.session_state['ranking_key'] = fingerprint
        except ValueError as error:
            st.error(str(error))
    if st.session_state.get('ranking_key') == fingerprint:
        ranking = st.session_state['ranking']
        st.subheader('Top 10 candidates')
        top = ranking.head(10).merge(resumes[['resume_id', 'role']], on='resume_id', validate='one_to_one')
        details_by_id = {identifier: coverage(resumes.loc[resumes.resume_id == identifier].iloc[0], job) for identifier in top.resume_id}
        for label in ['required', 'preferred']:
            top[label + '_coverage'] = top.resume_id.map(lambda identifier: f"{len(details_by_id[identifier][label + '_matched'])}/{len(details_by_id[identifier][label + '_matched']) + len(details_by_id[identifier][label + '_missing'])}")
        st.dataframe(top, hide_index=True, use_container_width=True)
        exported = ranking.merge(resumes[['resume_id', 'role']], on='resume_id', validate='one_to_one')
        exported.insert(0, 'rank', range(1, len(exported) + 1))
        exported['method'] = method
        exported['job_id'] = job['job_id']
        st.download_button('Export full ranked results (CSV)', exported.to_csv(index=False).encode(), 'talentrag_ranking.csv', 'text/csv')
        for identifier in top.resume_id:
            with st.expander(f"{identifier} · {top.loc[top.resume_id == identifier, 'role'].iloc[0]}"):
                candidate_details(identifier, job)
        st.subheader('Compare two candidates')
        selection = st.multiselect('Choose two from the top 10', top.resume_id.tolist(), default=top.resume_id.head(2).tolist(), max_selections=2)
        for column, identifier in zip(st.columns(2), selection):
            with column:
                candidate_details(identifier, job)
    elif 'ranking' in st.session_state:
        st.info('Job or method changed. Rank again to refresh results.')

    st.divider()
    st.subheader('Compare an uploaded resume with this job')
    st.caption('Uploads remain separate from the dataset collection. Raw-text mentions do not have structured skills or experience provenance.')
    upload = st.file_uploader('Upload TXT, PDF or DOCX (maximum 10 MB)', type=['txt', 'pdf', 'docx'])
    demo = st.selectbox('Or use a fictional demo TXT', ['None', 'fictional_backend.txt', 'fictional_analyst.txt'])
    for name in ['fictional_backend.txt', 'fictional_analyst.txt']:
        st.download_button('Download ' + name, (ROOT / 'demo_resumes' / name).read_bytes(), name, key=name)
    try:
        text = extract_text(upload.name, upload.getvalue()) if upload else (extract_text(demo, (ROOT / 'demo_resumes' / demo).read_bytes()) if demo != 'None' else None)
        if text is not None:
            st.text_area('Extracted raw text — preview before comparison', text, height=200, disabled=True)
            if st.button('Compare extracted text'):
                details = compare_upload(text, job)
                show_coverage(details)
                st.caption('Exact normalized phrases in uploaded raw text. No structured section or expertise claim is inferred.')
                for snippet in details['snippets']:
                    st.caption('Uploaded resume · raw text · retrieved passage')
                    st.text(snippet)
                if not details['snippets']:
                    st.info('No relevant raw-text snippet found.')
    except ValueError as error:
        st.error(str(error))

with evaluation_tab:
    st.subheader('Development evaluation')
    st.write('All candidates are ranked without match labels. The fixed sample excludes J_000000 and uses sample(n=20, random_state=42).')
    st.write('**Listed-positive overlap@5:** number of top-five IDs also listed as source positives (0–5). **Listed-positive recall@5:** that count divided by the job’s distinct listed positives. The table averages per-job values.')
    st.warning('Source positives are synthetic and incomplete. Unlisted pairs are unlabeled, not verified negatives. Development results are not hiring accuracy or a reviewed held-out evaluation.')
    result_path = ROOT / 'results' / 'development.csv'
    try:
        results = pd.read_csv(result_path) if result_path.exists() else None
        required_columns = {'method', 'listed_positive_overlap_at_5', 'listed_positive_recall_at_5', 'seconds'}
        if results is not None and not required_columns.issubset(results.columns):
            raise ValueError('Evaluation CSV has missing columns. Rerun evaluate_demo.py.')
    except (OSError, ValueError, pd.errors.ParserError) as error:
        results = None
        st.warning(f'Evaluation results unavailable: {error}')
    if results is not None:
        st.dataframe(results.groupby('method')[['listed_positive_overlap_at_5', 'listed_positive_recall_at_5', 'seconds']].mean(), use_container_width=True)
        st.caption('Mean seconds includes lazy BM25 index construction on its first query; inspect per-job timing in CSV.')
        st.dataframe(results, hide_index=True)
        st.download_button('Download evaluation CSV', result_path.read_bytes(), 'development.csv', 'text/csv')
        metadata_path = result_path.with_suffix('.json')
        if metadata_path.exists():
            st.download_button('Download evaluation metadata', metadata_path.read_bytes(), 'development.json', 'application/json')
        else:
            st.warning('Evaluation metadata is missing. Rerun evaluate_demo.py to regenerate it.')
    else:
        st.info('No evaluation has been run yet.')
    st.code('/opt/anaconda3/envs/talentrag/bin/python evaluate_demo.py')
    st.write('Candidate text explicitly includes Role, Summary, Skills list and Experience. BM25 queries include job description plus required/preferred skills. Ranking inputs never contain match-pair labels.')

with status_tab:
    st.subheader('Interim delivery status')
    st.write('**Implemented:** processed-data ingestion, exact required-skill baseline, BM25, deterministic ID ties, top-10 details, evidence sections, two-candidate comparison, CSV export, TXT/DOCX extraction, fixed development evaluation.')
    st.write('**Environment-dependent:** BM25 uses rank-bm25 when installed; the engine label explicitly identifies the offline local Okapi fallback. PDF uses pypdf when available, otherwise native macOS PDFKit. DOCX uses the standard-library ZIP/XML parser. Extraction failures are shown clearly. OCR is unavailable.')
    verification = ROOT / 'results' / 'verification.txt'
    st.write('**Actually tested:**')
    st.text(verification.read_text() if verification.exists() else 'Verification pending. No completed test claim yet.')
    st.write('**Unavailable / future:** semantic retrieval and reciprocal rank fusion, cross-encoder reranking, grounded LLM generation, richer evidence dataset, skill graph, recruiter copilot, reviewed held-out evaluation.')
    st.info('This prototype retrieves and ranks existing text. It does not generate candidate assessments or verify claims of expertise.')
