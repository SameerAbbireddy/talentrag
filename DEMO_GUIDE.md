# Five-minute demonstration

> Historical guide from the initial offline build. For the current installed rank-bm25/pypdf engine, portable setup and presentation instructions, use README.md and TEAM_DEMO.md. The older local-BM25/base-Conda/PDFKit notes below do not describe the current dependency setup.

Before the evaluation, run `/opt/anaconda3/envs/talentrag/bin/python launch_demo.py` in a normal Terminal from this directory and open http://127.0.0.1:8501. The agent sandbox blocked network socket binding, so confirm the page opens on your machine before presenting. No download is needed for the current fallback demo.

1. **0:00–0:45 — Context.** Point to the three dataset counts: 10,000 candidates, 2,500 jobs, 75,000 listed positive pairs. Explain the interim scope: ingestion → retrieval → ranking → source evidence. Select a dataset job by title and ID; inspect its required/preferred skills.
2. **0:45–1:45 — Ranking.** Run Skill-only and show top 10, scores and exact skills-list coverage. Expand a profile; point out resume ID and source section. Generic experience may produce “No relevant experience passage found.” Switch to BM25, rerun, and explain that its score measures text relevance. The engine label identifies the local fallback when rank-bm25 is missing.
3. **1:45–2:30 — Comparison and export.** Compare the default first two candidates. Distinguish matched skill-list entries from actual verbatim experience text. Download the full ranked CSV. Changing the job/method hides stale results until reranking.
4. **2:30–3:30 — Dependable upload.** Choose Custom job. Enter “Build Python and SQL services using Flask”; keep required Python, SQL, Flask and preferred Docker, Git. Rank candidates. Choose fictional_backend.txt in the demo selector, preview text, then Compare extracted text. All five requested mentions appear with actual project lines. Switch to fictional_analyst.txt to show missing Flask/Docker/Git. The examples are visibly fictional and separate from dataset profiles. You can also download and upload the TXT files.
5. **3:30–4:30 — Evaluation.** Open Data & Evaluation. Explain count overlap@5 and recall@5. Actual means: skill-only 0.20 overlap, BM25 0.15; neither establishes hiring accuracy or improvement. Download CSV/JSON to show sample IDs, full candidate count, method, actual engine and timing.
6. **4:30–5:00 — Status.** Open Project Status. Distinguish completed automated checks from blocked live-server/browser verification. Explain future semantic retrieval, fusion, reranking, grounded generation, skill graph, richer evidence and reviewed held-out evaluation.

## Viva answers

**What is the baseline?** Count exact normalized required skills in each structured skills list, descending, with resume ID breaking ties. It is interpretable but misses paraphrases and skills not listed explicitly.

**What does BM25 add?** It retrieves text using query-term rarity, term frequency with diminishing returns, and document-length normalization. It sees explicitly labelled role, summary, skills list and experience fields. It does not understand semantic equivalence or verify claims. The current offline implementation is labelled; the requested package will be used once available.

**Why is there no generated answer?** This interim system retrieves and displays source passages. Grounded generation and cross-encoder reranking have not been implemented. No language model was downloaded.

**What would hybrid mean?** Future semantic retrieval would compare pretrained sentence embeddings. Reciprocal rank fusion would sum 1/(k + rank) across lexical and semantic rankings while preserving resume IDs. It is not available in this build.

**Why are the results small?** Listed positives are synthetic and incomplete. Candidates absent from those lists are unlabeled. Overlap tests agreement with those source lists, not true suitability. A proper claim needs richer evidence and independently reviewed held-out labels.

**Why can a candidate have high coverage with no experience quote?** Structured skills mention tools, while synthetic experience bullets can be generic. The app preserves that distinction and reports the missing evidence.

**Are scores probabilities?** No. The baseline score is a skill count and BM25 is a relevance score. Neither is calibrated to a hiring outcome.
