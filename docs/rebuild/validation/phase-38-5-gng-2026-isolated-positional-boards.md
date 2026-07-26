# Phase 38.5 GNG 2026 Isolated Positional Boards

## Decision

`ISOLATED BOARDS GENERATED; PLAYER REVIEW REQUIRED; PRODUCTION UNCHANGED`

The four selected GNG formulas were applied to a 2023-2025 source window and joined to the Sleeper current-player layer. The results were written only to the isolated advanced-metrics dataset.

## Objects

- `fantasy-football-498121.fantasy_football_advanced_metrics.gng_2026_positional_candidate_boards`
- `fantasy-football-498121.fantasy_football_advanced_metrics.gng_2026_rookie_review`

The active production GNG version remains `pigskin-llm-20260704072119` for every position.

## Board Contract

| Position | Formula | Rows | Rank range | Null scores | Hard reviews | Any Sleeper flag |
|---|---|---:|---|---:|---:|---:|
| QB | Q4 GNG bonus proxy | 45 | 1-45 | 0 | 2 | 8 |
| RB | R7 H1/R2 compromise | 80 | 1-80 | 0 | 8 | 17 |
| WR | W10 H5 floor first | 100 | 1-100 | 0 | 13 | 24 |
| TE | H5 stability hybrid | 35 | 1-35 | 0 | 4 | 10 |

There are zero duplicate position-rank groups and every board has contiguous ranks.

## Sleeper Layer

The board uses the 12,200-player Sleeper snapshot fetched at `2026-07-11T23:53:26.619596Z`.

- Depth order 1 receives `+0.02`.
- Depth order 3 or worse receives `-0.04`.
- Injury, unknown depth, rookie, and roster-status problems produce explicit flags.
- Status and injury fields do not automatically move or delete players.

The initial GSIS-only dry run produced excessive false reviews. The final join uses `player_identity_bridge`, direct Sleeper IDs, GSIS IDs, and a unique normalized-name fallback. Three lower-board rows still have no Sleeper match: RB55 Bam Knight, RB63 Audric Estime, and WR81 Josh Palmer. They remain flagged for identity review.

The hard-review set otherwise consists mainly of active-status players with no current Sleeper team, including Russell Wilson, Kareem Hunt, Tyreek Hill, Keenan Allen, Stefon Diggs, Deebo Samuel, Zach Ertz, and Jonnu Smith. These are review findings, not silent exclusions.

## Rookie Lane

Sleeper active, rostered, first-year players were written separately because a prior-season production formula cannot score them fairly.

| Position | Rookie rows |
|---|---:|
| QB | 22 |
| RB | 45 |
| WR | 103 |
| TE | 49 |

This is a broad review population, not a draft ranking. Rookie ordering requires its own prospect and role inputs.

## Current Top Five

| Position | Rank 1 | Rank 2 | Rank 3 | Rank 4 | Rank 5 |
|---|---|---|---|---|---|
| QB | Brock Purdy | Trevor Lawrence | Drake Maye | Jalen Hurts | Joe Burrow |
| RB | Jonathan Taylor | Christian McCaffrey | Jahmyr Gibbs | Saquon Barkley | Bijan Robinson |
| WR | Puka Nacua | Jaxon Smith-Njigba | Rashee Rice | Amon-Ra St. Brown | Ja'Marr Chase |
| TE | Trey McBride | Tucker Kraft | Brock Bowers | Harold Fannin Jr. | Jake Ferguson |

## Artifacts and Checks

- Added `scripts/build_gng_2026_candidate_boards.py`.
- Added formula, board-size, source-window, and Sleeper-query regression checks.
- Generated `output/gng-2026-positional-candidate-boards.json`.
- Python compilation passed.
- BigQuery row-count, formula, duplicate-rank, null-score, rookie-count, and production-version checks passed.
- No production ranking, formula champion, or active row changed.

## Next Phase

Review top-player ordering, hard-review rows, injury flags, current-team changes, and the rookie lane. Correct confirmed identity issues before deciding whether the positional boards are ready for unified GNG interleaving.
