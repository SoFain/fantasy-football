# Phase 35.2 TE Fable v1.0a Backtest Report

## Final Decision

`TE FABLE V1.0A NO-MAN READY FOR OWNER REVIEW`

TE Fable v1.0a is predictive and clears the simple prior-year Standard PPG baseline on the untouched 2024 to 2025 holdout. The `vs_man` YPRR term does not earn its 5% weight. Removing it and reallocating that weight to standard YPRR improves aggregate top-12 precision, captured points, NDCG, and band regret without reducing pairwise performance in a meaningful way.

This phase created research views only. It did not write rankings, activate a champion, call Gemini, or deploy.

## Formula Variants

- `te_fable_v1a`: corrected owner formula with 5% shrunk `vs_man` YPRR.
- `te_fable_v1a_no_man`: removes the man split and increases standard YPRR from 8% to 13%. Total formula weight remains 1.00.
- `prior_year_standard_ppg`: simple returning-player benchmark.

Primary qualifiers require at least four games and 100 routes. Historical age is calculated at September 1 of the input season. The red-zone touchdown coefficient is predeclared at 0.14. No target-season values enter a score.

## Forward-Fold Results

### Aggregate

| Variant | Rows | Spearman | Pairwise | Top 6 | Top 12 | Points@12 | NDCG@12 | Band regret | Top-12 busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TE Fable v1.0a | 188 | 0.667 | 0.741 | 0.556 | 0.528 | 0.802 | 0.827 | 0.342 | 1 |
| TE Fable v1.0a no-man | 188 | 0.666 | 0.741 | 0.556 | **0.556** | **0.816** | **0.839** | **0.336** | 1 |
| Prior-year Standard PPG | 189 | 0.666 | 0.739 | **0.611** | 0.528 | 0.794 | **0.844** | 0.355 | 2 |

### Untouched 2024 To 2025 Holdout

| Variant | Rows | Spearman | Pairwise | Top 6 | Top 12 | Points@12 | Points@24 | NDCG@12 | NDCG@24 | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TE Fable v1.0a | 67 | **0.746** | **0.772** | 0.500 | 0.500 | **0.831** | **0.932** | **0.843** | **0.909** | 1 |
| TE Fable v1.0a no-man | 67 | 0.742 | **0.772** | 0.500 | 0.500 | **0.831** | **0.932** | **0.843** | **0.909** | 1 |
| Prior-year Standard PPG | 67 | 0.650 | 0.735 | 0.500 | 0.500 | 0.790 | 0.826 | 0.799 | 0.805 | 2 |

The no-man variant gives up 0.004 holdout Spearman while preserving every top-board holdout metric. Its aggregate top-12 behavior is better, so the added man-split complexity is not justified.

## Holdout Top-Board Audit

The 2024-input formula correctly placed Trey McBride first for his 2025 TE1 outcome. George Kittle, Brock Bowers, Sam LaPorta, and Hunter Henry also landed in the predicted top 12 and finished in the target cohort's top 12.

Material misses:

- David Njoku: predicted 5, target rank 26.
- Jonnu Smith: predicted 6, target rank 51.
- Cade Otton: predicted 7, target rank 30.
- Colby Parkinson: predicted 34, target rank 16. This was the only actual top-18 player outside the predicted top 24.

The misses show the remaining role-change problem. Prior-season route and target strength cannot anticipate every next-season depth-chart, team, quarterback, or injury change.

## Current 2026 Review Board Evidence

The no-man board generated from 2025 inputs begins:

1. Trey McBride
2. Brock Bowers
3. Tucker Kraft
4. George Kittle
5. Kyle Pitts
6. Tyler Warren
7. Jake Ferguson
8. Hunter Henry
9. Dallas Goedert
10. Harold Fannin Jr.
11. Sam LaPorta
12. Colby Parkinson

Among the 35 players shared with the active Standard TE board, no-man Fable rank correlation is 0.900. Four players move by at least eight slots. The largest review flags are Colby Parkinson up 15, Travis Kelce down 8, and Cole Kmet down 10. These are review evidence, not approved live changes.

## Objects And Files

Research views created in `fantasy_football_advanced_metrics`:

- `v_te_fable_v1a_identity_bridge`
- `v_te_fable_v1a_situational_splits`
- `v_te_fable_v1a_metric_inputs`
- `v_te_fable_v1a_scored_seasons`
- `v_te_fable_v1a_backtest_prep`

Implementation:

- `scripts/build_te_fable_v1a_metric_layer.py`
- `scripts/run_te_fable_v1a_backtest.py`
- `tests/test_te_fable_v1a.py`
- `output/te-fable-v1a-backtest.json`, local evidence only

## Checks

- Seven focused TE Fable tests passed.
- Both scripts compile.
- All SQL templates render without unresolved placeholders.
- Research views created successfully.
- Active ranking rows remained 1,050 after the test.
- No `analytics_pigskin_rankings` write occurred.

## Recommendation

Advance `te_fable_v1a_no_man` to a TE35 owner-review board comparison against the live Standard TE rankings. Do not promote yet. Review the four eight-slot movements and add point-in-time current role and injury warnings as display-only context before any champion decision.
