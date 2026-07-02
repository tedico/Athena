# Sprint Plan — Athena

## Phases
- [x] Phase 1 — Data layer: Papers DB created in Notion; Carousel DB extended (Status, Paper relation); schemas documented
- [x] Phase 2 — Skills: /athena-discover, /athena-write (with hard char gates), /athena-render (HTML template + Playwright, 7×1080×1350 PNGs)
- [x] Phase 3 — Ship: full smoke test — one real paper → one finished carousel on disk, QC'd against the brand book

## Current phase
MVP shipped (pending Ted's QC + PR merge) — iteration 2 is auto-posting to Instagram.

## Next
Ted: QC output/the-feeling-is-the-problem/ against the brand book, merge the
athena-mvp PR, post the first carousel. Then: brainstorm iteration 2
(auto-posting). Also verify the repo-local .claude/skills are discovered in a
fresh claude session from the repo root (smoke test drove the CLIs directly).

## Human
- QC the 7 rendered cards (output/the-feeling-is-the-problem/) and merge the PR
- Post the first carousel to Instagram; then flip its Notion statuses to Posted
- Drop the owl logo at template/assets/owl.png (masthead auto-uses it; wordmark-only until then)
- Export the "Athena Carousel" claude.ai design artifact as HTML into the repo
  (pixel-exact template reference; brand book suffices meanwhile — not a blocker)

## Blockers
none
