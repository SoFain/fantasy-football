# Phase 19.5 Modern Data Restore Report

Date: 2026-06-16

Final status: NOT AUTHORIZED, PLAN ONLY

No ingestion writes were run. No source tables were changed. No analytics marts were rebuilt. No Fraud Watch packets or content briefs were created. No scraping, LLM calls, Firebase artifacts, Cloud Run Jobs, Scheduler jobs, or migrations were used.

## Authorization State

Required authorization:

- `ALLOW_MODERN_SOURCE_INGEST=true`

Observed state:

- `ALLOW_MODERN_SOURCE_INGEST=<unset>`

Because the authorization flag was not set, Phase 19.5 stopped after the non-mutating plan-only command.

## Target Season And Week Window

Requested default target:

- season: `2025`
- week start: `1`
- week end: `18`

Important limitation:

- The current nflreadpy pipeline path is season-bounded only.
- `--week-start` and `--week-end` are accepted in plan-only output for documentation, but live ingestion rejects week bounds before extraction or BigQuery writes.

## Plan-Only Command

Command run:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --week-start 1 --week-end 18 --ingest-only --plan-only
```

Result:

- exit status: `0`
- `will_extract=false`
- `will_write_bigquery=false`
- `will_materialize=false`
- `ingest_only=true`
- `write_disposition=WRITE_APPEND`
- `destructive_risk.raw_load_truncate=false`
- `destructive_risk.derived_create_or_replace=false`
- `week_bound_supported=false`
- `requested_week_window.week_start=1`
- `requested_week_window.week_end=18`

Live-run behavior shown by the plan:

- `will_extract=true`
- `will_write_bigquery=true`
- `will_materialize=false`
- `will_call_llm=false`
- `will_scrape=false`
- `will_trigger_cloud_run_jobs=false`

## Planned Source Tables

The plan would load these source tables if later authorized:

- `play_by_play`
- `weekly_metrics`
- `team_descriptions`
- `draft_picks`
- `player_rosters`
- `player_contracts`
- `ngs_passing`
- `ngs_rushing`
- `ngs_receiving`
- `ftn_charting`
- `weekly_snap_counts`
- `injury_reports`
- `depth_charts`

Recommended restore command from plan, not run:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only
```

## Source Row Counts

No live BigQuery row-count checks were run in Phase 19.5 because the authorization gate required plan-only behavior.

Most recent documented source coverage from Phase 18.5:

| Table | 2025/2026 rows |
|---|---:|
| `play_by_play` | 0 |
| `weekly_metrics` | 0 |
| `analytics_player_weekly_truth` | 0 |
| `analytics_fraud_watch` | 0 |

After Phase 19.5:

| Table | Change |
|---|---|
| `play_by_play` | no write attempted |
| `weekly_metrics` | no write attempted |
| `analytics_player_weekly_truth` | no materialization attempted |
| `analytics_player_fantasy_points_by_profile` | no materialization attempted |
| `analytics_fraud_watch` | no materialization attempted |

## Analytics Materialization

Not run.

Blocked by:

- `ALLOW_MODERN_SOURCE_INGEST` was not set.
- Source restore was not authorized.
- `analytics_player_weekly_truth` still depends on missing modern `play_by_play` and `weekly_metrics` source rows.

The following commands were not run:

```powershell
.\venv\Scripts\python.exe -m src.materialize --only player-weekly-truth
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --season 2025
.\venv\Scripts\python.exe -m src.materialize --only fraud-watch
```

## Fraud Watch Packets

Not run.

Reason:

- Current-season `analytics_fraud_watch` source rows are still not restored or rebuilt.
- Historical Fraud Watch rows were not used as current-season content.

Packet counts:

- before: not queried in this phase
- after: no write attempted

## Content Brief

No `fraud_watch_show` content brief was created.

Content brief IDs:

- none

Current-season content suitability:

- blocked

Reason:

- Current-season Fraud Watch packets must be built only from real 2025 source rows.
- Those rows were not restored in this phase.

## Validations

Not run in Phase 19.5 because the explicit authorization gate limited the run to plan-only behavior.

The following validations remain the next step after authorized ingest and materialization:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
```

## Blockers

1. `ALLOW_MODERN_SOURCE_INGEST=true` was not set.
2. Week-bounded live ingestion is not supported by the current nflreadpy pipeline path.
3. Modern 2025/2026 source rows remain unrestored according to the last documented coverage.
4. Current-season Fraud Watch remains blocked until modern `play_by_play`, `weekly_metrics`, and derived truth rows exist.

## Next Authorized Step

Set authorization only when ready to write source data:

```powershell
$env:ALLOW_MODERN_SOURCE_INGEST = "true"
```

Then run a bounded season restore without week flags:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only
```

After source coverage is verified, run downstream materialization and validations separately.

## Decision

`NOT AUTHORIZED, PLAN ONLY`

Phase 19.5 proved the non-mutating plan for 2025 source restore but did not write data. Current-season Fraud Watch remains unsuitable for production content until real 2025 source rows are restored and marts are rebuilt.
