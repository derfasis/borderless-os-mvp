"""End-to-end smoke tests for the publicly demonstrable fictional workflow."""

from fastapi.testclient import TestClient

from borderless_os.api import app, index

client = TestClient(app)


def test_showcase_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Lighthouse AI" in response.text
    assert "Try fictional sample" in response.text
    assert "not_verified" in response.text


def test_sample_pdf_ingest_search_and_refusal():
    index.items.clear()
    pdf_response = client.get("/demo/sample.pdf")
    assert pdf_response.status_code == 200
    assert pdf_response.content.startswith(b"%PDF")

    ingest_response = client.post(
        "/ingest/pdf",
        files={"file": ("fictional-notice.pdf", pdf_response.content, "application/pdf")},
        data={"source_url": "https://example.org/fictional-notice.pdf", "published_on": "2026-01-01"},
    )
    assert ingest_response.status_code == 200, ingest_response.text
    assert ingest_response.json()["articles_indexed"] == 2
    assert ingest_response.json()["verification"] == "source_identity_not_independently_verified"

    found = client.post("/search", json={"question": "fictional application review"})
    assert found.status_code == 200
    assert found.json()["status"] == "passages_found_not_legally_verified"
    assert found.json()["legal_advice"] is False
    assert found.json()["passages"][0]["article"] == "1"
    assert found.json()["passages"][0]["pages"] == [1]

    missing = client.post("/search", json={"question": "volcanic submarine passage"})
    assert missing.status_code == 200
    assert missing.json()["status"] == "not_verified"
    assert missing.json()["passages"] == []
    assert missing.json()["legal_advice"] is False
