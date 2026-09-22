# Phase 32.6 BigQuery-Native Draft-Value Optimization Report

Final decision: **DRAFT VALUE METRICS READY WITH WARNINGS**

Phase 32.6 interpreted the Phase 32.5 tournament, audited the Python and BigQuery bottlenecks, added pure draft-value metric helpers, prototyped cross-position draft-value metrics from existing tournament evidence, and updated the permanent scorecard. No deployment occurred. No live rankings were regenerated. No champion formulas were activated. No Gemini, Pigskin chat, live Sleeper API, Cloud Run Job, Scheduler, ingestion, or materialization action was run.

## Phase 32.5 Interpretation

Current deterministic Pigskin baseline family score:

| Metric | Value |
|---|---:|
| pairwise win rate | 0.6697 |
| high-confidence pairwise win rate | 0.7575 |
| top-N hit rate | 0.5400 |
| VOR captured rate | 0.5981 |
| actual points captured rate | 0.7123 |
| missing-input rate | 0.0032 |

Best aggregate challenger:

| Family | Pairwise | High-confidence | Top-N | VOR captured | Captured points | Missing |
|---|---:|---:|---:|---:|---:|---:|
| simple projection points | 0.6728 | 0.7364 | 0.5387 | 0.5956 | 0.7115 | 0.0006 |

Decision: no challenger clearly beats the baseline. Simple projection is an approximate tie on pairwise rate, while the current Pigskin baseline remains stronger on high-confidence pairwise, top-N hit rate, VOR captured rate, and actual points captured rate.

Profile and position notes:

- Current Pigskin baseline remains strongest for GNG Keeper QB.
- Simple projection is a strong low-missing challenger for QB/RB and PPR WR.
- Seeded v0 TE/WR leaders have high missing-input rates because `pigskin_context_score` is unavailable historically.
- v2 trend-aware formulas underperformed and should not be activated.

No champion should be activated because the margin is too small, missing-input rates distort some winners, and cross-position draft-value scoring was only prototyped in this phase.

## Slow Job Audit

`INFORMATION_SCHEMA.JOBS_BY_PROJECT` and `INFORMATION_SCHEMA.JOBS_BY_USER` were both blocked by IAM:

- `JOBS_BY_PROJECT`: missing `bigquery.jobs.listAll`
- `JOBS_BY_USER`: missing `bigquery.jobs.list`

That means job IDs, slot-ms, byte counts, cache hits, and query text could not be recorded from BigQuery job metadata in this local session.

Observed bottleneck classification from the runner and table writes:

| Bottleneck | Classification | Evidence |
|---|---|---|
| Python result-row construction | high | `build_result_rows_for_candidates` loops candidates and feature rows, then stores full detail rows. |
| Pairwise metric calculation | high | `_pairwise_win_rate` performs nested Python comparisons per candidate/week. |
| Repeated feature scans | medium | each rolling target/profile call reloads source-window features. |
| DataFrame/load overhead | high | Phase 32.5 wrote 1,874,928 detail rows via JSON load plus delete/reload by run ID. |
| BigQuery compute | unknown | job metadata access was blocked. |
| Validation overhead | low | ranking validation patterns completed quickly after the write. |

## Python Bottleneck Analysis

Relevant code paths:

- `load_no_lookahead_feature_rows`: pulls source-window and target rows into Python for each target/profile/position slice.
- `build_result_rows_for_candidates`: constructs one detail row per candidate/player/week.
- `_assign_predicted_ranks`: sorts in Python per candidate/week.
- `_pairwise_win_rate`: nested comparisons in Python.
- `_top_n_capture_metrics` and `_value_over_replacement_captured_rate`: repeated per-summary sorting in Python.
- `save_executed_backtest`: deletes by backtest run ID and loads full run, result, and summary rows.

Highest-ROI shift: keep feature rows, formula scoring, ranks, pairwise alternatives, and summaries inside BigQuery. Use Python only for orchestration, dry-run preview, owner-readable reports, and scorecard updates.

## Table Layout Audit

Read-only table layout results:

| Table | Row count | Size bytes | Partitioning | Clustering |
|---|---:|---:|---|---|
| `ranking_backtest_results` | 1,933,500 | 1,671,221,373 | `RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))` | `backtest_run_id`, `position`, `scoring_profile_id`, `player_id_internal` |
| `ranking_backtest_candidate_summaries` | 1,872 | 2,777,235 | `DATE(created_at)` | `backtest_run_id`, `position`, `scoring_profile_id`, `candidate_id` |
| `ranking_backtest_runs` | 48 | 39,840 | `DATE(created_at)` | `formula_version`, `status`, `backtest_run_id`, `formula_set_id` |
| `analytics_player_fantasy_points_by_profile` | 297,792 | 263,924,850 | `RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))` | `player_id_internal`, `scoring_profile_id`, `position`, `team` |
| `player_week_advanced_metrics` | 217,230 | 229,649,470 | `RANGE_BUCKET(season, GENERATE_ARRAY(1999, 2050, 1))` | `week`, `player_id_internal`, `scoring_profile_id`, `position` |
| `pigskin_player_context_packet_current` | 4,084 | 34,235,020 | `RANGE_BUCKET(as_of_season, GENERATE_ARRAY(1999, 2050, 1))` | `as_of_week`, `player_id_internal`, `scoring_profile_id`, `position` |

Recommendations:

- Keep `ranking_backtest_results` partitioned by season, but consider clustering order `backtest_run_id`, `scoring_profile_id`, `candidate_id`, `player_id_internal` for candidate-heavy summaries.
- Keep candidate summaries clustered by `backtest_run_id`, `position`, `scoring_profile_id`, `candidate_id`.
- For a future `ranking_backtest_feature_mart`, partition by `target_season` and cluster by `scoring_profile_id`, `position`, `player_id_internal`, `source_window_end_season`.
- Do not add migrations yet. The highest ROI is a feature mart plus SQL-native scoring, not changing the existing evidence tables first.

## Feature Mart Design

Recommended table: `ranking_backtest_feature_mart`

Grain:

- `source_window_start_season`
- `source_window_end_season`
- `target_season`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `position`
- `player_id_internal`

Predictor columns:

- recent fantasy points by scoring profile
- profile points score
- opportunity score proxy
- efficiency score proxy
- analytical grade proxy
- role stability score
- availability rate
- usage and target/carry trends
- EPA and success-rate trends
- source freshness JSON
- missing-feature flags JSON

Target/outcome columns:

- target-season fantasy points
- actual positional rank
- actual overall rank
- position replacement points
- value over replacement
- top-24/top-50/top-100 labels
- pick-band labels

Keep predictor and target columns clearly separated so no target-season leakage reaches scoring.

## Implementation Form Decision

Recommended path:

1. Precomputed feature mart table.
2. Parameterized SQL or table-valued function for target slices.
3. SQL script or stored procedure for tournament scoring and summary writes.
4. Python orchestration only for bounded execution, reports, and scorecard updates.

Rejected for now:

- Materialized view: formula JSON and rolling-window parameters make this awkward.
- Python-only orchestration: already too slow and too memory-heavy.
- Full stored-procedure-only approach: harder to unit test and review until the SQL prototype stabilizes.

## SQL-Native Scoring Design

Design:

1. Store or pass candidate formulas as rows with JSON weights.
2. Use `JSON_VALUE` or `JSON_QUERY_ARRAY` to unnest feature weights into `(candidate_id, feature_name, weight)` rows.
3. Convert feature mart predictor columns into long-form feature rows.
4. Join weights to features on `feature_name`.
5. Calculate `predicted_score = SUM(feature_score * weight) / SUM(weight where feature available)`.
6. Rank with `ROW_NUMBER() OVER (PARTITION BY candidate_id, profile, target_season, week, position ORDER BY predicted_score DESC)` for position metrics.
7. Rank with `ROW_NUMBER() OVER (PARTITION BY candidate_id, profile, target_season, week ORDER BY predicted_score DESC)` for overall draft metrics.
8. Write summary rows first. Write detail rows only when requested.

Pairwise policy:

- Use high-confidence pairwise only by default.
- Use top-100 overall pairwise for draft-value reporting.
- Use full pairwise only for official tournament snapshots.
- Prefer rank-correlation and captured-value metrics for exploratory iterations.

## Overall Draft-Value Metric Design

Metrics defined:

- `overall_pairwise_draft_win_rate`
- `top_24_overall_hit_rate`
- `top_50_overall_hit_rate`
- `top_100_overall_hit_rate`
- `value_over_replacement_captured_rate`
- pick-band regret for `1-12`, `13-24`, `25-36`, `37-60`, `61-100`, `101+`

Implementation added in `src/ranking_formula_backtests.py`:

- `replacement_rank_for_position`
- `assign_pick_band`
- `build_overall_draft_value_rows`
- `build_overall_draft_value_summary`
- `build_overall_draft_value_metrics_sql`

The helpers are pure and do not write BigQuery rows.

## Prototype Draft-Value Results

Read-only prototype from existing `ranking_backtest_results` rows:

