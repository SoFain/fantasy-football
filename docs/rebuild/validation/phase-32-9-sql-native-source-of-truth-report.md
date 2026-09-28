# Phase 32.9 SQL-Native Source Of Truth Report

Final decision: **SQL NATIVE SOURCE OF TRUTH ACCEPTED WITH WARNINGS**

Phase 32.9 promotes the SQL-native tournament summary path to the preferred tournament evidence source. Python tournament evidence remains a historical reference. No deployment occurred, no live rankings were regenerated, and no champion formulas were activated.

## Files Changed

- `src/ranking_formula_backtests.py`
- `tests/test_ranking_formula_backtests.py`
- `docs/rebuild/ranking-algorithm-scorecard.md`
- `docs/rebuild/validation/phase-32-9-sql-native-source-of-truth-report.md`

Commit hash if committed: not committed in this phase.

## SQL-Native Path Boundary Confirmation

The official SQL-native path uses Python only for:

- SQL generation
- BigQuery job submission
- job status and metadata capture
- small fixture tests
- report and scorecard updates

Tests and source inspection confirmed the official SQL-native path does not call:

- `build_result_rows_for_candidates`
- `_pairwise_win_rate`
- `load_table_from_json`
- old Python full-tournament detail-row builders

The controlled write path uses BigQuery scripting:

- `CREATE TEMP TABLE sql_native_summary AS SELECT`
- bounded `DELETE` by `backtest_run_id`
- `INSERT ... SELECT` into summary tables

No Python player/candidate/week result-row construction is used.

## Metric Gap Closure

Implemented `overall_pairwise_draft_win_rate` in SQL.

Bounded method:

- compare only rows where either side is top 100 by predicted or actual overall rank
- require absolute predicted-score delta of at least 10
- compute pairwise ordering inside BigQuery
- avoid all-player all-player cross joins

Draft-utility metrics persisted in every written summary row:

- `ndcg_at_k`
- `value_captured_at_k`
- `elite_recall_at_k`
- `tier_accuracy`
- `bust_rate`
- `pick_band_regret`
- `overall_pairwise_draft_win_rate`
- `high_confidence_pairwise_win_rate`
- `value_over_replacement_captured_rate`

Missing metric counts after write:

| Metric | Missing rows |
|---|---:|
| `ndcg_at_k` | 0 |
| `value_captured_at_k` | 0 |
| `elite_recall_at_k` | 0 |
| `tier_accuracy` | 0 |
| `bust_rate` | 0 |
| `pick_band_regret` | 0 |
| `overall_pairwise_draft_win_rate` | 0 |
| `high_confidence_pairwise_win_rate` | 0 |
| `value_over_replacement_captured_rate` | 0 |

K policy remains:

- QB: 6, 12
- RB: 12, 24
- WR: 12, 24, 36
- TE: 3, 6, 12
- Overall: 24, 50, 100

## Dry-Run Results

Official summary write dry-run:

- version: `ranking_backtest_sql_native_v0_rolling_2017_2025`
- target seasons: 2017 through 2025
- profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`
- positions: QB, RB, WR, TE
- candidate count: 28
- expected run rows: 4
- expected summary rows: 112
- expected detail rows: 0
- write script references `ranking_backtest_results`: false
- write script references `ranking_formula_champions`: false

Read-only SQL-native tournament runtime before write:

- job ID: `3094fc75-b22c-409f-9341-5ca7ce6d4c42`
- summary rows: 112
- duration: 9.389s
- bytes processed: 54,356,741
- slot millis: 552,890

## Controlled Summary-Only Write Results

The write gate was set only inside the same PowerShell command process and removed afterward.

Authorization:

- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE=true` during the write
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE` unset after the write

Write result:

- job ID: `4d58afe0-9450-4fd9-82da-56df6731cb94`
- duration: 20.593s
- bytes processed: 54,643,889
- slot millis: 579,109
- run rows written: 4
- summary rows written: 112
- detail rows written: 0

Tables written:

- `ranking_backtest_runs`
- `ranking_backtest_candidate_summaries`

Tables not written:

- `ranking_backtest_results`
- `ranking_formula_champions`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_candidates`

