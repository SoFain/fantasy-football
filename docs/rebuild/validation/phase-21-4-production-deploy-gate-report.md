# Phase 21.4 Production Deploy Gate Report

## Final Decision

`PRODUCTION DEPLOY BLOCKED`

The repository and candidate image pass the technical preflight checks, but production deployment is still blocked because the live `validate-warehouse` Cloud Run Job proof remains unresolved and `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset.

No production deploy, staging deploy, Cloud Run Job trigger, Scheduler creation, LLM call, scrape, Firebase artifact creation, or production flag change was performed.

## Gate Inputs

| Input | Status |
| --- | --- |
| Phase 20 validation | `STAGING ONLY` |
| Phase 20.8 limited production deploy | `PRODUCTION DEPLOY BLOCKED` |
| Phase 21.1 live validate-warehouse proof | `LIVE VALIDATE-WAREHOUSE STILL BLOCKED` |
| Phase 21.2 artifact cleanup | `RELEASE PACKAGE NEEDS REVIEW` |
| Phase 21.3 production candidate | `NEW PRODUCTION CANDIDATE BUILT` |

## Precondition Checklist

| Precondition | Status | Evidence |
| --- | --- | --- |
| Live validate-warehouse proof passed or formally waived | blocker | Phase 21.1 reports `LIVE VALIDATE-WAREHOUSE STILL BLOCKED`; no waiver is recorded |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` | blocker | Current process env var is unset |
| Immutable digest-pinned production candidate verified | pass | Phase 21.3 built and verified a new candidate digest |
| Production rollback baseline exists | pass | Read-only production describe captured current revision and traffic |
| Tests pass | pass | `309` tests passed |
| `app.py` compiles | pass | `py_compile app.py` passed |
| `src` and `scripts` compile | pass | `compileall -q src scripts` passed |
| No pending migrations | pass | `run_bigquery_migrations.py --list-pending` reports no pending migrations |
| Validation dry-run passes | pass | `149` validation files discovered |
| Safety checker passes | pass | all deployment safety checks passed |
| Production flags remain false | pass | current production flags are unset, deploy preview sets all risk flags false |
| No Scheduler jobs | pass | none created |
| No Cloud Run Job triggers by default | pass | production job trigger flags unset and preview sets them false |
| No secret or Firebase issue | pass | safety checker passed no tracked secrets and no Firebase artifacts |

## Final Preflight Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 309 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, 149 validation files discovered |

## Live Proof Status

Phase 21.1 did not pass or waive the live validate-warehouse proof.

| Item | Status |
| --- | --- |
| Live validate-warehouse deploy | not run |
| Live validate-warehouse trigger | not run |
| Waiver | not recorded |
| Broad Cloud Run Jobs | not deployed |
| Scheduler jobs | not created |
| Release impact | production deployment remains blocked |

Required next action before production deployment:

1. Pass the live `validate-warehouse` proof.
2. Or record a formal waiver with approver, risk accepted, follow-up deadline, and release impact.

## Authorization Status

| Env var | Observed value |
| --- | --- |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | `<unset>` |

Because the authorization flag is unset, this phase produced a deploy preview only. No production command was executed.

## Candidate Image

Phase 21.3 candidate:

| Field | Value |
| --- | --- |
| Git short SHA | `ce0eb82eef63` |
| Image tag | `prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Image URI | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Digest | `sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Build ID | `84ab90b6-97d4-4e8f-8a1a-9b3028380b86` |
| Build status | `SUCCESS` |

Candidate warning:

- The image was built from the reviewed local source tree while it was dirty.
- `pipeline_execution.log` remains a tracked modified file and should be excluded or explicitly reviewed before merge.
- This is not a production deploy blocker by itself, but it is a release packaging warning.

## Current Production Baseline

Captured with read-only `gcloud run services describe`.

| Field | Value |
| --- | --- |
| Service | `nfl-studio-dashboard` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| URL | `https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app` |
| Latest ready revision | `nfl-studio-dashboard-00074-26x` |
| Latest created revision | `nfl-studio-dashboard-00074-26x` |
| Traffic split | `nfl-studio-dashboard-00074-26x=100` |
| Current image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Container concurrency | `80` |
| Timeout seconds | `3600` |
| Ingress | `all` |

Secret handling:

- `GEMINI_API_KEY` is present as a Secret Manager reference.
- No secret values were printed or committed.

## Production Risk Flag State

Current production service risk flags are unset. The app defaults these flags false.

| Flag | Current production value | Required deploy value |
| --- | --- | --- |
| `USE_COMPAT_PLAYER_PROFILES` | `<unset>` | `false` |
| `USE_COMPAT_SLEEPER_WATCH` | `<unset>` | `false` |
| `USE_COMPAT_TRADE_ASSETS` | `<unset>` | `false` |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `<unset>` | `false` |
| `USE_COMPAT_VIEWER_TEAM_CONTEXT` | `<unset>` | `false` |
| `USE_BACKTEST_DASHBOARD` | `<unset>` | `false` |
| `USE_CLAIM_LEDGER_UI` | `<unset>` | `false` |
| `USE_CONTENT_BRIEF_REVIEW_UI` | `<unset>` | `false` |
| `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` | `<unset>` | `false` |
| `DATA_OPS_ALLOW_JOB_TRIGGER` | `<unset>` | `false` |

## Deploy Command Preview

Do not run this command until:

1. Live validate-warehouse proof passes or is formally waived.
2. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is explicitly set by the operator.
3. The release package warning from Phase 21.2 is accepted or resolved.
4. The operator confirms the digest-pinned candidate image.

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false `
  --update-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest
```

Command properties:

- Uses digest-pinned image.
- Does not use `latest`.
- Does not enable `USE_COMPAT_TRADE_PLAYER_HISTORY` in production.
- Does not enable Data Ops Cloud Run Job triggers.
- Does not create Scheduler jobs.

## Rollback Baseline

Rollback to the current production revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00074-26x=100
```

Risk flag cleanup command if a future deploy accidentally enables any risk flag:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars USE_COMPAT_PLAYER_PROFILES,USE_COMPAT_SLEEPER_WATCH,USE_COMPAT_TRADE_ASSETS,USE_COMPAT_TRADE_PLAYER_HISTORY,USE_COMPAT_VIEWER_TEAM_CONTEXT,USE_BACKTEST_DASHBOARD,USE_CLAIM_LEDGER_UI,USE_CONTENT_BRIEF_REVIEW_UI,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS,DATA_OPS_ALLOW_JOB_TRIGGER
```

## Production Decision

`STAGING ONLY`

The all-flags-off production deploy can be reconsidered only after:

1. Live validate-warehouse proof is passed or formally waived.
2. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is set.
3. The release package warning around `pipeline_execution.log` and dirty-tree provenance is accepted or resolved.

## Final Status

`PRODUCTION DEPLOY BLOCKED`

The candidate image is ready for a future preview, and the production rollback baseline is captured. The deploy gate itself does not clear because required live-proof and deploy-authorization preconditions are still missing.
