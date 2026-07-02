# src/notion_io.py
"""Thin Notion REST wrapper. Property mapping lives here; nothing else does I/O.

Gotcha (documented in Useful Math too): the REST API takes DATABASE ids, not
the collection:// data-source ids the Notion MCP displays.
"""
from notion_client import Client

from src import config, slots


def client() -> Client:
    return Client(auth=config.require("NOTION_API_KEY"))


NOTION_TEXT_LIMIT = 2000  # max chars per rich text object (API request limit)


def _text_objects(text: str) -> list:
    """Split text into <=2000-char text objects; Notion rejects longer ones."""
    return [
        {"text": {"content": text[i:i + NOTION_TEXT_LIMIT]}}
        for i in range(0, len(text), NOTION_TEXT_LIMIT)
    ] or [{"text": {"content": ""}}]


def _rt(text: str) -> dict:
    return {"rich_text": _text_objects(text)}


def existing_paper_urls(client, papers_db_id: str) -> set:
    """All DOI/URL values in the Papers DB. Paginates (never trust one page)."""
    urls, cursor = set(), None
    while True:
        kwargs = {"database_id": papers_db_id, "page_size": 100}
        if cursor:
            kwargs["start_cursor"] = cursor
        resp = client.databases.query(**kwargs)
        for row in resp["results"]:
            url = row["properties"].get(slots.PAPER_URL, {}).get("url")
            if url:
                urls.add(url)
        if not resp.get("has_more"):
            return urls
        cursor = resp["next_cursor"]


def insert_paper(client, papers_db_id: str, paper: dict) -> dict:
    props = {
        slots.PAPER_TITLE: {"title": _text_objects(paper["title"])},
        slots.PAPER_AUTHORS: _rt(paper["authors"]),
        slots.PAPER_YEAR: {"number": paper["year"]},
        slots.PAPER_JOURNAL: _rt(paper["journal"]),
        slots.PAPER_URL: {"url": paper["doi_url"]},
        slots.PAPER_FINDING: _rt(paper["key_finding"]),
        slots.PAPER_WHY: _rt(paper["why_it_matters"]),
        slots.PAPER_REASON: _rt(paper.get("selection_reason", "")),
        slots.PAPER_STATUS: {"select": {"name": paper["status"]}},
    }
    return client.pages.create(
        parent={"database_id": papers_db_id}, properties=props
    )


def insert_carousel(client, carousel_db_id: str, payload: dict) -> dict:
    props = {
        slots.PROP_TITLE: {"title": _text_objects(payload["caption"])},
        slots.PROP_CHARCOUNT_TITLE: {"number": len(payload["caption"])},
        slots.PROP_HOOK: _rt(payload["hook"]),
        slots.PROP_CHARCOUNT_HOOK: {"number": len(payload["hook"])},
        slots.PROP_CTA: _rt(payload["cta"]),
        slots.PROP_CHARCOUNT_CTA: {"number": len(payload["cta"])},
        slots.PROP_STATUS: {"select": {"name": "Draft"}},
        slots.PROP_INPUT_TYPE: {"select": {"name": "Consensus"}},
        slots.PROP_VARIANT: {"multi_select": [{"name": "Consensus_Psychology"}]},
        slots.PROP_PAPER_RELATION: {"relation": [{"id": payload["paper_page_id"]}]},
    }
    for prop, count_prop, text in zip(
        slots.PROP_CARDS, slots.PROP_CHARCOUNT_CARDS, payload["cards"]
    ):
        props[prop] = _rt(text)
        props[count_prop] = {"number": len(text)}
    return client.pages.create(
        parent={"database_id": carousel_db_id}, properties=props
    )


def update_status(client, page_id: str, prop_name: str, value: str) -> None:
    client.pages.update(
        page_id=page_id,
        properties={prop_name: {"select": {"name": value}}},
    )


def fetch_carousel(client, page_id: str) -> dict:
    """Carousel row → render payload {hook, cards[5], cta, paper_page_id|None}."""
    page = client.pages.retrieve(page_id=page_id)
    props = page["properties"]

    def text_of(name):
        parts = props.get(name, {}).get("rich_text", [])
        return "".join(p["plain_text"] for p in parts)

    relation = props.get(slots.PROP_PAPER_RELATION, {}).get("relation", [])
    return {
        "hook": text_of(slots.PROP_HOOK),
        "cards": [text_of(n) for n in slots.PROP_CARDS],
        "cta": text_of(slots.PROP_CTA),
        "paper_page_id": relation[0]["id"] if relation else None,
    }
