# Phase 32.27 Direct NGS Metrics Report

Final decision: **DIRECT NGS METRICS IMPLEMENTED WITH WARNINGS**

Direct public nflverse Next Gen Stats receiving, rushing, and passing data exists in usable historical form for ranking research. The source is strong enough to feed the next BQML retrain and owner-review diagnostics. It is not a champion path by itself. Current Pigskin remains the live baseline.

## Scope Confirmation

- No deployment.
- No live ranking regeneration.
- No champion activation.
- No BQML training or hyperparameter tuning.
- No Pigskin chat, Gemini, LLM-backed ranking generation, live Sleeper API, or paid data.
- No detail rows written to `ranking_backtest_results`.
- No writes to `analytics_pigskin_rankings`, `ranking_formula_champions`, or live ranking candidate tables.
- No global truncates.

## Files Changed

- `src/nflverse_backfill.py`
- `src/nflverse_ngs_metrics.py`
- `src/ranking_formula_backtests.py`
- `tests/test_nflverse_ngs_metrics.py`
- `tests/test_ranking_formula_backtests.py`
- `bigquery/migrations/0039__direct_ngs_metrics.sql`
- `bigquery/contracts/player_week_ngs_metrics.md`
- `bigquery/validations/241_ngs_direct_metrics_objects.sql`
- `bigquery/validations/242_player_week_ngs_metrics_grain.sql`
- `bigquery/validations/243_player_week_ngs_metrics_ranges.sql`
- `bigquery/validations/244_ranking_feature_mart_ngs_columns.sql`
- `bigquery/validations/245_ranking_feature_mart_ngs_no_target_leakage.sql`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`

Commit hash: the final package commit is created after this report is written.

## Source Audit

`nflreadpy.load_nextgen_stats` supports `receiving`, `rushing`, and `passing`.

Prepared 2016-2025 source coverage:

| Source family | Fetched rows | Prepared rows | Skipped rows | Primary skip reason |
|---|---:|---:|---:|---|
| receiving | 14,731 | 14,716 | 15 | missing natural key `team` |
| rushing | 6,059 | 6,052 | 7 | missing natural key `team` |
| passing | 5,933 | 5,925 | 8 | missing natural key `team` |

Loaded raw table counts:

| Raw table | Rows |
|---|---:|
| `raw_nflverse_ngs_receiving` | 14,716 |
| `raw_nflverse_ngs_rushing` | 6,052 |
| `raw_nflverse_ngs_passing` | 5,925 |

Usable public source fields:

- Receiving: `avg_cushion`, `avg_separation`, `avg_intended_air_yards`, `percent_share_of_intended_air_yards`, `receptions`, `targets`, `catch_percentage`, `yards`, `rec_touchdowns`, `avg_yac`, `avg_expected_yac`, `avg_yac_above_expectation`.
- Rushing: `efficiency`, `percent_attempts_gte_eight_defenders`, `avg_time_to_los`, `rush_attempts`, `expected_rush_yards`, `rush_yards_over_expected`, `rush_yards_over_expected_per_att`, `rush_pct_over_expected`.
- Passing: `avg_time_to_throw`, `avg_intended_air_yards`, `aggressiveness`, `expected_completion_percentage`, `completion_percentage_above_expectation`.

Source limitation: the public receiving feed used here does not expose expected catch percentage or catch-over-expected. The derived table keeps those fields null and sets explicit unavailable flags.

## Migration and Derived Metrics

Migration applied:

- `0039__direct_ngs_metrics.sql`

Objects added or extended:

- Extended raw NGS tables with public nflverse columns.
- Created `player_week_ngs_metrics`.
- Added leakage-safe NGS feature columns to `ranking_backtest_feature_mart`.

Derived metric materialization:

- Gate used: `ALLOW_NFLVERSE_NGS_METRICS_MATERIALIZATION=true`.
- Gate removed after write.
- Source version: `nflverse_ngs_direct_latest`.
- Season range: 2016-2025.
- Insert job ID: `e637fc1f-57a1-4943-a486-3ed1cd06753e`.
- Rows written: 24,557.
- Week 0 aggregate rows were filtered out. Only weeks 1-23 are used.

Derived QB/RB/WR/TE coverage:

| Season | QB | RB | TE | WR |
|---:|---:|---:|---:|---:|
| 2016 | 534 | 521 | 343 | 1,126 |
| 2017 | 534 | 542 | 301 | 997 |
| 2018 | 539 | 523 | 271 | 1,023 |
| 2019 | 537 | 521 | 295 | 998 |
| 2020 | 540 | 533 | 323 | 1,065 |
| 2021 | 570 | 566 | 339 | 1,109 |
| 2022 | 563 | 569 | 311 | 1,033 |
| 2023 | 575 | 574 | 329 | 1,029 |
| 2024 | 571 | 554 | 311 | 995 |
| 2025 | 563 | 596 | 338 | 944 |

## Feature Mart Refresh

`ranking_backtest_feature_mart` was refreshed for target seasons 2017-2025 with source seasons strictly before the target season.

- 2017-2023 refreshed rows: 129,808.
- 2024 refreshed rows: 19,672.
- 2025 refreshed rows: 6,764.
- Total target-season rows after refresh: 156,244.

Recent coverage:

| Target season | Position | Rows | NGS populated count |
|---:|---|---:|---:|
| 2024 | QB | 2,292 | 2,280 passing |
| 2024 | RB | 5,104 | 4,240 rushing |
| 2024 | TE | 4,348 | 3,264 receiving |
| 2024 | WR | 7,928 | 7,020 receiving |
| 2025 | QB | 1,180 | 1,168 passing |
| 2025 | RB | 1,464 | 1,076 rushing |
| 2025 | TE | 1,568 | 1,364 receiving |
| 2025 | WR | 2,552 | 2,376 receiving |

Leakage guard:

- `player_week_ngs_metrics` stores source-season facts.
- `ranking_backtest_feature_mart` joins NGS rows only from source seasons before the target season.
- Validation `245_ranking_feature_mart_ngs_no_target_leakage.sql` passed.

## SQL-Native Diagnostic

Candidate family: `ngs_direct_metrics_v0`.

Candidates:

- `ngs_qb_passing_efficiency_v0`
- `ngs_rb_rushing_efficiency_v0`
- `ngs_te_receiving_efficiency_v0`
- `ngs_wr_receiving_efficiency_v0`

Dry-run:

- Candidate count: 4.
- Expected run rows: 4.
- Expected summary rows: 16.
- Expected detail rows: 0.
- Estimated bytes: 0 from BigQuery script dry-run compilation.

Controlled summary-only write:

- Gate used: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`.
- Gate removed after write.
- BigQuery job ID: `f4e89dde-fa1d-4075-b870-23cd9fcb6b87`.
- Wrote 4 rows to `ranking_backtest_runs`.
- Wrote 16 rows to `ranking_backtest_candidate_summaries`.
- Wrote 0 rows to `ranking_backtest_results`.
- Wrote 0 rows to `ranking_formula_champions`.

