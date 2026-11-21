"""Prototype HTTP API with fail-closed source retrieval."""

from __future__ import annotations

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .showcase import router as showcase_router
from .index import EvidenceIndex
from .ingest import extract_articles, pdf_to_pages, sha256

app = FastAPI(title="BORDERLESS OS – evidence-first MVP", version="0.1.0")
app.include_router(showcase_router)
index = EvidenceIndex()


class SearchRequest(BaseModel):
    question: str = Field(min_length=4, max_length=500)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ingest/pdf")
async def ingest_pdf(
    file: UploadFile = File(...),
    source_url: str = Form(...),
    published_on: str | None = Form(None),
) -> dict[str, str | int]:
    if not source_url.startswith(("https://", "http://")):
        raise HTTPException(status_code=422, detail="Source URL must use HTTP(S)")
    data = await file.read(10_000_001)
    if len(data) > 10_000_000:
        raise HTTPException(status_code=413, detail="Max size is 10 MB")
    try:
        articles = extract_articles(pdf_to_pages(data))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    digest = sha256(data)
    count = index.add(articles=articles, source_url=source_url,
                      published_on=published_on, digest=digest)
    return {"articles_indexed": count, "sha256": digest,
            "verification": "source_identity_not_independently_verified"}


@app.post("/search")
def search(payload: SearchRequest) -> dict:
    passages = index.search(payload.question)
    if not passages:
        return {"status": "not_verified", "reason": "Insufficient source evidence",
                "passages": [], "legal_advice": False}
    return {
        "status": "passages_found_not_legally_verified",
        "passages": [e.__dict__ for e in passages],
        "warning": "Source identity, currency and legal interpretation require human verification.",
        "legal_advice": False,
    }
