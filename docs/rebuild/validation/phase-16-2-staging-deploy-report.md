# Phase 16.2 Staging Deploy Report

Date: 2026-06-16

Final status: STAGING DEPLOY PASS WITH WARNINGS

## Goal

Deploy the rebuild branch to a staging-only Cloud Run service with safe defaults, then validate startup and safety controls without touching production.

## Pre-Deploy Checks

Commands run with the repo venv:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Results:

- Deployment safety check: passed.
- Unit tests: passed, 285 tests.
- `app.py` compile: passed.
- `src` and `scripts` compile: passed.
- Migration list-pending: no pending migrations.
- Validation dry-run: passed, 149 validation SQL files discovered.
- Git status before deploy: clean.

## Tooling

- `gcloud` was not on PATH.
- Usable SDK path: `C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd`.
- Google Cloud SDK version: 572.0.0.
- Active account: `sofain@gmail.com`.
- Active project: `fantasy-football-498121`.

## Build

Build command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' builds submit `
  --project=fantasy-football-498121 `
  --config=cloudbuild.yaml `
  --substitutions=_IMAGE_TAG=staging-81ed959,_COMMIT_HASH=81ed959,_VERSION_LABEL=staging-81ed959
```

Result: success.

Build ID: `aed21587-40a0-464c-b99e-25de1e86f384`

Image deployed to staging:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959
```

Image digest:

```text
sha256:c23f17591b8a051c5d809cad6027423aa78fe363a615b1b4648db5b512556f19
```

Warning: the current `cloudbuild.yaml` also pushes the `latest` image tag. No production Cloud Run service was updated, but the Artifact Registry `latest` tag now points to the same digest as `staging-81ed959`.

## Deployment

The existing production service remained:

```text
nfl-studio-dashboard
latest ready revision: nfl-studio-dashboard-00074-26x
```

Staging service deployed:

```text
nfl-studio-dashboard-staging
latest ready revision: nfl-studio-dashboard-staging-00001-vhj
service URL: https://nfl-studio-dashboard-staging-inypcgbx7a-uc.a.run.app
```

Deploy command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959 `
  --region=us-central1 `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --set-env-vars=BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain,DATASET_NAME=fantasy_football_brain,EXTERNAL_SEARCH_PROVIDER=vertex_ai_search,EXTERNAL_SEARCH_DAILY_LIMIT=0,EXTERNAL_SEARCH_MAX_RESULTS=3,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false `
  --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --port=8501 `
  --no-allow-unauthenticated `
  --quiet
```

## Environment And Secrets

Staging environment variables verified from Cloud Run:

```text
BQ_PROJECT=fantasy-football-498121
BQ_DATASET=fantasy_football_brain
DATASET_NAME=fantasy_football_brain
EXTERNAL_SEARCH_PROVIDER=vertex_ai_search
EXTERNAL_SEARCH_DAILY_LIMIT=0
EXTERNAL_SEARCH_MAX_RESULTS=3
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

Secret binding:

```text
GEMINI_API_KEY=GEMINI_API_KEY:latest
```

No LLM calls were made during deployment validation.

## Smoke Test

Cloud Run revision status:

- Revision ready: yes.
- Container healthy: yes.
- Startup probe: passed.
- Streamlit server started on `0.0.0.0:8501`.

Authenticated HTTP checks:

- `GET /`: returned HTTP 200 and Streamlit bootstrap HTML.
- `GET /_stcore/health`: returned HTTP 200 with body `ok`.

Recent logs showed Streamlit startup messages and no startup exceptions.

Browser-level tab QA was not completed. The staging service is private, and the local authenticated Cloud Run proxy could not be used because the SDK `cloud-run-proxy` component is not installed and this session cannot modify the SDK installation directory.

## Safety Verification

Pigskin safety:

- `### Context Tool Protocol ###` remains present in `app.py`.
- Pigskin is still instructed to use parameterized context tools.
- `execute_bigquery_sql` remains absent from Pigskin-visible tools.
- Raw/source table access remains blocked by schema and tests.

Cloud Run Jobs:

- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`.
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`.
- No Cloud Run Jobs were triggered.
- No scheduler jobs were created.

Production:

- Production Cloud Run service was not deployed.
- Production revision remained `nfl-studio-dashboard-00074-26x`.

Firebase:

- No Firebase artifacts were created.

## Rollback

No production rollback is required because production was not changed.

To remove the staging service if needed:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services delete nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --quiet
```

To roll staging back after a future staging revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard-staging `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions=<previous-staging-revision>=100
```

## Warnings

1. `gcloud` is installed but not on PATH. Deployment required the full `gcloud.cmd` path.
2. `cloudbuild.yaml` pushes both the staging tag and `latest`. Production was not redeployed, but future cleanup should split staging builds from the shared `latest` tag.
3. Full browser-level tab verification was not completed because the local Cloud Run proxy component is unavailable.
4. Staging deploy used a newly created separate service name, `nfl-studio-dashboard-staging`, because no concrete staging service name was already documented.

## Decision

STAGING DEPLOY PASS WITH WARNINGS

The staging service is deployed, private, healthy, and running safe default flags. Production was not updated. The remaining work is browser-level manual QA against the staging URL and cleanup of the build process so staging does not refresh the shared `latest` tag.
