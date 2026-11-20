from borderless_os.ingest import Article
from borderless_os.index import EvidenceIndex


def make_index():
    index = EvidenceIndex()
    index.add(articles=[Article(number="7", text="Fictional registration procedure", pages=[2])],
              source_url="https://example.org/fictional", published_on="2026-01-01", digest="abc")
    return index


def test_search_returns_original_quote_with_provenance():
    matches = make_index().search("registration procedure")
    assert matches[0].article == "7"
    assert matches[0].pages == [2]
    assert matches[0].source_url == "https://example.org/fictional"
    assert matches[0].verification == "source_identity_not_independently_verified"


def test_unknown_question_fails_closed():
    assert make_index().search("astronomy telescopes") == []


def test_does_not_generate_an_answer():
    assert make_index().search("registration")[0].quote == "Fictional registration procedure"
