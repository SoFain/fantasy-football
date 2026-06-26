# Phase 25.13 Production Data Ops Hardening Deploy And Smoke

Final decision: PRODUCTION DATA OPS HARDENING DEPLOYED WITH WARNINGS

Generated: 2026-06-26T11:27:04Z

## Scope

This phase deployed the Data Ops local-control hardening image to production with all production risk flags off.

No staging deploy was run. No Cloud Run Job was triggered. No Scheduler job was created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, or Firebase action was run. No Data Ops local subprocess control was clicked.

## Approval Source

Approval report:

`docs/rebuild/validation/phase-25-12-production-data-ops-hardening-deploy-gate-report.md`

Approval decision:

`APPROVED FOR PRODUCTION DATA OPS HARDENING DEPLOY ALL FLAGS OFF`

The deploy was allowed to proceed because the approval source matched the required decision exactly.

## Candidate Image Used

| Field | Value |
| --- | --- |
| Source commit | `22e32569c50d7493891c133d561cb4e4f16a569a` |
| Source commit message | `Gate Data Ops local subprocess controls` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Artifact Registry verification | passed |

## Authorization Gate

Before deploy:

| Gate | State |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

The deploy command was run inside a same-session wrapper:

```powershell
try {
  $env:ALLOW_LIMITED_PRODUCTION_DEPLOY = "true"
  # production deploy command
} finally {
  Remove-Item Env:\ALLOW_LIMITED_PRODUCTION_DEPLOY -ErrorAction SilentlyContinue
}
```

Observed deploy wrapper output:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=true
deploy_exit=0
ALLOW_LIMITED_PRODUCTION_DEPLOY=
```

After deploy, `ALLOW_LIMITED_PRODUCTION_DEPLOY` was unset. Temporary browser proxy environment variables were also removed.

## Pre-Deploy Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | passed |
| `.\venv\Scripts\python.exe -m py_compile app.py` | passed |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | passed |
| `.\venv\Scripts\python.exe -m unittest discover tests` | passed, 352 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | passed, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | passed |

The unit test run emitted expected local test logs for schema coercion and ingest-only planning. The command exited 0.

## Pre-Deploy Baseline

Read-only production describe before deploy:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Revision | `nfl-studio-dashboard-00076-p6s` |
| Traffic | `100 percent` to `nfl-studio-dashboard-00076-p6s` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret refs | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

Baseline production flags:

| Flag | State |
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
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

## Deploy Command

Executed command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false,USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false,DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --no-allow-unauthenticated `
  --quiet
