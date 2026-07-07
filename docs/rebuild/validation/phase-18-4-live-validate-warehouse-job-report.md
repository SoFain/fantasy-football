# Phase 18.4 Live Validate-Warehouse Job Report

Date: 2026-06-16

Final decision: LIVE VALIDATE-WAREHOUSE NOT AUTHORIZED

## Scope

Attempted to prove the live Cloud Run Jobs path for only `validate-warehouse` using a narrow validation pattern.

No live job was deployed. No live job was triggered. No scheduler jobs were created. No IAM changes were made. No LLM calls were made. No scraping occurred. No Firebase artifacts were created.

## GCloud Status

`gcloud` is not on PATH in this shell.

Full path works:

```text
C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd
```

Version:

```text
Google Cloud SDK 572.0.0
bq 2.1.32
core 2026.06.05
gcloud-crc32c 1.0.0
gsutil 5.37
```

Active account:

```text
sofain@gmail.com
```

Active project:

```text
fantasy-football-498121
```

## Authorization State

Required live authorization environment:

| Setting | State |
|---|---|
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` | missing |
| `CLOUD_RUN_JOBS_IMAGE` | missing |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | missing |
| `CLOUD_RUN_PROJECT=fantasy-football-498121` | missing |
| `CLOUD_RUN_REGION=us-central1` | missing |
| `BQ_PROJECT=fantasy-football-498121` | missing |
| `BQ_DATASET=fantasy_football_brain` | missing |
| `gcloud` authenticated | pass through full path |

Because the authorization gate is not satisfied, live deploy and live trigger were intentionally skipped.

## Image And Service Account Used For Dry-Run Preview

Immutable image previewed:

```text
us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z
```

Service account previewed:

```text
nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

This service account was used only in the dry-run command preview. No service account binding or IAM change was made.

## Preflight Results

Commands run:

```text
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

```text
deployment safety: pass
unit tests: 296 passed
app.py compile: pass
src and scripts compile: pass
```

Safety checker confirmed:

- no Firebase artifacts
- no tracked secret files
- no secret content
- required files exist
- feature flags default off
- Pigskin arbitrary SQL remains absent
- app, src, and scripts compile

## Dry-Run Deploy Preview

Command run:

```powershell
$image = "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z"
$serviceAccount = "nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com"
.\scripts\deploy_cloud_run_jobs.ps1 `
  --job-name validate-warehouse `
  --dry-run `
  --project fantasy-football-498121 `
  --region us-central1 `
  --dataset fantasy_football_brain `
  --image $image `
  --service-account $serviceAccount
```

Previewed command:

```text
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain --service-account nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Dry-run checks:

- Only `validate-warehouse` was previewed.
- Image tag is immutable.
- Service account is explicit.
- `BQ_PROJECT` and `BQ_DATASET` are set.
- No secrets are bound.
- No scheduler jobs are created.
- No live command was executed.

## Narrow Trigger Preview

Live trigger was not run.

Previewed narrow execute command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run jobs execute validate-warehouse `
  --project fantasy-football-498121 `
  --region us-central1 `
  --wait `
  --args --job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain,--pattern,model_runs
```

Intended validation pattern:

```text
model_runs
```

The job runner supports this narrow pattern through `src.job_runner --job-name validate-warehouse --pattern model_runs`, which dispatches to `scripts/run_bigquery_validations.py --run --pattern model_runs`.

## Live Deploy Command

Not run.

Reason:

```text
authorization environment missing
```

## Live Trigger Command

Not run.

Reason:

```text
authorization environment missing
```

## Execution Result

No Cloud Run Job execution was created.

Cloud Run execution ID:

```text
none
```

Status:

```text
not run
```

Duration:

```text
none
```

Logs summary:

```text
none, no live execution
```

No secrets appeared in local command output.

## Metadata Result

Because no live trigger occurred, no new `cloud_run_job_runs` row was expected.

Cloud Run job metadata validation was run:

```text
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

```text
8 passed, 0 failed
```

## Rollback Command

No rollback is required because no live Cloud Run Job was deployed or triggered.

If a future authorized deploy needs rollback, delete or redeploy only the `validate-warehouse` job:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run jobs delete validate-warehouse `
  --project fantasy-football-498121 `
  --region us-central1
```

or redeploy the previous approved immutable image tag for only `validate-warehouse`.

## Required State For A Live Retry

Before rerunning this phase live, set:

```powershell
$env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST = "true"
$env:CLOUD_RUN_JOBS_IMAGE = "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:prod-candidate-ce0eb82eef63-20260616T181911Z"
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT = "nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com"
$env:CLOUD_RUN_PROJECT = "fantasy-football-498121"
$env:CLOUD_RUN_REGION = "us-central1"
$env:BQ_PROJECT = "fantasy-football-498121"
$env:BQ_DATASET = "fantasy_football_brain"
```

Then rerun the same preflight before deploying.

## Final Decision

LIVE VALIDATE-WAREHOUSE NOT AUTHORIZED

The dry-run deploy and narrow trigger previews are valid. Local preflight and Cloud Run job metadata validations passed. Live proof remains blocked until the operator sets the required authorization environment and explicitly approves execution.
