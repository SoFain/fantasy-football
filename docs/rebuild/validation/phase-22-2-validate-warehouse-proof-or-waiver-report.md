# Phase 22.2 Validate-Warehouse Proof Or Waiver Report

## Decision

`LIVE VALIDATE-WAREHOUSE STILL BLOCKED`

The local environment passed preflight checks and `gcloud` is available with the expected project, but all required live proof environment gates are unset. No formal waiver details were supplied.

Because authorization is incomplete, this phase did not run a deploy preview, did not deploy or update `validate-warehouse`, and did not trigger any Cloud Run Job.

## Scope

Only `validate-warehouse` was in scope.

Not performed:

- no production deploy;
- no broad Cloud Run Job deploy;
- no Cloud Run Job trigger;
- no Scheduler job creation;
- no IAM change;
- no LLM call;
- no scraping;
- no Firebase artifact creation;
- no full validation catalog inside Cloud Run.

## Local Preflight

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

| Check | Result |
| --- | --- |
| Deployment safety | pass |
| Full unittest discovery | pass, 314 tests |
| `app.py` compile | pass |
| `src` and `scripts` compile | pass |
| Pending migrations | none |
| Validation dry-run | pass, validation catalog discovered |

Safety checker details:

| Check | Result |
| --- | --- |
| No Firebase artifacts | pass |
| No tracked secret files | pass |
| No secret content | pass |
| Required files exist | pass |
| Feature flags default off | pass |
| Pigskin `execute_bigquery_sql` absent | pass |
| `app.py` compiles | pass |
| `src` and `scripts` compile | pass |

## gcloud Status

`gcloud` was not available through the plain command path in this shell, but the documented full path worked:

```text
C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd
```

Results:

| Check | Result |
| --- | --- |
| Cloud SDK version | `572.0.0` |
| Active account | `sofain@gmail.com` |
| Active project | `fantasy-football-498121` |
| Expected project match | pass |

Non-blocking note:

- `gcloud --version` reported available component updates.

## Authorization State

Required live proof gates:

| Gate | Observed state |
| --- | --- |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | `<unset>` |
| `CLOUD_RUN_JOBS_IMAGE` | `<unset>` |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | `<unset>` |
| `CLOUD_RUN_PROJECT` | `<unset>` |
| `CLOUD_RUN_REGION` | `<unset>` |
| `BQ_PROJECT` | `<unset>` |
| `BQ_DATASET` | `<unset>` |

Required values for a future live proof:

```powershell
$env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST = "true"
$env:CLOUD_RUN_JOBS_IMAGE = "<immutable-or-digest-pinned-image>"
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT = "<service-account-or-explicit-waiver>"
$env:CLOUD_RUN_PROJECT = "fantasy-football-498121"
$env:CLOUD_RUN_REGION = "us-central1"
$env:BQ_PROJECT = "fantasy-football-498121"
$env:BQ_DATASET = "fantasy_football_brain"
```

Because all live gates are unset, live proof is not authorized.

## Candidate Image Context

Latest verified production candidate from Phase 21.3:

| Field | Value |
| --- | --- |
| Image tag | `prod-candidate-ce0eb82eef63-20260617T033954Z` |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:cc61f7e54de4db9c1b2ff0cd7e1e276ed48dd672610b7628a2ee46dbc0cace31` |
| Build ID | `84ab90b6-97d4-4e8f-8a1a-9b3028380b86` |
| Build status | `SUCCESS` |
| Known warning | built from dirty local source tree |

This image was not deployed or used in Phase 22.2.

## Dry-Run Preview

Dry-run preview command was not run.

Reason:

- the Phase 22.2 instructions require the deploy preview only after live proof gates are set;
- every required live proof gate was unset.

Expected future preview command after authorization:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --dry-run
```

## Deploy Command

No deploy command was run.

Expected future scope if authorized:

- deploy or update only `validate-warehouse`;
- use an immutable or digest-pinned image;
- use project `fantasy-football-498121`;
- use region `us-central1`;
- use dataset `fantasy_football_brain`;
- use an explicit service account or documented waiver;
- create no Scheduler jobs;
- deploy no other Cloud Run Jobs.

## Trigger Command

No trigger command was run.

Expected future trigger if authorized:

- trigger `validate-warehouse` exactly once;
- use a narrow, low-cost validation pattern such as `model_runs`;
- do not run the full validation catalog inside Cloud Run.

## Execution Result

No live execution occurred.

| Field | Value |
| --- | --- |
| Job name | not run |
| Execution ID | not applicable |
| Status | not applicable |
| Duration | not applicable |
| Logs summary | not applicable |
| Validation pattern | not applicable |
| BigQuery metadata row | not created in this phase |
| Secrets in logs | no live logs inspected because no execution occurred |

## Waiver Status

No waiver was supplied.

Required waiver details if the operator chooses to waive live proof:

| Required detail | Status |
| --- | --- |
| Approver name | missing |
| Date/time | missing |
| Reason | missing |
| Exact risk accepted | missing |
| Release impact | missing |
| Follow-up deadline | missing |
| Whether production may proceed despite waiver | missing |

## Metadata Validation

Command run:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

| Pattern | Result |
| --- | --- |
| `cloud_run_job` | 8 passed, 0 failed |

Validation details:

- `096_cloud_run_job_runs_grain.sql`: pass;
- `097_cloud_run_job_runs_status_values.sql`: pass;
- `098_cloud_run_job_runs_finished_has_duration.sql`: pass;
- `099_cloud_run_job_runs_failed_has_error.sql`: pass;
- `100_cloud_run_job_runs_model_run_join.sql`: pass;
- `136_cloud_run_job_runs_recent_status.sql`: pass;
- `137_cloud_run_job_runs_failed_has_error.sql`: pass;
- `138_cloud_run_job_runs_unknown_jobs.sql`: pass.

## Production Impact

Production remains blocked.

The production deploy gate cannot proceed until one of these happens:

1. The live `validate-warehouse` proof is authorized and passes; or
2. A formal waiver is recorded with approver, reason, exact risk accepted, release impact, and follow-up deadline.

No production deploy was run in this phase.

## Remaining Blockers

| Blocker | Impact |
| --- | --- |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` unset | Blocks live proof |
| `CLOUD_RUN_JOBS_IMAGE` unset | Blocks live proof |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` unset | Blocks live proof unless explicitly waived |
| `CLOUD_RUN_PROJECT` unset | Blocks live proof |
| `CLOUD_RUN_REGION` unset | Blocks live proof |
| `BQ_PROJECT` unset | Blocks live proof |
| `BQ_DATASET` unset | Blocks live proof |
| Formal waiver missing | Blocks production deploy if proof remains unrun |

## Final Status

`LIVE VALIDATE-WAREHOUSE STILL BLOCKED`

The environment is healthy enough to run the proof after authorization is supplied, but Phase 22.2 does not resolve the blocker because all required live gates are unset and no waiver was provided.
