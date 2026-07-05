# 🦉 Athena

## What & why

**Why this exists:** Athena is Ted's calm, literary brand about how the mind
works — a newsletter built on books. Its signature product: **3 books → 1
theme → 1 useful synthesized idea**, shipped as a 7-card Instagram carousel
(and eventually a Beehiiv newsletter). Athena synthesizes books; it never
summarizes them.

**What it solves:** turns the Notion pipeline — Book List (authority
sources) → Books → Issues (trio + theme + idea) → Carousels — into finished,
brand-book-exact 1080×1350 cards, with pen-and-ink illustrations from this
repo's own engine.

**Where it fits:** Athena is book-anchored, always 7 cards, always static
"paper" output — never video. Research papers are NOT an Athena lane
anymore (decided 2026-07-05): the paper→carousel code in this repo
(`add_papers`, `write_carousel`, the `/athena-*` skills) is the **parked
probe** that proved the Consensus supply line works. That supply line now
lives in [Alexandria](https://github.com/tedico/alexandria) (the shared
paper shelf), and paper-based video content ships via
[super-psychology](https://github.com/tedico/super-psychology). If a
psychology-carousel branch ever becomes real, it clones the parked code into
its own repo — engines are never shared.

Original MVP design (historical): [docs/superpowers/specs/2026-07-01-athena-mvp-design.md](docs/superpowers/specs/2026-07-01-athena-mvp-design.md)

## Constraints

- **Consensus is interactive-only** — the paper search runs as a Claude Code
  skill with the Consensus MCP in an interactive session; no headless/scheduled
  discovery in this iteration.
- **Char counts are hard code gates** — copy that exceeds a card's character
  band aborts the pipeline before any Notion write, no LLM-trust.
- **Rendering is deterministic** — text poured into an HTML template and
  screenshotted; no generative image models in the MVP.
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

- `.env` — `NOTION_API_KEY` (see `.env.example`; secrets are never committed —
  gitleaks pre-commit + GitHub push protection are active)
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
