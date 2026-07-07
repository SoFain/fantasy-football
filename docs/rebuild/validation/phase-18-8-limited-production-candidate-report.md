# Phase 18.8 Limited Production Candidate Report

Date: 2026-06-16

Final status: PRODUCTION PREVIEW ONLY

No production deploy was run. No production service update was run. No traffic changed. No scheduler jobs were created. No Cloud Run Jobs were triggered. No LLM calls were made. No Firebase artifacts were created.

## Purpose

Prepare a limited production deploy using the immutable production-candidate image with all production risk flags off, and execute only if explicitly authorized.

Required authorization:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=true
```

Observed authorization state:

```text
ALLOW_LIMITED_PRODUCTION_DEPLOY=<unset>
```

Because the authorization flag is unset, this phase produced a deployment preview only.

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

```text
deployment safety: pass
unit tests: 298 passed
app.py compile: pass
src and scripts compile: pass
pending migrations: none
validation dry-run: pass, 149 validation files discovered
```

Safety checker confirmed:

- no Firebase artifacts
- no tracked secret files
- no secret content
- required files exist
- feature flags default off
- Pigskin arbitrary SQL remains absent
- `app.py`, `src`, and `scripts` compile

## Production Baseline

Current production service:

```text
project: fantasy-football-498121
region: us-central1
service: nfl-studio-dashboard
url: https://nfl-studio-dashboard-inypcgbx7a-uc.a.run.app
```

Current serving revision:

```text
nfl-studio-dashboard-00074-26x
```

Current production image:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:1a2dfe2
```

Current production digest:

```text
sha256:6447b6f175c1aa2613907b630afeb40d56368ec99210abafacf82d5a94eca57e
```

Current traffic split:

```text
nfl-studio-dashboard-00074-26x: 100 percent
```

Runtime service account:

```text
nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Secret bindings:

```text
GEMINI_API_KEY -> GEMINI_API_KEY:latest
```

Production risk flags:

```text
all unset, which is safe because defaults are false
```

## Immutable Candidate Image

Candidate tag:

```text
prod-candidate-ce0eb82eef63-20260616T181911Z
```

Candidate tag URI:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z
```

Candidate digest URI:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4
```

Artifact Registry verification:

```text
digest: sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4
registry: us-central1-docker.pkg.dev
repository: nfl-studio-repo
slsa_build_level: unknown
```

## Production Deploy Preview

This command was prepared but not executed.

The preview uses the digest URI to avoid mutable tag drift:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run deploy nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image='us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:6d26118c3fdf3ce10d1983a8cfddb05956f65c34463d4ef02bcce47cb37f25c4' `
  --service-account='nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com' `
  --cpu=2 `
  --memory=8Gi `
  --concurrency=80 `
  --timeout=3600 `
  --max-instances=20 `
  --allow-unauthenticated `
  --set-env-vars='BQ_PROJECT=fantasy-football-498121,EXTERNAL_SEARCH_PROVIDER=vertex_ai_search,EXTERNAL_SEARCH_DAILY_LIMIT=10,EXTERNAL_SEARCH_MAX_RESULTS=3,VERTEX_AI_SEARCH_ENGINE_ID=fantasy-football-search-engine,GEMINI_MODEL=gemini-3.5-flash,USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false' `
  --update-secrets='GEMINI_API_KEY=GEMINI_API_KEY:latest'
```

Risk flag state in the preview:

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

## Rollback Plan

Rollback to the current production revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00074-26x=100
```

Fallback rollback to the nearest previous ready revision:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update-traffic nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --to-revisions nfl-studio-dashboard-00073-9wp=100
```

Risk flag cleanup command if a future deploy accidentally enables production risk flags:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run services update nfl-studio-dashboard `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --remove-env-vars USE_COMPAT_PLAYER_PROFILES,USE_COMPAT_SLEEPER_WATCH,USE_COMPAT_TRADE_ASSETS,USE_COMPAT_TRADE_PLAYER_HISTORY,USE_COMPAT_VIEWER_TEAM_CONTEXT,USE_BACKTEST_DASHBOARD,USE_CLAIM_LEDGER_UI,USE_CONTENT_BRIEF_REVIEW_UI,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS,DATA_OPS_ALLOW_JOB_TRIGGER
```

## Production Smoke Test

Not run.

Reason:

```text
production deploy was not authorized and was not executed
```

If authorized later, minimum smoke test:

1. Check `/_stcore/health`.
2. Confirm Streamlit loads.
3. Confirm login or session gate behaves as expected.
4. Confirm Pigskin does not expose arbitrary SQL.
5. Confirm Data Ops Cloud Run Job triggers are disabled.
6. Confirm all production risk flags are false.
7. Confirm rollback is not needed.

## Remaining Warnings

1. `ALLOW_LIMITED_PRODUCTION_DEPLOY` is unset, so production deploy is not authorized.
2. Phase 18.3 fixed staging UI warnings locally, but authenticated staging browser QA after those fixes is still pending.
3. Phase 18.4 live `validate-warehouse` Cloud Run Job proof remains not authorized.
4. Artifact Registry reports `slsa_build_level: unknown`.
5. `gcloud` is still not on PATH. The full `gcloud.cmd` path works.

## Final Decision

```text
PRODUCTION PREVIEW ONLY
```

The candidate image exists, baseline and rollback are captured, and preflight checks pass. Production was not deployed because explicit production authorization is absent and staging browser QA after the local UI fixes remains pending.
