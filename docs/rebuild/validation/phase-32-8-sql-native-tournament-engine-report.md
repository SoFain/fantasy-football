# Phase 32.8 SQL-Native Tournament Engine Report

Final decision: **SQL NATIVE TOURNAMENT ENGINE READY WITH WARNINGS**

Phase 32.8 moved the official ranking tournament path toward BigQuery-native execution. The feature mart now covers rolling target seasons 2017 through 2025, and the SQL-native tournament summary query computes draft-utility metrics without building player/candidate/week result rows in Python.

## Files Changed

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/validation/phase-32-8-sql-native-tournament-engine-report.md`

Commit hash if committed: not committed in this phase.

Current source base: `1228b7670c6d`

## Research Metric Contract

Draft-utility metrics are persisted in `ranking_backtest_candidate_summaries.metric_json`. No additive schema migration was needed because the summary table already has JSON storage for metric payloads.

Metric contract:

- `ndcg_at_k`
- `value_captured_at_k`
- `elite_recall_at_k`
- `tier_accuracy`
- `bust_rate`
- `pick_band_regret`
- `overall_pairwise_draft_win_rate`
- `high_confidence_pairwise_win_rate`
- `value_over_replacement_captured_rate`

K policy:

| Scope | K values |
|---|---|
| QB | 6, 12 |
| RB | 12, 24 |
| WR | 12, 24, 36 |
| TE | 3, 6, 12 |
| Overall | 24, 50, 100 |

## Feature Mart Expansion

The `ranking_backtest_feature_mart` was expanded with bounded delete/insert slices for target seasons 2017 through 2025.

Build scope:

- target seasons: 2017 through 2025
- source window: prior 3 years
- scoring profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`
- positions: QB, RB, WR, TE
- target table: `fantasy-football-498121.fantasy_football_brain.ranking_backtest_feature_mart`

Rows built:

| Target season | Row count | Source window |
|---:|---:|---|
| 2017 | 18,164 | 2014-2016 |
| 2018 | 17,108 | 2015-2017 |
| 2019 | 17,572 | 2016-2018 |
| 2020 | 18,540 | 2017-2019 |
| 2021 | 19,796 | 2018-2020 |
| 2022 | 19,432 | 2019-2021 |
| 2023 | 19,196 | 2020-2022 |
| 2024 | 19,672 | 2021-2023 |
| 2025 | 6,764 | 2022-2024 |

Total rows across the expanded mart: `156,244`

Coverage check:

- season/profile/position slices: `144`
- leakage rows where `source_window_end_season >= target_season`: `0`
- duplicate mart grain rows: `0`
- missing predictor flag rows: `0`
- missing outcome flag rows: `0`
- null VOR rows: `0`

## SQL-Native Scoring Implementation

Implemented the official SQL-native tournament path in `src/ranking_formula_backtests.py`:

- `draft_utility_metric_contract`
- `build_sql_native_tournament_summary_sql`
- `sql_native_tournament_candidates`
- `estimate_sql_native_tournament`
- `run_sql_native_tournament_summary`
- `build_sql_native_tournament_summary_write_sql`
- `write_sql_native_tournament_summaries`

The official SQL-native path:

- uses `ranking_backtest_feature_mart` as the source
- scores formulas in SQL
- ranks players with BigQuery window functions
- computes summary metrics in SQL
- computes high-confidence pairwise metrics in SQL
- writes future summaries with `CREATE TEMP TABLE ... AS SELECT` and `INSERT ... SELECT`

It does not call:

- `build_result_rows_for_candidates`
- `_pairwise_win_rate`
- `load_table_from_json`

## Draft-Utility Metric Implementation

Implemented in SQL:

- top-N hit rate
- rank correlation
- captured points rate
- value over replacement captured rate
- NDCG@K
- value captured at K
- elite recall at K
- tier accuracy
- bust rate
- pick-band regret
- high-confidence pairwise win rate

Not yet implemented:

- full pairwise explosion for official snapshots
- overall cross-position pairwise draft win rate inside the new summary query

The missing overall pairwise metric is left as `NULL` in `metric_json` for this phase.

## VOR Standardization

Final SQL-native VOR definition:

- replacement baseline is position-specific weekly replacement rank.
- replacement ranks: QB 12, RB 24, WR 24, TE 12.
- replacement points are computed per target season, target week, scoring profile, league type, roster format, and position.
- VOR is `GREATEST(actual_points - replacement_points, 0)`.
- captured VOR is aggregated across weekly top-K selections before division.

