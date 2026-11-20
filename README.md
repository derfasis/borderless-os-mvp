# BORDERLESS OS — source-first MVP

**Status:** Prototype code with automated tests, NOT a functioning immigration-advice product.

An engineering demonstration of a fail-closed PDF ingestion and evidence retrieval
service for Croatian public legal documents. It **does not** yet scrape official
portals, prove document authenticity, track amendments, interpret legislation,
perform OCR, or give legal advice.

## Implemented

- FastAPI endpoints: `GET /health`, `POST /ingest/pdf`, `POST /search`.
- PyMuPDF PDF text extraction (text-based documents only).
- Croatian `Članak N.` article-boundary extraction and PDF page references.
- SHA-256 hash, user-supplied source URL and publication-date metadata.
- Deterministic keyword retrieval returning original source passages, never AI-generated legal claims.
- Explicit `not_verified` outcome for missing evidence.
- 14 tests and GitHub Actions CI.

**Important:** A caller can supply a fraudulent URL or an outdated PDF. Returned
passages are never labelled as legally verified. Never use this prototype to
make immigration decisions without consulting current official sources and a
qualified professional where appropriate.

## Run it

```bash
python -m pip install -e '.[test]'
python -m pytest -q
uvicorn borderless_os.api:app --reload
```

Open http://localhost:8000/docs for an interactive API console.

## Next milestones (not yet implemented)

1. Confirm official publisher origin with an allowlist and download audit trail.
2. Integrate Docling/OCR with page-confidence flags and review queues.
3. Track law amendments and effective dates, preventing stale-law retrieval.
4. PostgreSQL + pgvector hybrid retrieval, with review-approved citations.
5. Next.js multilingual UX and human approval gates.
6. Manually verify at least 30 representative immigration Q&As before any public launch.

## Repository structure

```text
src/borderless_os/api.py       FastAPI endpoints
src/borderless_os/ingest.py    PDF extraction + article parsing
src/borderless_os/index.py     Source-cited keyword retrieval
tests/test_ingest.py          extraction and safety tests
tests/test_index.py           provenance and refusal tests
tests/test_api.py             API tests
.github/workflows/tests.yml   continuous integration
Dockerfile                    reproducible deployment
```

## Test-data warning

Every text example in the tests is intentionally **fictional** and is not a
statement of Croatian law.
