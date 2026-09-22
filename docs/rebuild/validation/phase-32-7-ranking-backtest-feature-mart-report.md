# Phase 32.7 Ranking Backtest Feature Mart Report

Final decision: **FEATURE MART IMPLEMENTED WITH WARNINGS**

Phase 32.7 added the additive `ranking_backtest_feature_mart` table, populated a bounded 2025 feature-mart slice, and prototyped SQL-native scoring for a small PPR TE slice. No deployment occurred. No live rankings were regenerated. No champion formulas were activated. No Pigskin chat, Gemini, live Sleeper API, Cloud Run Job, Scheduler, ingestion, or materialization action was run.

## Files Changed

- `bigquery/migrations/0030__ranking_backtest_feature_mart.sql`
- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/validation/phase-32-7-ranking-backtest-feature-mart-report.md`

Commit hash: not committed in this phase.

## Feature Mart Design

Table: `ranking_backtest_feature_mart`

Implemented grain:

- `source_window_start_season`
- `source_window_end_season`
- `target_season`
- `target_week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `position`
- `player_id_internal`

The prompt's preferred grain did not include week, but the existing backtest target is weekly. `target_week` was added to avoid collapsing weekly outcomes into one row per player-season.

Predictor columns are separated from outcome columns:

- predictor examples: `profile_points_score`, `opportunity_score_proxy`, `efficiency_score_proxy`, `analytical_grade_proxy`, `role_stability_score`, trend fields, availability, volatility, missing flags, source freshness
- outcome examples: `target_fantasy_points`, `actual_position_rank`, `actual_overall_rank`, `replacement_points`, `value_over_replacement`, `top_24_overall`, `top_50_overall`, `top_100_overall`, `actual_pick_band`

Leakage guard:

- source predictors use `metrics.season BETWEEN @source_window_start_season AND @source_window_end_season`
- source predictors also require `metrics.season < @target_season`
- target-season rows are used only for outcome columns

## Implementation Form Decision

Chosen form:

- precomputed BigQuery table for the feature mart
- SQL builder for bounded mart population
- SQL-native scoring prototype over the mart
- Python only for orchestration and reporting

Rejected for this phase:

- materialized view: rolling windows and formula weights are too parameterized
- table-valued function only: useful later, but less direct for persisted tournament evidence
- stored procedure only: harder to test before the SQL pattern stabilizes
- Python-only orchestration: Phase 32.5 already showed this is too slow for tournament iteration

## Migration Result

Migration applied:

- `0030__ranking_backtest_feature_mart.sql`

Result:

- table exists: `fantasy-football-498121.fantasy_football_brain.ranking_backtest_feature_mart`
- no unrelated migrations were pending before apply
- migration is additive DDL only

## Feature Mart Build

Bounded slice built:

