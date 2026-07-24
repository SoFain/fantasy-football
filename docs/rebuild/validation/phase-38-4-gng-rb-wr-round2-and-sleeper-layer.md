# Phase 38.4 GNG RB/WR Round Two and Sleeper Layer

## Decision

`RB R7 SELECTED; WR W10 SELECTED; SLEEPER CURRENT-CONTEXT GATE DEFINED`

QB Q4 and TE H5 remain locked. Five new RB candidates and five new WR candidates were evaluated over the same three leakage-safe folds. No production ranking changed.

## RB Round Two

| Candidate | Spearman | Pairwise | Top 12 | Top 24 | Points@12 | Points@24 | NDCG | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H1 baseline | 0.720 | 0.778 | 0.639 | 0.750 | 0.863 | 0.875 | **0.854** | 6 | **1** |
| R6 safe dual use | 0.733 | 0.771 | 0.639 | 0.764 | 0.854 | 0.896 | 0.826 | 5 | 2 |
| **R7 H1/R2 compromise** | 0.735 | **0.781** | **0.667** | **0.778** | **0.884** | **0.898** | 0.845 | **5** | **1** |
| R8 role-guarded R2 | 0.733 | 0.774 | **0.667** | 0.764 | 0.850 | **0.898** | 0.829 | **4** | 2 |
| R9 high-value floor | 0.734 | 0.776 | 0.611 | 0.750 | 0.851 | 0.885 | 0.814 | 5 | 2 |
| R10 efficiency capped | **0.736** | 0.777 | 0.611 | 0.764 | 0.846 | 0.886 | 0.834 | 5 | 2 |

R7 is selected. It improves every headline result except NDCG and preserves the one-bust ceiling. Its five misses were Raheem Mostert, Isiah Pacheco, Kyren Williams, James Cook, and Chuba Hubbard. Dalvin Cook remained the only bust.

R7 weights: 65% GNG profile points, 12.5% GNG weighted opportunity, 5% target share, 4% WOPR, 3.5% expected receiving first downs, 3.5% expected rushing first downs, 4% goal-line opportunities, and 2.5% snap share.

## WR Round Two

| Candidate | Spearman | Pairwise | Top 12 | Top 24 | Points@12 | Points@24 | NDCG | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| H5 baseline | 0.729 | 0.768 | 0.611 | 0.639 | **0.908** | 0.901 | **0.884** | 8 | **0** |
| W6 H5 air overlay | **0.730** | **0.769** | 0.611 | 0.653 | 0.900 | 0.910 | 0.873 | 7 | **0** |
| W7 H5 earning overlay | 0.722 | 0.762 | 0.583 | 0.653 | 0.886 | 0.898 | 0.863 | 8 | **0** |
| W8 H5 chain overlay | 0.729 | 0.767 | 0.611 | 0.653 | 0.897 | 0.911 | 0.869 | 7 | 1 |
| W9 H5 NGS overlay | 0.725 | 0.764 | **0.639** | **0.667** | 0.902 | 0.910 | 0.878 | 7 | 1 |
| **W10 H5 floor first** | 0.726 | 0.767 | 0.611 | **0.667** | 0.900 | **0.915** | 0.874 | **6** | **0** |

W10 is selected for the 2026 candidate board. It trades 0.003 Spearman, 0.010 NDCG, and 0.008 points@12 for better top-24 precision, 1.4 percentage points more points@24, two fewer misses, and no busts.

W10 weights: 30% profile points, 20% GNG weighted opportunity, 10% expected-points share, 8% opportunity quality, 8% snap share, 8% snap stability, 6% availability, 5% expected receiving first downs, 3% target share, and 2% WOPR.

## Sleeper Current-Player Layer

The research table contains 12,200 Sleeper players from one fetch at `2026-07-11T23:53:26.619596Z`. It is current enough for this phase, so the large API endpoint was not fetched again.

The layer is current-board only. It is never joined to historical folds.

- Active current-team players at depth order 1 receive a bounded `+0.02` role adjustment.
- Active players at depth order 3 or worse receive `-0.04`.
- Unknown depth order creates `DEPTH_CHART_UNKNOWN` without an adjustment.
- Inactive, teamless, or non-active status creates `SLEEPER_ROSTER_REVIEW` without an automatic rank change.
- Injury status creates `INJURY_UNCERTAIN` without an automatic injury penalty.
- First-year players create `ROOKIE_CONTEXT_REQUIRED` and stay in the rookie review lane.

This preserves the source contract that Sleeper status transitions are review evidence, not automatic ranking writes.

## Current Formula Set

| Position | Formula |
|---|---|
| QB | Q4 GNG bonus proxy |
| RB | R7 H1/R2 compromise |
| WR | W10 H5 floor first |
| TE | H5 stability hybrid |

All four current boards must join the Sleeper safety layer before review or promotion.

## Artifacts and Checks

- Extended `scripts/run_gng_position_candidate_expansion.py` with a separate round-two candidate set.
- Wrote `output/gng-position-candidate-expansion-round2.json`.
- Added `src/gng_sleeper_safety.py`.
- Extended focused tests for both round-two candidate counts and Sleeper safety behavior.
- No production table, champion, or ranking row changed.

## Next Phase

Generate isolated 2026 positional boards with the locked formulas and the Sleeper layer. Review the largest formula movements, every Sleeper flag, rookies, current-team changes, and the rank distribution before unified GNG interleaving.
