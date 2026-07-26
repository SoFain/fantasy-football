# Phase 32.19 Depth, Injury, Sleeper Context Report

Final decision: SLEEPER LIVE CONTEXT READY WITH WARNINGS

## Scope

Phase 32.19 remediated source context for ranking research only.

No production deploy occurred. No live rankings were regenerated. No champion formulas were activated. No Pigskin chat prompt was submitted. No Gemini or LLM-backed ranking generation was run.

## Files Changed

- `src/nflverse_backfill.py`
- `src/nflverse_backfill_plan.py`
- `src/sleeper_player_snapshot.py`
- `src/materialize_role_context.py`
- `tests/test_nflverse_backfill_executor.py`
- `tests/test_sleeper_player_snapshot.py`
- `tests/test_materialize_role_context.py`
- `bigquery/migrations/0036__sleeper_2026_player_context_snapshot.sql`
- `bigquery/migrations/0037__player_week_role_context_metrics.sql`
- `bigquery/validations/232_sleeper_2026_snapshot_objects.sql`
- `bigquery/validations/233_sleeper_player_context_current_grain.sql`
- `bigquery/validations/234_player_week_role_context_metrics_exists.sql`
- `bigquery/validations/235_player_week_role_context_metrics_ranges.sql`
- `docs/rebuild/ranking-opportunity-metrics-matrix.md`
- `docs/rebuild/ranking-algorithm-scorecard.md`

## Source Inspection

`nflreadpy` supports:

- `load_injuries(seasons)`
- `load_depth_charts(seasons)`
- `load_rosters_weekly(seasons)`
- `load_nextgen_stats(seasons, stat_type=...)`

Dispatcher support was added for injuries, depth charts, and NGS passing, rushing, and receiving.

## Historical Injury Backfill

Command:

```powershell
$env:ALLOW_NFLVERSE_HISTORICAL_BACKFILL='true'
.\venv\Scripts\python.exe -m src.nflverse_backfill --source-family injuries --season-start 2014 --season-end 2025 --write
Remove-Item Env:\ALLOW_NFLVERSE_HISTORICAL_BACKFILL
```

Result:

- fetched rows: 65,866
- prepared rows: 65,866
- written or merged rows: 65,866
- duplicate key groups after merge: 0
- table: `raw_nflverse_injuries`

Rows by season:

| Season | Rows |
|---:|---:|
| 2014 | 5,078 |
| 2015 | 5,232 |
| 2016 | 5,115 |
| 2017 | 5,104 |
| 2018 | 5,133 |
| 2019 | 5,392 |
| 2020 | 5,661 |
| 2021 | 5,587 |
| 2022 | 5,682 |
| 2023 | 5,599 |
| 2024 | 6,215 |
| 2025 | 6,068 |

The injury natural key was adjusted to retain practice-only rows where `report_status` is null:

- `season`
- `week`
- `team`
- `gsis_id`
- `report_status`
- `practice_status`
- `injury_notes`

Null-safe BigQuery merge behavior already exists in the raw backfill executor.

## Historical Depth Status

`nflreadpy.load_depth_charts([2025])` returned 554,215 current snapshot-style rows with columns such as:

- `dt`
- `team`
- `player_name`
- `gsis_id`
- `pos_abb`
- `pos_rank`

It did not return historical `season` or `week` fields. Prepare-only result:

- fetched rows: 554,215
- prepared rows: 0
- skipped rows: 554,215
- warning: missing `season`, `week`, and `position`

No depth rows were written. `raw_nflverse_depth_charts` remains at 0 rows.

Depth status: historical depth source blocked. Do not fabricate `depth_chart_role_score_3yr`.

## Sleeper 2026 Snapshot

Migration `0036__sleeper_2026_player_context_snapshot.sql` created:

- `raw_sleeper_players_snapshot`
- `sleeper_player_context_current`

Write command:

```powershell
$env:ALLOW_SLEEPER_2026_SNAPSHOT='true'
.\venv\Scripts\python.exe -m src.sleeper_player_snapshot --write
Remove-Item Env:\ALLOW_SLEEPER_2026_SNAPSHOT
```

Result:

- snapshot ID: `sleeper_players_20260705T175248Z`
- snapshot timestamp: `2026-07-05T17:52:48.174830+00:00`
- endpoint: `https://api.sleeper.app/v1/players/nfl`
- raw rows written: 12,200
- fantasy-position rows: 4,254
- latest context rows: 12,200
- distinct Sleeper player IDs in current context: 12,200

Warning: the first write attempt fetched the endpoint but failed before load because pandas inferred `fantasy_data_id` as `float64`. The write path was changed to `load_table_from_json`, and the corrected run wrote the snapshot. No rows were written by the failed attempt.

