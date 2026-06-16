# Phase 8-11 Final Green Gate Validation

Date: 2026-06-16

Final decision: GO WITH WARNINGS

## Scope

This was a validation-only pass.

- No new features were implemented.
- No migrations were applied.
- No Firebase artifacts were created.
- No arbitrary SQL path was reintroduced for Pigskin.
- No raw/source table access was exposed to Pigskin.

## Prior Blocker

The previous report, `docs/rebuild/validation/phase-8-11-validation-report.md`, recorded one blocker:

```text
tests.test_pigskin_chat_schema.PigskinChatSchemaTests.test_app_prompt_uses_context_tool_protocol
AssertionError: '### Context Tool Protocol ###' not found in app.py
```

The missing marker was:

```text
### Context Tool Protocol ###
```

## Marker And Prompt Status

Resolved.

Evidence:

- `app.py:2425` contains the exact marker `### Context Tool Protocol ###`.
- `app.py:2426` instructs Pigskin to use only provided parameterized context tools for warehouse-backed evidence.
- `app.py:2427` instructs Pigskin that it cannot write or execute SQL, request table access, invent table names, or describe unavailable warehouse tables as usable data.
- `app.py:2430` instructs Pigskin to say curated data is unavailable when a tool returns no rows.
- `app.py:2431` instructs Pigskin not to invent stats, injury claims, rankings, transactions, source freshness, or evidence.
- `app.py:2482` mandates curated context tools before player, ranking, trade, projection, roster, or causal claims.

## Pigskin Visible Tool Status

Resolved.

Allowed model-visible tools are defined in `src/pigskin_context_tools.py:43-156`:

- `get_player_context_packet`
- `search_players`
- `get_rankings_slice`
- `get_fraud_watch_candidates`
- `get_trade_player_history`
- `compare_players`
- `get_context_event_leads`

Blocked status:

- `execute_bigquery_sql` is not model-visible.
- No model-visible tool accepts raw SQL.
- No model-visible tool accepts an arbitrary table name.
- No model-visible tool accepts arbitrary WHERE clauses.
- Internal query helpers use fixed table names and BigQuery query parameters.
- `_table_id` validates trusted project, dataset, and internal table identifiers at `src/pigskin_context_tools.py:680-687`.
- `_query_records` uses `bigquery.QueryJobConfig` with scalar query parameters and a bytes cap at `src/pigskin_context_tools.py:617-631`.

## Raw Source Exposure Status

Resolved for Pigskin.

The rendered Pigskin schema contains no blocked raw/source table names from the validation list:

- `weekly_metrics`
- `play_by_play`
- `ngs_passing`
- `ngs_rushing`
- `ngs_receiving`
- `ftn_charting`
- `weekly_snap_counts`
- `injury_reports`
- `player_rosters`
- `player_contracts`
- `depth_charts`
- `market_values`
- raw Sleeper tables

Evidence:

- `src/pigskin_chat_schema.py:15-41` defines the blocked table set.
- `tests/test_pigskin_chat_schema.py:46-66` verifies blocked tables are absent from the rendered schema and the app prompt segment.
- `tests/test_pigskin_context_tools.py:31-43` verifies tool declarations do not expose SQL or raw tables and that `execute_bigquery_sql` is rejected.

Allowed Pigskin schema tables remain curated analytics/output tables:

- `analytics_player_weekly_truth`
- `analytics_fraud_watch`
- `analytics_pigskin_rankings`
- `analytics_pigskin_rankings_history`
- `analytics_game_environment`
- `analytics_player_qb_weekly`
- `analytics_player_qb_splits`
- `analytics_context_events`
- `analytics_external_context_search_results`

## Cloud Run And Firebase Status

Cloud Run remains the documented operating model.

Evidence:

- `docs/rebuild/cloud-run-operating-model.md` exists.
- `docs/rebuild/cloud-run-operating-model.md:5` states the platform stays on Cloud Run, BigQuery, Cloud Run Jobs, Cloud Scheduler, Cloud Storage, and Secret Manager, and that Firebase is not part of the target architecture unless explicitly reopened.
- A scoped file search found no Firebase artifacts such as `firebase.json`, `.firebaserc`, `firestore.rules`, `firestore.indexes.json`, or `functions/package.json`.

## Validation Results

Initial note:

- Bare `python` on this machine points to `C:\Python314` and does not have project dependencies such as `google-cloud-bigquery` and `pandas`.
- The validation was rerun with the repo venv interpreter: `.\venv\Scripts\python.exe`.

Results using `.\venv\Scripts\python.exe`:

```text
.\venv\Scripts\python.exe -m unittest tests.test_pigskin_chat_schema
Ran 5 tests
OK
```

```text
.\venv\Scripts\python.exe -m unittest tests.test_pigskin_context_tools
Ran 6 tests
OK
```

```text
.\venv\Scripts\python.exe -m unittest tests.test_bigquery_guardrails
Ran 7 tests
OK
```

```text
.\venv\Scripts\python.exe -m unittest discover tests
Ran 142 tests
OK
```

```text
.\venv\Scripts\python.exe -m py_compile app.py
OK
```

```text
.\venv\Scripts\python.exe -m compileall -q src scripts
OK
```

```text
.\venv\Scripts\python.exe scripts/run_bigquery_migrations.py --dry-run
OK
Pending migrations listed: 0001 through 0019
No migrations were applied.
```

```text
.\venv\Scripts\python.exe scripts/run_bigquery_migrations.py --list-pending
OK
No pending migrations.
```

## Remaining Warnings

1. Use the repo venv or activate it before validation:

```powershell
.\venv\Scripts\python.exe -m unittest discover tests
```

Bare `python` is not the project environment on this machine.

2. Existing Streamlit UI query debt remains outside this blocker. This validation confirmed Pigskin containment and did not make runtime changes, so no new direct UI raw/source reads were introduced here.

## Gate Decision

GO WITH WARNINGS

The Phase 8-11 NO-GO blocker is resolved. Pigskin now has the required `### Context Tool Protocol ###` marker, arbitrary SQL remains removed from the model-visible tool surface, raw/source tables are not exposed to Pigskin, tests pass under the repo venv, compile checks pass, and migration checks pass without applying migrations.
