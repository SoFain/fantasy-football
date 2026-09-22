# Phase 17.8 Production Candidate Plan

Date: 2026-06-16

Final recommendation: NOT READY

## Purpose

Prepare a limited production-candidate release plan with all risk flags off.

No production deployment was run. No Cloud Run Jobs were triggered. No scheduler jobs were created. No LLM calls were made. No Firebase artifacts were created.

## Phase 17 Prerequisite Review

| Gate | Status | Evidence |
|---|---|---|
| Authenticated staging QA complete | Pass with warnings | `phase-17-2-authenticated-staging-qa-report.md` reports `STAGING QA PASS WITH WARNINGS` |
| Immutable image tagging ready | Pass | `phase-17-3-immutable-image-tagging-report.md` reports `IMAGE TAGGING READY` |
| Live `validate-warehouse` job path | Deferred | `phase-17-4-live-validate-warehouse-job-report.md` reports `LIVE VALIDATE-WAREHOUSE NOT AUTHORIZED` |
| Real claims | Blocked | `phase-17-5-real-claims-ready-report.md` reports missing operator-supplied claims |
| Real trade review packets | Blocked | `phase-17-6-real-trade-review-packet-report.md` reports missing operator/viewer trade input |
| Current-season Fraud Watch | Blocked | `phase-17-7-current-season-fraud-watch-report.md` reports historical-only source coverage |
| PR merge readiness | Ready after human review | `phase-17-1-pr-artifact-readiness-report.md` reports `READY TO MERGE AFTER HUMAN REVIEW` |
| Staging rollback | Pass | Phase 16 production readiness decision records staging rollback as tested |

## Candidate Image

Candidate image tag:

```text
prod-candidate-57ab102c8656-20260616T165242Z
```

Git SHA:

```text
57ab102c8656
```

Registry URI:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-57ab102c8656-20260616T165242Z
```

Build status:

```text
not built
```

Reason:

```text
gcloud is missing from PATH in this shell.
```

Build command to run later:

```powershell
$tag = "prod-candidate-57ab102c8656-20260616T165242Z"
$shortSha = "57ab102c8656"
gcloud builds submit `
  --config cloudbuild.yaml `
  --substitutions "_IMAGE_TAG=$tag,_COMMIT_HASH=$shortSha,_VERSION_LABEL=$tag"
```

The current `cloudbuild.yaml` publishes only the explicit `_IMAGE_TAG`; it does not publish `latest`.

## Target Service

Target production service:

```text
nfl-studio-dashboard
```

Project:

```text
fantasy-football-498121
```

Region:

```text
us-central1
```

Current production service metadata was not refreshed in this phase because `gcloud` is unavailable locally.

## Required Production Flag State

All risk flags must remain false:

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

Production must not use the staging-only Trade History flag.

## Pre-Release Checks

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

- Deployment safety checker: pass.
- Unit tests: 290 passed.
- `app.py` compile: pass.
- `src` and `scripts` compile: pass.
- BigQuery migrations: no pending migrations.
- BigQuery validation dry-run: pass, 149 validation files discovered.

## Production Deployment Command

Do not execute without explicit operator approval.

Before deploy, capture current production service state:

```powershell
gcloud run services describe nfl-studio-dashboard `
  --project fantasy-football-498121 `
  --region us-central1 `
  --format export > production-before-phase-17-8.yaml
```

Deploy command:

```powershell
$image = "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-57ab102c8656-20260616T165242Z"
$riskFlags = "USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false"
gcloud run deploy nfl-studio-dashboard `
  --project fantasy-football-498121 `
  --region us-central1 `
  --image $image `
  --update-env-vars "BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain,$riskFlags" `
  --no-allow-unauthenticated
```

Notes:

- Use `--update-env-vars` so existing production env vars and Secret Manager bindings are preserved unless explicitly changed.
- Do not pass `--set-secrets` unless the operator confirms a secret binding change is required.
- Do not enable Cloud Run Job trigger flags.
- Do not create scheduler jobs.

## Rollback Command

Capture previous production revision before deployment:

```powershell
gcloud run services describe nfl-studio-dashboard `
  --project fantasy-football-498121 `
  --region us-central1 `
  --format "value(status.latestReadyRevisionName)"
```

Rollback traffic to the previous production revision:

```powershell
gcloud run services update-traffic nfl-studio-dashboard `
  --project fantasy-football-498121 `
  --region us-central1 `
  --to-revisions <previous-production-revision>=100
```

Ensure risk flags are disabled after rollback:

```powershell
$riskFlags = "USE_COMPAT_PLAYER_PROFILES=false,USE_COMPAT_SLEEPER_WATCH=false,USE_COMPAT_TRADE_ASSETS=false,USE_COMPAT_TRADE_PLAYER_HISTORY=false,USE_COMPAT_VIEWER_TEAM_CONTEXT=false,USE_BACKTEST_DASHBOARD=false,USE_CLAIM_LEDGER_UI=false,USE_CONTENT_BRIEF_REVIEW_UI=false,USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false,DATA_OPS_ALLOW_JOB_TRIGGER=false"
gcloud run services update nfl-studio-dashboard `
  --project fantasy-football-498121 `
  --region us-central1 `
  --update-env-vars $riskFlags
```

## Smoke Test Plan

After an approved production deploy:

1. Confirm Cloud Run revision is ready.
2. Confirm `/_stcore/health` returns ok.
3. Confirm the dashboard loads through authenticated access.
4. Confirm Pigskin Studio renders without exposing arbitrary SQL tools.
5. Confirm Show Prep renders and historical Fraud Watch is not presented as current-week production content.
6. Confirm Player Profiles and Versus Finder render, noting known legacy warnings if still present.
7. Confirm Viewer Team Lab renders with legacy path.
8. Confirm Trade Lab renders with `USE_COMPAT_TRADE_PLAYER_HISTORY=false`.
9. Confirm Data Ops renders and Cloud Run Job triggers are disabled.
10. Confirm Claim Ledger and Content Brief Review remain hidden or inactive because their flags are false.
11. Confirm no Cloud Run Jobs or scheduler jobs were created.

## Known Warnings

- Candidate image was not built because `gcloud` is unavailable locally.
- Live `validate-warehouse` Cloud Run Job proof remains deferred.
- Staging QA passed with warnings in legacy Player Profiles, Versus Finder, Show Prep Sleeper Watch, and Trade Lab Side B display behavior.
- Real reviewed claims are still blocked by missing operator-supplied claim text.
- Real Trade Review packets are still blocked by missing operator/viewer trade sides.
- Current-season Fraud Watch remains blocked by missing 2025/2026 upstream source rows.
- Production service metadata was not refreshed in this phase because `gcloud` is unavailable.

## Explicitly Disallowed Actions

- Do not deploy to production without explicit operator approval.
- Do not deploy `latest`.
- Do not enable `USE_COMPAT_TRADE_PLAYER_HISTORY=true` in production.
- Do not enable any other compatibility flag in production.
- Do not enable `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`.
- Do not enable `DATA_OPS_ALLOW_JOB_TRIGGER`.
- Do not create Cloud Scheduler jobs.
- Do not trigger Cloud Run Jobs.
- Do not call LLMs during deployment validation unless explicitly authorized.
- Do not publish demo claims, demo packets, or draft content briefs.
- Do not present historical Fraud Watch as current-week production content.

## Final Recommendation

NOT READY

The release plan is prepared, but the production candidate image is not built and the current production service state could not be captured because `gcloud` is unavailable in this environment. Once `gcloud` is available and authenticated, rerun the build command, record the image digest, capture the current production revision, and then request explicit operator approval before any production deploy.
