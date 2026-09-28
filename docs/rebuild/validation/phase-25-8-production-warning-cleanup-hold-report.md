# Phase 25.8 Production Warning Cleanup Hold Report

Final decision: PRODUCTION WARNING CLEANUP HOLD PASS WITH WARNINGS

## Scope

Phase 25.8 performed production hold monitoring after the Phase 25.7 warning-cleanup deploy.

No deployment was run. No rollback was run. No production feature flags were changed. No Trade Analyzer score flags were enabled in production. No Trade History compatibility was enabled in production. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, Firebase artifact creation, or authorization gate change occurred.

No Data Ops local subprocess controls were clicked.

## Authorization Gates

Checked before monitoring:

| Gate | State |
| --- | --- |
| ALLOW_LIMITED_PRODUCTION_DEPLOY | unset |
| ALLOW_TRADE_SCORE_MATERIALIZATION | unset |
| ALLOW_PROJECTION_CONTEXT_REFRESH | unset |
| ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST | unset |

## Production Service State

Read-only Cloud Run describe confirmed the expected production state:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00076-p6s` |
| Traffic | 100 percent to `nfl-studio-dashboard-00076-p6s` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Rollback baseline | `nfl-studio-dashboard-00075-x7p` |

## Production Flag State

All expected production risk flags remain false:

| Flag | Value |
| --- | --- |
| USE_COMPAT_PLAYER_PROFILES | `false` |
| USE_COMPAT_SLEEPER_WATCH | `false` |
| USE_COMPAT_TRADE_ASSETS | `false` |
| USE_COMPAT_TRADE_PLAYER_HISTORY | `false` |
| USE_COMPAT_VIEWER_TEAM_CONTEXT | `false` |
| USE_BACKTEST_DASHBOARD | `false` |
| USE_CLAIM_LEDGER_UI | `false` |
| USE_CONTENT_BRIEF_REVIEW_UI | `false` |
| USE_CLOUD_RUN_JOBS_FOR_DATA_OPS | `false` |
| DATA_OPS_ALLOW_JOB_TRIGGER | `false` |
| USE_TRADE_ANALYZER_SCORE_V0 | `false` |
| USE_COMPAT_TRADE_PLAYER_SCORE | `false` |

Trade History compatibility is false. Trade Analyzer score flags are false. Data Ops Cloud Run trigger flags are false.

## Health Results

Authenticated HTTP checks:

| Check | Result |
| --- | --- |
| `/_stcore/health` | 200, `ok` |
| `/` | 200 |
| Streamlit shell present | yes |
| Traceback in response | no |

## Browser Smoke Results

Browser smoke used a temporary local auth proxy for the private Cloud Run service. The token file was removed after the check.

| Check | Result |
| --- | --- |
| Login/session gate works | pass |
| Pigskin Studio tab present and clickable | pass |
| Show Prep tab present and clickable | pass |
| Player Profiles tab present and clickable | pass |
| Versus Finder tab present and clickable | pass |
| Viewer Team Lab tab present and clickable | pass |
| Trade Lab tab present and clickable | pass |
| Data Ops tab present and clickable | pass |
| `execute_bigquery_sql` absent from visible page text | pass |
| Raw/source table list absent from visible page text | pass |
| Trade History compat marker absent | pass |
| Trade Analyzer score UI absent | pass |
| No `Traceback`, `KeyError`, `NameError`, `pos_abb`, or `rolling_3_week_ppr` | pass |
| Browser console errors | 0 |
| Browser console warnings | 0 |

## Log Review

Log filter:

```text
resource.type="cloud_run_revision" AND resource.labels.service_name="nfl-studio-dashboard" AND resource.labels.revision_name="nfl-studio-dashboard-00076-p6s"
```

| Metric | Count |
| --- | ---: |
| Log entries inspected | 77 |
| ERROR severity | 0 |
| WARNING severity | 0 |
| Traceback-like text | 0 |
| Startup hard errors | 0 |
| Runtime hard errors | 0 |
| `use_container_width` deprecation messages | 0 |
| BigQuery Storage fallback messages | 0 |
| BigQuery Storage import/install errors | 0 |

Production warning cleanup remains effective.

## Job And Scheduler Status

Cloud Run Job execution check:

| Execution | Created | Status |
| --- | --- | --- |
| `validate-warehouse-gwbpg` | `2026-06-19T17:26:10.331740Z` | completed successfully |
| `validate-warehouse-qhwkq` | `2026-06-19T15:52:31.352288Z` | historical failed proof |

No new Cloud Run Job execution was created during this monitoring phase. The latest validate-warehouse execution remains the prior successful proof, `validate-warehouse-gwbpg`.

Cloud Scheduler check:

```text
SERVICE_DISABLED: Cloud Scheduler API has not been used in project fantasy-football-498121 before or it is disabled.
```

The Cloud Scheduler API remains disabled. It was not enabled, and no Scheduler job was created.

## Data Ops Local Subprocess Exposure Inventory

Cloud Run Job path status in the production UI:

| Item | Result |
| --- | --- |
| Cloud Run path | disabled |
| Trigger allow flag | disabled |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` text | false |
| `DATA_OPS_ALLOW_JOB_TRIGGER` text | false |
| Cloud Run Job trigger button | visible but disabled |
| Cloud Run Job action clicked | no |