| Family | Top-24 hit | Top-50 hit | Top-100 hit | Top-100 pairwise | VOR captured |
|---|---:|---:|---:|---:|---:|
| current Pigskin candidate | 0.6426 | 0.7230 | 0.5808 | 0.6721 | 0.9922 |
| scarcity adjusted draft value | 0.6483 | 0.7200 | 0.5807 | 0.6687 | 0.9923 |
| simple projection points | 0.6439 | 0.7238 | 0.5804 | 0.6730 | 0.9934 |
| value over replacement | 0.6390 | 0.7172 | 0.5802 | 0.6629 | 0.9917 |
| v1 improved mappings | 0.6315 | 0.7138 | 0.5802 | 0.6528 | 0.9892 |
| equal weight blend | 0.6360 | 0.7153 | 0.5802 | 0.6578 | 0.9908 |
| seeded v0 | 0.6028 | 0.7115 | 0.5802 | 0.6345 | 0.9932 |
| v2 trend aware | 0.5274 | 0.6679 | 0.5770 | 0.5448 | 0.9767 |

Interpretation: simple projection narrowly leads the top-100 pairwise prototype and VOR captured prototype, but the margin over current Pigskin is still too small to justify a champion switch. The top-100 hit metric is nearly flat, which means future work should focus on pick-band regret and top-24/top-50 discrimination.

Pick-band regret prototype:

- Most regret is concentrated in pick bands `1-12` and `13-24`.
- Bands `37-60`, `61-100`, and `101+` showed zero regret in this prototype because the top-end VOR calculation concentrates replacement value in early overall picks.
- This needs refinement before it becomes a champion-selection gate.

## BigQuery ML Feasibility

Feasible model families once `ranking_backtest_feature_mart` exists:

| Model | Target | Feasibility | Risk |
|---|---|---|---|
| linear regression | target fantasy points or VOR | high | explainable, likely underfits |
| boosted tree regression | target fantasy points or VOR | medium | stronger, less transparent |
| random forest regression | target fantasy points or VOR | medium | may be harder to explain |
| logistic top-N classifier | top-24/top-50/top-100 label | high | useful for draft bands, not direct point estimates |

Expected BigQuery ML shape:

```sql
CREATE OR REPLACE MODEL `fantasy_football_brain.ranking_formula_bqml_<model>`
OPTIONS(model_type='linear_reg', input_label_cols=['target_fantasy_points']) AS
SELECT
  predictor_columns,
  target_fantasy_points
FROM `fantasy_football_brain.ranking_backtest_feature_mart`
WHERE target_season BETWEEN 2017 AND 2024;
```

Do not train models until the feature mart exists and owner approves cost. BigQuery ML can join the tournament as another candidate family, but only if predictions are written to a bounded candidate output table or scored in a read-only evaluation query.

## Detail-Row Retention Policy

Recommended policy:

- Official tournaments may write full detail rows.
- Exploratory runs should write summaries only.
- Debug runs should write sampled detail rows.
- Pairwise detail rows should be skipped unless explicitly requested.

Reason: Phase 32.5 wrote 1.875 million result rows for one tournament. The row volume is manageable for evidence, but it slows iteration and makes future tuning more expensive than needed.

## Scorecard Update Summary

Updated:

- `docs/rebuild/ranking-algorithm-scorecard.md`

The scorecard now records:

- current Pigskin remains live baseline
- simple projection is the strongest challenger but only tied
- v2 trend-aware underperformed
- overall draft-value metrics now have a read-only prototype
- no champion formula is active

## Tests And Checks

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`

Results:

- Focused ranking tests passed: 54 tests.
- Full test discovery passed: 708 tests.
- No pending migrations.
- Validation dry-run discovered ranking formula and backtest validations through `209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`.

## No-Change Confirmation

Read-only verification after prototype queries:

- `ranking_formula_champions`: 0 rows
- active `analytics_pigskin_rankings`: still 45 QB, 80 RB, 100 WR, 60 TE for each of `ppr`, `half_ppr`, `standard`, `gng_keeper`

No live ranking rows were changed. No champion formulas were activated.

## Remaining Warnings

- Job metadata audit is incomplete because INFORMATION_SCHEMA job access is blocked by IAM.
- Pick-band regret needs refinement before champion selection.
- SQL-native scoring is designed but not implemented as a warehouse engine yet.
- BigQuery ML is feasible but should wait for a feature mart and owner cost approval.

## Recommended Next Phase

Recommended: **Phase 32.7: Implement ranking backtest feature mart**.

Secondary options:

- Phase 32.7: SQL-native tournament engine prototype
- Phase 32.7: Overall draft-value metrics implementation
- Phase 32.7: BigQuery ML baseline prototype
