# Phase 19.4 Ingest-Only Mode Report

Date: 2026-06-16

Final status: BOUNDED INGEST-ONLY MODE READY

No ingestion writes were run. No materialization writes were run. No scraping, LLM calls, Firebase artifacts, migrations, Cloud Run Jobs, or Scheduler jobs were used.

## Purpose

Phase 18 confirmed modern 2025/2026 rows are missing from:

- `play_by_play`
- `weekly_metrics`
- `analytics_player_weekly_truth`
- `analytics_fraud_watch`

Phase 19.4 makes the restore path safer before writing data by adding an ingest-only mode that restores source tables without immediately running downstream analytics materialization.

## CLI Options

Command inspected:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --help
```

Supported options now include:

- `--seasons`
- `--write-disposition`
- `--dataset`
- `--plan-only`
- `--ingest-only`
- `--allow-full-refresh`
- `--week-start`
- `--week-end`

Current week support:

- `--week-start` and `--week-end` are reserved.
- Live week-bounded ingestion is rejected before extraction or BigQuery writes because the current nflreadpy path is season-bounded only.

## Safety Behavior

Implemented in `src/pipeline.py`:

- `--plan-only` remains non-mutating.
- `--ingest-only` extracts, transforms, and loads source tables, then skips `materialize_all()`.
- Live runs require explicit `--seasons` unless `--allow-full-refresh` is set.
- CLI default write disposition is now `WRITE_APPEND`.
- `WRITE_TRUNCATE` requires `--allow-full-refresh`.
- The plan documents raw source tables, derived tables, partition behavior, destructive risk, and live-run behavior.
- The pipeline does not call LLMs, scrape, or trigger Cloud Run Jobs.

Rejected live command example:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --ingest-only
```

Observed result:

```text
python.exe -m src.pipeline: error: Explicit --seasons is required unless --allow-full-refresh is set.
```

## Plan-Only Command

Example:

```powershell
.\venv\Scripts\python.exe -m src.pipeline `
  --seasons 2025 `
  --write-disposition WRITE_APPEND `
  --dataset fantasy_football_brain `
  --ingest-only `
  --plan-only
```

Observed plan properties:

- `will_extract=false`
- `will_write_bigquery=false`
- `will_materialize=false`
- `live_run_behavior.will_extract=true`
- `live_run_behavior.will_write_bigquery=true`
- `live_run_behavior.will_materialize=false`
- `live_run_behavior.will_call_llm=false`
- `live_run_behavior.will_scrape=false`
- `live_run_behavior.will_trigger_cloud_run_jobs=false`
- `destructive_risk.raw_load_truncate=false`
- `destructive_risk.derived_create_or_replace=false`

## Authorized Ingest-Only Command

Do not run without explicit operator authorization:

```powershell
.\venv\Scripts\python.exe -m src.pipeline `
  --seasons 2025 `
  --write-disposition WRITE_APPEND `
  --dataset fantasy_football_brain `
  --ingest-only
```

Expected behavior:

- source extraction from `nflreadpy`
- transformation with existing `src.transform` functions
- BigQuery source table loads through existing `src.load`
- no downstream analytics materialization
- no ranking/projection generation
- no content packet generation
- no LLM calls
- no Cloud Run Job triggers

## Source Tables

The ingest-only path uses the existing load list:

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

Partitioning remains existing behavior from `src/load.py`: range partitioning on `season` where supported.

## Tests

Commands run:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_pipeline_plan
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

- `tests.test_pipeline_plan`: pass, `8 tests`
- full test discovery: pass, `304 tests`
- `app.py` compile: pass
- `src` and `scripts` compile: pass

New test coverage:

- plan-only remains non-mutating
- ingest-only plan skips materialization
- unbounded live runs are rejected
- bounded season live runs are accepted
- week bounds are rejected until supported
- `WRITE_TRUNCATE` requires full-refresh authorization
- ingest-only run skips `materialize_all()`

## Documentation

Added:

- `docs/rebuild/modern-source-data-restore.md`

Updated:

- `docs/rebuild/validation/phase-18-5-modern-source-data-report.md`

## Remaining Limitations

- Week-bounded ingestion is not supported by the current nflreadpy pipeline.
- Source-table selection is not implemented. The ingest-only path restores the existing pipeline source table set.
- `WRITE_APPEND` can duplicate rows if the same season is restored repeatedly without a later dedupe or partition replacement strategy.
- Downstream analytics materialization remains a separate, explicit step and still uses `CREATE OR REPLACE` for derived tables.

## Warning

Do not run the ingest-only command without operator authorization. The safe next write path is bounded by explicit season and should use `WRITE_APPEND`.

## Decision

`BOUNDED INGEST-ONLY MODE READY`

The restore path now has a non-mutating plan, a bounded ingest-only live mode, rejection of unbounded live ingestion, explicit full-refresh gating for truncation, and tests covering the safety behavior.
