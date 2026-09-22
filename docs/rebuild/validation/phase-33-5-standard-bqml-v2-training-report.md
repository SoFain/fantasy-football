# Phase 33.5 Standard BQML V2 Training

Final decision: STANDARD BQML V2 MODEL BEATS CURRENT BASELINE

## Scope

Phase 33.5 trained the first Standard-only BQML v2 foundation models from the Phase 33.3 41-predictor dataset.

No live ranking table changed. No champion was activated. No detail rows were written. No Gemini, Pigskin chat, Sleeper API, source ingest, materialization, or deploy occurred.

## Git State

Phase 33.4 was committed before training:

- `a1cb276 phase 33.4 audit nflverse source gaps`

Phase 33.5 changed:

- `src/bqml_v2_feature_contract.py`
- `tests/test_bqml_v2_feature_contract.py`
- `docs/rebuild/bqml-v2-ranking-architecture.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/validation/phase-33-5-standard-bqml-v2-training-report.md`

## Dataset Reconfirmation

Read-only Standard dataset check:

| Check | Result |
|---|---:|
| Dataset dry-run bytes | 1,201,855,586 |
| Predictor count | 41 |
| Total rows | 39,061 |
| Train rows, 2017-2023 | 32,452 |
| Validation rows, 2024 | 4,918 |
| Holdout rows, 2025 | 1,691 |
| Duplicate grain rows | 0 |
| Missing player IDs | 0 |
| Missing target labels | 0 |
| Leakage window rows | 0 |

Rows by position:

| Split | QB | RB | WR | TE |
|---|---:|---:|---:|---:|
| Train | 3,778 | 8,327 | 13,368 | 6,979 |
| Validation | 573 | 1,276 | 1,982 | 1,087 |
| Holdout | 295 | 366 | 638 | 392 |

Excluded fields confirmed:

- `passing_epa_per_play`
- `receiving_yards`
- `receiving_epa`
- `red_zone_targets`
- `red_zone_opportunities`
- `goal_line_opportunities`
- `ngs_catch_over_expected_score_3yr`
- `injury_risk_score_3yr`
- `depth_chart_role_score_3yr`
- `pigskin_context_score`
- route-derived blocked fields
- Sleeper current context

## Models Trained

All 16 planned models trained successfully.

| Model key | Job ID | Seconds | Bytes processed |
|---|---|---:|---:|
| `standard_qb_linear_points` | `dc84b755-2f0d-4e66-890c-7aa8fdeeb482` | 28.77 | 18,270,052 |
| `standard_qb_linear_vor` | `42a7dbe3-e04a-4dbc-b0cc-4bf3fd7908a5` | 9.04 | 18,270,052 |
| `standard_qb_logistic_elite` | `b865dd65-2afb-4dd0-a82f-948378675fb7` | 24.76 | 18,270,052 |
| `standard_qb_logistic_bust` | `7afa17ed-1a75-420d-ab5b-3d65bbcd87ad` | 22.17 | 20,756,980 |
| `standard_rb_linear_points` | `9e847cd2-b421-4f38-9df3-22ca2e2c1575` | 9.43 | 26,650,828 |
| `standard_rb_linear_vor` | `a5635c59-2380-45f6-a952-e2a987e880f6` | 8.47 | 26,650,828 |
| `standard_rb_logistic_elite` | `27844285-83ad-45d2-989f-6be629be319e` | 24.02 | 26,650,828 |
| `standard_rb_logistic_bust` | `32c9cd54-a6cb-40ca-98c7-298801feeda2` | 23.41 | 29,137,756 |
| `standard_wr_linear_points` | `1d14b127-da93-49fe-8d0a-cc4d953ce88f` | 9.18 | 28,801,549 |
| `standard_wr_linear_vor` | `7be07e23-186a-4f5c-90c1-839e92730935` | 29.46 | 28,801,549 |
| `standard_wr_logistic_elite` | `5f03df62-f7fd-4fd1-9fca-9f5a6a310b2a` | 40.30 | 28,801,549 |
| `standard_wr_logistic_bust` | `97769357-a321-4d1d-aba6-edc89825040f` | 32.81 | 31,289,741 |
| `standard_te_linear_points` | `a999cbea-f39e-4909-a718-ed2843b118af` | 8.59 | 33,688,532 |
| `standard_te_linear_vor` | `21737f4d-9f34-452b-a38e-fb246aa289af` | 8.98 | 33,688,532 |
| `standard_te_logistic_elite` | `36bbb4ef-26ff-4dbf-8bde-0b528fa51c63` | 34.92 | 33,688,532 |
| `standard_te_logistic_bust` | `6c28b07a-7931-4d4b-9d58-8c9fe3f444c6` | 27.98 | 36,175,460 |

No models were skipped.

## Prediction And Summary Output

Prediction/evaluation scope:

- Validation season: 2024
- Holdout season: 2025
- Scoring profile: `standard`
- League type: `redraft`
- Roster format: `one_qb`
- Candidate summaries: 32
- Detail rows written: 0

Summary write:

- Formula version: `ranking_backtest_sql_native_bqml_v2_standard_v0`
- `ranking_backtest_runs`: 2 rows
- `ranking_backtest_candidate_summaries`: 32 rows
- `ranking_backtest_results`: 0 rows
- `ranking_formula_champions`: 0 rows
- `analytics_pigskin_rankings`: 0 rows

The first summary-write script failed before writing because BigQuery treated an unqualified `target_season` in the run insert as ambiguous. Verification showed 0 run rows and 0 summary rows after that failure. The retry wrote only SQL-evaluated summary rows through the BigQuery client with `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` set inside the process and removed afterward.

Gate state after retry: unset.

## Combined 2024-2025 Results

Best Standard v2 lane by position:

| Position | Candidate | Top-N hit | Points captured | VOR captured | Pairwise | Overall pairwise | Label |
|---|---|---:|---:|---:|---:|---:|---|
| QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | 0.688 | 0.822 | 0.712 | 0.675 | 0.676 | owner-review challenger |
| RB | `bqml_v2_standard_rb_logistic_bust_inverse_v0` | 0.817 | 0.898 | 0.736 | 0.798 | 0.803 | owner-review challenger |
| WR | `bqml_v2_standard_wr_logistic_elite_v0` | 0.631 | 0.756 | 0.696 | 0.763 | 0.761 | owner-review challenger |
| TE | `bqml_v2_standard_te_linear_points_v0` | 0.611 | 0.742 | 0.687 | null | null | owner-review challenger |

Holdout notes:

- 2025 QB best lane: `bqml_v2_standard_qb_logistic_bust_inverse_v0`, VOR captured 0.851.
- 2025 RB top-N and points capture reached 1.000 for multiple lanes, but VOR captured was null because the denominator was unavailable or zero in that slice.
- 2025 WR best lane: `bqml_v2_standard_wr_logistic_elite_v0`, VOR captured 0.886.
- 2025 TE best lane: `bqml_v2_standard_te_logistic_bust_inverse_v0`, VOR captured 0.836.

## Baseline Comparison

Standard v2 beats Current Pigskin on combined 2024-2025 VOR capture and captured points for QB, RB, WR, and TE.

| Position | Best Standard v2 VOR | Current Pigskin VOR | Simple projection VOR |
|---|---:|---:|---:|
| QB | 0.712 | 0.626 | 0.624 |
| RB | 0.736 | 0.642 | 0.650 |
| WR | 0.696 | 0.581 | 0.574 |
| TE | 0.687 | 0.534 | 0.535 |

Prior BQML comparison:

- QB: prior enriched/NGS linear-points lanes remain stronger by combined VOR.
- RB: Standard v2 logistic bust inverse is the strongest listed Standard comparison lane.
- WR: Standard v2 logistic elite is the strongest listed Standard comparison lane.
- TE: Standard v2 linear points is the strongest listed Standard comparison lane.

## Feature Signal

Model weights are directional evidence only, not causal proof.

| Position | Strong signals |
|---|---|
| QB | Rushing xFP share, rushing attempts, QB rushing leverage, weekly volatility. QB weights look noisier than other positions. |
| RB | Target-share slope, xFP share, carry-share slope. |
| WR | Target-share slope, WOPR slope, air yards, receiving first-down proxy, receiving xFP share. |
| TE | Target-share slope, WOPR slope, air yards, receiving xFP share, offensive snap share. |

## Position Labels

| Position | Label | Reason |
|---|---|---|
| QB Standard | owner-review challenger | Clear lift over Current Pigskin, but not over prior BQML linear points. |
| RB Standard | owner-review challenger | Strongest Standard comparison in current summary evidence. |
| WR Standard | owner-review challenger | Strongest Standard comparison in current summary evidence. |
| TE Standard | owner-review challenger | Strongest TE comparison and clear lift over Current Pigskin. |

No global winner is recommended. This is Standard-only evidence.

## Checks

Passed:

- `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract`: passed, 19 tests.
- `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py`: passed.
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed.
- `git diff --check`: passed with line-ending warnings only.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: passed discovery, 245 validations found.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`: passed, 6 passed and 0 failed.
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest`: passed, 14 passed and 0 failed. Two informational dashboard queries returned review rows.

## Warnings

- Summary persistence used a client summary-row insert after the first SQL script hit an ambiguous column error. The evaluator itself remained SQL-native and only 32 summary rows were written.
- Some pairwise metrics are null where the high-confidence score-gap filter produced no pairs.
- 2025 RB VOR capture is null for the best lanes because the denominator was unavailable or zero in that slice.
- QB Standard v2 is useful but not the strongest BQML lane.
- The Phase 17 through Phase 30 historical validation backlog remains untracked owner-review material.

## Recommended Next Phase

Phase 33.6 should generate Standard BQML v2 owner-review boards for:

- `bqml_v2_standard_qb_logistic_bust_inverse_v0`
- `bqml_v2_standard_rb_logistic_bust_inverse_v0`
- `bqml_v2_standard_wr_logistic_elite_v0`
- `bqml_v2_standard_te_linear_points_v0`

Separately plan an additive feature-mart patch for EPA, receiving yards, red-zone targets, red-zone opportunities, and goal-line opportunities.
