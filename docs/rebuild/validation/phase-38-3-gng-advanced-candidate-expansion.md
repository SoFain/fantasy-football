# Phase 38.3 GNG Advanced Candidate Expansion

## Decision

`QB Q4 SELECTED; RB R2 RETAINED AS CHALLENGER; WR H5 RETAINED`

Five predeclared advanced candidates were tested for QB, RB, and WR over the same leakage-safe 2022-to-2023, 2023-to-2024, and 2024-to-2025 folds. No production or current ranking table changed.

## Method

Every input was converted to a position-and-fold percentile using only non-null observations. Composite weights were renormalized over present metrics. Candidates were locked by metric family before evaluation.

The initial warehouse inspection found several columns with zero historical coverage. Dead fields were replaced before the final run with populated feature-mart equivalents. The final candidates do not depend on DAKOTA, raw RB first-down rate, WR YPRR, TPRR, route participation, end-zone targets, first downs per route, or NGS catch over expectation.

## QB Candidates

| Candidate | Spearman | Top 12 | Top 24 | Points@12 | Points@24 | NDCG@24 | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H2 baseline | 0.553 | 0.667 | 0.861 | 0.821 | 0.922 | **0.919** | 3 | 0 |
| Q1 dual threat | 0.541 | 0.667 | 0.847 | 0.797 | 0.908 | 0.909 | 3 | 0 |
| Q2 passing quality | 0.512 | 0.667 | 0.847 | 0.828 | 0.904 | 0.895 | 3 | 0 |
| Q3 volume stability | 0.577 | 0.694 | 0.861 | **0.878** | 0.916 | 0.903 | 4 | 0 |
| **Q4 GNG bonus proxy** | **0.590** | **0.722** | **0.875** | **0.878** | **0.929** | 0.906 | **2** | 0 |
| Q5 balanced advanced | 0.570 | 0.694 | 0.847 | 0.841 | 0.908 | 0.912 | 3 | 0 |

Q4 weights: 30% GNG profile points, 15% passing yards, 15% expected passing first downs, 15% QB rushing baseline, 10% QB NGS efficiency, 10% attempts, and 5% CPOE.

Q4 misses were Jordan Love in the 2023 outcome and Sam Darnold in the 2024 outcome. It had no busts. Q4 replaces H2 for 2026 candidate generation. H2 remains the NDCG reference.

## RB Candidates

| Candidate | Spearman | Top 12 | Top 24 | Points@12 | Points@24 | NDCG@24 | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| H1 baseline | 0.720 | 0.639 | 0.750 | 0.863 | 0.875 | **0.854** | 6 | **1** |
| R1 GNG high value | 0.731 | 0.611 | 0.750 | 0.848 | 0.887 | 0.844 | 5 | 2 |
| **R2 dual use** | 0.729 | **0.667** | **0.764** | **0.865** | **0.896** | 0.844 | **5** | 2 |
| R3 rushing quality | 0.725 | 0.583 | 0.750 | 0.811 | 0.889 | 0.852 | 5 | 4 |
| R4 role durability | 0.729 | 0.611 | 0.736 | 0.844 | 0.873 | 0.788 | 5 | 2 |
| R5 balanced advanced | **0.740** | 0.611 | **0.764** | 0.844 | 0.886 | 0.850 | 5 | 2 |

R2 weights: 30% profile points, 25% GNG weighted opportunity, 10% target share, 8% WOPR, 7% expected receiving first downs, 7% expected rushing first downs, 8% goal-line opportunities, and 5% snap share.

R2 improves both precision cutoffs and captured points. It also changes the risk profile from one bust to two. Dalvin Cook remains, and Travis Etienne becomes a bust in the 2024 outcome. Keep H1 as the safe incumbent and carry R2 into current-player review as the upside challenger.

## WR Candidates

| Candidate | Spearman | Top 12 | Top 24 | Points@12 | Points@24 | NDCG@24 | Misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **H5 baseline** | 0.729 | 0.611 | 0.639 | **0.908** | 0.901 | **0.884** | 8 | **0** |
| W1 route earning | 0.708 | 0.611 | **0.667** | 0.882 | 0.898 | 0.867 | **7** | 1 |
| W2 air-yard alpha | 0.734 | **0.667** | 0.639 | 0.899 | 0.892 | 0.864 | **7** | 1 |
| W3 chain mover | 0.725 | 0.611 | 0.625 | 0.895 | 0.895 | 0.862 | **7** | 1 |
| W4 explosive quality | **0.734** | **0.667** | 0.625 | 0.904 | 0.899 | 0.878 | **7** | 2 |
| W5 role stability plus | 0.722 | 0.583 | **0.667** | 0.877 | **0.903** | 0.868 | **7** | 1 |

No WR challenger wins. W2 and W4 improve rank correlation and top-12 precision, but both lose captured points or NDCG and add busts. W1 and W5 improve top-24 precision but do the same. H5 remains the 2026 candidate formula.

## Coverage

QB inputs were complete except CPOE at 96 of 97 rows. Core RB advanced inputs covered 189 to 203 of 203 rows; NGS rushing fields covered 162. Core WR fields covered 319 to 336 of 337 rows. WR NGS efficiency fields covered 303. Trend fields covered 271 to 275 rows. Null-safe renormalization preserved all player-season rows.

## Artifacts and Checks

- Added `scripts/run_gng_position_candidate_expansion.py`.
- Wrote `output/gng-position-candidate-expansion.json` with definitions, coverage, folds, aggregates, misses, and busts.
- Added candidate-count and null-percentile regression tests.
- BigQuery-backed runner completed successfully on July 11, 2026.
- No ranking table, champion, or production row changed.

## Next Phase

Generate 2026 candidate boards using QB Q4, RB H1 plus a separate R2 comparison board, WR H5, and TE H5. Current-team, rookie, injury, and depth-chart context should decide whether any R2-specific RB movement is credible before one RB formula is selected.
