# Phase 19.7 Limited Production Deploy Report

Date: 2026-06-16

Final decision: PRODUCTION PREVIEW ONLY

No production deploy was run. No Cloud Run service was updated. No production traffic changed. No Scheduler jobs were created. No Cloud Run Jobs were triggered. No LLM calls were made. No Firebase artifacts were created.

## Authorization State

Required authorization:

- `ALLOW_LIMITED_PRODUCTION_DEPLOY=true`

Observed state:

- `ALLOW_LIMITED_PRODUCTION_DEPLOY=<unset>`

Because explicit production authorization was not set, this phase produced a command preview only.

## Preflight Results

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
- tests: pass, `304 tests`
- `app.py` compile: pass
- `src` and `scripts` compile: pass
- migrations: no pending migrations
- validation dry-run: pass
- Firebase artifacts: none detected
- tracked secrets: none detected
- production feature defaults: safe in code
- Pigskin `execute_bigquery_sql`: absent

## Production Baseline

Source:

- `docs/rebuild/validation/phase-18-2-production-baseline-report.md`

Captured production service:

```text
project: fantasy-football-498121
region: us-central1
service: nfl-studio-dashboard
url: https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app
service account: nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
current ready revision: nfl-studio-dashboard-00074-26x
current image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2
traffic: 100 percent to nfl-studio-dashboard-00074-26x
```

Production risk flags were documented as unset in the baseline report. The app defaults them to false.

## Candidate Image

Source:

- `docs/rebuild/validation/phase-18-1-production-candidate-image-report.md`

Immutable tag:

```text
prod-candidate-ce0eb82eef63-20260616T181911Z
```

Digest-pinned image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4
```

Build status:

```text
IMAGE BUILD PASS
```

## Gate Review

| Gate | Status |
|---|---|
| immutable production-candidate image exists | pass |
| production baseline captured | pass |
| rollback command exists | pass |
| no pending migrations | pass |
| tests pass | pass |
| safety checker passes | pass |
| staging QA rerun passed or warnings accepted | fail |
| live validate-warehouse proof passed or waived | not authorized, not waived |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` | unset |

The production deployment gate is not open.

## Staging QA Status

Source:

- `docs/rebuild/validation/phase-19-2-authenticated-staging-qa-rerun-report.md`

Current staging QA decision:

```text
STAGING QA FAIL
```

Reason:

- staging is still running image tag `staging-81ed959`
- staging does not contain the Phase 18.3 UI fixes
- authenticated browser QA cannot validate the current code until staging is redeployed with a current reviewed image

This is a blocker for production execution.

## Live Validate-Warehouse Status

Source:

- `docs/rebuild/validation/phase-19-3-live-validate-warehouse-job-report.md`

Current decision:

```text
LIVE VALIDATE-WAREHOUSE NOT AUTHORIZED
```

The dry-run preview is valid, and Cloud Run job metadata validations pass, but the live job proof has not been executed or explicitly waived.

## Required Production Flag State

If a later authorized production deploy occurs, all production risk flags must remain false:

```text
USE_COMPAT_PLAYER_PROFILES=false
USE_COMPAT_SLEEPER_WATCH=false
USE_COMPAT_TRADE_ASSETS=false
USE_COMPAT_TRADE_PLAYER_HISTORY=false
USE_COMPAT_VIEWER_TEAM_CONTEXT=false
USE_BACKTEST_DASHBOARD=false
USE_CLAIM_LEDGER_UI=false
USE_CONTENT_BRIEF_REVIEW_UI=false
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Production must not enable `USE_COMPAT_TRADE_PLAYER_HISTORY=true`.

## Deploy Command Preview

Not run.

This is the digest-pinned production deploy command to use only after production authorization and release gates are cleared:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --update-env-vars=USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Notes:

- This command uses the digest-pinned candidate image.
- It explicitly pins all risk flags false.
- It does not enable Cloud Run Job triggers.
- It does not create Scheduler jobs.
- It does not change secret bindings intentionally.
- It should not be run until staging QA is repaired and production approval is explicit.

## Rollback Command

Rollback to the captured current production revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00074-26x=100
```

Risk-flag cleanup command if a future deploy accidentally enables production risk flags:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars USE_COMPAT_PLAYER_PROFILES,USE_COMPAT_SLEEPER_WATCH,USE_COMPAT_TRADE_ASSETS,USE_COMPAT_TRADE_PLAYER_HISTORY,USE_COMPAT_VIEWER_TEAM_CONTEXT,USE_BACKTEST_DASHBOARD,USE_CLAIM_LEDGER_UI,USE_CONTENT_BRIEF_REVIEW_UI,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS,DATA_OPS_ALLOW_JOB_TRIGGER
```

## Production Smoke Result

Not run because no production deploy occurred.

Required smoke tests if a later deploy is authorized:

- health endpoint
- Streamlit loads
- login or session gate
- Pigskin safety
- Data Ops job triggers disabled
- all risk flags false

## Blockers

1. `ALLOW_LIMITED_PRODUCTION_DEPLOY=true` is not set.
2. Staging QA rerun is currently `STAGING QA FAIL`.
3. The live validate-warehouse job proof remains not authorized and not waived.

## Final Decision

`PRODUCTION PREVIEW ONLY`

The production candidate image is available and preflight passed, but production deploy is not authorized and release gates are not green. Production remains untouched.
