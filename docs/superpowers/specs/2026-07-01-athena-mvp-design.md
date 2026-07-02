# Athena MVP — Design

**Date:** 2026-07-01
**Status:** Approved by Ted (2026-07-01, brainstorming session)

## What Athena is (north star)

Athena is a content engine and newsletter funnel built on books and behavioral
science: a calm, literary brand ("a calm, literary voice that explains how the
mind works — one idea at a time, on warm paper, with an owl watching over it").
The signature long-term format is three-book trios per theme feeding a Beehiiv
newsletter; the secondary format goes deep on one concept.

**This MVP ships the smallest end-to-end slice:** one psychology paper → one
Instagram/TikTok carousel (the "one concept" format). Everything else — book
trios, bestseller-list ingestion, life-domain lanes, additional science variants
(neuroscience, evolutionary biology), Zo/cloud scheduling, auto-posting — is
explicitly out of scope for this iteration.

**Iteration 2 (agreed):** auto-posting to Instagram.

## Scope decisions (settled with Ted)

1. **One paper → one carousel.** No multi-paper synthesis or clustering in MVP.
2. **Single taxonomy tag:** `Variant = Consensus_Psychology`, `InputType =
   Consensus`. No life-domain lanes yet (they exist in the brand book as the
   four evergreen lanes and return in a later iteration).
3. **Output = copy + rendered cards (Option B).** Athena writes the card copy
   into Notion AND renders 7 finished 1080×1350 PNGs from a deterministic HTML
   template. Posting is manual (Ted downloads and posts).
4. **Interactive, not scheduled.** All stages run locally as Claude Code skills
   Ted triggers. The Consensus MCP is interactive-only in this setup (API key is
   Enterprise-only — lesson from Useful Math), and Zo-scheduled discovery is a
   possible later iteration (Zo⇄Consensus MCP connectivity unverified).

## Shape of the system

Three-stage, status-driven pipeline — the Useful Math pattern with carousel
production in place of video production:

```
/athena-discover → Papers DB (Notion) → /athena-write → Carousel DB (Notion)
                → /athena-render → 7 PNGs on disk → Ted posts manually
```

One paper = one carousel = seven 1080×1350 PNGs.

## Data layer (Notion, on the existing "🦉 Athena (Beehiiv)" page)

### New: Papers DB (the filter funnel)

| Field | Type | Notes |
|---|---|---|
| Title | title | paper title |
| Authors | text | |
| Year | number | |
| Journal | text | |
| DOI/URL | url | dedup key |
| Key Finding | text | one plain-English sentence |
| Why it matters | text | the A→B transformation in embryo |
| Status | select | `Discovered → Selected → Written → Rendered → Posted`, plus `Rejected` |

"Whittling" = flipping `Discovered → Selected` (Athena proposes, code + Ted can
override).

### Existing Carousel DB — kept as-is, lightly extended

Existing fields unchanged: `Content (2500 Chars Max)` (title), `Hook/Headline`,
`Card 1`–`Card 6`, `CTA`, all `CharCount_*` numbers, `InputType`, `Variant`.

Additions:
- `Status` (select): `Draft → Approved → Rendered → Posted`
- `Paper` (relation → Papers DB)

**Slot mapping (8 text slots, 7-card format):** `Hook/Headline` = card 01,
`Card 1`–`Card 5` = cards 02–06, `CTA` = card 07. **`Card 6` is intentionally
unused in MVP** (spare slot). `Content (2500 Chars Max)` (the title property) =
the Instagram post caption, written by `/athena-write` alongside the cards and
char-gated at 2500.

## Card grammar (from the brand book + carousel design artifact)

Every carousel is seven cards, 1080×1350, each with a designated beat, layout,
and accent:

| # | Beat | Layout / accent |
|---|---|---|
| 01 | Hook | Cover — big serif hook, Coral underline |
| 02 | Setup | Artwork (v0: Calm fallback, illustration slot empty) |
| 03 | Punchy | Punchy — dark label bar, one highlighted word |
| 04 | Turn | Coral emphasis |
| 05 | Insight | Columbia Blue signature |
| 06 | Reframe | Calm — centred serif, often Night background |
| 07 | CTA | CTA card |

Brand rules enforced by the template (from the Brand Book, the single source of
truth for visuals): Paper `#F4EDDF` background (never white), Ink `#24201A`
text, owl top-centre + @handle bottom-centre on every card, Newsreader for
headlines / Work Sans for everything else, nothing below 22px, **one accent per
card max** (Coral and Columbia Blue never on the same card), pen-and-ink
illustration style only (deferred to a later iteration).

## The three skills

### `/athena-discover <topic>`
Queries the Consensus MCP for psychology papers on a topic. Dedupes against
existing Papers rows by DOI/URL. Writes new rows as `Discovered`. Marks the
strongest 1–3 `Selected` with a one-line reason. Filter bar (judgment-based,
dead simple): real finding, actionable for a normal person, explainable in one
card.

### `/athena-write <paper>`
Takes a `Selected` paper and writes the 7-beat copy (Hook / Setup / Punchy /
Turn / Insight / Reframe / CTA) into the Carousel DB as `Draft`, linked to the
paper. **Char limits are a hard code gate, not LLM-trust** (Useful Math lesson):
out-of-band copy aborts before the Notion write. Computes every `CharCount_*`.

### `/athena-render <carousel>`
Python + Playwright. Pours the copy into `template/athena_cards.html` (built
once from the brand book), screenshots seven 1080×1350 PNGs into
`output/<slug>/`, flips carousel status to `Rendered` and paper status to
`Rendered`. Deterministic — no image-gen cost, no LLM QC judge needed.

## Gates & error handling

Interactive runs fail loudly in-session (no silent failures; SMS alerting joins
when stages get scheduled — per the household error-handling standard). Hard
gates in code:
- **discover:** dedup by DOI/URL before insert.
- **write:** every char count within band, else abort before writing Notion.
- **render:** all 7 slots non-empty, fonts loaded, screenshot dimensions exactly
  1080×1350, else abort and leave status untouched.

## Testing

- **TDD the deterministic parts:** char-gate logic, Notion I/O slot mapping,
  renderer output (file existence, dimensions).
- **Smoke test the LLM parts:** run the full pipeline once on a real topic.
- **Definition of shipped:** one "the pigeon in all of us"-grade carousel on
  disk, end-to-end, eyeballed by Ted against the brand book.

## Out of scope (explicit)

Book trios and the Books/Book List DBs · bestseller-list ingestion · life-domain
lanes · neuroscience/evo-bio variants · Zo/GitHub-Actions scheduling · Nano
Banana pen-and-ink illustrations · auto-posting (iteration 2) · Beehiiv
newsletter output · PDF notes / affiliate links.

## Known constraints & open items

- Consensus MCP: interactive-only (no headless API access on current plan).
- Zo⇄Consensus MCP connectivity: unverified; check when scheduling becomes
  relevant.
- Carousel design artifact (claude.ai): export HTML into the repo for
  pixel-exact template reference — Human item, not a blocker (brand book
  suffices to build the template).
