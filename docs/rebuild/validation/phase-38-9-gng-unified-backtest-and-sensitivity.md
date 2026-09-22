# Phase 38.9 GNG Unified Backtest and Sensitivity

## Decision

`QB13 / RB36 / WR55 / TE12 SELECTED; REVIEW BOARD PASSES STRUCTURAL GATES`

The selected QB Q4, RB R7, WR W10, and TE H5 queues were evaluated over three next-season folds. Nine replacement-rank variants were tested. No production object changed.

## Aggregate Sensitivity

| Variant | Spearman | Positive VORP@100 | Top 24 hit | Top 50 hit | Top 100 hit |
|---|---:|---:|---:|---:|---:|
| QB15/RB36/WR55/TE12 | 0.694 | 0.867 | 0.458 | **0.667** | **0.770** |
| **QB13/RB36/WR55/TE12** | **0.697** | 0.865 | **0.500** | 0.647 | 0.767 |
| QB17 | 0.692 | 0.860 | 0.472 | 0.660 | **0.770** |
| RB34 | 0.686 | 0.861 | 0.472 | 0.640 | 0.767 |
| RB38 | 0.696 | 0.861 | 0.472 | 0.653 | 0.760 |
| WR52 | 0.690 | **0.868** | 0.472 | **0.667** | 0.767 |
| WR58 | **0.698** | 0.859 | 0.486 | 0.653 | 0.767 |
| TE10 | 0.694 | 0.864 | 0.458 | 0.660 | **0.773** |
| TE14 | 0.684 | 0.865 | 0.458 | 0.653 | 0.767 |

QB13 is selected because its 50.0% top-24 hit rate is a 4.2-point improvement over QB15, rank correlation improves, and VORP capture falls only 0.2 points. It also reduces current Top-100 QB concentration from 13 to 11. RB36, WR55, and TE12 remain the balanced choices.

## Selected QB15 Reference Folds

The originally selected QB15 reference produced:

| Fold | Rows | Spearman | Positive VORP@100 | Top 24 | Top 50 | Top 100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022 to 2023 | 352 | 0.687 | 0.785 | 0.375 | 0.660 | 0.710 |
| 2023 to 2024 | 354 | 0.742 | 0.815 | 0.375 | 0.640 | 0.690 |
| 2024 to 2025 | 120 | 0.653 | 1.000 | 0.625 | 0.700 | 0.910 |

The final fold has only 120 complete scored rows, so its 1.000 VORP capture is inflated by near-complete selection coverage. Aggregate conclusions rely on all three folds and replacement sensitivity, not that result alone.

## Current Guardrails

- Jeremiyah Love is fixed at overall 20.
- QB4 cannot enter the top 24. Position-locked queue constraints place Jalen Hurts at 27.
- The top 24 contains three QBs.
- Every positional queue remains contiguous with zero order violations.
- The final Top 100 contains 32 RB, 48 WR, 11 QB, and 9 TE.
- The five owner-approved teamless players have zero Top-100 leaks.

Current-only rookie and QB floors are not inserted into historical folds because they depend on 2026 owner and roster context.

## Artifacts and Checks

- Added `scripts/run_unified_gng_2026_top100_backtest.py`.
- Wrote `output/unified-gng-2026-top100-backtest.json`.
- Updated the unified builder to QB13 and composable position-locked floors.
- Twelve focused unit tests passed.
- Unified row, identity, watchlist, position-order, rookie-cap, and top-24 QB checks passed.
- Production GNG rankings remain `pigskin-llm-20260704072119`.

## Recommendation

The isolated GNG system is ready for final player review and production packaging. Do not tune replacement ranks further. The remaining work is inspecting the final Top 100 for current-context anomalies, then promoting the positional and unified objects through guarded write paths.
