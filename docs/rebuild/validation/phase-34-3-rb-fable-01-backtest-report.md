# Phase 34.3 RB Fable 01 Backtest Report

> Superseded note: Phase 34.4 refined the age/availability component (volume-conditioned age forgiveness) and re-ran this backtest. The numbers below describe the original Phase 34.2B formula and remain the historical record. Current results: `docs/rebuild/validation/phase-34-4-rb-fable-01-refinement-report.md` and the regenerated `docs/rebuild/rb-fable-01-backtest-results.md`.

## Final Decision

`RB FABLE 01 PROMISING BUT NEEDS REFINEMENT`

RB Fable 01 has useful predictive signal. Across 204 complete forward rows, average NDCG@24 is 0.843, pairwise draft win rate is 0.769, and predicted top-24 players capture 86.8% of the ideal cohort's top-24 Standard points. It is not owner-review ready because average top-6 precision is 0.333 and the three folds contain six actual elite misses.

Current Pigskin still holds by default. No valid historical Current Pigskin baseline exists for a direct comparison, so RB Fable 01 has not earned challenger status.

## Files Changed

- `bigquery/views/v_rb_fable_01_situational_splits.sql`
- `bigquery/views/v_rb_fable_01_scored_seasons.sql`
- `bigquery/views/v_rb_fable_01_backtest_prep.sql`
- `scripts/build_rb_fable_01_metric_layer.py`
- `scripts/run_rb_fable_01_backtest.py`
- `tests/test_rb_fable_01_backtest.py`
- `tests/test_rb_fable_01_metric_sql.py`
- `docs/rebuild/rb-fable-01-backtest-results.md`
- this report

The evaluator also wrote local evidence to `output/phase-34-3-rb-fable-01-results.json`. That generated evidence is not a commit candidate.

## BigQuery Objects Queried

- `fantasy_football_advanced_metrics.v_rb_fable_01_backtest_prep`
- `fantasy_football_advanced_metrics.v_rb_fable_01_scored_seasons`
- `fantasy_football_advanced_metrics.v_rb_fable_01_metric_inputs`
- `fantasy_football_advanced_metrics.v_rb_fable_01_situational_splits`
- `fantasy_football_advanced_metrics.situational_identity_bridge_review`
- `fantasy_football_brain.analytics_player_fantasy_points_by_profile`
- `fantasy_football_brain.analytics_pigskin_rankings`, baseline availability check only
- `fantasy_football_brain.ranking_formula_candidates`, prior-formula availability check only

## Input Readiness

| Fold | Qualified | Complete score | Complete target | Complete score and target |
|---|---:|---:|---:|---:|
| 2022 to 2023 | 101 | 91 | 72 | 66 |
| 2023 to 2024 | 101 | 95 | 75 | 73 |
| 2024 to 2025 | 99 | 91 | 67 | 65 |

Counts match Phase 34.2B. Duplicate player-season count is zero. Identity collisions are zero. The fold query contains no input season after 2024 and no target season after 2025. Null-score rows remain excluded rather than imputed.

## Forward Predictive Results

| Fold | Rows | Top 6 | Top 12 | Top 24 | Top 36 | Points captured | NDCG@24 | Pairwise | Band regret | Score correlation | Rank correlation | Elite misses |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 to 2023 | 66 | 0.167 | 0.417 | 0.708 | 0.778 | 0.836 | 0.798 | 0.732 | 0.409 | 0.642 | 0.641 | 2 |
| 2023 to 2024 | 73 | 0.333 | 0.667 | 0.750 | 0.806 | 0.872 | 0.862 | 0.793 | 0.288 | 0.738 | 0.764 | 2 |
| 2024 to 2025 | 65 | 0.500 | 0.667 | 0.750 | 0.861 | 0.895 | 0.870 | 0.782 | 0.277 | 0.777 | 0.770 | 2 |

Aggregate averages:

- Top-6 hit rate: 0.333.
- Top-12 hit rate: 0.583.
- Top-24 hit rate: 0.736.
- Top-36 hit rate: 0.815.
- Points captured at 24: 0.868.
- NDCG@24: 0.843.
- Pairwise draft win rate: 0.769.
- Pick-band regret: 0.325 average positive band overreach.
- Total elite misses: 6.
- Total complete rows: 204.

Top-N hit rate is precision within the complete fold cohort. Points capture compares actual Standard points from predicted top 24 with the cohort's ideal top 24. Pick-band regret is the mean positive difference between predicted and actual bands using 1-6, 7-12, 13-24, 25-36, and 37+.

## Baseline Availability

`HISTORICAL CURRENT PIGSKIN BASELINE UNAVAILABLE`

The live Current Pigskin table contains the current 2026 Standard board, not leakage-safe historical boards for 2023-2025. It was not used as a proxy.

