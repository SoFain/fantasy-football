# Phase 38.18 Teamless Players Structurally Unranked

## Decision

Teamless status is now a shared structural exclusion. It is not a named exception or an injury-style review flag.

No live ranking, unified board, champion, or public object changed in this phase.

## Shared Contract

`v_ranking_post_formula_safety` now exposes `current_board_rank_eligible`.

- A matched Sleeper player with `team=NULL` receives `current_board_rank_eligible=FALSE`.
- The stored eligibility label is `teamless_unranked`.
- Candidate builders remove those rows before assigning ranks and backfill from eligible players.
- Public JSON generation fails closed if an overall or positional source row is teamless according to the current Sleeper layer.

Current status still stays out of historical formulas and backtests.

## Standard WR

The repaired Standard WR research board has 100 unique players and zero teamless rows. The elite-order guardrail remains:

| Rank | Player |
|---:|---|
| 13 | A.J. Brown |
| 14 | Justin Jefferson |
| 15 | Garrett Wilson |

The WR watchlist now contains 20 teamless qualified players. DeAndre Hopkins is unranked without another name-specific decision.

## GNG Research Boards

Both GNG research boards contain 260 players and zero rows without a current team.

The GNG watchlist contains 45 no-team rows:

- QB: 3.
- RB: 16.
- WR: 20.
- TE: 6.

## PPR and Half-PPR Promotion Guard

Future PPR and Half-PPR promotion SQL now excludes teamless candidates and teamless fallbacks before reranking.

| Profile | Position | Rank-eligible candidates | Teamless excluded |
|---|---|---:|---:|
| PPR | RB | 85 | 5 |
| PPR | WR | 125 | 7 |
| PPR | TE | 72 | 4 |
| Half-PPR | RB | 85 | 5 |
| Half-PPR | WR | 125 | 7 |
| Half-PPR | TE | 72 | 4 |

Both promotion SQL paths dry-run successfully. Neither live board was promoted.

## Live Audit

The active unified Top 100 boards currently contain zero no-team or missing-context players in every scoring profile.

The older active positional boards still contain rows rejected by the new current-team rule:

| Profile | Rejected active positional rows |
|---|---:|
| Standard | 10 |
| PPR | 7 |
| Half-PPR | 7 |
| GNG Keeper | 19 |

The public publisher now fails closed on those stale positional boards. A Standard local publication attempt stopped on `standard RB board contains teamless player Kareem Hunt`. Nothing was published.

## Next Gate

Rebuild and promote each affected positional queue, regenerate the unified boards from those queues, then publish new immutable JSON. Do not bypass the publisher failure.
