"""CLI: insert discovered papers into the Papers DB, deduped by DOI/URL.

Usage: python -m src.add_papers papers.json
"""
import json
import sys

from src import config, notion_io

REQUIRED = (
    "title", "authors", "year", "journal", "doi_url",
    "key_finding", "why_it_matters", "status",
)


class PaperError(ValueError):
    pass


def run(client, papers_db_id: str, papers: list) -> dict:
    # validate everything BEFORE inserting anything (all-or-nothing batch)
    for i, paper in enumerate(papers):
        missing = [f for f in REQUIRED if not str(paper.get(f, "")).strip()]
        if missing:
            raise PaperError(f"papers[{i}] missing: {', '.join(missing)}")

    existing = notion_io.existing_paper_urls(client, papers_db_id)
    inserted = skipped = 0
    for paper in papers:
        if paper["doi_url"] in existing:
            skipped += 1
            continue
        notion_io.insert_paper(client, papers_db_id, paper)
        existing.add(paper["doi_url"])
        inserted += 1
    return {"inserted": inserted, "skipped": skipped}


def main():
    with open(sys.argv[1]) as f:
        papers = json.load(f)["papers"]
    result = run(
        notion_io.client(), config.require("NOTION_PAPERS_DB_ID"), papers
    )
    print(f"inserted={result['inserted']} skipped_duplicates={result['skipped']}")


if __name__ == "__main__":
    main()