`PRIOR EPISODE FORMULA BASELINE UNAVAILABLE`

`standard_rb_elite_receiving_back_protection_v0` is not registered with historical outputs. It was not reconstructed.

## Player-Level Miss Audit

2022 to 2023:

- Predicted top-12 failures: Miles Sanders finished cohort RB47; Dameon Pierce finished cohort RB39.
- Elite misses: Raheem Mostert was predicted RB34 and finished cohort RB2. Isiah Pacheco was predicted RB36 and finished cohort RB12.

2023 to 2024:

- Predicted top-12 failure: Travis Etienne was predicted RB12 and finished cohort RB37.
- Elite misses: Derrick Henry was predicted RB25 and finished cohort RB2. Chuba Hubbard was predicted RB28 and finished cohort RB12.

2024 to 2025:

- No predicted top-12 player fell below cohort RB36.
- Elite misses: Javonte Williams was predicted RB30 and finished cohort RB10. Travis Etienne was predicted RB31 and finished cohort RB11.

Receiving-back misses total one, zero, and five by fold under the source-backed definition of at least 40 input receptions or 10% target share, actual cohort top 24, and predicted outside top 24. Extreme movement is unavailable because no valid historical baseline exists.

## Component Interpretation

- Opportunity is the leading positive component for nearly every top-ranked player. The formula follows its stated volume-first design.
- Efficiency shrinkage works. Devon Achane, Tony Pollard, Derrick Henry, Bucky Irving, and Jahmyr Gibbs receive visible efficiency lifts without small samples taking over the board.
- Receiving usage materially supports Alvin Kamara, Christian McCaffrey, Breece Hall, Bijan Robinson, and Devon Achane.
- Age and availability penalties are sometimes too blunt. Raheem Mostert's 2022 penalty contributed to a major elite miss. Christian McCaffrey received the strongest 2024 penalty among relevant stars before finishing cohort RB2 in 2025.
- High TFL percentage is reported as a diagnostic only. It is not a score component, so the report does not claim that negative-run risk directly lowered a player.

The complete top-25 predictive tables include touches, yards, TDs, contact efficiency, EPA, success, explosive rate, first-down rate, TFL rate, box-adjusted YPC, availability, age penalty, and rank reason in `docs/rebuild/rb-fable-01-backtest-results.md`.

## Same-Season Descriptive Diagnostic

**DESCRIPTIVE ONLY - NOT A FORWARD-LOOKING BACKTEST**

The companion results document contains the complete top-25 boards for all four seasons. Top-five shape:

| Season | Descriptive top five |
|---:|---|
| 2022 | Austin Ekeler, Josh Jacobs, Derrick Henry, Saquon Barkley, Christian McCaffrey |
| 2023 | Christian McCaffrey, Kyren Williams, Alvin Kamara, Saquon Barkley, Tony Pollard |
| 2024 | Saquon Barkley, Bijan Robinson, Kyren Williams, Jahmyr Gibbs, Jonathan Taylor |
| 2025 | Christian McCaffrey, Jonathan Taylor, Bijan Robinson, Jahmyr Gibbs, Devon Achane |

These boards explain formula shape only. Same-season alignment is not predictive evidence.

## Readiness Decision

- Promising: yes. Correlation, NDCG, pairwise ordering, and points capture improve across the three folds.
- Episode-ready: yes, as a transparent research segment with the miss audit included.
- Owner-review ready: no. Top-six precision and elite misses require refinement.
- Ready to challenge Current Pigskin: no. A valid historical baseline comparison does not exist.
- Default live decision: Current Pigskin holds.

## Safety Confirmation

- No live ranking write occurred.
- No champion was activated.
- No model was trained.
- No deployment occurred.
- No Gemini, Pigskin chat, Sleeper current-context, or market-target call occurred.
- No 2026 outcome was used.
- No production feature mart was changed.
- Broken tackles, YAC above expectation, and RB route metrics were not invented or added.

Checks run:

- Seven focused RB Fable SQL and evaluator tests passed.
- Deployment safety checker passed every check.
- BigQuery validation discovery passed through validation 245.
- Focused duplicate player-season count: 0.
- Focused leakage issue count: 0.
- Historical Current Pigskin target-season row count: 0.
- Registered prior episode formula count: 0.
- Deployed-view audit found no 2026, market-value, broken-tackle, YAC-above-expectation, or RB route-metric references.
- `git diff --check` passed. Existing line-ending notices are informational.

## Recommended Next Phase

Run a narrow Phase 34.4 refinement focused on age/availability calibration and elite-volume protection. Preserve the current opportunity weights initially. Re-evaluate the six elite misses without tuning all eleven individual weights or using 2026 outcomes.
