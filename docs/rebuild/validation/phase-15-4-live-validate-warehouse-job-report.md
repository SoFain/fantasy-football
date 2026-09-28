# Phase 15.4 Live Validate Warehouse Job Report

Date: 2026-06-16

Decision: NO-GO for live deployment from this local environment

## Scope

Phase 15.4 attempted the authorized live test path for only one Cloud Run Job:

- `validate-warehouse`

No other jobs were deployed or triggered. No scheduler jobs were created. No LLM calls were made. No Firebase artifacts were created.

## Authorization Status

Required live-test gates:

| Gate | Status |
| --- | --- |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` | missing |
| `CLOUD_RUN_JOBS_IMAGE` | missing |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | missing |
| `gcloud` installed | missing |
| `gcloud` authenticated | not checkable because `gcloud` is missing |

Live deployment and trigger were blocked.

## Preflight Results

Commands:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

- Deployment safety checker: pass.
- Unit tests: 285 passed.
- `app.py` compile: pass.
- `src` and `scripts` compile: pass.

## gcloud Status

Commands attempted:

```powershell
gcloud --version
gcloud auth list
gcloud config get-value project
```

Result:

```text
gcloud : The term 'gcloud' is not recognized as the name of a cmdlet, function, script file, or operable program.
```

Live Cloud Run deployment and execution cannot be run from this shell until the Google Cloud CLI is installed and authenticated.

## Dry-Run Preview

Because `CLOUD_RUN_JOBS_IMAGE` is missing, the dry-run script was run with an explicit placeholder image to prove the command shape without deploying:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --dry-run --image PLACEHOLDER_IMAGE_REQUIRED
```

Previewed command:

```powershell
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image PLACEHOLDER_IMAGE_REQUIRED --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain
```

This was dry-run only. It did not call `gcloud`, deploy a job, or trigger a job.

## Live Deploy Command

Not run.

Blocked by:

- missing `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true`
- missing `CLOUD_RUN_JOBS_IMAGE`
- missing `CLOUD_RUN_JOB_SERVICE_ACCOUNT` or explicit decision to use the default
- missing local `gcloud`

## Live Trigger Command

Not run.

The intended narrow live trigger, after deployment and authorization, should be a bounded validation pattern such as:

```powershell
gcloud run jobs execute validate-warehouse --project fantasy-football-498121 --region us-central1 --args "-m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain,--pattern,model_runs"
```

Confirm the exact Cloud Run Jobs argument override syntax in the target shell before running this command.

## Execution Status

No Cloud Run execution was created.

No new `cloud_run_job_runs` row was expected from Phase 15.4 because no live trigger ran.

## Validation After Attempt

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

- 8 passed.
- 0 failed.

## Logs Summary

No live Cloud Run logs exist for Phase 15.4 because no live execution was started.

Local dry-run and validation logs contained no secrets.

## Rollback Instructions

No rollback is needed for Phase 15.4 because nothing was deployed.

If a future live deployment is created and must be removed:

```powershell
gcloud run jobs delete validate-warehouse --project fantasy-football-498121 --region us-central1
```

If only a job update must be rolled back, redeploy the prior known-good image:

```powershell
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image <previous-known-good-image>
```

## Next Live-Test Requirements

Before retrying Phase 15.4:

1. Install and authenticate `gcloud`.
2. Set `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true`.
3. Set `CLOUD_RUN_JOBS_IMAGE` to the exact Artifact Registry image.
4. Set `CLOUD_RUN_JOB_SERVICE_ACCOUNT`, or document that the default service account is intentionally used.
5. Deploy only `validate-warehouse`.
6. Trigger only one narrow validation pattern, preferably `model_runs`.
7. Confirm `cloud_run_job_runs` records the live execution.

## Final Classification

Live job path: NO-GO from this local environment.

Dry-run path: GO.
