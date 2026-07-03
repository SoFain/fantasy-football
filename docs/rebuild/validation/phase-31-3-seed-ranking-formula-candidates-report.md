# Phase 31.3 Seed Ranking Formula Candidates Report

## Final Decision

RANKING FORMULA CANDIDATES SEEDED WITH WARNINGS

Initial draft QB/RB/WR/TE ranking formula candidates were seeded for backtesting only. One draft formula set was also seeded. No champion formulas were selected, and no backtest run/result/summary rows were written.

No production deploy occurred. No Pigskin prompts, LLM-backed actions, materializations, live Sleeper API calls, Cloud Run Jobs, or Scheduler jobs were run.

## Git State

Latest commit before this phase:

- `fe750c4 Add ranking formula backtest foundation`

Untracked historical validation backlog remains present. It was not staged for this phase.

## Files Changed

- `scripts/seed_ranking_formula_candidates.py`
- `tests/test_seed_ranking_formula_candidates.py`
- `src/ranking_formula_backtests.py`
- `docs/rebuild/validation/phase-31-3-seed-ranking-formula-candidates-report.md`

## Validator And Feature Inventory

Allowed positions:

- `QB`
- `RB`
- `WR`
- `TE`

Allowed input tables:

- `player_week_advanced_metrics`
- `player_recent_advanced_metrics_current`
- `player_role_usage_metrics_current`
- `pigskin_player_context_packet_current`
- `analytics_player_weekly_truth`
- `analytics_player_fantasy_points_by_profile`

Blocked metrics:

- `alignment`
- `contact_yards`
- `first_read_share`
- `route_share`
- `true_pressure`
- `yprr`

Seed formulas use only allowlisted features and do not include blocked metrics, SQL strings, raw table names, or code-like expressions.

## Seeded Candidate Summary

Seeded candidate rows:

| Position | Candidate count | Candidate IDs |
| --- | ---: | --- |
| QB | 3 | `ranking_formula_qb_balanced_v0_2026_001`, `ranking_formula_qb_volume_v0_2026_001`, `ranking_formula_qb_efficiency_v0_2026_001` |
| RB | 3 | `ranking_formula_rb_balanced_v0_2026_001`, `ranking_formula_rb_volume_v0_2026_001`, `ranking_formula_rb_efficiency_v0_2026_001` |
| WR | 3 | `ranking_formula_wr_balanced_v0_2026_001`, `ranking_formula_wr_volume_v0_2026_001`, `ranking_formula_wr_efficiency_v0_2026_001` |
| TE | 3 | `ranking_formula_te_balanced_v0_2026_001`, `ranking_formula_te_volume_v0_2026_001`, `ranking_formula_te_efficiency_v0_2026_001` |

All 12 candidate rows have:

- `formula_version=ranking_formula_v0_2026_001`
- `status=draft`
- `score_expression=weighted_linear`
- valid `formula_json`
- valid `feature_allowlist_json`
- valid `target_definition_json`
- valid `source_requirements_json`

## Formula Set Summary

Seeded formula set:

- `formula_set_id=ranking_formula_set_v0_2026_001`
- `formula_set_name=Initial 2026 Draft Ranking Formula Set`
- `formula_set_version=formula_set_v0_2026_001`
- `status=draft`

Baseline references:

- QB: `ranking_formula_qb_balanced_v0_2026_001`
- RB: `ranking_formula_rb_balanced_v0_2026_001`
- WR: `ranking_formula_wr_balanced_v0_2026_001`
- TE: `ranking_formula_te_balanced_v0_2026_001`

This is a draft grouping only, not a champion selection.

## Dry-Run Seed Result

Command:

- `.\venv\Scripts\python.exe scripts\seed_ranking_formula_candidates.py`

Result:

