# Phase 25.9 Data Ops Local Subprocess Hardening Report

Final decision: DATA OPS LOCAL SUBPROCESS HARDENING READY WITH WARNINGS

Date: 2026-06-26

## Scope

Phase 25.9 added default-off gates for local subprocess, ingestion, external refresh, BigQuery-writing, and LLM-backed controls that were visible in production during Phase 25.8 monitoring.

No production deploy occurred. No staging deploy occurred. No production flags were changed. No Cloud Run Jobs, Scheduler jobs, ingestion, materialization, LLM actions, Pigskin prompts, scraping, or Firebase artifact creation occurred.

Authorization gate check:

- `ALLOW_LIMITED_PRODUCTION_DEPLOY` was unset.
- `ALLOW_TRADE_SCORE_MATERIALIZATION` was unset.
- `ALLOW_PROJECTION_CONTEXT_REFRESH` was unset.
- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` was unset.

## Files Changed

| File | Change |
| --- | --- |
| `app.py` | Added local admin gate helpers, Data Ops gate status panel, disabled mutating Data Ops buttons by default, and gated the Trade Lab AI outlook action. |
| `src/compat_flags.py` | Added `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` and `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`, both default false through the existing flag parser. |
| `tests/test_data_ops_local_controls.py` | Added focused tests for default false flags, disabled controls, Cloud Run gate separation, default false risk flags, and Pigskin SQL tool absence. |

## New Flags

| Flag | Default | Purpose |
| --- | --- | --- |
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` | Controls whether local admin subprocess controls are visible as active controls. With the default false state, controls are rendered disabled with an explicit gate message. |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` | Controls whether visible local controls may execute. Both local flags must be true before any guarded button can run. |

The existing Cloud Run Job gates remain separate:

| Flag | Default |
| --- | --- |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |

## Controls Inventoried

| Control | Location | Call path | BigQuery write risk | External API risk | LLM risk | Local subprocess | Current gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `Run AI {projection_years}-Year Outlook Analysis` | `app.py:4427` | `create_gemini_model(...).generate_content(...)` | No direct write | Gemini API | Yes | No | Disabled unless both local gates are true. |
| `Run Validation Sweep` | `app.py:5110` | `run_subprocess_live(["validate.py"])` | No expected write | BigQuery reads | No | Yes | Disabled unless both local gates are true. |
| `Ingest Realtime Player News` | `app.py:5129` | `run_subprocess_live(["-m", "src.ingest_news"])` | Yes | Sleeper or related source APIs | No | Yes | Disabled unless both local gates are true. |
| `Load Context Event Ledger` | `app.py:5142` | `run_subprocess_live(["-m", "src.ingest_context_events"])` | Yes | Local or curated source load | No | Yes | Disabled unless both local gates are true. |
| `Ingest FantasyCalc Market Values` | `app.py:5157` | `run_subprocess_live(["-m", "src.fetch_market_values"])` | Yes | FantasyCalc API | No | Yes | Disabled unless both local gates are true. |
| `Verify Player Context` | `app.py:5186` | `run_subprocess_live(["-m", "src.verify_player_context", ...])` | Yes | External verification search | No | Yes | Disabled unless both local gates are true. |
| `Ingest CFBD College Stats` | `app.py:5216` | `run_subprocess_live(["-m", "src.ingest_college_data", ...])` | Yes | CollegeFootballData API | No | Yes | Disabled unless both local gates are true. |
| `Run Ingestion Pipeline` | `app.py:5257` | `run_subprocess_live(["-m", "src.pipeline", ...])` | Yes, including operator-selected write disposition | nflverse or cached source path | No | Yes | Disabled unless both local gates are true. |
| `Generate Pigskin Rankings` | `app.py:5273` | `run_subprocess_live(["-m", "src.generate_pigskin_rankings", "--refresh-sleeper"])` | Yes | Sleeper refresh | Yes | Yes | Disabled unless both local gates are true. |
| `Upload and Import Scouting Metrics` | `app.py:5328` | BigQuery `load_table_from_dataframe(..., WRITE_APPEND)` | Yes | No | No | No | Disabled unless both local gates are true. |

## Default Behavior

Default production behavior with no new flags set:

- Data Ops page remains visible.
- Runtime status, Cloud Run Job status, and flag diagnostics remain visible.
- Cloud Run Job triggering remains disabled by the existing Cloud Run flags.
- Local subprocess and BigQuery-writing controls render disabled.
- The local admin gate panel states both new flags are false.
- The Trade Lab AI outlook action is hidden unless local admin controls are explicitly enabled.
- No button callback can execute unless both new local flags are true.

If `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=true` and `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`, controls can be shown for review but remain disabled.

If both new local flags are true, the existing behavior is reachable for an explicitly authorized admin session.

## Test Coverage

Added `tests/test_data_ops_local_controls.py` covering:

- New local flags default false.
- New local flags can be explicitly enabled from env input.
- Trade History compatibility and Trade Analyzer score flags remain default false.
- Mutating Data Ops buttons include `disabled=not local_controls_can_run`.
- Trade Lab AI outlook action is gated by the same local admin controls.
- Cloud Run Job trigger gates remain separate from local subprocess gates.
- `execute_bigquery_sql` remains absent from the app source.

Existing coverage also continues to verify Cloud Run Job trigger guardrails, Pigskin context tools, compatibility rollout defaults, and deployment safety.

## Checks Run

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Passed |
| `.\venv\Scripts\python.exe -m py_compile app.py` | Passed |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | Passed |
| `.\venv\Scripts\python.exe -m unittest discover tests` | Passed, 352 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | Passed, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | Passed, 160 validation files discovered |

## Feature Exposure Verification

- Production risk flags remain default false.
- Trade Analyzer score flags remain default false.
- Trade History compatibility remains default false.
- Cloud Run Job trigger flags remain default false and independent.
- Claim Ledger UI, Content Brief Review UI, Backtest Dashboard, Sleeper Watch compatibility, Trade Assets compatibility, and Viewer Team Context compatibility were not enabled.
- Pigskin arbitrary SQL was not reintroduced.
- `execute_bigquery_sql` remains absent from Pigskin-visible tools.
- No raw/source table list was exposed to Pigskin.

## Remaining Warnings

- This phase changed code only. Production remains on the previously deployed revision until a later deploy phase.
- A staging deploy and authenticated browser QA are recommended before any production warning-cleanup redeploy.
- The Data Ops page still shows read-only diagnostics and disabled controls. This is intentional for operator visibility.

## Recommended Next Work

Recommended Phase 25.10: build and deploy a staging image with these Data Ops local-control gates, then run authenticated staging QA against Data Ops, Trade Lab, Pigskin Studio, and regression tabs.
