# Team presentation guide

## Startup checklist

- Follow README Python 3.12 setup; install requirements in a fresh environment, not copied `.venv` or borrowed base Conda paths.
- Download/preprocess using `data/README.md`; public Git excludes data binaries.
- Run `python -m pip check`, `python -m unittest discover -s tests -v`, `python tests/ui_smoke.py`, `python evaluate_demo.py`.
- Start `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502`; open http://127.0.0.1:8502. Leave an already-working instance running.
- Confirm 10,000 profiles, 2,500 jobs and 75,000 pairs; BM25 engine should identify rank-bm25 after installation.
- Use the fictional TXT examples; no personal resumes are needed.

## Exact click-by-click sequence

1. Open **Match Candidates** → **Job source** → **Dataset job**. Choose a title/ID under **Select a job**; show description and skill lists.
2. Choose **Skill-only** under **Ranking method** → **Rank candidates**. Show **Top 10 candidates** and explain required-skill counts.
3. Expand a resume ID. Read coverage, then **Relevant retrieved passages** and source section. If no experience quote exists, read the evidence-gap message honestly.
4. Choose **BM25** → **Rank candidates**. Explain lexical relevance and identify the actual engine label.
5. Under **Compare two candidates**, keep or change the two top-10 IDs. Click **Export full ranked results (CSV)**.
6. Choose **Custom job**. Set **Job description** to `Build Python and SQL services using Flask`; required `Python, SQL, Flask`; preferred `Docker, Git`.
7. Under **Or use a fictional demo TXT**, choose `fictional_backend.txt`, read **Extracted raw text — preview before comparison**, click **Compare extracted text**. Switch to `fictional_analyst.txt` to show missing Flask/Docker/Git. Alternatively download either TXT and select it in **Upload TXT, PDF or DOCX (maximum 10 MB)**.
8. Open **Data & Evaluation**. Show per-job rows/downloads. Explain mean overlap@5: baseline 0.20, BM25 0.15; these are counts, not accuracy percentages.
9. Open **Project Status**. Explain future features. Its historical PDFKit sentence is outdated: portable current extraction uses pypdf; README is the current dependency record.

Suggested timing: 45 seconds context, 90 seconds retrieval/comparison, 75 seconds upload, 60 seconds evaluation and 30 seconds status.

## Two-to-three-minute explanation script

“TalentRAG demonstrates the retrieval and matching stage of a planned resume RAG system. Given a job, it ranks 10,000 synthetic profiles. It does not generate an LLM assessment or predict hiring success.

We preserve raw data and clean whitespace and duplicate skill mentions. Jobs and resumes have unique IDs. A pair table links jobs to source-listed positives. These labels are used after ranking for evaluation, never as ranking inputs.

Skill-only counts exact normalized required skills in each profile's skills list. BM25 searches labelled text made from role, summary, skills and experience. It uses word rarity, diminishing returns for repetition and document-length normalization. Both methods resolve score ties by resume ID.

The top ten include coverage and source passages. A skills-list mention differs from an experience quote. Quotes preserve wording and source section, but do not verify expertise. Generic synthetic bullets sometimes contain no relevant evidence; the app states that explicitly. Uploaded resumes are previewed as raw text and compared separately from the structured collection.

The fixed development evaluation uses 20 jobs and every candidate. Mean listed-positive overlap in the top five is 0.20 for the baseline and 0.15 for BM25. These are counts of agreement with incomplete synthetic lists, not hiring accuracy. Unlisted pairs are unlabeled, not verified mismatches. We cannot claim BM25 improved this metric.

Future work includes semantic retrieval, fusion, reranking, grounded generation and richer evidence. Independently reviewed held-out labels are needed before stronger suitability claims.”

## Four-member explanation split

| Presenter | Suggested component | Prepare to explain |
| --- | --- | --- |
| Member 1 | Objective and data | Source, synthetic nature, counts, IDs, preprocessing/audits |
| Member 2 | Retrieval/ranking | Exact baseline, BM25 fields/tokenization, ties and scores |
| Member 3 | UI/evidence | Job inputs, comparison/export, raw uploads, provenance |
| Member 4 | Evaluation/roadmap | Fixed sample, overlap/recall, unlabeled pairs, limits/future |

These are presentation roles, not authorship claims. Describe personal contributions only when substantiated.

## Honest answers and fallback plan

- **Does it generate?** No; this interim stage retrieves, ranks and displays evidence.
- **Are scores hiring probabilities?** No; counts and lexical relevance have no outcome calibration.
- **Why no experience quote?** Generic source text may not mention requested skills; no evidence is manufactured.
- **Why small overlap?** It measures agreement with incomplete synthetic lists, not independent reviewer judgments.
- **Scanned PDF?** No OCR; use provided TXT examples for a reliable demonstration.
- **Windows guaranteed?** No actual Windows test is claimed; run the checks on the evaluation laptop.
- **Port occupied?** Keep the working app or choose another port; do not terminate unrelated processes.
- **Data absent after clone?** Follow `data/README.md`, audit, preprocess and rerun evaluation.
- **Browser tested by agent?** AppTest passed; owner reported live startup. A separate interactive agent browser test was not performed.
