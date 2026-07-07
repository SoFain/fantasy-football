# Phase 20.1 Current Staging Image Report

Date: 2026-06-16

Final decision: CURRENT STAGING IMAGE DEPLOYED WITH WARNINGS

Production was not touched. No Cloud Run Jobs were triggered. No Scheduler jobs were created. No LLM calls were made. No scraping occurred. No Firebase artifacts were created.

## Purpose

Build and deploy a current reviewed staging image containing the Phase 18.3 UI fixes so authenticated staging browser QA can be rerun against the current code instead of stale image `staging-81ed959`.

## Pre-Build Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- deployment safety: pass
- full tests: pass, `304 tests`
- `app.py` compile: pass
- `src` and `scripts` compile: pass
- migrations: no pending migrations
- validation dry-run: pass
- no tracked secrets detected
- no Firebase artifacts detected
- Pigskin arbitrary SQL safety check: pass

## Phase 18.3 UI Fix Confirmation

Targeted test command:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes
```

Result:

- pass, `6 tests`

Fix evidence:

- `src/ui_data_guards.py` contains `ensure_player_profile_display_columns()`
- `src/ui_data_guards.py` backfills `pos_abb`
- `src/ui_data_guards.py` contains `ensure_sleeper_watch_display_columns()`
- `src/ui_data_guards.py` backfills `rolling_3_week_ppr`
- `app.py` imports and uses the UI data guards
- `app.py` shows `Trade player history source: compat_trade_player_history` when the staging-approved flag is enabled
- `tests/test_staging_ui_warning_fixes.py` covers Player Profiles, Versus Finder shared profile handling, Sleeper Watch, and Trade Lab Side B selection behavior

## Build

Build tag:

```text
staging-ce0eb82eef63-20260617T011919Z
```

Build command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions="_IMAGE_TAG=staging-ce0eb82eef63-20260617T011919Z,_COMMIT_HASH=ce0eb82eef63,_VERSION_LABEL=staging-ce0eb82eef63-20260617T011919Z"
```

Build result:

```text
SUCCESS
```

Cloud Build ID:

```text
78e7f6ff-19e0-4d14-ad52-8d46fb95250b
```

Image tag:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-ce0eb82eef63-20260617T011919Z
```

Image digest:

```text
sha256:fff643754107c848b650d63d60038c6f0e96835c622473cb47866f0f99c43194
```

Digest-pinned image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:fff643754107c848b650d63d60038c6f0e96835c622473cb47866f0f99c43194
```

## Staging Baseline Before Deploy

Service:

```text
nfl-studio-dashboard-staging
```

Previous ready revision:

```text
nfl-studio-dashboard-staging-00009-zkq
```

Previous image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959
```

Previous traffic:

```text
nfl-studio-dashboard-staging-00009-zkq:100
```

Previous feature flag state already matched the intended staging rollout:

- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`
- all other risk flags false

## Deploy

Deploy command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:fff643754107c848b650d63d60038c6f0e96835c622473cb47866f0f99c43194 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Deploy result:

```text
Service [nfl-studio-dashboard-staging] revision [nfl-studio-dashboard-staging-00010-2gs] has been deployed and is serving 100 percent of traffic.
```

## Staging Revision

Current staging metadata after deploy:

```text
service: nfl-studio-dashboard-staging
url: https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app
ready revision: nfl-studio-dashboard-staging-00010-2gs
traffic: nfl-studio-dashboard-staging-00010-2gs:100
image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:fff643754107c848b650d63d60038c6f0e96835c622473cb47866f0f99c43194
service account: nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

## Environment Flags

Current staging flag state:

```text
USE_COMPAT_TRADE_PLAYER_HISTORY=true
USE_COMPAT_PLAYER_PROFILES=false
USE_COMPAT_SLEEPER_WATCH=false
USE_COMPAT_TRADE_ASSETS=false
USE_COMPAT_VIEWER_TEAM_CONTEXT=false
USE_BACKTEST_DASHBOARD=false
USE_CLAIM_LEDGER_UI=false
USE_CONTENT_BRIEF_REVIEW_UI=false
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Env var diff:

- image changed from `staging-81ed959` to digest `sha256:fff643754107c848b650d63d60038c6f0e96835c622473cb47866f0f99c43194`
- approved staging flag state was preserved
- no additional compatibility flags were enabled
- Cloud Run Job trigger flags remain false

## Health Check

Direct unauthenticated health check:

```text
403 Forbidden
```

This is expected for a private staging service.

Authenticated health check:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' auth print-identity-token
Invoke-WebRequest https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app/_stcore/health
```

Result:

```text
AUTH_STATUS=200
AUTH_BODY=ok
```

## Production Verification

Production service was checked after staging deploy:

```text
service: nfl-studio-dashboard
ready revision: nfl-studio-dashboard-00074-26x
traffic: nfl-studio-dashboard-00074-26x:100
image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2
```

Production was not changed.

## Rollback Command

Rollback staging to the previous ready revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-staging-00009-zkq=100
```

Risk-flag cleanup command if needed:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --update-env-vars=USE_COMPAT_TRADE_PLAYER_HISTORY=true,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false
```

## Warnings

1. The worktree is dirty and includes untracked docs/tests plus local Phase 18/19/20 artifacts. This was expected for the current reviewed staging build, but it must be classified before a merge or production release.
2. The staging service is private, so unauthenticated health checks return `403`. Authenticated health returned `200 ok`.
3. This deploy only proves startup and metadata health. Authenticated browser-click QA still needs to be rerun as Phase 20.2.

## Final Decision

`CURRENT STAGING IMAGE DEPLOYED WITH WARNINGS`

The current reviewed staging image is deployed to `nfl-studio-dashboard-staging`, includes the Phase 18.3 UI fixes, uses only the staging-approved Trade History compatibility flag, keeps all other risk flags false, and leaves production untouched.
