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
