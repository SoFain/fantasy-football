# Phase 38.17 Standard WR Elite Order and Watchlist

## Decision

The owner-approved A.J. Brown elite-order guardrail is active on the repaired Standard WR research board. Hunter Renfrow, Gabe Davis, and Sterling Shepard joined the existing teamless watchlist.

No active ranking, unified board, champion, or public JSON feed changed.

## Elite Guardrail

The guardrail reorders only the three occupied slots. It does not create a broad top-12 anchor or alter another player's slot.

| Final rank | Player | Post-safety rank | Formula rank | Guardrail movement |
|---:|---|---:|---:|---:|
| 13 | A.J. Brown | 15 | 15 | +2 |
| 14 | Justin Jefferson | 13 | 13 | -1 |
| 15 | Garrett Wilson | 14 | 14 | -1 |

Each row stores `OWNER_APPROVED_ELITE_ORDER` plus the unchanged formula score and current-role adjustment provenance.

## Teamless Watchlist

The unranked watchlist now contains six owner-approved WRs:

- Stefon Diggs
- Deebo Samuel
- Keenan Allen
- Hunter Renfrow
- Gabe Davis
- Sterling Shepard

All six have `current_team=NULL`, `sleeper_hard_review=TRUE`, and `watchlist_code=OWNER_APPROVED_TEAMLESS_WATCHLIST`. None remains on the 100-player candidate board.

The shared decisions live in `src/ranking_owner_decisions.py`. The Standard WR and GNG builders import that source instead of keeping separate name lists.

## Research Objects

- Board: `fantasy_football_advanced_metrics.standard_wr_fable_v1_post_formula_review`
- Watchlist: `fantasy_football_advanced_metrics.standard_wr_fable_v1_unranked_watchlist`

Board validation:

- 100 rows.
- 100 unique players.
- 100 unique ranks from 1 through 100.
- Zero missing Sleeper identities.

## New Cutoff Review

Removing the six approved watchlist players initially backfilled DeAndre Hopkins at WR95. Phase 38.18 superseded the named-only rule: every player without a current team is now structurally unranked. Hopkins and every lower teamless WR moved to the watchlist.

## Checks

- Focused Python unit tests passed.
- Edited Python modules compiled.
- Research tables were written and read back successfully.
- GNG candidate generation completed without `--apply` using the shared watchlist source.
- Active Standard WR remains `pigskin-llm-20260704071412`, 100 rows, ranks 1 through 100.
