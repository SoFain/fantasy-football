# Phase 24.3R Production Deploy and Smoke Report

Validation date: 2026-06-25

## Final Decision

`PRODUCTION DEPLOYED WITH WARNINGS`

Production was deployed with all required risk flags and score flags set to `false`. The deployed image is the fixed digest-pinned candidate approved by `phase-24-2r-production-deploy-gate-report.md`.

No rollback was performed. No hard smoke failure was observed.

Warnings:

- Cloud Run deploy progress emitted stderr records in PowerShell, but the deploy command exited `0` and Cloud Run reported the revision deployed successfully.
- New revision logs include non-blocking warnings about Streamlit `use_container_width` deprecation and BigQuery Storage module not installed, falling back to the REST endpoint.
- Smoke testing was read-only and did not click LLM-backed analysis actions, submit Pigskin prompts, or trigger Data Ops jobs.

## Approval Source

Approval source used:

```text
docs/rebuild/validation/phase-24-2r-production-deploy-gate-report.md
```

Approval decision:

```text
APPROVED FOR PRODUCTION DEPLOY ALL FLAGS OFF
```

The old blocked gate was not used as the approval source:

```text
docs/rebuild/validation/phase-24-2-production-deploy-gate-report.md
```

## Fixed Image

Image deployed:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29
```

Artifact Registry verification passed before deploy.

Old failed digest not used:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b
```

## Pre-Deploy Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

## Authorization Gate

The deploy gate was set only inside the deploy command session:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=true
```

The deploy command exited `0`.

The gate was removed afterward:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=
```

## Pre-Deploy Baseline

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Current revision | `nfl-studio-dashboard-00074-26x` |
| Traffic split | `nfl-studio-dashboard-00074-26x:100%` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Ingress | `all` |

Required production risk flags were `<unset>` before deploy and therefore safe by default.

Rollback baseline:

```text
nfl-studio-dashboard-00074-26x
```

## Deploy Command

Command executed:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false,USE_TRADE_ANALYZER_SCORE_V0=false,USE_COMPAT_TRADE_PLAYER_SCORE=false `
  --update-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --quiet
```

Deploy result:

```text
Service [nfl-studio-dashboard] revision [nfl-studio-dashboard-00075-x7p] has been deployed and is serving 100 percent of traffic.
```

## Post-Deploy Production State

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Latest ready revision | `nfl-studio-dashboard-00075-x7p` |
| Latest created revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic split | `nfl-studio-dashboard-00075-x7p:100%` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Secret reference | `GEMINI_API_KEY=GEMINI_API_KEY:latest` |
| Ingress | `all` |

## Final Production Flags

| Flag | Final production state |
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

Other production environment:

| Env var | State |
| --- | --- |
| `BQ_PROJECT` | `fantasy-football-498121` |
| `EXTERNAL_SEARCH_DAILY_LIMIT` | `10` |
| `EXTERNAL_SEARCH_MAX_RESULTS` | `3` |
| `EXTERNAL_SEARCH_PROVIDER` | `vertex_ai_search` |
| `GEMINI_API_KEY` | Secret Manager reference |
| `GEMINI_MODEL` | `gemini-3.5-flash` |
| `VERTEX_AI_SEARCH_ENGINE_ID` | `fantasy-football-search-engine` |

## Smoke Test Results

Authenticated HTTP smoke:

| Check | Result |
| --- | --- |
| `/_stcore/health` | `200`, body `ok` |
| Root Streamlit page | `200` |
| Root page contains Streamlit shell | pass |
| Root page traceback check | pass, no `Traceback` |

Authenticated browser smoke used Chrome through Playwright with a Cloud Run identity token. No LLM-backed actions, Pigskin prompts, or Data Ops job triggers were clicked.

| Check | Result |
| --- | --- |
| Cloud Run authenticated page load | pass |
| Streamlit login form visible | pass |
| Login/session gate | pass |
| Pigskin Studio tab clicked | pass |
| Show Prep tab clicked | pass |
| Player Profiles tab clicked | pass |
| Versus Finder tab clicked | pass |
| Viewer Team Lab tab clicked | pass |
| Trade Lab tab clicked | pass |
| Data Ops tab clicked | pass |
| Obvious traceback across tab smoke | pass, none found |
| `execute_bigquery_sql` visible | absent |
| Pigskin raw/source table list visible | absent |
| Trade History compat marker | absent |
| Trade Analyzer score UI | absent |
| Data Ops Cloud Run Jobs triggerable | not triggerable with flags false |

Production log smoke for revision `nfl-studio-dashboard-00075-x7p`:

| Check | Result |
| --- | --- |
| ERROR log entries | `0` |
| Startup/runtime hard errors | none found |
| Non-blocking warnings | Streamlit `use_container_width` deprecation, BigQuery Storage module fallback to REST |

## Scheduler and Job Trigger Status

| Item | Result |
| --- | --- |
| Scheduler jobs created | no |
| Cloud Run Jobs triggered | no |
| Data Ops trigger flags | `false` |
| Cloud Scheduler API enabled check | no enabled `cloudscheduler.googleapis.com` service returned |

## Rollback

Rollback was not performed.

Rollback command if needed:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=nfl-studio-dashboard-00074-26x=100
```

## Production Final State

| Item | Result |
| --- | --- |
| Production deploy | completed |
| Serving revision | `nfl-studio-dashboard-00075-x7p` |
| Traffic | `100%` to `nfl-studio-dashboard-00075-x7p` |
| Fixed image | deployed |
| Old failed image | not used |
| Production risk flags | all `false` |
| Score flags | `false` |
| Trade History compatibility | `false` |
| Data Ops job trigger flags | `false` |
| Pigskin SQL safety | intact in code and browser smoke |
| LLM-backed actions | not clicked |
| Data Ops jobs | not triggered |
| Scheduler jobs | not created |
| Firebase artifacts | none created |

## Follow-Up

Monitor production after the deploy. If health, login, Pigskin SQL safety, or Data Ops trigger gating regresses, roll back to `nfl-studio-dashboard-00074-26x`.
