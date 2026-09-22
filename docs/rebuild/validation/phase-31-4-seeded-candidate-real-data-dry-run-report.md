# Phase 31.4 Seeded Candidate Real-Data Dry-Run Report

## Final Decision

SEEDED CANDIDATE REAL-DATA DRY-RUN READY WITH WARNINGS

The ranking formula runner now loads seeded draft candidates from BigQuery, loads bounded historical feature rows from approved input tables, and produces result-shaped and candidate-summary-shaped rows in memory. No backtest run, result, summary, champion, or formula seed rows were written in this phase.

No production deploy occurred. No Pigskin calls, LLM-backed actions, materializations, live Sleeper API calls, Cloud Run Jobs, or Scheduler jobs were run.

## Git State

Starting commit:

- `850db0c Seed draft ranking formula candidates`

Untracked historical validation backlog remains present and was not staged for this phase.

## Files Changed

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/validation/phase-31-4-seeded-candidate-real-data-dry-run-report.md`

## Seeded Candidate Loading Behavior

Added safe, parameterized loaders:

- `load_ranking_formula_candidates`
- `load_ranking_formula_set`
- `load_candidates_for_formula_set`

Loader behavior:

- validates every loaded `formula_json`
- defaults to `status=draft`
- rejects unsupported statuses
- rejects unknown positions
- rejects SQL/code/table-name expressions through the existing validator
- rejects blocked metrics unless source availability flags are explicitly true
- uses fixed SQL with query parameters, not arbitrary caller SQL

The formula set loader resolves the draft formula set `ranking_formula_set_v0_2026_001` and can load the position-specific candidate reference for QB/RB/WR/TE.

## Bounded Input Loading Behavior

Added bounded real-data loader:

- `load_bounded_feature_rows`

Bounds enforced:

- position required
- `season_start` and `season_end` required
- maximum season span: `1`
- optional week bounds checked
- default limit: `100`
- maximum limit clamp: `500`
- explicit/defaulted `scoring_profile_id`, `league_type_id`, and `roster_format_id`

Approved tables used:

- `player_week_advanced_metrics`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`

Approved table list remains:

- `player_week_advanced_metrics`
- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `pigskin_player_context_packet_current`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`

No raw/source tables are referenced.

## Formula Evaluation Behavior

Added in-memory result shaping:

- `run_seeded_candidate_real_data_dry_run`
- `build_result_rows_for_candidates`
- `evaluate_formula_for_feature_row`

Formula evaluation:

- uses weighted linear scoring
- clamps `predicted_score` to `0` through `100`
- records available feature values in `feature_values_json`
- records unavailable formula inputs in `missing_flags_json`
- does not substitute missing features with zero
- includes source freshness when available
- includes actual target fields only when target data is available

## Candidate Summary Behavior

Added in-memory summary shaping:

- `build_summary_from_results`

Summary fields produced:

- `sample_size`
- `top_n_hit_rate` when target hits exist
- `rank_correlation` when actual and predicted ranks are available
- `missing_input_rate`

Null metric reasons are written into `metric_json` for metrics that are not safely computable in the dry-run skeleton:

- `pairwise_win_rate`
- `mean_absolute_error`
- `regret_score`
- `actual_points_captured_rate`

## Test Results

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`: passed, 26 tests
- `.\venv\Scripts\python.exe -m unittest tests.test_seed_ranking_formula_candidates`: passed, 6 tests
- `.\venv\Scripts\python.exe -m unittest discover tests`: passed, 648 tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovered 209 validation files

## Dry-Run Results By Position

All dry-runs used:

- formula set: `ranking_formula_set_v0_2026_001`
- status: `draft`
- season: `2014`
- weeks: `1` through `4`
- limit: `100`
- mode: dry-run only
- write gate: unset

| Position | Candidate count | Input row count | Result-shaped rows | Summary-shaped rows | Sample size | Missing input rate | Top-N hit rate | Rank correlation |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| QB | 1 | 100 | 100 | 1 | 100 | 0.808 | null | null |
| RB | 1 | 100 | 100 | 1 | 100 | 0.800 | null | null |
| WR | 1 | 100 | 100 | 1 | 100 | 0.800 | null | null |
| TE | 1 | 100 | 100 | 1 | 100 | 0.800 | null | null |

## Row Counts After Dry-Run

- `ranking_formula_candidates`: `12`
- `ranking_formula_sets`: `1`
- `ranking_backtest_runs`: `0`
- `ranking_backtest_results`: `0`
- `ranking_backtest_candidate_summaries`: `0`
- `ranking_formula_champions`: `0`

## Missing Feature And Target Warnings

The bounded 2014 `player_week_advanced_metrics` rows exist, but the joined `analytics_player_weekly_truth` slice for 2014 weeks 1 through 4 returned no QB rows in the spot check. As a result:

- `actual_points` is unavailable in this slice
- `top_n_hit_rate` remains null
- `rank_correlation` remains null

Several seeded formula features are also unavailable in the current approved historical feature rows. They are reported as missing features, not treated as zero.

## No Pigskin Exposure Confirmation

Searched:

- `app.py`
- `src/pigskin_context_tools.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_qa.py`

Search terms:

- `ranking_formula`
- `ranking_backtest`
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE`

Result:

- no ranking formula read/write tool exposed to Pigskin
- no arbitrary SQL path added
- no Streamlit request-time formula/backtest write path added

## Remaining Warnings

- Formula-set dry-runs currently evaluate the one baseline candidate referenced by the formula set for each position, not all three seeded candidates per position.
- Target metrics are unavailable for the tested 2014 weeks 1 through 4 slice because truth rows did not join.
- Feature mapping is intentionally conservative. Missing seeded formula features are surfaced in `missing_flags_json`.
- No backtest results or summaries were written. Controlled write remains a separate future phase.

## Recommended Next Phase

Phase 31.5 should improve feature mapping and target-data availability, then run a bounded comparison dry-run across all three seeded candidates per position. A controlled write of bounded backtest run/results/summaries should wait until those dry-run warnings are accepted.
