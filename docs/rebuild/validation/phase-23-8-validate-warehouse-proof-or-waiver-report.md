# Phase 23.8 Validate-Warehouse Proof Or Waiver Report

Date: 2026-06-19

## Final Decision

`LIVE VALIDATE-WAREHOUSE STILL BLOCKED`

The current local preflight passed, `gcloud` is available through the documented full SDK path with the expected project, and Cloud Run job metadata validations passed. The live proof was not run because all required authorization gates are unset in this process and no formal waiver was supplied.

No production deploy, broad Cloud Run Job deploy, Cloud Run Job trigger, Scheduler job creation, IAM change, LLM call, scrape, or Firebase artifact creation was performed.

## Scope

Only `validate-warehouse` was in scope.

Not run:

- no production deploy
- no broad Cloud Run Job deployment
- no `validate-warehouse` deploy or update
- no Cloud Run Job trigger
- no Scheduler job creation
- no IAM change
- no LLM call
- no scrape
- no Firebase artifact creation

## Commands Run

Preflight:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run
```

Current gate and metadata checks:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Read-only gcloud checks:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' --version
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' auth list --filter=status:ACTIVE --format='value(account)'
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' config get-value project
```

## Preflight Result

| Check | Result |
| --- | --- |
| Deployment safety | pass |
| Unit tests | pass, 343 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Pending migrations | none |
| Validation dry-run | pass, 160 validation files discovered |

Safety checker details:

| Check | Result |
| --- | --- |
| No Firebase artifacts | pass |
| No tracked secret files | pass |
| No detected secret content | pass |
| Required files exist | pass |
| Feature flags default off | pass |
| Pigskin `execute_bigquery_sql` absent | pass |
| `app.py` compiles | pass |
| `src` and `scripts` compile | pass |

Unit test output included existing mocked job, load, pipeline, and ranking logs. No live ingestion, live Cloud Run Job, production deploy, scrape, or LLM call was run by this phase.

## Gcloud Status

Plain `gcloud` was not required. The documented full path was used:

```text
C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd
```

Observed:

| Item | Result |
| --- | --- |
| Google Cloud SDK | `572.0.0` |
| Active account | `sofain@gmail.com` |
| Active project | `fantasy-football-498121` |
| Expected project match | pass |

## Authorization State

Required live proof gates:

| Gate | Required | Observed |
| --- | --- | --- |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | `true` | `<unset>` |
| `CLOUD_RUN_JOBS_IMAGE` | clean digest-pinned image | `<unset>` |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | service account or explicit waiver | `<unset>` |
| `CLOUD_RUN_PROJECT` | `fantasy-football-498121` | `<unset>` |
| `CLOUD_RUN_REGION` | `us-central1` | `<unset>` |
| `BQ_PROJECT` | `fantasy-football-498121` | `<unset>` |
| `BQ_DATASET` | `fantasy_football_brain` | `<unset>` |

Because authorization is incomplete, the live proof is not authorized.

## Waiver Status

No formal waiver was supplied.

Required waiver details remain missing:

| Required detail | Status |
| --- | --- |
| Approver | missing |
| Date/time | missing |
| Reason | missing |
| Exact risk accepted | missing |
| Release impact | missing |
| Follow-up deadline | missing |
| Whether production may proceed despite waiver | missing |

## Dry-Run Preview

The validate-warehouse deploy dry-run preview was not run.

Reason:

- Phase 23.8 requires the live proof gates before proceeding to the dry-run preview path.
- All required live proof gates are unset.

Expected command after authorization:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --dry-run
```

## Deploy And Trigger Result

No deploy or trigger was run.

| Field | Result |
| --- | --- |
| Job name | `validate-warehouse`, not deployed |
| Execution ID | not created |
| Status | not applicable |
| Duration | not applicable |
| Logs summary | not applicable |
| Validation pattern | not run |
| Metadata row | no new row expected |
| Error | not applicable |

## Cloud Run Job Metadata Validation

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

| Pattern | Result |
| --- | --- |
| `cloud_run_job` | 8 passed, 0 failed |

Validation files passed:

- `096_cloud_run_job_runs_grain.sql`
- `097_cloud_run_job_runs_status_values.sql`
- `098_cloud_run_job_runs_finished_has_duration.sql`
- `099_cloud_run_job_runs_failed_has_error.sql`
- `100_cloud_run_job_runs_model_run_join.sql`
- `136_cloud_run_job_runs_recent_status.sql`
- `137_cloud_run_job_runs_failed_has_error.sql`
- `138_cloud_run_job_runs_unknown_jobs.sql`

## Production Impact

Production remains blocked on this proof or a formal waiver.

Production may proceed only after one of the following occurs:

1. The operator authorizes and runs a live `validate-warehouse` proof with all required gates set.
2. The operator supplies a formal waiver with approver, date/time, reason, exact risk accepted, release impact, follow-up deadline, and explicit permission for production to proceed despite the waiver.

Future authorized proof requirements:

```powershell
$env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST = "true"
$env:CLOUD_RUN_JOBS_IMAGE = "<clean digest-pinned image>"
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT = "<service account or explicit waiver>"
$env:CLOUD_RUN_PROJECT = "fantasy-football-498121"
$env:CLOUD_RUN_REGION = "us-central1"
$env:BQ_PROJECT = "fantasy-football-498121"
$env:BQ_DATASET = "fantasy_football_brain"
```

Future live proof must still:

- deploy or update only `validate-warehouse`
- use a digest-pinned image
- trigger exactly once
- use the narrow `model_runs` validation pattern
- create no Scheduler jobs
- deploy no broad Cloud Run Job set
- expose no secret values in logs

## Acceptance Criteria

| Criterion | Status |
| --- | --- |
| no production deploy | pass |
| only `validate-warehouse` touched if run | not run because gates missing |
| no Scheduler jobs | pass |
| no broad Cloud Run Jobs | pass |
| no LLM calls | pass |
| no Firebase artifacts | pass |
