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