Persistence caveat: `ranking_backtest_runs.formula_version` uses `ranking_backtest_sql_native_ngs_direct_v0`, while candidate summaries store family `formula_version = ngs_direct_metrics_v0`. Query by `backtest_run_id LIKE 'ranking_backtest_sql_native_ngs_direct_v0%'` or by `candidate_id LIKE 'ngs_%'`.

## Diagnostic Results

2017-2025 PPR aggregate:

| Candidate | Sample | Pairwise | Top-N | Captured | VOR captured | NDCG | Bust | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `ngs_qb_passing_efficiency_v0` | 4,646 | 0.7299 | 0.5812 | 0.7905 | 0.6214 | 0.7517 | 0.0696 | 0.0091 |
| `ngs_rb_rushing_efficiency_v0` | 9,961 | 0.7512 | 0.6247 | 0.7627 | 0.6483 | 0.6989 | 0.0870 | 0.1229 |
| `ngs_te_receiving_efficiency_v0` | 8,453 | 0.6916 | 0.4837 | 0.6714 | 0.5557 | 0.6369 | 0.2669 | 0.0916 |
| `ngs_wr_receiving_efficiency_v0` | 15,978 | 0.7452 | 0.5159 | 0.7266 | 0.6106 | 0.6719 | 0.2052 | 0.0627 |

Read:

- Direct NGS shows useful RB and WR/TE component signal.
- It is not a direct champion replacement. Current Pigskin remains stronger as the live baseline because it blends more stable cross-source context.
- The NGS signals should feed a new BQML retrain and owner-review boards.
- Expected-catch and catch-over-expected remain source gaps and must stay flagged.

## Checks and Validations

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_nflverse_ngs_metrics tests.test_ranking_formula_backtests tests.test_nflverse_backfill_executor`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern "241_ngs_direct|242_player_week_ngs|243_player_week_ngs|244_ranking_feature_mart_ngs|245_ranking_feature_mart_ngs"`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Validation results:

- NGS validations: 5 passed, 0 failed.
- Ranking backtest validations: 3 passed, 0 failed.
- Ranking formula validations: 6 passed, 0 failed.
- No pending migrations.

Warning:

- A broad earlier validation pattern containing `ngs|ranking_feature_mart_ngs` matched unrelated `projection_rankings` validations. `093_projection_rankings_rank_order.sql` returned a known unrelated rank-order warning. The scoped NGS validation set passed.

## Gate State After Phase

All checked gates were unset after bounded writes:

- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_NGS_METRICS_MATERIALIZATION`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`

## Recommendation

Next phase: **Phase 32.28 - BQML retrain with NGS features**.

Reason: direct NGS coverage is real, leakage-safe, and now present in the feature mart. The standalone NGS candidates are useful explainability lanes, but the best next use is as model input alongside current Pigskin, enriched ideal stats, PBP xFP, first-down proxies, injury context, and role context.

Do not activate any champion from this phase.
