# Athena MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One psychology paper → one finished 7-card Instagram carousel (seven 1080×1350 PNGs on disk), via Consensus search → Notion funnel → deterministic HTML render.

**Architecture:** Status-driven pipeline over two Notion databases (Papers, Carousel). Three Claude Code skills do the LLM work (discover/write/render orchestration); all hard guarantees live in Python CLIs — char-count gates before any Notion write, dedup by DOI, exact-dimension screenshot verification. Rendering is Playwright screenshotting a static brand-book-exact HTML template — no generative images.

**Tech Stack:** Python 3 · notion-client 2.3.0 (pinned — 3.x removed `databases.query`) · Playwright (chromium) · Pillow · pytest · Notion MCP + Consensus MCP (interactive, inside skills) · Google Fonts (Newsreader, Work Sans)

**Spec:** `docs/superpowers/specs/2026-07-01-athena-mvp-design.md` (approved 2026-07-01)

---

## Ground rules for the executor

- Work on branch `athena-mvp` off `main`. **Never merge or push to `main`** — at the end, open a PR and Ted merges. One branch, one PR, no stacking.
- Every commit ends with the trailer (own line, exactly):
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- Commit messages carry status signal (what changed + where it leaves the project).
- **Public repo:** Notion IDs and keys go in `.env` (gitignored), never in committed code.
- All `python`/`pytest` commands run from the repo root with the venv active
  (`source .venv/bin/activate`).

## File structure (end state)

```
Athena/
├── .claude/skills/
│   ├── athena-discover/SKILL.md   # Consensus → Papers DB
│   ├── athena-write/SKILL.md      # paper → 7-beat copy → Carousel DB
│   └── athena-render/SKILL.md     # carousel → PNGs
├── src/
│   ├── __init__.py
│   ├── config.py          # .env loading; fails loudly on missing vars
│   ├── gates.py           # char bands + payload validation (the hard gate)
│   ├── slots.py           # Notion property names, slot↔card map, beat metadata
│   ├── notion_io.py       # thin Notion REST wrapper (query/insert/update)
│   ├── add_papers.py      # CLI: papers JSON → dedup by DOI → insert
│   ├── write_carousel.py  # CLI: carousel JSON → gates → insert as Draft
│   └── render.py          # CLI: carousel page-id → 7 verified PNGs → status flips
├── template/
│   ├── athena_cards.html  # brand-book-exact 7-card template with {{PLACEHOLDERS}}
│   └── assets/            # owl.png dropped here by Ted (Human item; optional v0)
├── tests/
│   ├── test_gates.py
│   ├── test_slots.py
│   ├── test_template_fill.py
│   ├── test_render.py     # needs chromium; marked "browser"
│   └── test_notion_io.py  # mocked client, no network
├── output/                # gitignored render output
├── requirements.txt
└── .env / .env.example
```

---

### Task 0: Branch + Python project skeleton

**Files:**
- Create: `requirements.txt`, `pytest.ini`, `src/__init__.py`, `tests/__init__.py`
- Modify: `.env.example`

- [ ] **Step 1: Create the branch**

```bash
cd ~/Documents/Projekts/Athena && git checkout -b athena-mvp
```

- [ ] **Step 2: Write requirements.txt**

```
notion-client==2.3.0
playwright>=1.40
Pillow>=10.0
python-dotenv>=1.0
pytest>=8.0
```

- [ ] **Step 3: Write pytest.ini** (registers the browser marker so render tests can be skipped when chromium is unavailable)

```ini
[pytest]
markers =
    browser: needs Playwright chromium installed
```

- [ ] **Step 4: Update .env.example** (full replacement of the file)

```
# Copy to .env and fill in — .env is gitignored, never commit real values
NOTION_API_KEY=
# Notion DATABASE ids (32-hex from the database page URL), NOT the
# collection:// data-source ids the Notion MCP shows — different UUIDs
# for the same table. REST API wants the database id.
NOTION_PAPERS_DB_ID=
NOTION_CAROUSEL_DB_ID=
```

- [ ] **Step 5: Create empty packages and the venv, install, sanity-check**

```bash
touch src/__init__.py && mkdir -p tests && touch tests/__init__.py
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && playwright install chromium
pytest --collect-only
```

Expected: `no tests ran` (collects 0, exits clean).

- [ ] **Step 6: Commit**

```bash
git add requirements.txt pytest.ini src/__init__.py tests/__init__.py .env.example
git commit -m "Set up Python skeleton on athena-mvp branch

requirements (notion-client pinned 2.3.0), pytest browser marker, env var
contract for Notion ids. Project state: scaffold only, no pipeline code yet.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 1: Notion data layer (interactive, via Notion MCP)

No code — this creates the two databases the code targets. Done by the executing
Claude session with Notion MCP tools.

- [ ] **Step 1: Create the Papers DB** on the "🦉 Athena (Beehiiv)" page (parent page id `3727934f-075d-80fb-8796-f17e468cac5d`) using `notion-create-database`:

- Title: `Papers`
- Properties:
  - `Title` — title
  - `Authors` — rich_text
  - `Year` — number
  - `Journal` — rich_text
  - `DOI/URL` — url
  - `Key Finding` — rich_text
  - `Why it matters` — rich_text
  - `Selection Reason` — rich_text
  - `Status` — select, options exactly: `Discovered`, `Selected`, `Written`, `Rendered`, `Posted`, `Rejected`

- [ ] **Step 2: Extend the Carousel DB** (the unnamed database, data source `collection://38c7934f-075d-8067-9d29-000b3f358b9c`) via `notion-update-data-source`, adding:

- `Status` — select, options exactly: `Draft`, `Approved`, `Rendered`, `Posted`
- `Paper` — relation → the Papers DB from Step 1

Also rename the data source from "New database" to `Carousels`.

- [ ] **Step 3: Record the DATABASE ids in `.env`** (not committed). Get each database's page URL (`notion-fetch` on the database returns `url": "https://app.notion.com/p/<32-hex>"`); the 32-hex is the database id. Carousel DB id is `38c7934f075d803c9415efbdba74ee15`. Write both into `.env` as `NOTION_PAPERS_DB_ID` / `NOTION_CAROUSEL_DB_ID` along with Ted's `NOTION_API_KEY`.

- [ ] **Step 4: Verify REST access.** Run (venv active, after Task 2 lands config.py — or use a one-liner):

```bash
python -c "
import os
from dotenv import load_dotenv; load_dotenv()
from notion_client import Client
c = Client(auth=os.environ['NOTION_API_KEY'])
for var in ('NOTION_PAPERS_DB_ID','NOTION_CAROUSEL_DB_ID'):
    r = c.databases.query(database_id=os.environ[var], page_size=1)
    print(var, 'OK', len(r['results']), 'rows')
"
```

Expected: both lines print `OK`. **If this 404s: the integration hasn't been granted access to the Athena page → log to SPRINT.md `## Human`: "Share the 🦉 Athena (Beehiiv) page with the Notion integration (Connections → add)" and pause here until done.**

- [ ] **Step 5: Update SPRINT.md** — tick Phase 1, set Current phase to Phase 2, commit:

```bash
git add SPRINT.md
git commit -m "Phase 1 complete: Notion data layer live

Papers DB created (funnel statuses Discovered→Posted + Rejected); Carousel DB
renamed to Carousels and extended with Status + Paper relation; REST access
verified. Ids live in .env only (public repo). Project state: entering Phase 2
(pipeline code).

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: config.py — env loading that fails loudly

**Files:**
- Create: `src/config.py`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_config.py
import pytest


def test_missing_env_var_raises(monkeypatch):
    monkeypatch.delenv("NOTION_API_KEY", raising=False)
    from src import config
    with pytest.raises(config.ConfigError, match="NOTION_API_KEY"):
        config.require("NOTION_API_KEY")


def test_present_env_var_returned(monkeypatch):
    monkeypatch.setenv("NOTION_API_KEY", "secret_x")
    from src import config
    assert config.require("NOTION_API_KEY") == "secret_x"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError` / `AttributeError` (config doesn't exist).

- [ ] **Step 3: Write minimal implementation**

```python
# src/config.py
"""Env-var access. Everything sensitive lives in .env (public repo)."""
import os

from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    pass


def require(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise ConfigError(
            f"{name} is not set. Copy .env.example to .env and fill it in."
        )
    return value
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_config.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/config.py tests/test_config.py
git commit -m "Add config module: loud-failing env access

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: slots.py — property names, slot↔card map, beat metadata

The single source of truth for Notion property strings and the 7-card grammar.
Everything else imports from here (DRY).

**Files:**
- Create: `src/slots.py`
- Test: `tests/test_slots.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_slots.py
from src import slots


def test_seven_cards_in_order():
    assert [c.number for c in slots.CARDS] == [1, 2, 3, 4, 5, 6, 7]


def test_beat_grammar_matches_spec():
    assert [c.beat for c in slots.CARDS] == [
        "hook", "setup", "punchy", "turn", "insight", "reframe", "cta",
    ]


def test_payload_keys_cover_all_cards():
    # card 1 ← hook, cards 2-6 ← cards[0..4], card 7 ← cta
    assert slots.CARDS[0].payload_key == "hook"
    assert [c.payload_key for c in slots.CARDS[1:6]] == [
        "cards.0", "cards.1", "cards.2", "cards.3", "cards.4",
    ]
    assert slots.CARDS[6].payload_key == "cta"


def test_notion_property_names_exact():
    # exact strings from Ted's existing schema — typos here corrupt real data
    assert slots.PROP_TITLE == "Content (2500 Chars Max)"
    assert slots.PROP_HOOK == "Hook/Headline"
    assert slots.PROP_CARDS == ["Card 1", "Card 2", "Card 3", "Card 4", "Card 5"]
    assert slots.PROP_CTA == "CTA"
    assert slots.PROP_CHARCOUNT_HOOK == "CharCount_Headline (100 Max)"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_slots.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write minimal implementation**

```python
# src/slots.py
"""7-card grammar + exact Notion property names (single source of truth).

Card 6 in the Notion schema is an intentionally unused spare (8 text slots,
7-card format). 'Content (2500 Chars Max)' is the title property = IG caption.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Card:
    number: int
    beat: str        # rhetorical job
    layout: str      # template CSS class
    payload_key: str # where its text lives in the carousel JSON payload


CARDS = (
    Card(1, "hook", "cover", "hook"),
    Card(2, "setup", "calm", "cards.0"),      # artwork layout deferred; calm fallback
    Card(3, "punchy", "punchy", "cards.1"),
    Card(4, "turn", "turn", "cards.2"),       # coral accent
    Card(5, "insight", "insight", "cards.3"), # columbia blue accent
    Card(6, "reframe", "calm-night", "cards.4"),
    Card(7, "cta", "cta", "cta"),
)

# --- Carousels DB property names (exact strings from the live schema) ---
PROP_TITLE = "Content (2500 Chars Max)"
PROP_HOOK = "Hook/Headline"
PROP_CARDS = ["Card 1", "Card 2", "Card 3", "Card 4", "Card 5"]
PROP_CTA = "CTA"
PROP_CHARCOUNT_HOOK = "CharCount_Headline (100 Max)"
PROP_CHARCOUNT_CARDS = [f"CharCount_Card{i}" for i in range(1, 6)]
PROP_CHARCOUNT_CTA = "CharCount_CTA"
PROP_CHARCOUNT_TITLE = "CharCount_Content"
PROP_INPUT_TYPE = "InputType"       # select → "Consensus"
PROP_VARIANT = "Variant"            # multi_select → ["Consensus_Psychology"]
PROP_STATUS = "Status"              # select (added in Task 1)
PROP_PAPER_RELATION = "Paper"       # relation (added in Task 1)

# --- Papers DB property names ---
PAPER_TITLE = "Title"
PAPER_AUTHORS = "Authors"
PAPER_YEAR = "Year"
PAPER_JOURNAL = "Journal"
PAPER_URL = "DOI/URL"
PAPER_FINDING = "Key Finding"
PAPER_WHY = "Why it matters"
PAPER_REASON = "Selection Reason"
PAPER_STATUS = "Status"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_slots.py -v`
Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/slots.py tests/test_slots.py
git commit -m "Add slots module: 7-card grammar + exact Notion property names

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: gates.py — the hard char gate

Bands (design decision, adjustable constants): hook 10–100 · body cards 20–280
· CTA 10–200 · caption 50–2500. Lengths measured with `len()` on the exact
string that will be written to Notion.

**Files:**
- Create: `src/gates.py`
- Test: `tests/test_gates.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_gates.py
import pytest

from src import gates


def good_payload():
    return {
        "paper_page_id": "abc123",
        "caption": "A caption that is comfortably over the fifty character minimum for captions.",
        "hook": "The pigeon in all of us",
        "cards": [
            "Card two text that is long enough to pass the gate.",
            "Card three text that is long enough to pass the gate.",
            "Card four text that is long enough to pass the gate.",
            "Card five text that is long enough to pass the gate.",
            "Card six text that is long enough to pass the gate.",
        ],
        "cta": "Follow @athena for one useful idea a week.",
    }


def test_good_payload_passes():
    gates.validate_carousel(good_payload())  # no raise


def test_hook_over_100_fails():
    p = good_payload()
    p["hook"] = "x" * 101
    with pytest.raises(gates.GateError, match="hook"):
        gates.validate_carousel(p)


def test_card_over_280_fails():
    p = good_payload()
    p["cards"][2] = "x" * 281
    with pytest.raises(gates.GateError, match="cards.2"):
        gates.validate_carousel(p)


def test_short_card_fails():
    p = good_payload()
    p["cards"][0] = "too short"
    with pytest.raises(gates.GateError, match="cards.0"):
        gates.validate_carousel(p)


def test_must_have_exactly_five_cards():
    p = good_payload()
    p["cards"] = p["cards"][:4]
    with pytest.raises(gates.GateError, match="exactly 5"):
        gates.validate_carousel(p)


def test_missing_field_fails():
    p = good_payload()
    del p["cta"]
    with pytest.raises(gates.GateError, match="cta"):
        gates.validate_carousel(p)


def test_all_violations_reported_at_once():
    p = good_payload()
    p["hook"] = ""
    p["cta"] = "x" * 999
    with pytest.raises(gates.GateError) as e:
        gates.validate_carousel(p)
    assert "hook" in str(e.value) and "cta" in str(e.value)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_gates.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write minimal implementation**

```python
# src/gates.py
"""Hard char-count gates. Code-enforced, never LLM-trusted (Useful Math lesson).

A payload that fails NEVER reaches Notion. All violations are reported in one
error so the copy can be fixed in a single pass.
"""

BANDS = {
    "hook": (10, 100),
    "card": (20, 280),
    "cta": (10, 200),
    "caption": (50, 2500),
}


class GateError(ValueError):
    pass


def _check(violations, field, text, band):
    lo, hi = BANDS[band]
    n = len(text)
    if not lo <= n <= hi:
        violations.append(f"{field}: {n} chars, band is {lo}-{hi}")


def validate_carousel(payload: dict) -> None:
    violations = []
    for field in ("paper_page_id", "caption", "hook", "cards", "cta"):
        if field not in payload:
            violations.append(f"{field}: missing")
    if violations:
        raise GateError("; ".join(violations))

    cards = payload["cards"]
    if not isinstance(cards, list) or len(cards) != 5:
        raise GateError(f"cards: exactly 5 required, got {len(cards)}")

    _check(violations, "hook", payload["hook"], "hook")
    _check(violations, "caption", payload["caption"], "caption")
    _check(violations, "cta", payload["cta"], "cta")
    for i, text in enumerate(cards):
        _check(violations, f"cards.{i}", text, "card")

    if violations:
        raise GateError("; ".join(violations))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_gates.py -v`
Expected: 7 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/gates.py tests/test_gates.py
git commit -m "Add char-count gates: hard code enforcement before any Notion write

Bands: hook 10-100, cards 20-280, CTA 10-200, caption 50-2500. All violations
reported in one pass.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: notion_io.py — thin Notion wrapper

Thin by design: builds property dicts and calls the client. Tested with a mock
client (no network). LLM-side orchestration stays in the skills.

**Files:**
- Create: `src/notion_io.py`
- Test: `tests/test_notion_io.py`

- [ ] **Step 1: Write the failing test**

```python
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


def test_update_status():
    client = MagicMock()
    notion_io.update_status(client, "page1", "Status", "Rendered")
    client.pages.update.assert_called_once_with(
        page_id="page1",
        properties={"Status": {"select": {"name": "Rendered"}}},
    )


def _paper_row(url):
    return {"properties": {slots.PAPER_URL: {"url": url}}}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_notion_io.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write minimal implementation**

```python
# src/notion_io.py
"""Thin Notion REST wrapper. Property mapping lives here; nothing else does I/O.

Gotcha (documented in Useful Math too): the REST API takes DATABASE ids, not
the collection:// data-source ids the Notion MCP displays.
"""
from notion_client import Client

from src import config, slots


def client() -> Client:
    return Client(auth=config.require("NOTION_API_KEY"))


def _rt(text: str) -> dict:
    return {"rich_text": [{"text": {"content": text}}]}


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
        slots.PAPER_TITLE: {"title": [{"text": {"content": paper["title"]}}]},
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
        slots.PROP_TITLE: {"title": [{"text": {"content": payload["caption"]}}]},
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_notion_io.py -v`
Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/notion_io.py tests/test_notion_io.py
git commit -m "Add Notion I/O wrapper: paginated dedup query, slot-mapped inserts, status updates

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: add_papers.py — dedup + insert CLI

Contract: `python -m src.add_papers papers.json` where the JSON is
`{"papers": [{title, authors, year, journal, doi_url, key_finding,
why_it_matters, status, selection_reason}]}`. Skips rows whose `doi_url`
already exists; prints a summary; exits 0.

**Files:**
- Create: `src/add_papers.py`
- Test: `tests/test_add_papers.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_add_papers.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write minimal implementation**

```python
# src/add_papers.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_add_papers.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/add_papers.py tests/test_add_papers.py
git commit -m "Add paper-ingest CLI: all-or-nothing validation, DOI dedup

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: write_carousel.py — gate + insert CLI

Contract: `python -m src.write_carousel carousel.json` where the JSON is the
gates payload `{paper_page_id, caption, hook, cards[5], cta}`. Gate failure →
non-zero exit, nothing written. Success → Carousel row created as `Draft`,
paper status flipped to `Written`, page URL printed.

**Files:**
- Create: `src/write_carousel.py`
- Test: `tests/test_write_carousel.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_write_carousel.py
from unittest.mock import MagicMock

import pytest

from src import gates, write_carousel


def good_payload():
    return {
        "paper_page_id": "paper1",
        "caption": "A caption that is comfortably over the fifty character minimum for captions.",
        "hook": "The pigeon in all of us",
        "cards": [
            "Card two text that is long enough to pass the gate.",
            "Card three text that is long enough to pass the gate.",
            "Card four text that is long enough to pass the gate.",
            "Card five text that is long enough to pass the gate.",
            "Card six text that is long enough to pass the gate.",
        ],
        "cta": "Follow @athena for one useful idea a week.",
    }


def test_gate_failure_writes_nothing(monkeypatch):
    client = MagicMock()
    bad = good_payload()
    bad["hook"] = "x" * 500
    with pytest.raises(gates.GateError):
        write_carousel.run(client, "db2", bad)
    client.pages.create.assert_not_called()
    client.pages.update.assert_not_called()


def test_success_inserts_and_flips_paper_status(monkeypatch):
    client = MagicMock()
    client.pages.create.return_value = {"id": "car1", "url": "https://notion.so/car1"}
    result = write_carousel.run(client, "db2", good_payload())
    assert result["url"] == "https://notion.so/car1"
    client.pages.update.assert_called_once_with(
        page_id="paper1",
        properties={"Status": {"select": {"name": "Written"}}},
    )
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_write_carousel.py -v`
Expected: FAIL — module missing.

- [ ] **Step 3: Write minimal implementation**

```python
# src/write_carousel.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_write_carousel.py -v`
Expected: 2 PASS.

- [ ] **Step 5: Commit**

```bash
git add src/write_carousel.py tests/test_write_carousel.py
git commit -m "Add carousel-write CLI: char gate first, Draft insert, paper status flip

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 8: athena_cards.html — the brand template

Static HTML, 7 card divs, `{{PLACEHOLDER}}` slots. All values from the Brand
Book: Paper `#F4EDDF`, Ink `#24201A`, Coral `#E4694A`, Columbia `#B9D9EB`,
Slate `#3F5169`, Taupe `#8A7E70`, Night `#14110D`; Newsreader + Work Sans;
Display 76 / Quote 48 / Subhead 40 / Body 34 / Label 22 / Handle 26 px; owl
top-centre (image if `assets/owl.png` exists — `onerror` hides it, wordmark
stays), `@athena.reads` handle bottom-centre; one accent per card max.

**Files:**
- Create: `template/athena_cards.html`

- [ ] **Step 1: Write the template**

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Athena carousel</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,500;1,400&family=Work+Sans:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root {
    --paper: #F4EDDF; --ink: #24201A; --coral: #E4694A;
    --columbia: #B9D9EB; --slate: #3F5169; --taupe: #8A7E70; --night: #14110D;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { background: #777; }
  .card {
    width: 1080px; height: 1350px; background: var(--paper); color: var(--ink);
    position: relative; display: flex; flex-direction: column;
    align-items: center; justify-content: center; text-align: center;
    padding: 120px 96px; overflow: hidden; margin: 24px auto;
  }
  .masthead {
    position: absolute; top: 56px; left: 0; right: 0; text-align: center;
    font-family: "Work Sans", sans-serif; font-weight: 500; font-size: 26px;
    letter-spacing: .35em; color: var(--slate);
  }
  .masthead img { height: 56px; display: block; margin: 0 auto 8px; }
  .handle {
    position: absolute; bottom: 56px; left: 0; right: 0; text-align: center;
    font-family: "Work Sans", sans-serif; font-size: 26px;
    letter-spacing: .25em; color: var(--taupe);
  }
  .display { font-family: "Newsreader", serif; font-weight: 500; font-size: 76px; line-height: 1.15; }
  .quote   { font-family: "Newsreader", serif; font-style: italic; font-size: 48px; line-height: 1.35; }
  .subhead { font-family: "Work Sans", sans-serif; font-weight: 600; font-size: 40px; line-height: 1.3; }
  .body    { font-family: "Work Sans", sans-serif; font-size: 34px; line-height: 1.5; }
  .label {
    font-family: "Work Sans", sans-serif; font-weight: 600; font-size: 22px;
    letter-spacing: .3em; text-transform: uppercase;
  }
  /* card 1 — cover: coral underline under the hook */
  .cover .display::after {
    content: ""; display: block; width: 180px; height: 6px;
    background: var(--coral); margin: 48px auto 0;
  }
  /* cards 2 (calm) and 6 (calm on night) */
  .calm-night { background: var(--night); color: var(--paper); }
  .calm-night .masthead { color: var(--paper); }
  .calm-night .handle { color: var(--taupe); }
  /* card 3 — punchy: slate label bar above the statement */
  .punchy .bar {
    background: var(--slate); color: var(--paper); padding: 14px 36px;
    margin-bottom: 56px;
  }
  /* card 4 — turn: coral eyebrow label */
  .turn .eyebrow { color: var(--coral); margin-bottom: 48px; }
  /* card 5 — insight: columbia highlight behind the text block */
  .insight .highlight {
    background: var(--columbia); padding: 40px 48px;
    box-decoration-break: clone; -webkit-box-decoration-break: clone;
  }
  /* card 7 — CTA */
  .cta .eyebrow { color: var(--slate); margin-bottom: 48px; }
</style>
</head>
<body>

<section class="card cover" data-card="1">
  <div class="masthead"><img src="assets/owl.png" alt="" onerror="this.style.display='none'">ATHENA…</div>
  <h1 class="display">{{HOOK}}</h1>
  <div class="handle">@athena.reads</div>
</section>

<section class="card calm" data-card="2">
  <div class="masthead"><img src="assets/owl.png" alt="" onerror="this.style.display='none'">ATHENA…</div>
  <p class="quote">{{CARD2}}</p>
  <div class="handle">@athena.reads</div>
</section>

<section class="card punchy" data-card="3">
  <div class="masthead"><img src="assets/owl.png" alt="" onerror="this.style.display='none'">ATHENA…</div>
  <div><span class="label bar" style="display:inline-block;">THE STUDY</span>
  <p class="subhead">{{CARD3}}</p></div>
  <div class="handle">@athena.reads</div>
</section>

<section class="card turn" data-card="4">
  <div class="masthead"><img src="assets/owl.png" alt="" onerror="this.style.display='none'">ATHENA…</div>
  <div><div class="label eyebrow">THE TURN</div>
  <p class="body">{{CARD4}}</p></div>
  <div class="handle">@athena.reads</div>
</section>

<section class="card insight" data-card="5">
  <div class="masthead"><img src="assets/owl.png" alt="" onerror="this.style.display='none'">ATHENA…</div>
  <p class="body highlight">{{CARD5}}</p>
  <div class="handle">@athena.reads</div>
</section>

<section class="card calm-night" data-card="6">
  <div class="masthead"><img src="assets/owl.png" alt="" onerror="this.style.display='none'">ATHENA…</div>
  <p class="quote">{{CARD6}}</p>
  <div class="handle">@athena.reads</div>
</section>

<section class="card cta" data-card="7">
  <div class="masthead"><img src="assets/owl.png" alt="" onerror="this.style.display='none'">ATHENA…</div>
  <div><div class="label eyebrow">ONE USEFUL IDEA A WEEK</div>
  <p class="subhead">{{CTA}}</p></div>
  <div class="handle">@athena.reads</div>
</section>

</body>
</html>
```

- [ ] **Step 2: Eyeball it** — substitute sample copy by hand into a scratch
copy (`/private/tmp/.../athena_preview.html` or scratchpad), open in a browser,
check: paper background, serif hook, one accent per card, masthead/handle
present on all 7. This is a visual sanity check, not a test.

- [ ] **Step 3: Commit**

```bash
git add template/athena_cards.html
git commit -m "Add brand-book-exact 7-card HTML template (paper bg, Newsreader/Work Sans, one accent per card)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 9: render.py — fill, screenshot, verify, flip statuses

Split: `fill_template` (pure, unit-tested) · `render_cards` (browser,
`@pytest.mark.browser`) · `main` (Notion orchestration, tested by smoke test).

**Files:**
- Create: `src/render.py`
- Test: `tests/test_template_fill.py`, `tests/test_render.py`

- [ ] **Step 1: Write the failing fill tests**

```python
# tests/test_template_fill.py
import pytest

from src import render


COPY = {
    "hook": "The pigeon in all of us",
    "cards": ["two", "three", "four", "five", "six"],
    "cta": "Follow for more",
}


def test_all_placeholders_replaced():
    html = render.fill_template(render.TEMPLATE_PATH.read_text(), COPY)
    assert "{{" not in html and "}}" not in html
    assert "The pigeon in all of us" in html


def test_html_is_escaped():
    copy = dict(COPY, hook="<script>alert(1)</script>")
    html = render.fill_template(render.TEMPLATE_PATH.read_text(), copy)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html


def test_empty_slot_refuses():
    copy = dict(COPY, cta="")
    with pytest.raises(render.RenderError, match="cta"):
        render.fill_template(render.TEMPLATE_PATH.read_text(), copy)
```

- [ ] **Step 2: Write the failing browser test**

```python
# tests/test_render.py
import pytest
from PIL import Image

from src import render


@pytest.mark.browser
def test_renders_seven_pngs_at_exact_dims(tmp_path):
    copy = {
        "hook": "The pigeon in all of us",
        "cards": [
            "Fifty years ago, a psychologist put a pigeon in a box.",
            "The pigeon learned superstition in under a minute.",
            "Reward arrived at random. The pigeon invented rituals.",
            "We do the same thing with luck, streaks, and routines.",
            "Noticing the ritual is the first step out of it.",
        ],
        "cta": "Follow @athena for one useful idea a week.",
    }
    paths = render.render_carousel_copy(copy, tmp_path)
    assert [p.name for p in paths] == [f"card-0{i}.png" for i in range(1, 8)]
    for p in paths:
        assert Image.open(p).size == (1080, 1350)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `pytest tests/test_template_fill.py tests/test_render.py -v`
Expected: FAIL — module missing.

- [ ] **Step 4: Write the implementation**

```python
# src/render.py
"""CLI: render a Carousel row to seven verified 1080x1350 PNGs.

Usage: python -m src.render <carousel_page_id> [--slug my-carousel]
Gates: all 7 slots non-empty; fonts loaded (15s budget); every screenshot
exactly 1080x1350 — anything else aborts with statuses untouched.
"""
import argparse
import html as html_lib
import re
import tempfile
from pathlib import Path

from PIL import Image

from src import notion_io, slots

TEMPLATE_PATH = Path(__file__).parent.parent / "template" / "athena_cards.html"
CARD_SIZE = (1080, 1350)


class RenderError(RuntimeError):
    pass


def fill_template(template_text: str, copy: dict) -> str:
    values = {
        "HOOK": copy["hook"],
        "CARD2": copy["cards"][0],
        "CARD3": copy["cards"][1],
        "CARD4": copy["cards"][2],
        "CARD5": copy["cards"][3],
        "CARD6": copy["cards"][4],
        "CTA": copy["cta"],
    }
    empties = [k for k, v in {**copy, "cards": ""}.items() if isinstance(v, str) and not v.strip()]
    empties += [f"cards.{i}" for i, v in enumerate(copy["cards"]) if not v.strip()]
    if empties:
        raise RenderError(f"empty slots: {', '.join(empties)}")

    filled = template_text
    for key, value in values.items():
        filled = filled.replace("{{" + key + "}}", html_lib.escape(value))
    leftover = re.findall(r"\{\{[A-Z0-9]+\}\}", filled)
    if leftover:
        raise RenderError(f"unfilled placeholders: {leftover}")
    return filled


def render_carousel_copy(copy: dict, out_dir: Path) -> list:
    """Pure copy → PNGs (no Notion). Used by main() and by tests."""
    from playwright.sync_api import sync_playwright

    filled = fill_template(TEMPLATE_PATH.read_text(), copy)
    out_dir.mkdir(parents=True, exist_ok=True)
    # write next to the template so relative assets/ URLs resolve
    with tempfile.NamedTemporaryFile(
        "w", suffix=".html", dir=TEMPLATE_PATH.parent, delete=False
    ) as f:
        f.write(filled)
        page_path = Path(f.name)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(
                viewport={"width": 1200, "height": 1500}, device_scale_factor=1
            )
            page.goto(page_path.as_uri())
            page.wait_for_function(
                "document.fonts.status === 'loaded'", timeout=15000
            )
            cards = page.locator(".card")
            if cards.count() != 7:
                raise RenderError(f"expected 7 cards, found {cards.count()}")
            paths = []
            for i in range(7):
                out = out_dir / f"card-0{i + 1}.png"
                cards.nth(i).screenshot(path=str(out))
                paths.append(out)
            browser.close()
    finally:
        page_path.unlink(missing_ok=True)

    for path in paths:
        size = Image.open(path).size
        if size != CARD_SIZE:
            raise RenderError(f"{path.name} is {size}, must be {CARD_SIZE}")
    return paths


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("carousel_page_id")
    parser.add_argument("--slug", default=None)
    args = parser.parse_args()

    client = notion_io.client()
    copy = notion_io.fetch_carousel(client, args.carousel_page_id)
    slug = args.slug or re.sub(r"[^a-z0-9]+", "-", copy["hook"].lower()).strip("-")
    out_dir = Path("output") / slug

    paths = render_carousel_copy(copy, out_dir)

    notion_io.update_status(
        client, args.carousel_page_id, slots.PROP_STATUS, "Rendered"
    )
    if copy["paper_page_id"]:
        notion_io.update_status(
            client, copy["paper_page_id"], slots.PAPER_STATUS, "Rendered"
        )
    print(f"rendered {len(paths)} cards → {out_dir}/")


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run all tests**

Run: `pytest -v`
Expected: everything passes, including the browser test (chromium was installed
in Task 0). If running somewhere without chromium: `pytest -v -m "not browser"`.

- [ ] **Step 6: Visual check** — run the browser test's copy through
`render_carousel_copy` into `output/preview/`, open the 7 PNGs, eyeball against
the brand book (paper bg, accents, masthead/handle).

```bash
python -c "
from pathlib import Path
from src.render import render_carousel_copy
copy = {
  'hook': 'The pigeon in all of us',
  'cards': [
    'Fifty years ago, a psychologist put a pigeon in a box.',
    'The pigeon learned superstition in under a minute.',
    'Reward arrived at random. The pigeon invented rituals.',
    'We do the same thing with luck, streaks, and routines.',
    'Noticing the ritual is the first step out of it.',
  ],
  'cta': 'Follow @athena for one useful idea a week.',
}
render_carousel_copy(copy, Path('output/preview'))
print('open output/preview/ and eyeball')
"
open output/preview/
```

- [ ] **Step 7: Commit**

```bash
git add src/render.py tests/test_template_fill.py tests/test_render.py
git commit -m "Add renderer: template fill + Playwright screenshots, hard 1080x1350 gate

Pure fill_template is unit-tested (escaping, empty-slot refusal); browser test
verifies 7 PNGs at exact dims. Statuses flip only after all gates pass.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 10: The three skills

Skills are repo-local (`.claude/skills/`) so they ship with the project and
work when Claude Code runs from the repo root.

**Files:**
- Create: `.claude/skills/athena-discover/SKILL.md`
- Create: `.claude/skills/athena-write/SKILL.md`
- Create: `.claude/skills/athena-render/SKILL.md`

- [ ] **Step 1: Write athena-discover**

```markdown
---
name: athena-discover
description: Use when Ted wants to find psychology papers for Athena carousels — searches Consensus for a topic, filters for carousel-worthy findings, writes them to the Papers DB deduped by DOI.
---

# Athena: Discover papers

You need the Consensus MCP (search tool) connected. If it is not available,
stop and tell Ted — do not substitute web search.

1. Take the topic from the invocation (e.g. `/athena-discover procrastination`).
   If none given, ask Ted for one.
2. Search Consensus for psychology papers on the topic (plain query, no
   filters unless Ted asked). Aim for 5-15 candidate papers.
3. For each paper worth keeping, apply the filter bar — keep only if ALL hold:
   - a real empirical finding (not a proposal or pure theory),
   - actionable for a normal person,
   - explainable in one Instagram card.
4. Build `papers.json` in the scratchpad directory:
   `{"papers": [{"title", "authors", "year", "journal", "doi_url",
   "key_finding" (one plain-English sentence), "why_it_matters" (the A→B in
   one sentence), "status", "selection_reason"}]}`
   - Mark the strongest 1-3 papers `"status": "Selected"` with a one-line
     `selection_reason`; the rest `"Discovered"` with reason `""`.
   - Every paper needs a `doi_url` (DOI link preferred, else the paper URL) —
     it is the dedup key.
5. Run: `source .venv/bin/activate && python -m src.add_papers <path>/papers.json`
6. Report to Ted: inserted/skipped counts and which papers were Selected, with
   their one-line reasons.
```

- [ ] **Step 2: Write athena-write**

```markdown
---
name: athena-write
description: Use when Ted wants carousel copy written from a Selected paper — writes the 7-beat card copy and caption into the Carousels DB as Draft, char-gated in code.
---

# Athena: Write carousel copy

1. Identify the paper: Ted names it, or query the Papers DB (Notion MCP) for
   `Status = Selected` and confirm the pick with Ted. You need its Notion
   page id, Key Finding, and Why it matters.
2. Write the copy in Athena's voice — calm, literary, first-person-essayistic;
   describe rather than explain; no hype, no listicle tone. Seven beats:
   - **hook** (card 1, 10-100 chars): the big serif line. Announce the idea.
   - **cards[0]** setup (card 2, 20-280): the study's story, told like a scene.
   - **cards[1]** punchy (card 3, 20-280): the finding as one punchy statement.
   - **cards[2]** turn (card 4, 20-280): the negative frame — what it costs
     you to ignore this.
   - **cards[3]** insight (card 5, 20-280): the actionable move, concrete.
   - **cards[4]** reframe (card 6, 20-280): the reflective, quotable line.
   - **cta** (card 7, 10-200): follow/apply call, quiet not salesy.
   Plus **caption** (50-2500 chars): IG caption — the idea in 2-3 short
   paragraphs, cite the paper (authors, year, journal), end with a question.
3. Count characters yourself and stay inside every band — but do not trust
   yourself: the gate is enforced in code and will reject out-of-band copy.
4. Build `carousel.json` in the scratchpad:
   `{"paper_page_id", "caption", "hook", "cards": [5 strings], "cta"}`
5. Run: `source .venv/bin/activate && python -m src.write_carousel <path>/carousel.json`
   - If the gate rejects: fix ONLY the flagged fields, re-run. Never bypass.
6. Report the created Draft's Notion URL and show Ted the copy.
```

- [ ] **Step 3: Write athena-render**

```markdown
---
name: athena-render
description: Use when Ted wants a Draft carousel rendered to PNGs — runs the Playwright renderer, verifies 7 exact-dimension cards, flips statuses to Rendered.
---

# Athena: Render carousel

1. Identify the carousel: Ted names it, or query the Carousels DB (Notion MCP)
   for `Status = Draft` and confirm with Ted. You need its Notion page id.
2. Run: `source .venv/bin/activate && python -m src.render <carousel_page_id>`
   (optionally `--slug <short-name>`; default slug derives from the hook).
3. On success it prints the output dir (`output/<slug>/`, 7 PNGs). Open it:
   `open output/<slug>/`
4. Tell Ted the cards are ready to eyeball against the brand book and post.
   Posting is manual in this iteration; after Ted posts, statuses flip to
   Posted by hand or on request.
5. On failure (char gate, missing slots, wrong dims, fonts): report the exact
   error and fix the data, not the gate.
```

- [ ] **Step 4: Verify skill discovery** — from the repo root, confirm the
skills list in a fresh `claude` session shows the three `athena-*` skills
(or run `/athena-render` with no args and see it ask for a carousel). If
project-local skills don't appear, move the three dirs to
`~/.claude/skills/` and note the move in README's Configuration section.

- [ ] **Step 5: Commit**

```bash
git add .claude/skills
git commit -m "Add the three pipeline skills: discover (Consensus->Papers), write (7-beat copy, gated), render (PNGs)

Phase 2 code complete. Project state: ready for end-to-end smoke test.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 11: End-to-end smoke test + ship

The definition of shipped: one real carousel on disk, end to end.

- [ ] **Step 1: Discover** — run `/athena-discover procrastination` for real
(Consensus MCP). Verify rows appear in the Papers DB with correct statuses;
run it twice and confirm the second run reports all-skipped (dedup works).

- [ ] **Step 2: Write** — run `/athena-write` on the strongest Selected paper.
Verify: Carousel row is Draft, all CharCount_* populated, paper flipped to
Written. Deliberately check the gate once: hand it a hook >100 chars in a
scratch JSON and confirm non-zero exit with nothing written.

- [ ] **Step 3: Render** — run `/athena-render` on the Draft. Verify 7 PNGs at
1080×1350 in `output/<slug>/`, carousel + paper flipped to Rendered.

- [ ] **Step 4: Ted's QC pass** — Ted eyeballs the 7 cards against the brand
book (paper bg, type, accents, masthead/handle). Fix template issues found;
re-render; re-run `pytest -v` after any code change.

- [ ] **Step 5: Update docs** — README: fill in real usage notes learned during
smoke (skills location if moved, any font caveat). SPRINT.md: tick Phases 2-3,
Current phase → "MVP shipped — iteration 2 (auto-posting) next", update `Next:`
and `Human:` (owl.png asset if still missing; "post the first carousel").

- [ ] **Step 6: Commit + PR**

```bash
git add README.md SPRINT.md
git commit -m "MVP shipped: first end-to-end carousel rendered and QC'd

Smoke test passed: Consensus discovery (deduped), gated copywrite, 7-card
render at exact dims. Project state: MVP complete; iteration 2 = auto-posting.

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
git push -u origin athena-mvp
gh pr create --title "Athena MVP: paper-to-carousel pipeline" --body "$(cat <<'EOF'
One psychology paper → one 7-card rendered carousel, end to end.

- Notion data layer: Papers DB (funnel) + Carousels DB extensions
- Char gates enforced in code before any Notion write
- Deterministic render: brand-book HTML template + Playwright, hard 1080×1350 gate
- Three skills: /athena-discover, /athena-write, /athena-render
- Smoke-tested: first real carousel in output/

Spec: docs/superpowers/specs/2026-07-01-athena-mvp-design.md
Plan: docs/superpowers/plans/2026-07-01-athena-mvp.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Ted merges. **Do not merge it yourself.**

---

## Self-review notes (done at write time)

- **Spec coverage:** data layer (Task 1), discover/dedup (Tasks 5-6), write +
  char gates (Tasks 4, 7), render + dims gate (Tasks 8-9), skills (Task 10),
  smoke test / definition of shipped (Task 11). Card 6 spare + caption-as-title
  handled in slots.py/notion_io.py. Out-of-scope items untouched. ✓
- **Gate parity note:** `gates.validate_carousel` enforces bands at write time;
  `render.fill_template` re-checks only non-emptiness at render time (Notion
  edits between write and render can't blank a card silently). Band re-check at
  render is deliberately skipped — the render gate is about geometry, not copy.
- **Type consistency:** payload keys (`paper_page_id, caption, hook, cards[5],
  cta`) identical across gates/write_carousel/notion_io; `fetch_carousel`
  returns the render subset (`hook, cards, cta, paper_page_id`); slot constants
  used everywhere, no string literals duplicated. ✓
- **Known seam:** Task 1 Step 4 verifies REST access before any code exists to
  depend on it; if access fails it's a Human item, not a code bug.
