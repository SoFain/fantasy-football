# Phase 31.1 Ranking Formula Backtest Foundation Report

## Final Decision

RANKING FORMULA BACKTEST FOUNDATION NEEDS MIGRATION APPLY

The ranking formula backtest foundation is ready for local dry-run formula testing and migration review. Migration `0028__ranking_formula_backtest_foundation.sql` remains pending and was not applied, so live warehouse writes and live ranking validation patterns are deferred to a later authorized phase.

No production deploy occurred. No BigQuery rows were written. No materializations, Pigskin prompts, LLM-backed actions, Cloud Run Jobs, or Scheduler jobs were run.

## Repo State

Latest commit before this phase package:

- `aef3fde Add app login gate for public Cloud Run access`

The worktree also contains historical untracked validation reports from earlier phases. They were not staged for this phase.

## Files Changed

Contracts:

- `bigquery/contracts/ranking_formula_candidates.md`
- `bigquery/contracts/ranking_backtest_runs.md`
- `bigquery/contracts/ranking_backtest_results.md`
- `bigquery/contracts/ranking_backtest_candidate_summaries.md`
- `bigquery/contracts/ranking_formula_champions.md`
- `bigquery/contracts/ranking_formula_sets.md`

Migration:

- `bigquery/migrations/0028__ranking_formula_backtest_foundation.sql`

Validations:

- `bigquery/validations/201_ranking_formula_tables_exist.sql`
- `bigquery/validations/202_ranking_formula_candidates_required_json.sql`
- `bigquery/validations/203_ranking_formula_candidates_status_position_values.sql`
- `bigquery/validations/204_ranking_backtest_results_grain.sql`
- `bigquery/validations/205_ranking_backtest_results_score_ranges.sql`
- `bigquery/validations/206_ranking_formula_champions_active_grain.sql`
- `bigquery/validations/207_ranking_formula_sets_status_values.sql`
- `bigquery/validations/208_ranking_formula_candidates_blocked_metrics_guard.sql`
- `bigquery/validations/209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`

Code, tests, and docs:

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-formula-backtest-foundation.md`
- `docs/rebuild/validation/phase-31-1-ranking-formula-backtest-foundation-report.md`

## Table And Migration Status

Migration `0028` is additive and creates:

- `ranking_formula_candidates`
- `ranking_backtest_runs`
- `ranking_backtest_results`
- `ranking_backtest_candidate_summaries`
- `ranking_formula_champions`
- `ranking_formula_sets`

Migration status:

- `0028` discovered by migration dry-run
- `0028` listed as pending by ledger-aware check
- `0028` was not applied

## Formula JSON Validation Behavior

The validator requires:

- `version`
- `position`
- `score_expression`
- `features`
- `weights`
- `normalization`

Allowed positions:

- `QB`
- `RB`
- `WR`
- `TE`

First supported expression:

- `weighted_linear`

Rejected inputs:

- missing required fields
- unknown positions
- unknown features
- SQL-like strings
- table-name references such as `weekly_metrics`
- Python/code-like strings
- negative weights
- unused weights
- scores outside `0` to `100`

## Allowed Feature And Input Policy

Allowed input tables are curated or compatibility-safe:

- `player_week_advanced_metrics`
- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `pigskin_player_context_packet_current`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`

Blocked metrics are rejected unless a formula explicitly declares the matching source availability flag as true:

- `route_share`
- `yprr`
- `first_read_share`
- `true_pressure`
- `contact_yards`
- `alignment`

Blocked metrics are unavailable by default. They are not treated as zero.

## Dry-Run Runner Behavior

Module:

- `src.ranking_formula_backtests`

Dry-run behavior:

- default mode is non-mutating
- validates formulas
- enforces approved input table names
- builds candidate rows
- builds backtest run metadata
- builds candidate-level summary rows
- does not write to BigQuery
- does not expose anything to Pigskin chat

Explicit dry-runs:

- QB 2014: passed, `candidate_count=1`, `candidate_summary_count=1`, `write=false`
- RB 2014: passed, `candidate_count=1`, `candidate_summary_count=1`, `write=false`
- WR 2014: passed, `candidate_count=1`, `candidate_summary_count=1`, `write=false`
- TE 2014: passed, `candidate_count=1`, `candidate_summary_count=1`, `write=false`

## Gated Write Behavior

Write mode requires:

`ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true`

Unauthorized write smoke:

- Command: `.\venv\Scripts\python.exe -m src.ranking_formula_backtests --position QB --season-start 2014 --season-end 2014 --write`
- Result: failed closed before any client write
- Error: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE must be true to write ranking formula backtests`

The mocked authorized write path targets only ranking formula tables:

- `ranking_formula_candidates`
- `ranking_backtest_runs`
- `ranking_backtest_candidate_summaries`

No Streamlit request-time write path was added. No Pigskin chat/tool declaration exposes the ranking formula write gate or ranking formula tables.

## Candidate Summary Design

Added table:

- `ranking_backtest_candidate_summaries`

Grain:

- `backtest_run_id`
- `candidate_id`
- `position`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `target_name`

Metrics:

- `sample_size`
- `pairwise_win_rate`
- `top_n_hit_rate`
- `rank_correlation`
- `mean_absolute_error`
- `regret_score`
- `actual_points_captured_rate`
- `missing_input_rate`

Initial dry-run summary rows are shape-only rows with `sample_size=0`. Real summary metrics are deferred until a bounded backtest phase after migration apply.

## Checks Run

- `git status --short --untracked-files=all`: reviewed
- `git log -10 --oneline`: reviewed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m py_compile app.py`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`: passed, 19 tests
- `.\venv\Scripts\python.exe -m unittest discover tests`: passed, 635 tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run`: discovered migration `0028`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: `0028` pending
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovered 209 validation files

## Warnings

- Migration `0028` is pending and must be applied in a later authorized phase before live ranking formula table validations can pass.
- The runner is still a skeleton. It validates and plans formulas, but it does not compute real weekly rankings from warehouse rows yet.
- Candidate summary rows are shape-only in dry-run mode until real bounded backtests are implemented.
- Write mode is tested with a fake client only. Live writes require explicit authorization and migration apply.

## Recommended Next Phase

Phase 31.2 should apply migration `0028` only if authorized, verify the six empty objects, and run validations `201` through `209`. After that, seed initial QB/RB/WR/TE draft formulas or run a bounded dry-run formula backtest against real historical player/week inputs.
