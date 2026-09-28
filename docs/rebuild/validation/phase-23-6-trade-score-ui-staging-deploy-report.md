# Phase 23.6 Trade Score UI Staging Deploy Report

Date: 2026-06-18

## Final Decision

`TRADE SCORE UI STAGING DEPLOYED WITH WARNINGS`

The Trade Analyzer score UI was deployed to staging only. Production was untouched. The staging service now runs the current reviewed image with the Trade History compatibility path and Trade Analyzer score UI flags enabled for staging review.

No production deploy, Cloud Run Job trigger, Scheduler job creation, LLM call, scrape, Firebase artifact creation, or production feature flag change was performed.

## Score Data Prerequisite

The score data prerequisite passed.

| Check | Result |
| --- | ---: |
| target score rows | 77 |
| model version | `trade_score_v0_2025_001` |
| season/week | `2025` / `18` |
| scoring context | `ppr` / `redraft` / `one_qb` |

Phase 23.5 decision: `TRADE SCORE SANITY PASS WITH WARNINGS`.

Staging warning: all 77 score rows are below confidence 70. These rows are staging-review data only and are not production trade advice.

## Pre-Build Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 25 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout` | pass, 10 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes` | pass, 13 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 343 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern trade_score` | pass, 1 of 1 |

Safety checker confirmed:

- no Firebase artifacts
- no tracked secret files
- no detected secret content
- feature flags default off
- Pigskin `execute_bigquery_sql` absent
- app and `src` plus `scripts` compile

## Build

The first build command attempted to call `gcloud` from PATH and did not start because the current PowerShell shell did not have `gcloud` on PATH. The build was rerun with the documented full SDK path:

`C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`

Successful build:

| Field | Value |
| --- | --- |
| build ID | `ad393608-a679-4a18-8a3c-d5fafd286434` |
| git short SHA | `ce0eb82eef63` |
| image tag | `staging-ce0eb82eef63-20260618T221717Z` |
| image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-ce0eb82eef63-20260618T221717Z` |
| image digest | `sha256:1fe0253f07332361a5f54e1a654477920de7ad4b0813cef2806acd5be4f4ebc2` |
| digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:1fe0253f07332361a5f54e1a654477920de7ad4b0813cef2806acd5be4f4ebc2` |
| build status | `SUCCESS` |

Build command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit --project=fantasy-football-498121 --config=cloudbuild.yaml --substitutions="_IMAGE_TAG=staging-ce0eb82eef63-20260618T221717Z,_COMMIT_HASH=ce0eb82eef63,_VERSION_LABEL=staging-ce0eb82eef63-20260618T221717Z" .
```

## Staging Deploy

Target:

| Field | Value |
| --- | --- |
| service | `nfl-studio-dashboard-staging` |
| project | `fantasy-football-498121` |
| region | `us-central1` |
| revision | `nfl-studio-dashboard-staging-00016-xct` |
| traffic | 100 percent to `nfl-studio-dashboard-staging-00016-xct` |
| service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| URL | `https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app` |

Deploy command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard-staging --project=fantasy-football-498121 --region=us-central1 --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:1fe0253f07332361a5f54e1a654477920de7ad4b0813cef2806acd5be4f4ebc2 --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true,USE_TRADE_ANALYZER_SCORE_V0=true,USE_COMPAT_TRADE_PLAYER_SCORE=true,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false --quiet
```

Deploy result:

```text
Service [nfl-studio-dashboard-staging] revision [nfl-studio-dashboard-staging-00016-xct] has been deployed and is serving 100 percent of traffic.
```

## Staging Feature Flags

Enabled in staging:

| Flag | Value |
| --- | --- |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `true` |
| `USE_TRADE_ANALYZER_SCORE_V0` | `true` |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `true` |

False in staging:

| Flag | Value |
| --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `false` |
| `USE_BACKTEST_DASHBOARD` | `false` |
| `USE_CLAIM_LEDGER_UI` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `false` |

## Health Check

| Check | Result |
| --- | --- |
| unauthenticated `/_stcore/health` | `403 Forbidden`, expected for private staging |
| authenticated `/_stcore/health` | `200 ok` |
| authenticated `/` | `200`, Streamlit HTML present |

Health URL checked:

`https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app/_stcore/health`

## Production Untouched

Read-only production describe after the staging deploy:

| Field | Value |
| --- | --- |
| production service | `nfl-studio-dashboard` |
| production revision | `nfl-studio-dashboard-00074-26x` |
| production image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| `USE_TRADE_ANALYZER_SCORE_V0` | unset |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | unset |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | unset |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | unset |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | unset |

## Warnings

- Trade Analyzer score rows are staging-review only.
- All 77 materialized score rows have confidence below 70.
- Browser-click QA of the Trade Lab score panel is still required after this deploy.
- `gcloud` was not on the current PowerShell PATH, so full `gcloud.cmd` path was used.

## Acceptance Criteria Status

| Criterion | Status |
| --- | --- |
| score data exists first | pass |
| production untouched | pass |
| score flags enabled only in staging | pass |
| all other risk flags false | pass |
| no Cloud Run Jobs triggered | pass |
| no Firebase artifacts | pass |