- `dry_run=true`
- `wrote=false`
- candidate payload count: `12`
- formula set payload count: `1`
- target tables: `ranking_formula_candidates`, `ranking_formula_sets`
- non-target tables declared: `ranking_backtest_runs`, `ranking_backtest_results`, `ranking_backtest_candidate_summaries`, `ranking_formula_champions`

Pre-apply row counts remained:

- `ranking_formula_candidates`: `0`
- `ranking_formula_sets`: `0`
- `ranking_backtest_runs`: `0`
- `ranking_backtest_results`: `0`
- `ranking_backtest_candidate_summaries`: `0`
- `ranking_formula_champions`: `0`

## Apply Seed Result

Write gate handling:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` was set only inside the apply command process.
- The gate was removed immediately afterward.
- Post-apply check confirmed the environment variable was unset.

Apply command:

- `.\venv\Scripts\python.exe scripts\seed_ranking_formula_candidates.py --apply`

Result:

- `wrote=true`
- candidate rows written/upserted: `12`
- formula set rows written/upserted: `1`
- target tables only: `ranking_formula_candidates`, `ranking_formula_sets`

## Row Counts After Seeding

Seeded tables:

- `ranking_formula_candidates`: `12`
- `ranking_formula_sets`: `1`

Non-target tables:

- `ranking_backtest_runs`: `0`
- `ranking_backtest_results`: `0`
- `ranking_backtest_candidate_summaries`: `0`
- `ranking_formula_champions`: `0`

Candidate count by position:

- QB draft rows: `3`
- RB draft rows: `3`
- WR draft rows: `3`
- TE draft rows: `3`

Formula JSON blocked metric check:

- invalid candidate count: `0`

## Focused Validation Results

- `201_ranking_formula_tables_exist.sql`: PASS, `table_count=6`
- `202_ranking_formula_candidates_required_json.sql`: PASS, `rows_missing_required_json=0`
- `203_ranking_formula_candidates_status_position_values.sql`: PASS, `invalid_candidate_rows=0`
- `204_ranking_backtest_results_grain.sql`: PASS, `duplicate_result_rows=0`
- `205_ranking_backtest_results_score_ranges.sql`: PASS, `invalid_score_rows=0`
- `206_ranking_formula_champions_active_grain.sql`: PASS, `duplicate_active_champions=0`
- `207_ranking_formula_sets_status_values.sql`: PASS, `invalid_formula_set_rows=0`
- `208_ranking_formula_candidates_blocked_metrics_guard.sql`: PASS, `blocked_metric_without_source_rows=0`
- `209_ranking_backtest_candidate_summaries_grain_and_ranges.sql`: PASS, `duplicate_summary_rows=0`

## Checks Run

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`: passed
- `.\venv\Scripts\python.exe -m compileall -q src scripts`: passed
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`: passed, 19 tests
- `.\venv\Scripts\python.exe -m unittest tests.test_seed_ranking_formula_candidates`: passed, 6 tests
- `.\venv\Scripts\python.exe -m unittest discover tests`: passed, 641 tests
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`: no pending migrations
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`: discovered 209 validation files

## Non-Mutating Runner Result

The current runner does not yet load seeded candidates from BigQuery. Existing per-position dry-run skeleton commands were run for QB, RB, WR, and TE:

- each returned `write=false`
- each returned `candidate_count=1`
- each returned `candidate_summary_count=1`

Seeded-candidate loading is the next implementation gap before real formula comparison.

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

- no Pigskin-visible formula read/write tools exposed
- no arbitrary SQL path added
- no Streamlit request-time formula/backtest write path added

## Remaining Warnings

- The seeded candidates are draft formulas only. They are not production rankings.
- No champion formulas were selected.
- The runner cannot yet load seeded candidates from BigQuery.
- Backtest result and candidate summary tables remain empty by design.

## Recommended Next Phase

Phase 31.4 should implement seeded-candidate runner loading and run a bounded real-data dry-run formula backtest. Keep writes disabled unless a later prompt explicitly authorizes backtest result or summary materialization.
