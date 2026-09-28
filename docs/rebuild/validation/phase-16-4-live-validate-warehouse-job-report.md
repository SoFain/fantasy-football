# Phase 16.4 Live Validate Warehouse Job Report

Date: 2026-06-16

Final decision: LIVE JOB TEST NOT AUTHORIZED

## Goal

Run one narrowly scoped live Cloud Run Job test for `validate-warehouse`, only if all live authorization gates are present.

## Gcloud Status

Plain `gcloud` command status:

```text
gcloud is not on PATH in this shell.
```

Installed SDK command used for inspection:

```text
C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd
```

SDK version:

```text
Google Cloud SDK 572.0.0
bq 2.1.32
core 2026.06.05
gcloud-crc32c 1.0.0
gsutil 5.37
```

Authenticated account:

```text
sofain@gmail.com
```

Confirmed target project:

```text
fantasy-football-498121
```

Confirmed target region for preview:

```text
us-central1
```

## Authorization Status

Required live gates:

```text
ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=<unset>
CLOUD_RUN_JOBS_IMAGE=<unset>
CLOUD_RUN_JOB_SERVICE_ACCOUNT=<unset>
CLOUD_RUN_PROJECT=<unset>
CLOUD_RUN_REGION=<unset>
BQ_PROJECT=<unset>
BQ_DATASET=<unset>
```

Live deployment and trigger were not authorized because:

1. `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` was not set.
2. `CLOUD_RUN_JOBS_IMAGE` was not set.
3. `CLOUD_RUN_JOB_SERVICE_ACCOUNT` was not set and no waiver was provided.

No live Cloud Run Job deploy was run.

No Cloud Run Job execution was triggered.

No scheduler jobs were created.

No IAM changes were made.

No LLM calls were made.

No Firebase artifacts were created.

## Local Preflight

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

- Deployment safety check: passed.
- Unit tests: passed, 285 tests.
- `app.py` compile: passed.
- `src` and `scripts` compile: passed.

## Dry-Run Deploy Preview

Dry-run preview command:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 `
  --job-name validate-warehouse `
  --dry-run `
  --project fantasy-football-498121 `
  --region us-central1 `
  --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959 `
  --service-account nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Preview output:

```text
Project: fantasy-football-498121
Region: us-central1
Dataset: fantasy_football_brain
Image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959
Dry run: True
Run after deploy: False
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:staging-81ed959 --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain --service-account nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

The dry-run preview was limited to `validate-warehouse`.

Warning: this deploy preview does not include a narrow validation `--pattern` in the job args. Before a live execution, the trigger path should pass a bounded pattern such as `model_runs` or `^096_` through a safe override path.

## Existing Cloud Run Jobs

Read-only Cloud Run Jobs list:

```text
materialize-ai-vibes
```

No `validate-warehouse` Cloud Run Job resource was deployed during this phase.

## Trigger Status

No trigger command was run.

No Cloud Run execution was created.

No Cloud logs for a new execution exist because no execution was started.

No job cost or bytes processed were produced by this phase.

## BigQuery Metadata

No new `cloud_run_job_runs` metadata row was expected or created because no live job was triggered.

Existing latest `validate-warehouse` metadata row:

```text
job_run_id=validate-warehouse-20260616T133114Z-5e7c51a8
status=running
started_at=2026-06-16T13:31:14.856847Z
finished_at=None
error_message=None
metadata_json.dry_run=true
metadata_json.pattern=^096_
```

This is the previously documented local dry-run metadata artifact, not a new live Cloud Run execution.

## Cloud Run Job Validation

Command run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

```text
8 passed, 0 failed
```

Validation files passed:

- `096_cloud_run_job_runs_grain.sql`
- `097_cloud_run_job_runs_status_values.sql`
- `098_cloud_run_job_runs_finished_has_duration.sql`
- `099_cloud_run_job_runs_failed_has_error.sql`
- `100_cloud_run_job_runs_model_run_join.sql`
- `136_cloud_run_job_runs_recent_status.sql`
- `137_cloud_run_job_runs_failed_has_error.sql`
- `138_cloud_run_job_runs_unknown_jobs.sql`

## Rollback

No rollback is required because no job was deployed and no execution was triggered.

If a future authorized deployment creates `validate-warehouse`, remove it with:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run jobs delete validate-warehouse `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --quiet
```

## Required Next Attempt Inputs

Set or explicitly document these before the next live attempt:

```powershell
$env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST="true"
$env:CLOUD_RUN_JOBS_IMAGE="us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:<approved-tag>"
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT="nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com"
$env:CLOUD_RUN_PROJECT="fantasy-football-498121"
$env:CLOUD_RUN_REGION="us-central1"
$env:BQ_PROJECT="fantasy-football-498121"
$env:BQ_DATASET="fantasy_football_brain"
```

Also confirm the live trigger path can pass a narrow validation pattern before execution.

## Final Decision

LIVE JOB TEST NOT AUTHORIZED

The repo and local validation posture are healthy, and the `validate-warehouse` dry-run deployment command shape is correct for a single job. The live test is blocked until the required authorization env vars, image, and service account gate are explicitly set or waived.
