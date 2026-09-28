# Phase 36.1 Unified Fable v1 Standard Top-100 Report

## Final Decision

`REVIEW-ONLY TOP-100 GENERATED`

The first unified Standard preseason top-100 is complete. It freezes each positional queue, maps positional rank to fitted historical Standard PPG, calculates value over replacement, applies position-level availability and onesie multipliers, and sorts by adjusted VORP. No player is reordered inside a position.

The board is coherent enough for owner review. It is not ready for live promotion because the unified interleaving has not yet completed a pooled realized-VORP backtest or a draft-slot simulation.

## Positional Inputs

| Position | Frozen queue |
|---|---|
| QB | Active guarded 75/25 Standard QB, `standard-qb-guarded-75-25-20260711214758` |
| RB | Active RB Fable v1 Standard champion, `rb-fable-v1-standard-20260710054940` |
| WR | Retained WR Fable v1 2025-source research score, ordered directly by `wr_fable_v1_score` |
| TE | Active guarded TE Fable champion, `te-fable-guarded-pigskin-20260711010953` |

The active Standard WR table still uses `pigskin-llm-20260704071412`. It was deliberately not used because the repository's final WR formula decision retained WR Fable v1. This phase does not promote WR Fable or alter the active WR table.

## Historical Curves

Curves were fit on 2022-2025 Standard PPG, pooling qualified player-seasons with at least six games:

| Position | Fitted curve |
|---|---|
| QB | `25.482 - 3.298 * ln(rank)` |
| RB | `21.231 - 3.689 * ln(rank)` |
| WR | `16.312 - 2.440 * ln(rank)` |
| TE | `11.123 - 2.028 * ln(rank)` |

Availability is the average capped `games_played / 17` among historical players through each replacement rank. Fitted values are QB 0.911, RB 0.884, WR 0.866, and TE 0.843. Onesie multipliers remain the attached contract values: QB 0.85, TE 0.90, RB/WR 1.00.

## Replacement Calibration

The attached starting baselines, QB13/RB28/WR40/TE13, produced 29 RB, 43 WR, 14 QB, and 14 TE. That failed the composition smoke test by underpulling RB and overpulling TE.

Replacement ranks were tuned first, as the contract requires. The selected review setup is:

- QB13
- RB34
- WR40
- TE9

Final composition: 35 RB, 43 WR, 13 QB, and 9 TE. WR is one player above the expected 38-42 band; forcing another adjustment for one boundary player is not justified before the historical interleaving backtest.

## Top 12

| Overall | Player | Position rank |
|---:|---|---|
| 1 | Christian McCaffrey | RB1 |
| 2 | Jonathan Taylor | RB2 |
| 3 | Bijan Robinson | RB3 |
| 4 | Amon-Ra St. Brown | WR1 |
| 5 | Jahmyr Gibbs | RB4 |
| 6 | Josh Allen | QB1 |
| 7 | Jaxon Smith-Njigba | WR2 |
| 8 | Devon Achane | RB5 |
| 9 | James Cook | RB6 |
| 10 | Puka Nacua | WR3 |
| 11 | Javonte Williams | RB7 |
| 12 | Rashee Rice | WR4 |

## Checks

- Three focused unit tests passed for curve fitting, queue monotonicity, and skip-ahead rejection.
- Exactly 100 unique player IDs.
- Positional ranks are contiguous from 1 through each position's final included player.
- No duplicate identity entered the board.
- Historical curve inputs stop at 2025. No 2026 outcome is used.
- BigQuery statements are SELECT-only.

## Known Review Risks

- The unified board inherits every positional queue decision. VORP does not repair a questionable positional rank.
- WR Fable v1 excludes players without a qualified 2025 source season. No ADP or market splice was invented in this phase.
- Current injury and depth flags are displayed but do not change order.
- Several TE rows retain `STALE_ROSTER` or `CURRENT_TEAM_UNKNOWN` warnings from the active guarded board.
- Negative adjusted VORP appears at the final boundary because the deliverable requires exactly 100 players. Those rows are below modeled replacement but still win the last cross-position slots.

## Files

- `scripts/build_unified_fable_v1_top100.py`
- `tests/test_unified_fable_v1_top100.py`
- `docs/rebuild/unified-fable-v1-standard-top100.md`
- `output/unified-fable-v1-standard-top100.json` (local evidence)
- this report

## Next Gate

Run the 2022-to-2023, 2023-to-2024, and 2024-to-2025 pooled realized-VORP folds using the same frozen-queue rule. Do not promote or publish a live overall board until that backtest measures cross-position ordering rather than positional ranking alone.
