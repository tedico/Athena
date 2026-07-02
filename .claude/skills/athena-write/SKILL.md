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
