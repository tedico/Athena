# tests/test_notion_io.py
from unittest.mock import MagicMock

from src import notion_io, slots


def test_existing_urls_queries_all_pages():
    client = MagicMock()
    client.databases.query.side_effect = [
        {"results": [_paper_row("https://doi.org/10.1/a")], "has_more": True,
         "next_cursor": "cur1"},
        {"results": [_paper_row("https://doi.org/10.1/b")], "has_more": False,
         "next_cursor": None},
    ]
    urls = notion_io.existing_paper_urls(client, "db1")
    assert urls == {"https://doi.org/10.1/a", "https://doi.org/10.1/b"}
    assert client.databases.query.call_count == 2  # paginated!


def test_insert_paper_builds_correct_properties():
    client = MagicMock()
    notion_io.insert_paper(client, "db1", {
        "title": "T", "authors": "A", "year": 2020, "journal": "J",
        "doi_url": "https://doi.org/x", "key_finding": "F",
        "why_it_matters": "W", "status": "Discovered", "selection_reason": "",
    })
    props = client.pages.create.call_args.kwargs["properties"]
    assert props[slots.PAPER_TITLE]["title"][0]["text"]["content"] == "T"
    assert props[slots.PAPER_URL]["url"] == "https://doi.org/x"
    assert props[slots.PAPER_STATUS]["select"]["name"] == "Discovered"


def test_insert_carousel_maps_slots_and_charcounts():
    client = MagicMock()
    payload = {
        "paper_page_id": "paper1",
        "caption": "c" * 60,
        "hook": "h" * 20,
        "cards": ["a" * 30, "b" * 30, "c" * 30, "d" * 30, "e" * 30],
        "cta": "f" * 20,
    }
    notion_io.insert_carousel(client, "db2", payload)
    props = client.pages.create.call_args.kwargs["properties"]
    assert props[slots.PROP_HOOK]["rich_text"][0]["text"]["content"] == "h" * 20
    assert props[slots.PROP_CHARCOUNT_HOOK]["number"] == 20
    assert props[slots.PROP_CARDS[4]]["rich_text"][0]["text"]["content"] == "e" * 30
    assert props[slots.PROP_CHARCOUNT_CARDS[4]]["number"] == 30
    assert props[slots.PROP_STATUS]["select"]["name"] == "Draft"
    assert props[slots.PROP_INPUT_TYPE]["select"]["name"] == "Consensus"
    assert props[slots.PROP_VARIANT]["multi_select"] == [
        {"name": "Consensus_Psychology"}
    ]
    assert props[slots.PROP_PAPER_RELATION]["relation"] == [{"id": "paper1"}]


def test_long_caption_chunked_into_valid_text_objects():
    client = MagicMock()
    payload = {
        "paper_page_id": "paper1",
        "caption": "c" * 2500,
        "hook": "h" * 20,
        "cards": ["a" * 30, "b" * 30, "c" * 30, "d" * 30, "e" * 30],
        "cta": "f" * 20,
    }
    notion_io.insert_carousel(client, "db2", payload)
    title_objects = client.pages.create.call_args.kwargs["properties"][
        slots.PROP_TITLE
    ]["title"]
    assert len(title_objects) == 2
    assert all(len(o["text"]["content"]) <= 2000 for o in title_objects)
    assert "".join(o["text"]["content"] for o in title_objects) == "c" * 2500
    assert client.pages.create.call_args.kwargs["properties"][
        slots.PROP_CHARCOUNT_TITLE
    ]["number"] == 2500


def test_update_status():
    client = MagicMock()
    notion_io.update_status(client, "page1", "Status", "Rendered")
    client.pages.update.assert_called_once_with(
        page_id="page1",
        properties={"Status": {"select": {"name": "Rendered"}}},
    )


def _paper_row(url):
    return {"properties": {slots.PAPER_URL: {"url": url}}}
