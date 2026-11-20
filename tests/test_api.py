import fitz
from fastapi.testclient import TestClient

from borderless_os.api import app, index

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_missing_evidence_is_not_verified():
    index.items.clear()
    response = client.post("/search", json={"question": "unknown requirements"})
    assert response.status_code == 200
    assert response.json()["status"] == "not_verified"
    assert response.json()["legal_advice"] is False


def test_pdf_ingest_then_search_returns_page_and_article():
    index.items.clear()
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Clanak 1.\nFictional registration procedure")
    data = doc.tobytes()
    doc.close()
    result = client.post("/ingest/pdf", files={"file": ("demo.pdf", data, "application/pdf")},
                         data={"source_url": "https://example.org/fictional.pdf",
                               "published_on": "2026-01-01"})
    assert result.status_code == 200, result.text
    assert result.json()["articles_indexed"] == 1
    search = client.post("/search", json={"question": "registration procedure"}).json()
    assert search["status"] == "passages_found_not_legally_verified"
    assert search["passages"][0]["article"] == "1"
    assert search["passages"][0]["pages"] == [1]
    assert search["passages"][0]["verification"] == "source_identity_not_independently_verified"


def test_rejects_invalid_uploaded_pdf():
    response = client.post("/ingest/pdf", files={"file": ("bad.pdf", b"bad", "application/pdf")},
                           data={"source_url": "https://example.org/bad.pdf"})
    assert response.status_code == 422
