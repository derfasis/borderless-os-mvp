"""Minimal interactive product showcase with an entirely fictional PDF fixture.

No claims of legal correctness, document provenance, or current requirements.
"""

from pathlib import Path

import fitz
from fastapi import APIRouter
from fastapi.responses import FileResponse, Response

router = APIRouter()


@router.get("/", include_in_schema=False)
def showcase() -> FileResponse:
    """Serve the interactive evidence cockpit."""
    return FileResponse(Path(__file__).with_name("demo.html"), media_type="text/html")


@router.get("/demo/sample.pdf", include_in_schema=False)
def synthetic_sample_pdf() -> Response:
    """Generate a clearly fictional, text-based PDF for a reproducible demo."""
    doc = fitz.open()
    try:
        page = doc.new_page()
        text = (
            "Clanak 1.\n"
            "Fictional application review procedure.\n"
            "DEMO ONLY: This is not a real government requirement.\n"
            "A fictional applicant submits example form ALPHA for review.\n"
            "Clanak 2.\n"
            "Fictional missing-document handling.\n"
            "If the example record is incomplete, a human reviewer is needed.\n"
            "There is no real deadline or immigration advice in this document."
        )
        page.insert_text((55, 65), text, fontsize=11, lineheight=1.5)
        pdf_bytes = doc.tobytes()
    finally:
        doc.close()
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'inline; filename="fictional-notice.pdf"'},
    )
