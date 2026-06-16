# BigQuery Query Guardrails

Source of truth: `docs/CODEX_PROJECT_CONTEXT.md`.

This repo now has a shared query guardrail layer for Streamlit and legacy server-side SQL paths:

- Wrapper module: `src/bigquery_guardrails.py`
- Cached Streamlit helper: `app.py::execute_bq_cached`
- Curated chat schema: `src/pigskin_chat_schema.py`
- Pigskin context tools: `src/pigskin_context_tools.py`

## Goals

1. Put cost caps and labels on user-facing BigQuery jobs.
2. Log query cost and execution metadata in one place.
3. Keep a default-off legacy Pigskin SQL guardrail available for server-side compatibility.
4. Keep existing admin and Data Ops behavior working while the compatibility marts are built.

Pigskin chat now uses parameterized context tools instead of model-generated SQL. See [pigskin-context-tools.md](pigskin-context-tools.md).

## Default Query Wrapper

Use `query_to_dataframe()` or `run_bigquery_query()` from `src/bigquery_guardrails.py` for new UI and admin queries.

The wrapper applies:

- `maximum_bytes_billed`, defaulting to `BQ_MAX_BYTES_BILLED` or `2 GB`
- query labels:
  - `app=ai-vs-meatbags`
  - `component`
  - `environment`
  - `query_name`
- optional `query_parameters`
- optional `dry_run`
- optional `allow_large_query`
- structured logs for query name, component, bytes processed, cache hit, duration, dry run, and blocked status

Long-running ETL, materialization, migration, and Cloud Run Job paths may use `allow_large_query=True` or keep their existing specialized job configs until intentionally migrated.

## Legacy Pigskin Chat SQL Policy

Pigskin chat no longer receives a general SQL tool. The policy below documents the legacy containment layer that remains available only for server-side compatibility.

Pigskin should use marts and evidence packets instead of raw tables because raw tables do not carry the project contract. They may have mismatched player names, stale teams, unversioned projection inputs, missing freshness flags, and fields that are expensive to scan from the UI. Curated marts are where player identity, source freshness, scoring assumptions, and missing-data flags should be normalized before the writing AI sees the data.

Allowed tables are defined in `PIGSKIN_CHAT_ALLOWED_TABLES`:

- `analytics_player_weekly_truth`
- `analytics_fraud_watch`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_history`
- `analytics_game_environment`
- `analytics_player_qb_weekly`
- `analytics_player_qb_splits`
- `analytics_context_events`
- `analytics_external_context_search_results`

Blocked tables are defined in `PIGSKIN_CHAT_BLOCKED_TABLES`, including raw/source tables such as `weekly_metrics`, `play_by_play`, Sleeper source tables, `market_values`, `sleeper_players_current`, and `realtime_player_news`.

The legacy Pigskin SQL path validates:

1. the raw model SQL before repair
2. the repaired SQL before execution
3. the final SQL again inside `pigskin_query_to_dataframe()`

Rejected SQL is not executed. The rejection is logged with:

- timestamp
- component `pigskin_chat`
- query text
- extracted tables
- blocked tables
- non-allowed tables
- blocked flag

## Table Extraction

`extract_bigquery_table_references()` catches:

- backticked full table names such as `` `project.dataset.table` ``
- dataset table names such as `fantasy_football_brain.analytics_player_weekly_truth`
- bare known table names
- common `FROM` and `JOIN` references
- known blocked table names anywhere outside comments and string literals

The extractor ignores simple CTE names so allowed queries using `WITH latest AS (...) SELECT ... FROM latest` are not blocked only because of the CTE alias.

## Representative Runtime Wiring

Current representative call sites:

- `app.py::execute_bq_cached` routes normal cached Streamlit queries through `query_to_dataframe()`.
- Pigskin chat uses `execute_pigskin_context_tool()` from `src/pigskin_context_tools.py`.
- `app.py::get_persisted_last_success` routes a parameterized admin status query through `query_to_dataframe()`.

This is intentionally not a full query rewrite. Existing materialization, migration, and ingestion code should move to this wrapper only when the work is scoped and validated.

## Adding A New Allowed Mart

Do not add a raw/source table to the Pigskin allowlist.

To add a new context source safely:

1. Create or document the BigQuery table or compatibility view contract.
2. Add source freshness fields and missing-data flags.
3. Add validation queries for grain, duplicate rows, and required columns.
4. Add or extend a parameterized context tool in `src/pigskin_context_tools.py`.
5. Add tests proving user inputs are parameters and result limits are capped.
6. Keep raw/source tables out of the model-visible tool declarations.

## Validation

Guardrail behavior is covered by:

- `tests/test_bigquery_guardrails.py`
- `tests/test_pigskin_chat_schema.py`
- existing model run tests

Recommended checks:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_model_runs
.\venv\Scripts\python.exe -m unittest tests.test_bigquery_guardrails
.\venv\Scripts\python.exe -m py_compile app.py src\bigquery_guardrails.py src\pigskin_chat_schema.py tests\test_bigquery_guardrails.py
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
```