- target season: 2025
- source window: 2022-2024
- profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`
- positions: QB, RB, WR, TE
- row count: 6,764

Row counts by profile and position:

| Profile | Position | Row count | Player count | Week count |
|---|---|---:|---:|---:|
| `gng_keeper` | QB | 295 | 36 | 18 |
| `gng_keeper` | RB | 366 | 34 | 18 |
| `gng_keeper` | TE | 392 | 38 | 18 |
| `gng_keeper` | WR | 638 | 64 | 18 |
| `half_ppr` | QB | 295 | 36 | 18 |
| `half_ppr` | RB | 366 | 34 | 18 |
| `half_ppr` | TE | 392 | 38 | 18 |
| `half_ppr` | WR | 638 | 64 | 18 |
| `ppr` | QB | 295 | 36 | 18 |
| `ppr` | RB | 366 | 34 | 18 |
| `ppr` | TE | 392 | 38 | 18 |
| `ppr` | WR | 638 | 64 | 18 |
| `standard` | QB | 295 | 36 | 18 |
| `standard` | RB | 366 | 34 | 18 |
| `standard` | TE | 392 | 38 | 18 |
| `standard` | WR | 638 | 64 | 18 |

The build used bounded delete plus insert for the selected slice only. No global truncate was used.

## SQL-Native Scoring Prototype

Prototype slice:

- target season: 2025
- profile: `ppr`
- position: TE
- candidate count: 3

Algorithms:

- `current_pigskin_candidate_score_v1`
- `simple_projection_points_baseline`
- `v2_trend_balanced`

SQL-native prototype result:

| Candidate | Row count | Missing input | Top-N hit | Captured points | VOR captured | Rank correlation |
|---|---:|---:|---:|---:|---:|---:|
| current Pigskin candidate | 392 | 0.0045 | 0.7778 | 0.8676 | 0.8629 | 0.5394 |
| simple projection points | 392 | 0.0000 | 0.7778 | 0.8646 | 0.8547 | 0.5732 |
| v2 trend balanced | 392 | 0.0159 | 0.5648 | 0.5878 | 0.4824 | 0.0735 |

Uncached query stats for the scoring prototype:

- job ID: `7260699a-b2fa-4c41-be80-7d2fb51a3700`
- duration: 1.346 seconds
- total bytes processed: 1,212,475
- slot millis: 157
- returned rows: 3

## Comparison Against Python Evidence

Existing Python-written tournament evidence for the same PPR 2025 TE slice:

| Candidate | Row count | Top-N hit | Captured points | VOR captured | Rank correlation | Pairwise |
|---|---:|---:|---:|---:|---:|---:|
| current Pigskin candidate | 392 | 0.7778 | 0.8676 | 0.8561 | 0.5432 | 0.6952 |
| simple projection points | 392 | 0.7778 | 0.8646 | 0.8492 | 0.5760 | 0.7121 |
| v2 trend balanced | 392 | 0.5648 | 0.5878 | 0.4891 | 0.0758 | 0.5128 |

Comparison result:

- row counts match
- top-N hit rates match
- captured points match
- VOR captured rates are close, with small differences from replacement-value implementation details
- rank correlations are close
- SQL prototype does not compute pairwise yet

## Detail-Row Retention Policy

Policy added to the scorecard:

- official tournaments may write full detail rows
- exploratory runs should write summaries only
- debug runs should write sampled detail rows
- pairwise detail rows should be skipped unless explicitly requested

## BigQuery ML Preparation

Future BQML baselines can use `ranking_backtest_feature_mart` as the training table.

Candidate model shapes:

| Model | Target variable | Likely features |
|---|---|---|
| linear regression | `target_fantasy_points` or `value_over_replacement` | profile score, opportunity, efficiency, role stability, trend fields, availability |
| boosted tree regression | `target_fantasy_points` or `value_over_replacement` | same, plus pick-band labels for evaluation only |
| random forest regression | `target_fantasy_points` or `value_over_replacement` | same predictor set |
| logistic top-N classifier | `top_24_overall`, `top_50_overall`, or `top_100_overall` | same predictor set |

Do not train models until a separate cost-approved phase.

## Tests And Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- Focused ranking tests passed: 61 tests.
- Full test discovery passed: 715 tests.
- No pending migrations after applying `0030`.
- Validation dry-run discovered ranking formula and backtest validations through `209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`.

## No-Change Confirmation

Read-only verification after mart build and SQL prototype:

- `ranking_formula_champions`: 0 rows
- active `analytics_pigskin_rankings`: still 45 QB, 80 RB, 100 WR, 60 TE for each of `ppr`, `half_ppr`, `standard`, `gng_keeper`

No live ranking rows were changed. No champion formulas were activated. Formula and backtest tables were not exposed to Pigskin chat.

## Remaining Warnings

- SQL-native prototype does not compute pairwise metrics yet.
- VOR captured has small differences from Python evidence and should be standardized before official tournament replacement.
- Feature mart currently has only the bounded 2025 slice.
- BigQuery ML remains design-only.
- Job metadata audit remains limited by IAM, but direct query job stats were captured for the prototype query.

## Recommended Next Phase

Recommended: **Phase 32.8: SQL-native tournament engine**.

Secondary options:

- Phase 32.8: BigQuery ML baseline prototype
- Phase 32.8: Overall draft-value metric persistence
- Phase 32.8: Formula comparison dashboard
