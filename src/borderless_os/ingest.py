"""Extract source passages, preserving article numbers and PDF page references.

This is a prototype, not an OCR or legal-validity engine. Image-only PDFs are
rejected rather than guessed at. Docling and human verification are planned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re

import fitz  # PyMuPDF

ARTICLE_RE = re.compile(r"(?im)^\s*(?:Članak|Clanak)\s+(\d+[a-z]?)\s*\.?\s*$")


@dataclass
class Article:
    number: str
    text: str = ""
    pages: list[int] = field(default_factory=list)

    def append(self, value: str, page_number: int) -> None:
        cleaned = value.strip()
        if cleaned:
            self.text = (self.text + "\n" + cleaned).strip()
            if page_number not in self.pages:
                self.pages.append(page_number)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def pdf_to_pages(data: bytes) -> list[str]:
    """Use PyMuPDF; fail closed when a scanned/image-only file has no text."""
    if not data.startswith(b"%PDF"):
        raise ValueError("Input is not a PDF file")
    try:
        with fitz.open(stream=data, filetype="pdf") as doc:
            if doc.is_encrypted:
                raise ValueError("Encrypted PDFs are not supported")
            pages = [page.get_text(sort=True) for page in doc]
    except (fitz.FileDataError, fitz.EmptyFileError) as exc:
        raise ValueError("Corrupt or unsupported PDF") from exc
    if not any(page.strip() for page in pages):
        raise ValueError("No extractable text; OCR/human review required")
    return pages


def extract_articles(pages: list[str]) -> list[Article]:
    """Find Croatian 'Članak N.' headings and preserve cross-page continuation."""
    articles: list[Article] = []
    current: Article | None = None
    for page_no, page in enumerate(pages, start=1):
        matches = list(ARTICLE_RE.finditer(page))
        if not matches:
            if current:
                current.append(page, page_no)
            continue
        before_first = page[: matches[0].start()]
        if current:
            current.append(before_first, page_no)
        for idx, match in enumerate(matches):
            current = Article(number=match.group(1))
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(page)
            current.append(page[match.end() : end], page_no)
            articles.append(current)
    if not articles:
        raise ValueError("No Croatian article headings detected; review required")
    return articles