```

Deploy result:

```text
Service [nfl-studio-dashboard] revision [nfl-studio-dashboard-00077-2jp] has been deployed and is serving 100 percent of traffic.
```

## Final Production State

Read-only production describe after deploy:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Latest ready revision | `nfl-studio-dashboard-00077-2jp` |
| Latest created revision | `nfl-studio-dashboard-00077-2jp` |
| Traffic | `100 percent` to `nfl-studio-dashboard-00077-2jp` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret refs | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

Final production flags:

| Flag | State |
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
| `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS` | `false` |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | `false` |

## HTTP Smoke

Authenticated HTTP checks used a Cloud Run identity token. The token was not printed or written to the report.

| Check | Result |
| --- | --- |
| `/_stcore/health` | `200`, body `ok` |
| `/` root | `200` |
| Streamlit shell present | yes |
| Root response contains `Traceback` | no |

## Browser Smoke

Authenticated browser smoke used a temporary websocket-aware local auth proxy that injected a Cloud Run identity token into HTTP and Streamlit websocket traffic. The proxy process was stopped after QA. No token file was committed. No LLM-backed action, Pigskin prompt, Data Ops local subprocess control, or Cloud Run Job trigger was clicked.

| Check | Result |
| --- | --- |
| Login/session gate | pass, login form submitted |
| Pigskin Studio tab | pass, clicked and loaded |
| Show Prep tab | pass, clicked and loaded |
| Player Profiles tab | pass, clicked and loaded |
| Versus Finder tab | pass, clicked and loaded |
| Viewer Team Lab tab | pass, clicked and loaded |
| Trade Lab tab | pass, clicked and loaded |
| Data Ops tab | pass, clicked and loaded |
| Browser console errors | `0` |
| Browser console warnings | `0` |
| `Traceback`, `KeyError`, `NameError`, `pos_abb`, `rolling_3_week_ppr` | absent |
| `execute_bigquery_sql` visible in Pigskin | absent |
| Raw/source table list visible in Pigskin | absent |
| Trade History compatibility marker | absent |
| Trade Analyzer score UI | absent |
| Scouting CSV uploader | absent |
| Trade Lab AI outlook action | absent |

## Data Ops Hardening Verification

Focused Data Ops DOM inspection:

| Control | Result |
| --- | --- |
| `Trigger Cloud Run Job` button | visible but disabled |
| `Run Validation Sweep` button | visible but disabled |
| `Upload scouting CSV` file input | absent |
| `Run ingestion pipeline` | absent |
| `Generate Pigskin Rankings` | absent |
| Data Ops local subprocess flag copy | confirms both local gates false |
| Cloud Run Job trigger flag copy | confirms both Cloud Run job gates false |

This satisfies the Phase 25.13 requirement that controls be unavailable or disabled. No Data Ops button was clicked.

## Log Review

Cloud Run log review for revision `nfl-studio-dashboard-00077-2jp`, freshness window 45 minutes:

| Metric | Count |
| --- | --- |
| Entries inspected | `230` |
| ERROR or higher severity | `0` |
| WARNING severity | `34` |
| Warning-like app text | `0` |
| Traceback-like text | `0` |
| `use_container_width` messages | `0` |
| BigQuery Storage fallback messages | `0` |
| BigQuery Storage import/install errors | `0` |
| Cloud Run Job trigger evidence | `0` |

The WARNING severity entries were unauthenticated request warnings caused by a failed local proxy attempt during smoke setup. They are not app runtime errors.

Two text-pattern matches required review:

| Pattern | Result |
| --- | --- |
| Local subprocess-like text | deploy audit record containing configuration text, not subprocess execution |
| LLM-like text | deploy audit record containing configuration text, not an LLM call |

No hard startup error, runtime error, traceback, local subprocess execution, LLM action, or Cloud Run Job trigger was found.

## Scheduler And Cloud Run Job Status

| Check | Result |
| --- | --- |
| Cloud Scheduler jobs list | Cloud Scheduler API disabled. It was not enabled. No Scheduler job was created by this phase. |
| Cloud Run Job executions | latest listed execution remains `validate-warehouse-gwbpg`, created `2026-06-19T17:26:10.331740Z` |
| New Cloud Run Job trigger during Phase 25.13 | none found |

## Rollback Status

Rollback was not performed. No rollback trigger was met.

Rollback target remains the pre-deploy baseline revision:

`nfl-studio-dashboard-00076-p6s`

Rollback command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00076-p6s=100
```

## Remaining Warnings

- The log window contains unauthenticated request warnings from a failed local proxy setup attempt. Authenticated HTTP and browser checks passed afterward.
- Data Ops still displays disabled labels for `Trigger Cloud Run Job` and `Run Validation Sweep`. Both buttons are disabled with production gates false. No executable production trigger was found.
- Cloud Scheduler enumeration cannot complete because the Cloud Scheduler API is disabled. The API was not enabled.

## Decision

Production is serving `nfl-studio-dashboard-00077-2jp` on the Data Ops hardening digest with all risk, score, Trade History compatibility, Cloud Run job trigger, and local subprocess flags false.

No rollback was needed.

Final decision: PRODUCTION DATA OPS HARDENING DEPLOYED WITH WARNINGS