## SQL-Native Evidence Summary

Persisted family aggregate:

| Family | Top-N | Captured points | VOR captured | Rank corr | High-confidence | Overall pairwise | NDCG@K | Tier accuracy | Bust rate | Missing |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| current Pigskin | 0.5411 | 0.7132 | 0.6007 | 0.5079 | 0.7385 | 0.7455 | 0.6578 | 0.4307 | 0.1592 | 0.0050 |
| simple projection | 0.5399 | 0.7121 | 0.5970 | 0.5145 | 0.7238 | 0.7262 | 0.6589 | 0.4353 | 0.1601 | 0.0000 |
| scarcity adjusted | 0.5386 | 0.7098 | 0.5908 | 0.5078 | 0.7202 | 0.7289 | 0.6463 | 0.4278 | 0.1553 | 0.0273 |
| value over replacement | 0.5233 | 0.6935 | 0.5658 | 0.4922 | 0.7126 | 0.7189 | 0.6360 | 0.4221 | 0.1683 | 0.0005 |
| equal weight | 0.5194 | 0.6868 | 0.5551 | 0.4853 | 0.7146 | 0.7214 | 0.6305 | 0.4183 | 0.1700 | 0.0018 |
| v1 improved | 0.5151 | 0.6834 | 0.5503 | 0.4714 | 0.7105 | 0.7180 | 0.6259 | 0.4146 | 0.1697 | 0.1357 |
| v2 trend balanced | 0.4059 | 0.5558 | 0.4033 | 0.2070 | 0.5559 | 0.5554 | 0.4840 | 0.3305 | 0.2936 | 0.1684 |

## SQL-Native vs Python Evidence

SQL-native evidence is accepted as preferred because it is:

- internally consistent
- much faster than the old Python tournament path
- computed from the reusable feature mart
- summary-first
- able to persist draft-utility metrics directly in `metric_json`

Python evidence remains a historical reference. Overlapping metrics are close enough to support the transition, while small VOR differences are expected because the SQL-native path now uses the standardized feature-mart VOR definition.

Decision: current Pigskin remains the baseline. Simple projection is close on rank correlation and NDCG, but it does not beat current Pigskin on captured points, VOR captured, high-confidence pairwise, or overall pairwise. No challenger becomes a champion from this phase.

## Scorecard Update

Updated `docs/rebuild/ranking-algorithm-scorecard.md` with:

- SQL-native source-of-truth decision
- controlled summary-only write stats
- persisted SQL-native family leaderboard
- overall pairwise gap closure
- no champion active confirmation
- next experiment guidance

## Checks Run

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Results:

- focused ranking tests: 70 passed
- full test discovery: 724 passed
- pending migrations: none
- ranking backtest validations: 3 passed, 0 failed
- ranking formula validations: 6 passed, 0 failed

## No-Change Safety

- No deployment occurred.
- No live rankings were regenerated.
- No active ranking rows were overwritten.
- `ranking_formula_champions` row count remains 0.
- Active `analytics_pigskin_rankings` counts remain 45 QB, 80 RB, 100 WR, 60 TE for each scoring profile.
- No Pigskin-facing file exposes formula/backtest tools.
- No Pigskin chat was called.
- No Gemini or LLM-backed ranking generation was called.
- No live Sleeper API call was made.
- `ALLOW_RANKING_FORMULA_BACKTEST_WRITE` is unset after execution.

## Remaining Warnings

- SQL-native summary is now preferred, but the older Python evidence is still useful as historical reference during owner review.
- Overall pairwise is bounded, not exhaustive. That is intentional to avoid full pairwise explosion.
- No champion formula was selected. This phase writes evidence only.
- Phase 32.8 and 32.9 changes remain uncommitted.

## Recommended Next Phase

Recommended: **Phase 32.10: Owner review of challenger algorithms**

Alternate next phases:

- Phase 32.10: BigQuery ML baseline prototype
- Phase 32.10: Formula comparison dashboard
- Phase 32.10: Generate formula-driven candidate rankings
