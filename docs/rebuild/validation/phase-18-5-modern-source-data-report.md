# Phase 18.5 Modern Source Data Report

Date: 2026-06-16

Final status: PARTIAL SOURCE COVERAGE, CURRENT-SEASON FRAUD WATCH BLOCKED

No ingestion writes were run in this phase. No materialization writes were run. No scraping, LLM calls, Firebase artifacts, migrations, or Cloud Run Jobs were used.

## Purpose

Restore or ingest modern 2025/2026 source rows needed for current-season projections, truth tables, and Fraud Watch materialization.

Phase 17.7 showed current-season Fraud Watch was blocked because these warehouse tables had no 2025 or 2026 rows:

- `play_by_play`
- `weekly_metrics`
- `analytics_player_weekly_truth`
- `analytics_fraud_watch`

## Target Window

Default target used for planning:

- `season=2025`
- weeks available from source or warehouse
- scoring profile context: `ppr`

No NFL schedule or current week was inferred. The target is based on the existing warehouse having 2025 downstream rows in `analytics_player_fantasy_points_by_profile`, `projection_rankings_current`, and `compat_sleeper_watch_candidates`.

## Current Source Coverage

Bounded BigQuery coverage query for `season IN (2025, 2026)`:

```text
play_by_play:
  metadata_rows: 143402
  modern_rows: 0

weekly_metrics:
  metadata_rows: 52787
  modern_rows: 0

analytics_player_weekly_truth:
  metadata_rows: 50635
  modern_rows: 0

analytics_fraud_watch:
  metadata_rows: 3638
  modern_rows: 0

analytics_player_fantasy_points_by_profile:
  metadata_rows: 55617
  2025 weeks 1-18 populated

projection_rankings_current:
  metadata_rows: 50
  2025 week 1 rows: 50

compat_sleeper_watch_candidates:
  metadata_rows: 0
  query returned 2025 weeks 1-18 rows
```

Interpretation:

- Current-season raw source coverage is missing for 2025 and 2026.
- Some downstream 2025 tables exist, but they are not enough to rebuild `analytics_player_weekly_truth` or current-season Fraud Watch.
- `compat_sleeper_watch_candidates` behaves like a view or zero-byte object in table metadata, but the query path returned 2025 rows.

## Existing Ingestion Path

Inspected files:

- `src/pipeline.py`
- `src/extract.py`
- `src/load.py`
- `src/materialize.py`
- `src/materialize_fantasy_points.py`

Existing source library:

- `nflreadpy`

## Phase 19.4 Addendum

Phase 19.4 added a safer bounded ingest-only restore mode before any modern source-data writes were run.

New CLI controls:

- `--ingest-only`
- `--allow-full-refresh`
- `--week-start`
- `--week-end`

Current behavior:

- `--plan-only` remains non-mutating.
- Live runs now require explicit `--seasons` unless `--allow-full-refresh` is set.
- `WRITE_APPEND` is the live CLI default.
- `WRITE_TRUNCATE` requires `--allow-full-refresh`.
- `--ingest-only` extracts, transforms, and loads source tables, then skips `materialize_all()`.
- Week-bounded ingestion is still not supported by the nflreadpy path. Supplying `--week-start` or `--week-end` to a live run exits before extraction or BigQuery writes.

Plan-only command:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only --plan-only
```

Authorized ingest-only command, not run in Phase 19.4:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only
```

Documentation:

- `docs/rebuild/modern-source-data-restore.md`

Existing pipeline load tables:

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

Partition behavior:

- `src/load.py` uses BigQuery range partitioning on `season` where supported.

Important limitation:

- `src.pipeline` is season-bounded, not week-bounded.
- The pipeline immediately calls `materialize_all()` after source loads.
- `src.materialize.py` uses `CREATE OR REPLACE TABLE` for derived analytics tables including `analytics_player_weekly_truth` and `analytics_fraud_watch`.

