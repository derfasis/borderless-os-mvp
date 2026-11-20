import fitz
import pytest

from borderless_os.ingest import extract_articles, pdf_to_pages, sha256


def pdf_bytes(pages: list[str]) -> bytes:
    doc = fitz.open()
    for text in pages:
        page = doc.new_page()
        page.insert_text((50, 50), text, fontname="helv", fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


def test_pdf_text_extraction():
    assert "Hello" in pdf_to_pages(pdf_bytes(["Hello"]))[0]


def test_pdf_rejects_non_pdf():
    with pytest.raises(ValueError, match="not a PDF"):
        pdf_to_pages(b"not a pdf")


def test_pdf_rejects_scanned_blank_file():
    with pytest.raises(ValueError, match="OCR/human review"):
        pdf_to_pages(pdf_bytes([""]))


def test_source_hash_is_deterministic():
    assert sha256(b"test") == sha256(b"test")
    assert sha256(b"test") != sha256(b"different")


def test_split_by_article_not_character_length():
    articles = extract_articles(["Članak 1.\nFirst provision.\nČlanak 2.\nSecond provision."])
    assert [(a.number, a.text) for a in articles] == [
        ("1", "First provision."), ("2", "Second provision.")
    ]


def test_article_continues_across_pages_with_citations():
    articles = extract_articles(["Članak 1.\nFirst line.",
                                 "Additional paragraph.\nČlanak 2.\nNext provision."])
    assert articles[0].pages == [1, 2]
    assert "Additional paragraph" in articles[0].text
    assert articles[1].pages == [2]


def test_no_article_headings_needs_human_review():
    with pytest.raises(ValueError, match="review required"):
        extract_articles(["Plain text without structured article headings."])
