# tests/test_add_papers.py
from unittest.mock import MagicMock

from src import add_papers


def _paper(url):
    return {
        "title": "T", "authors": "A", "year": 2020, "journal": "J",
        "doi_url": url, "key_finding": "F", "why_it_matters": "W",
        "status": "Discovered", "selection_reason": "",
    }


def test_dedup_skips_existing(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(add_papers.notion_io, "existing_paper_urls",
                        lambda c, db: {"https://doi.org/old"})
    inserted = []
    monkeypatch.setattr(add_papers.notion_io, "insert_paper",
                        lambda c, db, p: inserted.append(p["doi_url"]))
    result = add_papers.run(
        client, "db1",
        [_paper("https://doi.org/old"), _paper("https://doi.org/new")],
    )
    assert inserted == ["https://doi.org/new"]
    assert result == {"inserted": 1, "skipped": 1}


def test_missing_required_field_aborts_before_any_insert(monkeypatch):
    client = MagicMock()
    monkeypatch.setattr(add_papers.notion_io, "existing_paper_urls",
                        lambda c, db: set())
    bad = _paper("https://doi.org/x")
    del bad["key_finding"]
    import pytest
    with pytest.raises(add_papers.PaperError, match="key_finding"):
        add_papers.run(client, "db1", [_paper("https://doi.org/y"), bad])
    client.pages.create.assert_not_called()