## Plan-Only Mode Added

Because the pipeline did not have a dry-run or plan mode, Phase 18.5 added a non-mutating plan mode:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --plan-only
```

Result:

```text
source_library: nflreadpy
seasons: [2025]
dataset: fantasy_football_brain
write_disposition: WRITE_APPEND
bounded_by: season
week_bound_supported: false
will_extract: false
will_write_bigquery: false
will_materialize: false
destructive_risk.raw_load_truncate: false
destructive_risk.derived_create_or_replace: true
```

Recommended restore command, not run:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain
```

Reason it was not run:

- It would be bounded by season, not week.
- It would append source rows, which avoids truncation but may duplicate season rows if rerun without dedupe.
- It would immediately run derived materialization that uses `CREATE OR REPLACE TABLE`.
- Operator approval is needed before running a write path with those derived-table replacement semantics.

## Materialization Dry-Runs

Player weekly truth dry-run:

```powershell
.\venv\Scripts\python.exe -m src.materialize --project fantasy-football-498121 --dataset fantasy_football_brain --only player-weekly-truth --dry-run
```

Result:

```text
Dry run passed. Estimated bytes processed: 63684247
```

Fantasy points dry-run for 2025:

```powershell
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --project fantasy-football-498121 --dataset fantasy_football_brain --season 2025 --dry-run
```

Result:

```text
Fetched 0 rows from analytics_player_weekly_truth
Built 0 fantasy point rows from analytics_player_weekly_truth for profiles half_ppr,ppr,standard
analytics_player_fantasy_points_by_profile rows built: 0
```

Interpretation:

- SQL shape is valid.
- 2025 fantasy-point rebuild from truth data is blocked because `analytics_player_weekly_truth` has no 2025 rows.

## Validations

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern market
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern content_brief
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern backtest
```

Results:

```text
market: 9 passed, 0 failed
content_brief: 11 passed, 0 failed
backtest: 11 passed, 0 failed
```

Backtest returned existing informational dashboard rows:

```text
latest_backtest_runs: 1
backtest_summary_rows: 6
backtest_run_count: 1
```

These are review warnings, not failures.

No dedicated raw modern-source coverage validation currently exists. Source coverage was verified with bounded BigQuery reads in this report.

## Tests and Compile

Commands run:

```powershell
.\venv\Scripts\python.exe -m py_compile src/pipeline.py
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe -m unittest tests.test_pipeline_plan
.\venv\Scripts\python.exe -m unittest discover tests
```

Results:

```text
tests.test_pipeline_plan: 2 passed
full test suite: 298 passed
app.py compile: pass
src and scripts compile: pass
```

## After Counts

No ingestion or materialization writes were run, so after counts remain unchanged:

```text
play_by_play 2025/2026: 0 rows
weekly_metrics 2025/2026: 0 rows
analytics_player_weekly_truth 2025/2026: 0 rows
analytics_fraud_watch 2025/2026: 0 rows
```

## Current-Season Readiness

Status: BLOCKED

Modern source coverage is partial:

- downstream 2025 fantasy points, rankings, and sleeper watch rows exist
- raw 2025/2026 `play_by_play` and `weekly_metrics` rows are missing
- 2025/2026 `analytics_player_weekly_truth` rows are missing
- 2025/2026 `analytics_fraud_watch` rows are missing

Current-season Fraud Watch is not ready for production content.

## Recommended Next Step

Before running writes, choose one of these paths:

1. Split `src.pipeline` into explicit ingest-only and materialize-only modes, then run:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only
```

2. Authorize the existing all-in pipeline with `WRITE_APPEND`, accepting that derived analytics tables will be recreated:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain
```

Preferred path:

- Add ingest-only mode first.
- Re-check 2025 source row counts.
- Run bounded derived materialization dry-runs.
- Then materialize `analytics_player_weekly_truth`, `analytics_fraud_watch`, and current-season Fraud Watch packets.
