# Phase 33.8 Standard BQML V2 Patched Training Report

Final decision: PATCHED STANDARD BQML V2 MODELS READY FOR OWNER REVIEW WITH WARNINGS

## Scope

Phase 33.8 retrained the Standard-only BQML v2 model set after the Phase 33.7 EPA, receiving, red-zone, and goal-line feature-mart patch.

No production deploy occurred. No live ranking rows were written. No champion was activated. No Gemini, Pigskin chat, Sleeper API, source ingest, or materialization outside the summary-only backtest evidence write occurred.

Latest commit at phase start was `4ad74d4 phase 33.7 document feature patch evidence`. The prompt referenced `23cb77f`, but `4ad74d4` is the follow-up evidence commit for the same Phase 33.7 patch package.

## Dataset Reconfirmation

Standard training dataset checks:

| Check | Result |
|---|---:|
| Predictor count | 47 |
| Standard training dataset dry-run bytes | 1,219,493,385 |
| Standard coverage dry-run bytes | 26,143,117 |
| Standard integrity dry-run bytes | 12,851,069 |
| Integrity row count | 39,061 |
| Leakage rows | 0 |
| Duplicate grain rows | 0 |
| Missing player IDs | 0 |
| Missing target labels | 0 |

The six Phase 33.7 patched fields are active in the Standard predictor set:

- `passing_epa_per_play`
- `receiving_yards`
- `receiving_epa`
- `red_zone_targets`
- `red_zone_opportunities`
- `goal_line_opportunities`

`ngs_catch_over_expected_score_3yr` remains blocked because the loaded source lane does not provide a real catch-over-expected field.

## Models Trained

Trained 16 Standard-only BQML models:

| Position | Families |
|---|---|
| QB | linear points, linear VOR, logistic elite, logistic bust |
| RB | linear points, linear VOR, logistic elite, logistic bust |
| WR | linear points, linear VOR, logistic elite, logistic bust |
| TE | linear points, linear VOR, logistic elite, logistic bust |

Training used seasons 2017-2023. Evaluation used 2024 validation and 2025 holdout.

Training job IDs:

| Model | Job ID | Bytes |
|---|---|---:|
| `ranking_bqml_v2_standard_patched_qb_linear_points_v0` | `a54b71c2-f221-4cdd-951f-427a3a56a138` | 18,571,140 |
| `ranking_bqml_v2_standard_patched_qb_linear_vor_v0` | `231eced6-c635-4ce7-b931-9aa4420b1685` | 18,571,140 |
| `ranking_bqml_v2_standard_patched_qb_logistic_elite_v0` | `d9ddf8d9-fcb7-42bf-beeb-e69b04cde78c` | 18,571,140 |
| `ranking_bqml_v2_standard_patched_qb_logistic_bust_v0` | `4e58b518-1db4-446c-be70-e7d0909d109f` | 21,058,068 |
| `ranking_bqml_v2_standard_patched_rb_linear_points_v0` | `5a4e2fda-5779-4710-acad-ed1d4f316a48` | 29,127,964 |
| `ranking_bqml_v2_standard_patched_rb_linear_vor_v0` | `42b13e02-395f-4509-858c-88d4d9ad6a8d` | 29,127,964 |
| `ranking_bqml_v2_standard_patched_rb_logistic_elite_v0` | `2292551a-5f72-496b-a2b2-dbbb866b723d` | 29,127,964 |
| `ranking_bqml_v2_standard_patched_rb_logistic_bust_v0` | `e01584ae-e133-44a9-8317-89b7a96d3d3f` | 31,614,892 |
| `ranking_bqml_v2_standard_patched_wr_linear_points_v0` | `e3ce65f9-8384-4e46-8907-a1e092db4944` | 32,436,621 |
| `ranking_bqml_v2_standard_patched_wr_linear_vor_v0` | `65938b8b-62cb-43f0-b5b4-b1754c2e1408` | 32,436,621 |
| `ranking_bqml_v2_standard_patched_wr_logistic_elite_v0` | `06ea250b-af1c-41ee-9fad-6a21918f863b` | 32,436,621 |
| `ranking_bqml_v2_standard_patched_wr_logistic_bust_v0` | `8e48f288-3244-4840-b4b5-b474acb97157` | 34,924,813 |
| `ranking_bqml_v2_standard_patched_te_linear_points_v0` | `457680f8-e2ad-4b11-ad48-e574d419cac0` | 37,321,708 |
| `ranking_bqml_v2_standard_patched_te_linear_vor_v0` | `82c9021b-c1a6-4b20-9f07-4e87317b1223` | 37,321,708 |
| `ranking_bqml_v2_standard_patched_te_logistic_elite_v0` | `67c5c581-969e-459b-8379-896d52ffaa4e` | 37,321,708 |
| `ranking_bqml_v2_standard_patched_te_logistic_bust_v0` | `3572b6bd-bc91-4153-884b-d0984f349c70` | 39,808,636 |

