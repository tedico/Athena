# 🦉 Athena

## What & why

Athena is a content engine for a calm, literary brand about how the mind works.
This repo is the MVP slice: **one psychology paper → one Instagram/TikTok
carousel** — search academic literature (via the Consensus MCP), whittle papers
in a Notion funnel, write 7-card copy, and render seven finished 1080×1350 PNGs
from a brand-book-exact HTML template. The long-term system (three-book trios,
Beehiiv newsletter, auto-posting) grows from this seed.

Full design: [docs/superpowers/specs/2026-07-01-athena-mvp-design.md](docs/superpowers/specs/2026-07-01-athena-mvp-design.md)

## Constraints

- **Consensus is interactive-only** — the paper search runs as a Claude Code
  skill with the Consensus MCP in an interactive session; no headless/scheduled
  discovery in this iteration.
- **Char counts are hard code gates** — copy that exceeds a card's character
  band aborts the pipeline before any Notion write, no LLM-trust.
- **Rendering is deterministic** — text poured into an HTML template and
  screenshotted; the only generative step is the optional illustration engine
  (`src/illustrate.py`), which never touches copy or layout.
- **Posting is manual** — auto-posting to Instagram is iteration 2.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # add your Notion API key (never committed)
```

Requires: a Notion integration with access to the Athena page, and the
Consensus MCP connected in Claude Code (for the discover stage).

## Usage

Three Claude Code skills, run in order:

```
/athena-discover <topic>   # Consensus search → Papers DB (Discovered/Selected)
/athena-write <paper>      # Selected paper → 7-card copy in Carousel DB (Draft)
/athena-render <carousel>  # copy → output/<slug>/card-0{1..7}.png (Rendered)
```

Then download the PNGs and post. The skills live in `.claude/skills/` (repo-local,
available when Claude Code runs from the repo root); each one orchestrates a
tested CLI (`src/add_papers.py`, `src/write_carousel.py`, `src/render.py`) that
can also be run directly.

**Illustrations** (pen-and-ink, transparent background, brand-Ink line work):

```bash
python -m src.illustrate "a moth drawn toward a candle flame" -o moth.png
python -m src.illustrate --from-png raw.png -o clean.png  # transparency pass only
```

`src/illustrate.py` is Athena's own engine (cloned from Useful Math on
2026-07-05, then adapted) — **engines are never shared across projects**. It
wraps the brand prompt template around a subject, calls Gemini, then converts
the white paper to alpha with the line work tinted Ink `#24201A`, so the PNG
sits directly on the Paper card background.

## How it works

Status-driven pipeline over two Notion databases:

```
/athena-discover → Papers DB → /athena-write → Carousel DB → /athena-render → 7 PNGs → manual post
```

Each carousel is seven cards with fixed beats:
Hook → Setup → Punchy → Turn → Insight → Reframe → CTA, styled per the Athena
brand book (Paper background, Newsreader + Work Sans, owl + @handle on every
card, one accent per card max).

## Configuration

- `.env` — `NOTION_API_KEY`, `GOOGLE_API_KEY` (see `.env.example`; secrets are
  never committed — gitleaks pre-commit + GitHub push protection are active)
- Notion database IDs — constants documented in `src/` once Phase 1 lands
- `template/athena_cards.html` — the brand-book-exact card template

## Troubleshooting

- **Render aborts with a char-count error** — the copy in Notion exceeds a
  card's band; edit the card text or re-run `/athena-write`.
- **PNGs are the wrong size** — the renderer hard-fails unless screenshots are
  exactly 1080×1350; check Playwright viewport config.
- **Discover finds nothing new** — dedup is by DOI/URL; the topic may already
  be harvested.

## Legend

- 🦉 — Athena, obviously
- **Paper** — one academic paper (a row in the Papers DB)
- **Carousel** — one 7-card Instagram post (a row in the Carousel DB)
- **Beat** — a card's assigned rhetorical job (Hook, Setup, Punchy, …)
- **A→B** — the transformation a piece of content promises the reader
