# Phase 38.12 Standard Site Rank and Verdict Repair

## Decision

`LIVE AND VERIFIED THROUGH DATA, QUERY, BUILD, AND REVISION CHECKS`

The Standard Player Profiles `ALL` board was incorrectly sorting positional Pigskin scores as if they were comparable overall scores. This displayed Josh Allen at overall 1 even though the published unified Standard board ranks him 6.

## Root Cause

`app.py` sorted the `ALL` directory by `display_score` across QB, RB, WR, and TE. Those scores are position-specific and cannot define overall draft order. The correct source already existed in `unified_draft_rankings_current`.

The same score sort also existed in the Pigskin live-ranking context query, allowing chat and the visible table to disagree with the unified board.

## Repairs

- Added a scoring-profile-scoped unified ranking query.
- Merged unified overall rank and formula metadata into Player Profiles.
- `ALL` now follows `unified_overall_rank` and shows only the unified Top 100.
- Position tabs retain their positional rank order.
- Pigskin's `ALL` context query now orders by unified rank.
- Added a formula banner above the table with each positional source, replacement rank, and unified board version.
- Renamed `Adjustment` to `Rank Change`.
- Replaced technical codes with readable labels such as `Formula rank`, `Role upgrade +2`, and `Injury noted, no move`.

The verified Standard unified top ten begins Christian McCaffrey, Jonathan Taylor, Bijan Robinson, Amon-Ra St. Brown, Jahmyr Gibbs, Josh Allen, Jaxon Smith-Njigba, Devon Achane, James Cook, and Puka Nacua.

## LLM Verdict Refresh

Gemini `gemini-3.5-flash` rewrote only `pigskin_verdict` for the 260 Standard rows displayed by Player Profiles. Ranks, scores, adjustment codes, and rationales were untouched.

- Generated rows: 260.
- Blank verdicts after update: 0.
- Rows marked with refreshed model provenance: 260.
- Distinct positional ranks after update: 260.
- Rollback rows: 270 active Standard rows.

Rollback table: `fantasy-football-498121.fantasy_football_advanced_metrics.standard_pigskin_verdict_rollback_20260712`.

RB32 Kimani Vidal now has a specific LLM verdict instead of `Pigskin ranking not materialized yet.`

## Deployment

- Image tag: `prod-aeaa4c45b157-r2026.07.12-standard-rank-ui`.
- Image digest: `sha256:d9dd2f821ff434086ce4e85dbb64d72de816272784538f09e19db4e9c4e5eeec`.
- Cloud Build: `db412900-8b00-41ee-8c8b-15b88aa4c578`.
- Cloud Run revision: `nfl-studio-dashboard-00092-rc5`.
- Traffic: 100%.

## Validation

- Python compilation passed.
- Thirteen focused Player Profiles tests passed.
- Live Standard `ALL` context query returned McCaffrey 1 and Allen 6.
- Cloud Run deployment completed successfully.
- Browser reload reached the new revision but required a fresh login, so no credentials were requested or entered. Visual post-login confirmation remains a user-session check.