## Summary Evidence Write

Formula version:

- `ranking_backtest_sql_native_bqml_v2_standard_patched_v0`

Write gate:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`
- Set only inside the write command process.
- Removed immediately afterward.

Write job:

- `ba463b16-a0aa-46aa-8ebf-94a74df4d212`
- Bytes processed: 10,697,801

Rows written:

| Table | Rows |
|---|---:|
| `ranking_backtest_runs` | 2 |
| `ranking_backtest_candidate_summaries` | 32 |
| `ranking_backtest_results` | 0 |
| `analytics_pigskin_rankings` | 0 |

The first write attempt failed before writing rows because the generated SQL grouped by an ambiguous `target_season` name in the run insert. The generated SQL artifact was patched locally to qualify `bqml_summary.target_season`. The fixed statement dry-ran successfully before the gated write.

Generated SQL artifacts remain local and are not commit candidates:

- `output/phase-33-8-patched-summary.sql`
- `output/phase-33-8-patched-summary-write.sql`

## Metric Summary

Best patched signals versus original Standard v2:

| Slice | Patched candidate | Evidence |
|---|---|---|
| 2024 RB | `bqml_v2_standard_patched_rb_logistic_elite_v0` | top-N 0.644, points 0.797 |
| 2024 WR | `bqml_v2_standard_patched_wr_linear_points_v0` | top-N 0.435, points 0.626 |
| 2025 WR | `bqml_v2_standard_patched_wr_logistic_bust_inverse_v0` | points 0.888, VOR 0.888 |
| 2025 TE | `bqml_v2_standard_patched_te_logistic_bust_inverse_v0` | top-N 0.764, points 0.848, VOR 0.843, NDCG 0.712 |

Original Standard v2 still wins important slices:

| Slice | Original candidate | Evidence |
|---|---|---|
| 2024 TE | `bqml_v2_standard_te_linear_points_v0` | top-N 0.463, points 0.652, VOR 0.551, NDCG 0.584 |
| 2025 QB | `bqml_v2_standard_qb_logistic_bust_inverse_v0` | top-N 0.852, points 0.890, VOR 0.851, NDCG 0.832 |
| 2025 RB | `bqml_v2_standard_rb_linear_points_v0` | NDCG 0.848, with perfect top-N and points in the slice |
| 2025 WR | `bqml_v2_standard_wr_logistic_elite_v0` | top-N 0.831, NDCG 0.751 |

Decision read: the patched model set is useful owner-review evidence, but it is not a clean replacement for the original Standard v2 model set.

## Feature Signal

Selected `ML.WEIGHTS` checks:

| Position | Model | High-magnitude fields |
|---|---|---|
| QB | linear points | `passing_epa_per_play`, `weekly_volatility_3yr`, `recent_points_avg`, `rushing_xfp_pbp_3yr`, `team_environment_score` |
| RB | logistic elite | `target_share_slope_3yr`, `xfp_share_3yr`, `carry_share_slope_3yr`, `red_zone_opportunities`, `receiving_xfp_pbp_3yr` |
| WR | logistic bust | `target_share_slope_3yr`, `wopr_slope_3yr`, `xfp_share_3yr`, `receiving_xfp_share_pbp_3yr`, `air_yards`, `receiving_epa` |
| TE | logistic bust | `target_share_slope_3yr`, `xfp_share_3yr`, `wopr_slope_3yr`, `air_yards`, `receiving_xfp_share_pbp_3yr`, `receiving_epa` |

The patched fields are active. The ranking outcome remains mixed.

## Checks Run

| Check | Result |
|---|---|
| `.\venv\Scripts\python.exe -m unittest tests.test_bqml_v2_feature_contract` | PASS, 19 tests |
| `.\venv\Scripts\python.exe -m py_compile src\bqml_v2_feature_contract.py src\ranking_formula_backtests.py` | PASS |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | PASS |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | PASS |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | PASS, 245 validation files discovered |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest` | PASS, 3 passed and 0 failed |
| `git diff --check` | PASS after normalizing the docs appended in this phase |

## Production and Live Ranking Safety

Confirmed:

- No deployment.
- No live ranking write.
- No champion activation.
- No `ranking_backtest_results` rows for the patched formula version.
- No `analytics_pigskin_rankings` rows for the patched formula version.
- No Gemini call.
- No Pigskin chat call.
- No Sleeper API call.
- No source ingest.

## Warnings

- The patched Standard v2 set does not uniformly beat original Standard v2.
- QB remains noisy even after adding `passing_epa_per_play`.
- 2025 RB VOR denominator remains null in the summary slice.
- `ngs_catch_over_expected_score_3yr` remains blocked by source availability.
- Generated SQL artifacts under `output/` are local evidence only and should not be committed.

## Recommended Next Phase

Generate owner-review boards for the patched Standard v2 challenger lanes only if the owner wants to inspect them. Keep Current Pigskin live. Do not activate a patched champion from summary evidence alone.
