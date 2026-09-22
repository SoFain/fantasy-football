# Phase 25.1 Production Hold Monitoring Report

Validation date: 2026-06-25 local, with Cloud Run and BigQuery timestamps in UTC.

## Final Decision

`PRODUCTION HOLD PASS WITH WARNINGS`

Production remains healthy on the Phase 24.3R all-flags-off revision. No deployment, rollback, feature flag change, Cloud Run Job trigger, Scheduler change, ingestion, materialization, Pigskin prompt, LLM-backed action, scraping, or Firebase artifact creation occurred during this monitoring phase.

Warnings are limited to known non-blocking runtime messages:

- BigQuery Storage module fallback to the REST endpoint.
- Streamlit `use_container_width` deprecation messages.

No hard rollback trigger was found.

## Authorization Gate State

All checked authorization gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | empty |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | empty |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | empty |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | empty |

No authorization gate was set during this phase.

## Production Service State

Read-only Cloud Run describe confirmed the expected production service state:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Latest ready revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic | `nfl-studio-dashboard-00075-x7p:100%` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Rollback baseline | `nfl-studio-dashboard-00074-26x` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Ingress | `all` |

Secret values were not printed.

## Production Flag State

All production risk and score flags are explicitly false:

| Flag | Production state |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |
| `USE_BACKTEST_DASHBOARD` | `false` |
| `USE_CLAIM_LEDGER_UI` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` |

Trade History compatibility is disabled in production. Trade Analyzer score UI is disabled in production. Data Ops job trigger flags are disabled in production.

Other environment values observed:

| Env var | State |
| --- | --- |
| `BQ_PROJECT` | `fantasy-football-498121` |
| `EXTERNAL_SEARCH_DAILY_LIMIT` | `10` |
| `EXTERNAL_SEARCH_MAX_RESULTS` | `3` |
| `EXTERNAL_SEARCH_PROVIDER` | `vertex_ai_search` |
| `GEMINI_MODEL` | `gemini-3.5-flash` |
| `VERTEX_AI_SEARCH_ENGINE_ID` | `fantasy-football-search-engine` |
| `GEMINI_API_KEY` | Secret Manager reference |

## Health Checks

Authenticated HTTP checks passed:

| Check | Result |
| --- | --- |
| `/_stcore/health` | HTTP `200`, body `ok` |
| `/` | HTTP `200` |
| Streamlit shell present | yes |
| `Traceback` in root response | no |

## Production Browser Smoke

Authenticated browser smoke remained read-only. No Pigskin prompt was submitted and no LLM-backed action was clicked.

| Area | Result |
| --- | --- |
| Login/session gate | pass |
| Pigskin Studio | pass |
| Show Prep | pass |
| Player Profiles | pass |
| Versus Finder | pass |
| Viewer Team Lab | pass |
| Trade Lab | pass |
| Data Ops | pass |
| `execute_bigquery_sql` visible | no |
| Raw/source table list visible to Pigskin | no |
| Trade History compat marker visible | no |
| Trade Analyzer score UI visible | no |
| Cloud Run Job trigger available by default | no |
| Final browser traceback | no |

## Log Review

Cloud Logging was reviewed for revision `nfl-studio-dashboard-00075-x7p` over the recent production window.

| Metric | Count |
| --- | ---: |
| Log entries reviewed | 233 |
| ERROR or higher severity | 0 |
| WARNING severity | 0 |
| Warning-like text | 28 |
| Traceback-like text | 0 |
| BigQuery Storage fallback messages | 14 |
| Streamlit deprecation messages | 24 |
| Startup hard errors | 0 |
| Runtime hard errors | 0 |

Sample warning text was the known BigQuery Storage fallback:

```text
BigQuery Storage module not found, fetch data with the REST endpoint instead.
```

No startup failure, runtime hard error, repeated 500, auth/session error, secret access error, Pigskin SQL safety regression, or Cloud Run Job trigger attempt was found in the reviewed logs.

## Job and Scheduler Status

No Scheduler jobs were created unexpectedly. The Cloud Scheduler API is not enabled for the project.

Recent `validate-warehouse` executions remain the prior Phase 24 proof attempts:

| Execution | Created | Completion | Status |
| --- | --- | --- | --- |
| `validate-warehouse-gwbpg` | `2026-06-19T17:26:10.331740Z` | `2026-06-19T17:27:44.706610Z` | succeeded |
| `validate-warehouse-qhwkq` | `2026-06-19T15:52:31.352288Z` | `2026-06-19T15:58:38.936261Z` | failed |

Latest `cloud_run_job_runs` metadata row:

| Field | Value |
| --- | --- |
| `job_run_id` | `validate-warehouse-20260619T172733Z-e1070248` |
| `job_name` | `validate-warehouse` |
| `cloud_run_execution_name` | `validate-warehouse-gwbpg` |
| `status` | `success` |
| `started_at` | `2026-06-19T17:27:33.735808+00:00` |
| `finished_at` | `2026-06-19T17:27:38.611873+00:00` |
| `duration_seconds` | `4.876065` |
| `metadata_json` | `{"pattern": "model_runs", "returncode": 0, "row_count": 0}` |

No new Cloud Run Job execution was triggered during this monitoring phase.

## Validation Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job` | pass, 8 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

Safety checker details:

| Check | Result |
| --- | --- |
| `no_firebase_artifacts` | pass |
| `no_tracked_secret_files` | pass |
| `no_secret_content` | pass |
| `required_files_exist` | pass |
| `feature_flags_default_off` | pass |
| `pigskin_no_execute_bigquery_sql` | pass |
| `app_py_compiles` | pass |
| `src_scripts_compile` | pass |

## Rollback Status

Rollback was not performed. No hard rollback trigger was observed.

Rollback command remains available if needed:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00074-26x=100
```

## Recommended Next Work

- Keep production on `nfl-studio-dashboard-00075-x7p` with all risk and score flags false.
- Continue normal production monitoring through the release hold window.
- Keep Trade Analyzer score UI staging-only until a separate production score rollout is approved.
- Keep Data Ops Cloud Run Job triggers disabled in production.
- Address non-blocking runtime warnings in a later cleanup pass: install BigQuery Storage support if desired and update Streamlit `use_container_width` usage.
- Continue resolving draft claim identity and review warnings before any public Claim Ledger or accountability rollout.
