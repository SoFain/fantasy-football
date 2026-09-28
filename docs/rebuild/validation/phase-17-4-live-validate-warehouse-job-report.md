# Phase 17.4 Live Validate-Warehouse Cloud Run Job Report

Date: 2026-06-16

Final decision: LIVE VALIDATE-WAREHOUSE NOT AUTHORIZED

## Purpose

Prove the live Cloud Run Job path for only `validate-warehouse` using a narrow, low-cost validation pattern.

No live Cloud Run Job was deployed or triggered in this phase because the authorization gate was not satisfied.

## Authorization State

Required environment state:

| Setting | Status |
|---|---|
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` | Missing |
| `CLOUD_RUN_JOBS_IMAGE` | Missing |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | Missing, no waiver supplied |
| `CLOUD_RUN_PROJECT=fantasy-football-498121` | Missing |
| `CLOUD_RUN_REGION=us-central1` | Missing |
| `BQ_PROJECT=fantasy-football-498121` | Missing |
| `BQ_DATASET=fantasy_football_brain` | Missing |
| `gcloud` available and authenticated | Missing from PATH |

Because these gates failed, deployment and live execution were intentionally skipped.

## Tooling Check

`gcloud` check:

```text
gcloud=<missing from PATH>
```

The local shell cannot deploy or execute Cloud Run Jobs until Google Cloud SDK is installed or added to PATH and authenticated.

## Local Preflight

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

- Deployment safety checker: pass.
- Unit tests: 290 tests passed.
- `app.py` compile: pass.
- `src` and `scripts` compile: pass.

## Dry-Run Deploy Preview

Dry-run command used:

```powershell
$tag = .\venv\Scripts\python.exe scripts\build_image_tag.py --channel staging
$image = "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:$tag"
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --dry-run --image $image --project fantasy-football-498121 --region us-central1 --dataset fantasy_football_brain
```

Previewed job:

```text
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-8dd0dbf68f67-20260616T163819Z --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain
```

Dry-run findings:

- Only `validate-warehouse` was previewed.
- The image tag was immutable and staging-style.
- `BQ_PROJECT` and `BQ_DATASET` were set.
- No secrets were bound.
- No scheduler jobs were created.
- No live command was executed.
- Service account was not included because `CLOUD_RUN_JOB_SERVICE_ACCOUNT` was not set and no waiver was supplied.

## Narrow Trigger Preview

The deploy script defines the Cloud Run Job. The narrow validation pattern is supplied at execute time through job args.

Dry-run execute preview:

```text
gcloud run jobs execute validate-warehouse --region us-central1 --project fantasy-football-498121 --format=json --args --job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain,--pattern,model_runs
```

This would run `validate-warehouse` with `--pattern model_runs`, not the full validation catalog.

## Live Deploy Command

Not run. Authorization was missing.

## Live Trigger Command

Not run. Authorization was missing.

## Execution Result

No Cloud Run execution was created.

## Metadata Result

No new `cloud_run_job_runs` row was expected because no live trigger occurred.

Existing Cloud Run Job metadata validations were run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

- 8 passed, 0 failed.

## Rollback Command

No rollback is required because no live deploy or trigger occurred.

If a future authorized deploy fails, roll back by deleting or updating only the `validate-warehouse` job:

```powershell
gcloud run jobs delete validate-warehouse --project fantasy-football-498121 --region us-central1
```

or redeploy the prior approved immutable image tag.

## Required Next Attempt State

Before rerunning a live proof:

```powershell
$env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST = "true"
$env:CLOUD_RUN_JOBS_IMAGE = "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:<immutable-tag>"
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT = "<service-account>"
$env:CLOUD_RUN_PROJECT = "fantasy-football-498121"
$env:CLOUD_RUN_REGION = "us-central1"
$env:BQ_PROJECT = "fantasy-football-498121"
$env:BQ_DATASET = "fantasy_football_brain"
```

Also install or expose `gcloud` on PATH and authenticate it to `fantasy-football-498121`.

## Final Decision

LIVE VALIDATE-WAREHOUSE NOT AUTHORIZED

The dry-run deploy and narrow trigger previews are valid, and local checks passed. The live proof remains blocked by missing authorization environment variables, missing explicit service account or waiver, and missing `gcloud`.