This explains small differences from older Python evidence that recomputed replacement inside helper paths.

## Dry-Run Results

SQL-native full tournament dry-run:

- candidate count: `16`
- estimated bytes processed: `2,402,699`

SQL-native full tournament read-only run:

- job ID: `138a1812-d56f-4ff2-bbcc-855518bffc37`
- summary rows: `64`
- duration: `6.195s`
- bytes processed: `53,106,789`
- slot millis: `227,584`

No summary rows were written because `ALLOW_RANKING_FORMULA_BACKTEST_WRITE` was unset.

## Bounded SQL vs Python Comparison

Bounded slice:

- scoring profile: `ppr`
- target season: `2025`
- position: `TE`
- summary rows: `4`
- query job ID: `59242add-2189-481c-a1ba-f2e135fe50a8`
- bytes processed: `2,402,699`

| Candidate | Top-N | Captured points | VOR captured | Rank corr | Missing |
|---|---:|---:|---:|---:|---:|
| current Pigskin candidate | 0.7778 | 0.8624 | 0.8570 | 0.5394 | 0.0045 |
| simple projection points | 0.7778 | 0.8605 | 0.8522 | 0.5732 | 0.0000 |
| scarcity adjusted draft value | 0.7037 | 0.7902 | 0.7520 | 0.4659 | 0.0010 |
| v2 trend balanced | 0.5648 | 0.5911 | 0.4850 | 0.0735 | 0.0159 |

Prior Python evidence for the same bounded TE slice had matching top-N rates and close rank correlations. Captured points and VOR differ slightly because SQL now uses the standardized mart VOR definition.

## Controlled Write Status

Controlled write was not run.

Authorization state:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`: unset

Future write behavior:

- summary-only writes use BigQuery `INSERT ... SELECT`
- detail rows are not written in exploratory mode
- `ranking_formula_champions` is not touched
- `analytics_pigskin_rankings` is not touched
- `analytics_pigskin_rankings_candidates` is not touched

## Scorecard Update

Updated `docs/rebuild/ranking-algorithm-scorecard.md` with:

- SQL-native tournament section
- draft-utility metric contract
- rolling mart row counts
- bounded TE comparison table
- VOR standardization
- BQML follow-up plan

SQL-native results supplement the Python evidence for now. They do not replace the live baseline or activate a champion.

## BQML Follow-Up Plan

No models were trained.

The feature mart can support:

- linear regression using `target_fantasy_points` or `value_over_replacement`
- boosted tree regression for non-linear usage/efficiency interactions
- random forest regression as a robust baseline
- logistic top-N classifier using position-specific top-K labels

Feature columns should remain predictor-only. Target/outcome columns must not be used as predictors.

## Checks Run

Passed:

- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- SQL-native tournament dry-run
- SQL-native write script inspection
- feature mart coverage, leakage, grain, and flags checks
- champion count check
- active ranking count check

Check results:

- safety checker: passed
- compileall: passed
- focused ranking tests: 70 tests passed
- full test discovery: 724 tests passed
- migrations: no pending migrations
- validation dry-run: passed

## No-Change Confirmation

- No deployment occurred.
- No staging deploy occurred.
- No production deploy occurred.
- No live rankings were regenerated.
- No active ranking rows were overwritten.
- No champion formulas were activated.
- `ranking_formula_champions` row count remains `0`.
- Active ranking counts remain 45 QB, 80 RB, 100 WR, 60 TE for each of `ppr`, `half_ppr`, `standard`, and `gng_keeper`.
- No Pigskin chat was called.
- No Gemini or LLM-backed ranking generation was called.
- No live Sleeper API call was made.

## Remaining Warnings

- Overall pairwise draft win rate is not yet implemented in the SQL-native summary query.
- Controlled summary write was not run because the write gate was unset.
- Full official detail-row snapshots remain intentionally out of scope.
- SQL-native evidence supplements Python evidence until owner review accepts it as the tournament source of truth.

## Recommended Next Phase

Recommended: **Phase 32.9: Owner review of draft-utility metrics**

Alternate next phases:

- Phase 32.9: BigQuery ML baseline prototype
- Phase 32.9: Formula comparison dashboard
- Phase 32.9: Generate formula-driven candidate rankings
