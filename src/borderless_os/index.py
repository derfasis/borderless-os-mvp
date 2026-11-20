"""Minimal evidence retrieval: returns *quotes*, never generated legal rules."""

from __future__ import annotations

from dataclasses import dataclass
import re

from .ingest import Article


@dataclass
class Evidence:
    article: str
    pages: list[int]
    source_url: str
    published_on: str | None
    sha256: str
    quote: str
    verification: str = "source_identity_not_independently_verified"


class EvidenceIndex:
    def __init__(self) -> None:
        self.items: list[Evidence] = []

    def add(self, *, articles: list[Article], source_url: str,
            published_on: str | None, digest: str) -> int:
        for a in articles:
            self.items.append(Evidence(article=a.number, pages=a.pages,
                                       source_url=source_url,
                                       published_on=published_on,
                                       sha256=digest, quote=a.text))
        return len(articles)

    def search(self, question: str, limit: int = 3) -> list[Evidence]:
        # Small deterministic baseline; production design calls for pgvector and
        # manually reviewed source integrity and effective-date checks.
        words = set(re.findall(r"\w{4,}", question.casefold()))
        if not words:
            return []
        scored: list[tuple[int, Evidence]] = []
        for item in self.items:
            document_words = set(re.findall(r"\w{4,}", item.quote.casefold()))
            score = len(words & document_words)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda entry: entry[0], reverse=True)
        return [item for _, item in scored[:limit]]
