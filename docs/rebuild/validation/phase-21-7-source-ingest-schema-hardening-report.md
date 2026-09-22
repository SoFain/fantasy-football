# Phase 21.7 Source Ingest Schema Hardening Report

## Final Decision

`SOURCE INGEST HARDENING PASS`

The future source append path is now schema-aware for existing BigQuery tables. The known `play_by_play.lateral_sack_player_id` STRING versus INTEGER autodetect mismatch is covered by tests, and plan-only remains non-mutating.

No live ingestion, `WRITE_APPEND`, `WRITE_TRUNCATE`, BigQuery mutation, materialization, deploy, Cloud Run Job trigger, Scheduler creation, LLM call, scrape, or Firebase artifact creation was performed.

## Root Cause

Phase 20 local ingest attempts failed during append to `play_by_play` because:

- `src.load.load_df_to_partitioned_table` pinned only `season` in the load schema.
- The rest of the dataframe schema was delegated to BigQuery autodetect.
- The existing BigQuery table expects `play_by_play.lateral_sack_player_id` as `STRING`.
- BigQuery autodetect inferred the 2025 dataframe value as `INTEGER`.

Observed failure text:

```text
Provided Schema does not match Table fantasy-football-498121:fantasy_football_brain.play_by_play. Field lateral_sack_player_id has changed type from STRING to INTEGER
```

## Code Changes

### `src/load.py`

Added schema-aware append behavior:

- fetches the existing BigQuery table schema before `WRITE_APPEND`;
- builds a schema compatibility report before the load;
- coerces dataframe columns to target-compatible pandas dtypes where safe;
- coerces target `STRING` fields to pandas string dtype;
- coerces target numeric fields to numeric pandas dtypes only when safe;
- rejects non-coercible numeric mismatches before starting the load job;
- rejects new dataframe fields that are absent from the existing target schema;
- logs the compatibility report and fields coerced;
- disables autodetect when an existing schema is found and uses the target schema subset for the dataframe columns.

Added helper functions:

- `get_schema_aware_append_policy()`
- `is_player_id_column()`
- `build_schema_compatibility_report()`
- `coerce_dataframe_to_existing_schema()`
- `prepare_dataframe_for_bigquery_load()`

### `src/pipeline.py`

Added the append schema policy to plan-only output:

- `schema_aware_append.enabled_for_write_disposition`
- `schema_aware_append.known_player_id_string_fields`
- `schema_aware_append.wildcard_string_fields`
- `schema_aware_append.numeric_stats_policy`
- `schema_aware_append.table_schema_lookup`

Plan-only still reports `will_extract=false`, `will_write_bigquery=false`, and `will_materialize=false`.

### `tests/test_pipeline_plan.py`

Added focused schema hardening tests:

- `lateral_sack_player_id` integer-like source values are coerced to string when target schema is `STRING`;
- any `*_player_id` field with target `STRING` is coerced safely;
- numeric stat fields remain numeric when target schema is numeric;
- incompatible nonnumeric values for numeric target fields fail clearly;
- append load uses existing target schema and disables autodetect after coercion;
- existing truncate and unbounded-ingest guardrail tests remain in place.

## Supported Coercions

| BigQuery target type | Behavior |
| --- | --- |
| `STRING` | Coerces present dataframe column values to pandas string dtype, preserving nulls. Integer-like floats are rendered without `.0`. |
| `INTEGER` or `INT64` | Coerces numeric-compatible values to nullable integer dtype. Fails on nonnumeric values. |
| `FLOAT`, `FLOAT64`, `NUMERIC`, `BIGNUMERIC` | Coerces numeric-compatible values with `pd.to_numeric`. Fails on nonnumeric values. |
| `BOOLEAN` or `BOOL` | Coerces bool-like values only. Fails on unrecognized values. |

Numeric stat columns are not blindly stringified. They remain numeric when the existing BigQuery target schema is numeric.

## Player ID Fields Covered

Explicit fields:

- `player_id`
- `passer_player_id`
- `rusher_player_id`
- `receiver_player_id`
- `lateral_receiver_player_id`
- `lateral_rusher_player_id`
- `lateral_sack_player_id`
- `lateral_interception_player_id`
- `lateral_punt_returner_player_id`
- `lateral_kickoff_returner_player_id`
- `interception_player_id`
- `sack_player_id`
- `fantasy_player_id`

Wildcard policy:

- any `*_player_id` field is marked ID-like when the existing BigQuery schema says the target type is `STRING`.

## Pre-Load Schema Report

For append mode, the report includes:

- table name;
- write disposition;
- whether an existing schema was found;
- fields coerced;
- fields missing in the dataframe;
- new dataframe fields not in the target schema;
- incompatible fields;
- whether the load is safe to proceed.

If `safe_to_proceed=false`, the load fails before calling `load_table_from_dataframe`.

## Plan-Only Verification

Command run:

```powershell
.\venv\Scripts\python.exe -m src.pipeline --seasons 2025 --write-disposition WRITE_APPEND --dataset fantasy_football_brain --ingest-only --plan-only
```

Result:

- `will_extract=false`
- `will_write_bigquery=false`
- `will_materialize=false`
- schema-aware append policy is present
- known player ID string fields include `lateral_sack_player_id`
- no BigQuery mutation occurred

## Validation Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_pipeline_plan` | pass, 13 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 314 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, 149 validation files discovered |

## Remaining Unsupported Cases

- Schema evolution is intentionally not automatic. New dataframe columns not present in an existing append target are reported and block the load.
- Nested or repeated fields are not specially coerced.
- Date, datetime, and timestamp coercion is not expanded beyond existing pandas and BigQuery dataframe behavior.
- The current ingestion path remains season-bounded only. Week-bounded ingest remains explicitly rejected.
- This hardening does not dedupe already loaded rows. Duplicate control remains a separate operator decision before any future live append.

## Future 2025 or 2026 Retry Assessment

Future append-mode source ingest can be retried only after normal operator authorization and duplicate-control review. The specific `lateral_sack_player_id` mismatch is now handled before BigQuery load submission, and other target `STRING` player ID fields are protected by the same schema-aware path.

Recommended next live ingest preconditions:

1. Confirm target season and source-table scope.
2. Run plan-only first.
3. Confirm no duplicate-control blocker.
4. Use `WRITE_APPEND`.
5. Do not pass `WRITE_TRUNCATE` unless `--allow-full-refresh` is explicitly authorized.

## Safety Confirmation

| Safety item | Status |
| --- | --- |
| BigQuery data mutated | no |
| Live ingestion run | no |
| `WRITE_APPEND` live run | no |
| `WRITE_TRUNCATE` live run | no |
| Materialization run | no |
| Deployment run | no |
| Cloud Run Jobs triggered | no |
| Scheduler jobs created | no |
| LLM calls | no |
| Scraping | no |
| Firebase artifacts | none |
