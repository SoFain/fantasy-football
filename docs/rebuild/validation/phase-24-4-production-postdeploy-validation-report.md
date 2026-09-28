# Phase 24.4 Production Postdeploy Validation Report

Validation date: 2026-06-25

## Final Decision

`PRODUCTION VALIDATION PASS WITH WARNINGS`

Production remains on the Phase 24.3R revision and passed postdeploy validation. No rollback was performed.

Production classification:

```text
PRODUCTION DEPLOYED ALL FLAGS OFF
```

Trade Analyzer classification:

```text
VALIDATED, PRODUCTION DISABLED
```

Trade Analyzer score objects and compatibility views validate successfully, but the production UI flags remain `false`, so the Trade Analyzer score UI is not visible in production.

## Authorization Gate State

All checked authorization gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | empty |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | empty |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | empty |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | empty |

No authorization gate was set during this phase.

## Local Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

## BigQuery Validations

| Pattern | Result |
| --- | --- |
| `cloud_run_job` | pass, 8 passed, 0 failed |
| `compat_trade_player_history` | pass, 6 passed, 0 failed |
| `trade_player_scores` | pass, 11 passed, 0 failed |
| `compat_trade_player_scores` | pass, 2 passed, 0 failed |
| `market` | pass, 9 passed, 0 failed |
| `content_brief` | pass, 11 passed, 0 failed |
| `claim` | pass, 17 passed, 0 failed |
| `backtest` | pass, 11 passed, 0 failed |

Review-only warnings:

| Validation | Warning |
| --- | --- |
| `026_compat_trade_player_history_identity_coverage.sql` | informational row returned, missing identity count `0`, missing identity rate `0.0` |
| `120_claims_player_identity_coverage.sql` | informational row returned, `1` of `3` claim player rows missing internal player identity |
| `142_claim_ledger_ui_sources_exist.sql` | informational row returned, `3` active claim sources |
| `143_claim_ledger_ui_draft_claims_allowed_missing_fields.sql` | informational row returned, `1` draft claim missing review fields |
| `139_backtest_dashboard_latest_runs.sql` | informational row returned, latest backtest run exists |
| `140_backtest_dashboard_summary_available.sql` | informational row returned, `6` backtest summary rows |

No targeted validation pattern failed.

## Production Service State

Read-only service describe confirmed:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Latest ready revision | `nfl-studio-dashboard-00075-x7p` |
| Latest created revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic | `nfl-studio-dashboard-00075-x7p:100%` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Ingress | `all` |

Secret values were not printed.

## Production Flag State

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

Trade History compatibility is disabled in production. Trade Analyzer score flags are disabled in production. Data Ops job trigger flags are disabled in production.

Other production environment summary:

| Env var | State |
| --- | --- |
| `BQ_PROJECT` | `fantasy-football-498121` |
| `EXTERNAL_SEARCH_DAILY_LIMIT` | `10` |
| `EXTERNAL_SEARCH_MAX_RESULTS` | `3` |
| `EXTERNAL_SEARCH_PROVIDER` | `vertex_ai_search` |
| `GEMINI_API_KEY` | Secret Manager reference |
| `GEMINI_MODEL` | `gemini-3.5-flash` |
| `VERTEX_AI_SEARCH_ENGINE_ID` | `fantasy-football-search-engine` |

## Health and Browser Smoke

Authenticated HTTP checks:

| Check | Result |
| --- | --- |
| `/_stcore/health` | `200`, body `ok` |
| `/` root | `200` |
| Root contains Streamlit shell | pass |
| Root response traceback check | pass, no `Traceback` |

Authenticated browser smoke used Chrome through Playwright with a Cloud Run identity token. No LLM-backed actions were clicked. No Pigskin prompt was submitted. No Data Ops job was triggered.

| Check | Result |
| --- | --- |
| Cloud Run authenticated page load | pass |
| Streamlit login form visible | pass |
| Login/session gate | pass |
| Pigskin Studio tab selected | pass |
| Show Prep tab selected | pass |
| Player Profiles tab selected | pass |
| Versus Finder tab selected | pass |
| Viewer Team Lab tab selected | pass |
| Trade Lab tab selected | pass |
| Data Ops tab selected | pass |
| Obvious traceback across tab smoke | pass, none found |
| `execute_bigquery_sql` visible | absent |
| Pigskin raw/source table list visible | absent |
| Trade History compat marker | absent |
| Trade Analyzer score UI | absent |
| Data Ops job trigger availability | unavailable with flags false |

## Log Review

Cloud Run logs for revision `nfl-studio-dashboard-00075-x7p`:

| Check | Result |
| --- | --- |
| Log entries inspected | `231` |
| ERROR or higher count | `0` |
| WARNING severity count | `0` |
| Warning-like text count | `28` |
| Traceback-like count | `0` |
| Startup hard errors | none found |
| Runtime hard errors | none found |

Known non-blocking warnings observed:

- `BigQuery Storage module not found, fetch data with the REST endpoint instead.`

The previously observed Streamlit `use_container_width` deprecation warning remains an accepted Phase 24.3R warning, though it was not present in the latest sampled warning rows.

## Scheduler and Cloud Run Job Status

| Check | Result |
| --- | --- |
| Cloud Scheduler API enabled query | no enabled `cloudscheduler.googleapis.com` service returned |
| Scheduler jobs created by this phase | none |
| Cloud Run Jobs triggered by this phase | none |
| Latest `validate-warehouse` execution | `validate-warehouse-gwbpg`, created `2026-06-19T17:26:10.331740Z`, completed successfully |
| Latest `cloud_run_job_runs` row | `validate-warehouse-20260619T172733Z-e1070248`, status `success`, pattern `model_runs` |

No Cloud Run Job execution occurred during this postdeploy validation.

## Rollback Status

Rollback was not performed.

Rollback command if a hard failure appears later:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00074-26x=100
```

Hard rollback criteria were not met.

## Remaining Warnings

1. Review-only validation rows remain for claim identity coverage, draft claim review fields, and backtest dashboard informational checks.
2. Production logs contain BigQuery Storage fallback warnings. This is not a hard failure, but installing the BigQuery Storage dependency in a future image would reduce fallback noise and improve dataframe reads.
3. The Streamlit `use_container_width` deprecation warning from Phase 24.3R should be cleaned up before it becomes a runtime compatibility issue.

## Recommended Phase 25 Work

1. Monitor production revision `nfl-studio-dashboard-00075-x7p` for another short window and capture a production hold report.
2. Fix Streamlit `use_container_width` deprecation warnings.
3. Add BigQuery Storage dependencies or explicitly accept REST fallback performance.
4. Resolve the draft claim identity and review-field warnings before enabling any public claim or accountability UI.
5. Keep Trade Analyzer score UI staging-only until a separate production feature-flag rollout is approved.
6. Keep Data Ops Cloud Run Job triggers disabled in production until a separate controlled rollout is approved.