Visible local subprocess controls in production:

| Control | Visible | Enabled | Current gate | Can mutate or run subprocesses | Recommended hardening |
| --- | --- | --- | --- | --- | --- |
| `Run AI 3-Year Outlook Analysis` | yes | yes | none observed in UI inventory | can run LLM-backed local subprocess path if clicked | hide or disable in production unless explicit admin/write gate is true |
| `Run Validation Sweep` | yes | yes | none observed in UI inventory | runs local validation subprocess | keep read-only if desired, or gate behind production-safe diagnostics flag |
| `Ingest Realtime Player News` | yes | yes | none observed in UI inventory | can write refreshed news/context tables | hide or disable in production unless explicit ingest gate is true |
| `Load Context Event Ledger` | yes | yes | none observed in UI inventory | can load or refresh context event ledger | hide or disable in production unless explicit ingest gate is true |
| `Ingest FantasyCalc Market Values` | yes | yes | none observed in UI inventory | can fetch external data and write market values | hide or disable in production unless explicit ingest gate is true |
| `Verify Player Context` | yes | yes | none observed in UI inventory | can run external verification and store returned context | hide or disable in production unless explicit external-search/write gate is true |
| `Ingest CFBD College Stats` | yes | yes | none observed in UI inventory | can ingest college stats with supplied API key | hide or disable in production unless explicit ingest gate is true |
| `Run Ingestion Pipeline` | yes | yes | none observed in UI inventory | can run source ingestion pipeline and write BigQuery tables | hide or disable in production unless explicit ingest gate is true |
| `Generate Pigskin Rankings` | yes | yes | none observed in UI inventory | can invoke LLM-backed ranking generation and append history | hide or disable in production unless explicit LLM/write gate is true |

Important: these controls were only inventoried. None were clicked.

This exposure is a pre-existing production hardening issue and was already noted during Phase 25.7. The Phase 25.8 instruction explicitly says not to roll back solely because pre-existing local Data Ops subprocess controls are visible.

## Validation Results

Lightweight validation commands all passed:

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job` | pass, 8 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_player_scores` | pass, 11 passed, 0 failed |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern compat_trade_player_scores` | pass, 2 passed, 0 failed |

No ingestion, materialization, Cloud Run Job trigger, or scheduler command was run.

## Rollback Status

Rollback was not used.

Hard rollback checks:

| Trigger | Result |
| --- | --- |
| Health fails | no |
| Streamlit cannot load | no |
| Production flags unsafe | no |
| Trade Analyzer score UI appears in production | no |
| Trade History compatibility appears in production | no |
| Data Ops Cloud Run Job trigger becomes available | no |
| Pigskin SQL safety regresses | no |
| Raw/source tables exposed | no |
| Repeated ERROR logs or traceback | no |

Rollback command remains available if needed:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00075-x7p=100
```

## Recommended Next Phase

Recommended Phase 25.9: harden production Data Ops local subprocess controls.

Recommended scope:

1. Add a production-safe feature gate for local subprocess controls, separate from Cloud Run Job trigger flags.
2. Default the gate false in production.
3. Keep read-only diagnostics visible only if explicitly classified safe.
4. Hide or disable ingestion, external API refresh, LLM-backed generation, and BigQuery-writing subprocess controls unless an explicit admin/write gate is true.
5. Add tests proving production defaults hide or disable mutating Data Ops controls while preserving the disabled Cloud Run Job trigger state.
6. Deploy first to staging, then rerun the normal all-flags-off production gate.

## Final Decision

Production warning cleanup is holding on `nfl-studio-dashboard-00076-p6s`.

The warning cleanup remains effective. No rollback was required.
