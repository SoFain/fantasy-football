# Modern Source Data Restore

Purpose: restore missing modern nflreadpy source rows in a bounded, reviewable way before downstream analytics materialization.

## Safety Rules

- Use `.\venv\Scripts\python.exe`.
- Do not use system Python.
- Do not scrape.
- Do not call LLMs.
- Do not create Firebase artifacts.
- Do not run unbounded ingestion.
- Do not use `WRITE_TRUNCATE` unless an operator explicitly authorizes a full refresh with `--allow-full-refresh`.
- Do not run downstream analytics materialization as part of source restore.

## Current Pipeline Bounds

The current nflreadpy pipeline is season-bounded only.

Supported:

- `--seasons`
- `--plan-only`
- `--ingest-only`
- `--write-disposition WRITE_APPEND`
- `--allow-full-refresh` for explicitly authorized broad or truncating runs

Reserved but not supported for live ingestion:

- `--week-start`
- `--week-end`

If week bounds are supplied to a live run, the pipeline exits before extraction or BigQuery writes.

## Non-Mutating Plan

Use plan-only first:

```powershell
.\venv\Scripts\python.exe -m src.pipeline `
  --seasons 2025 `
  --write-disposition WRITE_APPEND `
  --dataset fantasy_football_brain `
  --ingest-only `
  --plan-only
```

Expected plan behavior:

- `will_extract=false`
- `will_write_bigquery=false`
- `will_materialize=false`
- `live_run_behavior.will_extract=true`
- `live_run_behavior.will_write_bigquery=true`
- `live_run_behavior.will_materialize=false`
- `destructive_risk.raw_load_truncate=false`
- `destructive_risk.derived_create_or_replace=false`

## Ingest-Only Restore Command

Run only after operator authorization:

```powershell
.\venv\Scripts\python.exe -m src.pipeline `
  --seasons 2025 `
  --write-disposition WRITE_APPEND `
  --dataset fantasy_football_brain `
  --ingest-only
```

This path extracts, transforms, and loads source tables, then stops before `materialize_all()`.

## Tables Loaded

The ingest path loads these source tables:

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

Partitioning remains the existing `src/load.py` behavior: range partitioning on `season` where supported.

## Full Refresh Guard

These live commands are rejected by default:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --ingest-only
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_TRUNCATE --ingest-only
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --week-start 1 --week-end 1 --ingest-only
```

`--allow-full-refresh` is required for a broad default season window or `WRITE_TRUNCATE`. It should not be used for modern source-data restore unless the operator intentionally wants a full refresh.

## Downstream Materialization

After source restore, run validations and row-count checks before materializing:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Materialize analytics separately only after source coverage is confirmed. This keeps source restoration separate from `CREATE OR REPLACE` analytics work.
