"""CLI: gate the 7-card copy, then write it to the Carousels DB as Draft.

Usage: python -m src.write_carousel carousel.json
The gate runs FIRST — a failing payload never touches Notion.
"""
import json
import sys

from src import config, gates, notion_io, slots


def run(client, carousel_db_id: str, payload: dict) -> dict:
    gates.validate_carousel(payload)  # raises GateError → nothing written
    page = notion_io.insert_carousel(client, carousel_db_id, payload)
    notion_io.update_status(
        client, payload["paper_page_id"], slots.PAPER_STATUS, "Written"
    )
    return {"id": page["id"], "url": page.get("url", "")}


def main():
    with open(sys.argv[1]) as f:
        payload = json.load(f)
    result = run(
        notion_io.client(), config.require("NOTION_CAROUSEL_DB_ID"), payload
    )
    print(f"carousel created as Draft: {result['url']}")


if __name__ == "__main__":
    main()
