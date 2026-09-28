# Phase 31.2 Ranking Backtest Migration Apply Report

## Final Decision

RANKING BACKTEST MIGRATION APPLIED

Migration `0028__ranking_formula_backtest_foundation.sql` was applied successfully. The six ranking formula backtest tables exist, required fields are present, and all new tables remain empty after migration and dry-run checks.

No production deploy occurred. No Pigskin prompts, LLM-backed actions, materializations, Cloud Run Jobs, Scheduler jobs, live Sleeper API calls, or formula/backtest row writes were run.

## Git State

Latest commit reviewed:

- `fe750c4 Add ranking formula backtest foundation`

Untracked historical validation backlog remains present and was not staged or modified by this phase. No unexpected staged files were present.

## Migration Apply Status

Pre-apply migration checks:

- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: pending `0028` only
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run`: discovered migrations `0001` through `0028`

Apply command:

- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --apply`

Result:

- Applied `0028: ranking formula backtest foundation`
- Applied migration count: `1`
- Post-apply pending check: no pending migrations

## Pre-Apply Checks

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`: passed, 19 tests
- `.\venv\Scripts\python.exe -m unittest discover tests`: passed, 635 tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovered 209 validation files

## Created Object Verification

Read-only BigQuery verification confirmed each table exists, required fields are present, and row counts are zero.

| Table | Exists | Missing required fields | Row count |
| --- | --- | --- | --- |
| `ranking_formula_candidates` | true | none | 0 |
| `ranking_backtest_runs` | true | none | 0 |
| `ranking_backtest_results` | true | none | 0 |
| `ranking_backtest_candidate_summaries` | true | none | 0 |
| `ranking_formula_champions` | true | none | 0 |
| `ranking_formula_sets` | true | none | 0 |

## Validation Results

Focused ranking formula validations only:

- `201_ranking_formula_tables_exist.sql`: PASS, `table_count=6`
- `202_ranking_formula_candidates_required_json.sql`: PASS, `rows_missing_required_json=0`
- `203_ranking_formula_candidates_status_position_values.sql`: PASS, `invalid_candidate_rows=0`
- `204_ranking_backtest_results_grain.sql`: PASS, `duplicate_result_rows=0`
- `205_ranking_backtest_results_score_ranges.sql`: PASS, `invalid_score_rows=0`
- `206_ranking_formula_champions_active_grain.sql`: PASS, `duplicate_active_champions=0`
- `207_ranking_formula_sets_status_values.sql`: PASS, `invalid_formula_set_rows=0`
- `208_ranking_formula_candidates_blocked_metrics_guard.sql`: PASS, `blocked_metric_without_source_rows=0`
- `209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`: PASS, `duplicate_summary_rows=0`

## Non-Mutating Dry-Run Results

Commands:

- `.\venv\Scripts\python.exe -m src.ranking_formula_backtests --position QB --season-start 2014 --season-end 2014 --dry-run`
- `.\venv\Scripts\python.exe -m src.ranking_formula_backtests --position RB --season-start 2014 --season-end 2014 --dry-run`
- `.\venv\Scripts\python.exe -m src.ranking_formula_backtests --position WR --season-start 2014 --season-end 2014 --dry-run`
- `.\venv\Scripts\python.exe -m src.ranking_formula_backtests --position TE --season-start 2014 --season-end 2014 --dry-run`

Results:

- QB: `write=false`, `candidate_count=1`, `candidate_summary_count=1`
- RB: `write=false`, `candidate_count=1`, `candidate_summary_count=1`
- WR: `write=false`, `candidate_count=1`, `candidate_summary_count=1`
- TE: `write=false`, `candidate_count=1`, `candidate_summary_count=1`

Post-dry-run table counts remained `0` for all six ranking formula tables.

## Write Gate Closed Confirmation

Unauthorized write smoke:

- Command: `.\venv\Scripts\python.exe -m src.ranking_formula_backtests --position QB --season-start 2014 --season-end 2014 --write`
- Result: failed closed before any client write
- Error: `ALLOW_RANKING_FORMULA_BACKTEST_WRITE must be true to write ranking formula backtests`

All ranking formula table row counts remained `0` afterward.

## Pigskin Exposure Confirmation

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

- no matches in Pigskin-visible app/tool files
- no arbitrary SQL exposure added
- no Streamlit request-time formula/backtest write path found

## Remaining Warnings

- Tables are intentionally empty. Formula candidate seeding is deferred.
- The dry-run runner still produces planned shapes only. Real historical scoring work starts in a later bounded phase.
- Live writes remain disabled unless `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` is explicitly set in a future phase.

## Recommended Next Phase

Phase 31.3 should either seed initial QB/RB/WR/TE formula candidates or run a bounded real-data dry-run formula backtest. Keep Pigskin chat out of the write path.
