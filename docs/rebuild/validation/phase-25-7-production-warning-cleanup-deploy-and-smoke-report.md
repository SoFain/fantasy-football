# Phase 25.7 Production Warning Cleanup Deploy And Smoke Report

Final decision: PRODUCTION WARNING CLEANUP DEPLOYED WITH WARNINGS

## Scope

Phase 25.7 deployed the warning-cleanup production candidate to production with all production risk flags off.

No staging deploy was run. No production feature flags were enabled. No Trade Analyzer score flags were enabled in production. No Trade History compatibility was enabled in production. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No ingestion, score materialization, LLM-backed action, Pigskin prompt, scraping, or Firebase artifact creation occurred.

## Approval Source

Approval source:

```text
docs/rebuild/validation/phase-25-6-production-warning-cleanup-deploy-gate-report.md
```

Phase 25.6 final decision:

```text
APPROVED FOR PRODUCTION WARNING CLEANUP DEPLOY ALL FLAGS OFF
```

The deploy proceeded because the approval text matched exactly.

## Candidate Image Used

Verified and deployed digest-pinned image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4
```

Artifact Registry verification before deploy:

| Field | Value |
| --- | --- |
| Digest | `sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Fully qualified digest | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| Registry | `us-central1-docker.pkg.dev` |
| Repository | `nfl-studio-repo` |

## Pre-deploy Checks

All required pre-deploy checks passed with process exit code 0:

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

Note: the unit tests printed expected mocked job and pipeline logs. The unittest process exited 0. No live ingestion or materialization command was run.

## Pre-deploy Production Baseline

Read-only production describe before deploy:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic | 100 percent to `nfl-studio-dashboard-00075-x7p` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

Pre-deploy production flags were all false:

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

## Authorization Gate

The deploy gate was set only inside the same PowerShell command and removed in `finally`.

Observed output:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=true
DEPLOY_EXIT=0
ALLOW_LIMITED_PRODUCTION_DEPLOY_AFTER=
```

Post-deploy verification:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=
```

## Deploy Command

```powershell
try {
  $env:ALLOW_LIMITED_PRODUCTION_DEPLOY = 'true'

  & 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
    --project=fantasy-football-498121 `
    --region=us-central1 `
    --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4 `
    --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
    --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false `
    --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
    --no-allow-unauthenticated `
    --quiet
} finally {
  Remove-Item Env:\ALLOW_LIMITED_PRODUCTION_DEPLOY -ErrorAction SilentlyContinue
}
```

Deploy result:

```text
Service [nfl-studio-dashboard] revision [nfl-studio-dashboard-00076-p6s] has been deployed and is serving 100 percent of traffic.
Service URL: https://nfl-studio-dashboard-583607027760.us-central1.run.app
```

## Final Production State

Read-only production describe after deploy:

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Revision | `nfl-studio-dashboard-00076-p6s` |
| Traffic | 100 percent to `nfl-studio-dashboard-00076-p6s` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:81b1fcb1d6697d32b46111450f736f68fff6b1c25cc05859eeaaa9ba6ed579c4` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |

Final production flag state:

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

## Smoke Test Results

Authenticated HTTP checks:

| Check | Result |
| --- | --- |
| `/_stcore/health` | 200, `ok` |
| `/` | 200 |
| Streamlit shell present | yes |
| Traceback in root response | no |

Browser smoke used a temporary local proxy with a Cloud Run identity token because the production service is private. The temporary token file was removed after the check.

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

Focused Data Ops check:

| Check | Result |
| --- | --- |
| Cloud Run path metric | disabled |
| Trigger allow flag metric | disabled |
| Cloud Run trigger button | disabled |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` visible as false | yes |
| `DATA_OPS_ALLOW_JOB_TRIGGER` visible as false | yes |
| Cloud Run Job action clicked | no |

Warning: Data Ops still exposes pre-existing local subprocess controls, including validation sweep and ingestion pipeline buttons. These were not clicked. This is not a new regression from the warning-cleanup deploy and would not be removed by rollback to `nfl-studio-dashboard-00075-x7p`, but it remains a production exposure item for future hardening.

## Log Review

Log filter:

```text
resource.type="cloud_run_revision" AND resource.labels.service_name="nfl-studio-dashboard" AND resource.labels.revision_name="nfl-studio-dashboard-00076-p6s"
```

| Metric | Count |
| --- | ---: |
| Log entries inspected | 143 |
| ERROR severity | 0 |
| WARNING severity | 0 |
| Traceback-like text | 0 |
| Startup hard errors | 0 |
| Runtime hard errors | 0 |
| `use_container_width` deprecation messages | 0 |
| BigQuery Storage fallback messages | 0 |
| BigQuery Storage import/install errors | 0 |

The warning cleanup is effective in the deployed production revision.

## Scheduler And Cloud Run Job Status

Cloud Run Job executions:

| Latest execution | Created | Status |
| --- | --- | --- |
| `validate-warehouse-gwbpg` | `2026-06-19T17:26:10.331740Z` | completed successfully |
| `validate-warehouse-qhwkq` | `2026-06-19T15:52:31.352288Z` | historical failed proof |

No new Cloud Run Job execution was created during this deploy phase.

Cloud Scheduler API check:

```text
SERVICE_DISABLED: Cloud Scheduler API has not been used in project fantasy-football-498121 before or it is disabled.
```

The API was not enabled, and no Scheduler job was created.

## Rollback Status

Rollback was not used.

Hard rollback checks did not fail:

| Trigger | Result |
| --- | --- |
| Health fails | no |
| Streamlit cannot load | no |
| Production flags unsafe | no |
| Trade Analyzer score UI appears in production | no |
| Trade History compatibility appears in production | no |
| Cloud Run Job trigger becomes available | no |
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

## Remaining Warnings

1. Production Data Ops still exposes local subprocess controls. Cloud Run Job triggering is disabled, and no controls were clicked, but local production write controls should be reviewed in a future hardening phase.
2. Cloud Scheduler API is disabled, so scheduler enumeration cannot complete without enabling the API. It was not enabled.
3. Historical untracked validation reports remain in the worktree for owner review.

## Final Decision

Production warning cleanup is deployed on `nfl-studio-dashboard-00076-p6s` with all production risk flags, Trade History compatibility, Trade Analyzer score flags, and Data Ops Cloud Run trigger flags false.

No rollback was performed.
