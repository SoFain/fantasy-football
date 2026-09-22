# Phase 14.7 Cloud Run Validate Warehouse Test

Date: 2026-06-16

## Purpose

Run the safest Cloud Run Jobs rollout step for `validate-warehouse`, with live deployment and live trigger gated by explicit operator authorization.

## Authorization Status

Required live authorization:

```text
ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true
```

Observed environment:

```text
ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST is not set
```

Decision:

- No live Cloud Run Job deployment was run.
- No live Cloud Run Job trigger was run.
- No scheduler jobs were created.
- No IAM changes were made.
- No LLM calls were made.
- No Firebase artifacts were created.

## Preflight Results

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

- Deployment safety check: passed
- Unit tests: 284 passed
- `app.py` compile: passed
- `src` and `scripts` compile: passed

Safety check details:

- no Firebase artifacts
- no tracked secret files
- no tracked secret content
- required deployment files exist
- feature flags default off
- Pigskin arbitrary SQL remains removed

## Dry-Run Deployment Preview

Environment notes:

- `CLOUD_RUN_JOBS_IMAGE` was not set.
- `CLOUD_RUN_JOB_SERVICE_ACCOUNT` was not set.
- `CLOUD_RUN_PROJECT` was not set.
- `CLOUD_RUN_REGION` was not set.
- `gcloud` is not installed on this workstation, so the current live service image could not be read locally.

Dry-run command used the documented shared image path:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --project fantasy-football-498121 --region us-central1 --dataset fantasy_football_brain --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest --dry-run
```

Previewed command:

```powershell
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain
```

No live deploy was run.

## Data Ops Trigger Preview

Dry-run trigger preview from `src.cloud_run_jobs`:

```text
gcloud run jobs execute validate-warehouse --region us-central1 --project fantasy-football-498121 --format=json --args '--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain,--pattern,^096_'
```

Feature flag defaults:

- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`: false
- `DATA_OPS_ALLOW_JOB_TRIGGER`: false
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` plus global Cloud Run Jobs enabled: false by default

Trigger state:

- Dry-run preview works.
- Live trigger remains disabled by default.
- Live trigger still requires both flags and explicit confirmation.
- No secrets appeared in the preview command.

## Metadata Issue Found And Fixed

A local `src.job_runner --dry-run` command was attempted with:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name validate-warehouse --dry-run --pattern "^096_"
```

This did not deploy or execute a Cloud Run Job, but it did write a `cloud_run_job_runs` metadata start row before failing during the immediate finish update.

BigQuery error:

```text
UPDATE or DELETE statement over table fantasy-football-498121.fantasy_football_brain.cloud_run_job_runs would affect rows in the streaming buffer, which is not supported
```

Root cause:

- `start_job_run()` used `insert_rows_json`.
- `finish_job_run()` immediately updated the same row.
- BigQuery can reject updates against rows still in the streaming buffer.

Fix applied:

- `src/job_runner.py` now uses `load_table_from_json()` for `cloud_run_job_runs` start rows when the real BigQuery client supports it.
- `src/cloud_run_jobs.py` now uses `load_table_from_json()` for Streamlit trigger metadata rows when the real BigQuery client supports it.
- Existing fake clients still use `insert_rows_json` in unit tests.

Tests added:

- `tests.test_job_runner.JobRunnerTests.test_records_start_metadata_with_load_job_when_available`
- `tests.test_cloud_run_jobs.CloudRunJobsTests.test_trigger_metadata_uses_load_job_when_available`

## Metadata State

Read-only metadata check found one row from the failed local dry-run:

- `job_run_id`: `validate-warehouse-20260616T133114Z-5e7c51a8`
- `job_name`: `validate-warehouse`
- `status`: `running`
- `dry_run`: true in `metadata_json`
- `finished_at`: null
- `duration_seconds`: null
- `error_message`: null

A bounded cleanup update was attempted, but BigQuery still rejected it because the row remained in the streaming buffer. No further mutation was attempted.

This row does not represent a Cloud Run execution. It is a metadata artifact from a local dry-run. It should be marked failed once the streaming buffer clears, or ignored in favor of the fixed metadata writer on the next authorized test.

Cloud Run job metadata validations still passed:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

- 8 passed
- 0 failed

## IAM And Service Account

No live job was deployed, so no runtime service account was used.

The dry-run deploy command did not include `--service-account` because `CLOUD_RUN_JOB_SERVICE_ACCOUNT` was not set. Before live deployment, provide the intended least-privilege job service account or set:

```powershell
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT="<service-account-email>"
```

## Rollback

No Cloud Run resource rollback is needed because no live deployment occurred.

If the next authorized test deploys `validate-warehouse`, rollback should be:

```powershell
gcloud run jobs delete validate-warehouse --project fantasy-football-498121 --region us-central1
```

Feature flag rollback:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

## Next Authorized Command Set

Before the next live attempt, set:

```powershell
$env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST="true"
$env:CLOUD_RUN_JOBS_IMAGE="us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest"
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT="<service-account-email>"
```

Then run only:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --project fantasy-football-498121 --region us-central1 --dataset fantasy_football_brain --image $env:CLOUD_RUN_JOBS_IMAGE --service-account $env:CLOUD_RUN_JOB_SERVICE_ACCOUNT --dry-run
```

If the dry-run is correct and `gcloud` is installed:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --project fantasy-football-498121 --region us-central1 --dataset fantasy_football_brain --image $env:CLOUD_RUN_JOBS_IMAGE --service-account $env:CLOUD_RUN_JOB_SERVICE_ACCOUNT
```

Trigger only after separate explicit authorization.

## Decision

GO WITH WARNINGS

The deployment path was proven to the dry-run preview stage only. Live deployment and live trigger are blocked by missing `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true`, missing `gcloud`, and missing explicit runtime service account configuration.