Tyreek Hill current context check:

- `gsis_id`: `00-0033040`
- `sleeper_current_team`: null
- `identity_current_team`: `MIA`
- `status`: `Active`
- `injury_status`: `Questionable`
- source freshness: `2026-07-05T17:52:48.174830Z`

Downstream current-roster display should prefer `sleeper_current_team` over `identity_current_team` when avoiding stale-team inference.

## Role Context Metrics

Migration `0037__player_week_role_context_metrics.sql` created:

- `player_week_role_context_metrics`

Materialization command:

```powershell
$env:ALLOW_ROLE_CONTEXT_MATERIALIZATION='true'
.\venv\Scripts\python.exe -m src.materialize_role_context --season-start 2014 --season-end 2025 --write
Remove-Item Env:\ALLOW_ROLE_CONTEXT_MATERIALIZATION
```

Result:

- role context run ID: `role_context_2014_2025_20260705T175612Z`
- grouped player-week rows: 65,864
- seasons: 12
- min injury risk score: 0.0
- max injury risk score: 100.0
- average injury risk score: 37.8235
- missing identity count: 32,405
- missing depth score count: 65,864

This table is a research context table only. It does not update `analytics_pigskin_rankings`, `ranking_formula_champions`, or live formula output.

## NGS Fallback

No NGS rows were backfilled in this phase.

Fallback readiness added:

- `ngs_passing` dispatches to `nflreadpy.load_nextgen_stats(seasons, stat_type="passing")`
- `ngs_rushing` dispatches to `nflreadpy.load_nextgen_stats(seasons, stat_type="rushing")`
- `ngs_receiving` dispatches to `nflreadpy.load_nextgen_stats(seasons, stat_type="receiving")`

NGS fallback should be handled in a separate bounded phase if the owner wants a direct NGS source sprint.

## Validations

Passed:

- `scripts/check_deployment_safety.py`
- `python -m compileall -q src scripts`
- `python -m unittest tests.test_nflverse_backfill_executor tests.test_materialize_role_context tests.test_sleeper_player_snapshot`
- `python -m unittest discover tests`
- `scripts/run_bigquery_migrations.py --list-pending`
- `scripts/run_bigquery_validations.py --dry-run`
- `scripts/run_bigquery_validations.py --run --pattern raw_nflverse`
- `scripts/run_bigquery_validations.py --run --pattern sleeper_2026`
- `scripts/run_bigquery_validations.py --run --pattern sleeper_player_context_current`
- `scripts/run_bigquery_validations.py --run --pattern player_week_role_context`

Validation results:

- full test suite: 779 tests passed
- pending migrations: none
- raw nflverse validations: 3 passed, 0 failed, one informational coverage warning
- Sleeper snapshot validations: 2 passed, 0 failed
- role context validations: 2 passed, 0 failed

Adjacent warning:

- `scripts/run_bigquery_validations.py --run --pattern sleeper` included older Sleeper Watch validations. New validations passed, but existing `compat_sleeper_watch_candidates` duplicate grain and identity-coverage checks still failed. Those are adjacent pre-existing checks, not failures in `raw_sleeper_players_snapshot` or `sleeper_player_context_current`.

## Gates

All temporary gates were removed after use:

- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`: unset
- `ALLOW_SLEEPER_2026_SNAPSHOT`: unset
- `ALLOW_ROLE_CONTEXT_MATERIALIZATION`: unset
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`: unset
- `ALLOW_TRADE_SCORE_MATERIALIZATION`: unset
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`: unset

## Production Status

Read-only production check:

- service: `nfl-studio-dashboard`
- latest ready revision: `nfl-studio-dashboard-00082-7bf`
- traffic: 100 percent to `nfl-studio-dashboard-00082-7bf`

No production deploy occurred.

## Remaining Warnings

- Historical depth chart context remains blocked because the available source does not provide historical `season/week`.
- `player_week_role_context_metrics` identity coverage needs remediation before treating injury risk as model-ready.
- `injury_risk_score_3yr` is not yet wired into a refreshed `player_week_ideal_stats` or `ranking_backtest_feature_mart` run.
- The corrected Sleeper snapshot write required a second endpoint call after the first local type-conversion failure.
- No NGS backfill was run.

## Recommended Next Phase

Phase 32.20 should be a bounded injury-context feature refresh:

1. Join `player_week_role_context_metrics` into `player_week_ideal_stats`.
2. Refresh `ranking_backtest_feature_mart` for a narrow validation slice.
3. Run SQL-native summaries only.
4. Keep depth flagged unavailable.
5. Do not activate champions or live rankings.
