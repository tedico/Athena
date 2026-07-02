# Sprint Plan — Athena

## Phases
- [x] Phase 1 — Data layer: Papers DB created in Notion; Carousel DB extended (Status, Paper relation); schemas documented
- [x] Phase 2 — Skills: /athena-discover, /athena-write (with hard char gates), /athena-render (HTML template + Playwright, 7×1080×1350 PNGs)
- [x] Phase 3 — Ship: full smoke test — one real paper → one finished carousel on disk, QC'd against the brand book

## Current phase
MVP shipped (pending Ted's QC + PR merge) — iteration 2 is the CORRECTION LOOP:
Ted exercises the pipeline, flags wrong outputs, we fix until this stage is
very-high-percentage correct. Auto-posting is DEFERRED until that bar is met.

## Next
Negative-feedback session: Ted runs the pipeline for real (discover → write →
render on topics he picks), collects every mistake (copy voice, card layout,
data handling, skill behavior), and we fix them one by one. Also verify the
repo-local .claude/skills are discovered in a fresh claude session from the
repo root (smoke test drove the CLIs directly).

## Human
- QC the 7 rendered cards (output/the-feeling-is-the-problem/) and merge the PR
- Post the first carousel to Instagram; then flip its Notion statuses to Posted
- Drop the owl logo at template/assets/owl.png (masthead auto-uses it; wordmark-only until then)
- Export the "Athena Carousel" claude.ai design artifact as HTML into the repo
  (pixel-exact template reference; brand book suffices meanwhile — not a blocker)

## Blockers
none
