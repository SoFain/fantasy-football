# Phase 20.3 Validate-Warehouse Proof Decision Report

Date: 2026-06-16

## Decision

LIVE PROOF BLOCKED

The live `validate-warehouse` Cloud Run Job proof is not authorized in the current environment. It is not waived either, because no waiver approval, approver, accepted risk statement, or follow-up deadline was supplied.

No Cloud Run Job was deployed. No Cloud Run Job was triggered. No Scheduler jobs were created. No IAM changes were made. No LLM calls were made. No scraping occurred. No Firebase artifacts were created.

## Scope

Only this Cloud Run Job was in scope:

```text
validate-warehouse
```

No other Cloud Run Jobs were deployed, updated, previewed for live execution, or triggered.

## Environment Inspection

Cloud SDK:

```text
Google Cloud SDK 572.0.0
bq 2.1.32
core 2026.06.05
gcloud-crc32c 1.0.0
gsutil 5.37
```

Authentication:

```text
ACTIVE  ACCOUNT
*       sofain@gmail.com
```

Active project:

```text
fantasy-football-498121
```

Required live authorization environment:

| Variable | State |
| --- | --- |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | `<unset>` |
| `CLOUD_RUN_JOBS_IMAGE` | `<unset>` |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | `<unset>` |
| `CLOUD_RUN_PROJECT` | `<unset>` |
| `CLOUD_RUN_REGION` | `<unset>` |
| `BQ_PROJECT` | `<unset>` |
| `BQ_DATASET` | `<unset>` |

Because the authorization variables are missing, live deploy and live trigger were intentionally skipped.

## Preflight Checks

Commands run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
.\venv\Scripts\python.exe -m unittest discover tests
.\venv\Scripts\python.exe -m py_compile app.py
.\venv\Scripts\python.exe -m compileall -q src scripts
```

Results:

| Check | Result |
| --- | --- |
| Deployment safety | PASS |
| Full unittest discovery | PASS, 309 tests |
| `app.py` compile | PASS |
| `src` and `scripts` compile | PASS |

Deployment safety details:

| Safety check | Result |
| --- | --- |
| `no_firebase_artifacts` | PASS |
| `no_tracked_secret_files` | PASS |
| `no_secret_content` | PASS |
| `required_files_exist` | PASS |
| `feature_flags_default_off` | PASS |
| `pigskin_no_execute_bigquery_sql` | PASS |
| `app_py_compiles` | PASS |
| `src_scripts_compile` | PASS |

## Dry-Run Preview

Not run in Phase 20.3.

Reason:

- The Phase 20.3 task only calls for dry-run preview if live proof is authorized.
- Live proof is not authorized because the required environment variables are unset.
- Prior Phase 17.4 and Phase 18.4 reports already documented valid dry-run command shapes for `validate-warehouse`.

## Live Execution Details

Not run.

Reason:

- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` was not set.
- `CLOUD_RUN_JOBS_IMAGE` was not set.
- `CLOUD_RUN_JOB_SERVICE_ACCOUNT` was not set and no explicit waiver was supplied.
- `CLOUD_RUN_PROJECT`, `CLOUD_RUN_REGION`, `BQ_PROJECT`, and `BQ_DATASET` were not set in the environment.

No Cloud Run Job execution ID exists for Phase 20.3 because no live job was executed.

## Waiver Status

No waiver was granted.

Required waiver fields were not available:

| Waiver field | Status |
| --- | --- |
| Reason | Not supplied |
| Approver | Not supplied |
| Risk accepted | Not supplied |
| Production release impact | Not supplied |
| Follow-up deadline | Not supplied |

Therefore, the correct decision is blocked rather than waived.

## Release Impact

The live `validate-warehouse` Cloud Run Job path remains an open release warning.

For a limited production deploy with all risk flags off, the operator must either:

1. Authorize and run the live proof using only `validate-warehouse` with a narrow validation pattern, or
2. Provide an explicit waiver with approver, risk accepted, release impact, and follow-up deadline.

## Required Authorization To Proceed Later

Set the required environment explicitly before rerunning this phase:

```powershell
$env:ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST = "true"
$env:CLOUD_RUN_JOBS_IMAGE = "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:<immutable-tag-or-digest>"
$env:CLOUD_RUN_JOB_SERVICE_ACCOUNT = "nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com"
$env:CLOUD_RUN_PROJECT = "fantasy-football-498121"
$env:CLOUD_RUN_REGION = "us-central1"
$env:BQ_PROJECT = "fantasy-football-498121"
$env:BQ_DATASET = "fantasy_football_brain"
```

Then run the dry-run preview first:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --dry-run
```

Live execution must remain limited to:

- Job: `validate-warehouse`
- Pattern: `model_runs` or another known low-cost validation pattern
- No scheduler creation
- No other Cloud Run Jobs
- No IAM mutation unless separately authorized

## Remaining Blockers

1. Required live-proof authorization environment is missing.
2. No explicit service account waiver was supplied.
3. No waiver decision was supplied.

## Final Status

LIVE PROOF BLOCKED

The environment is healthy enough for local preflight, but the live Cloud Run Job proof remains blocked by missing explicit authorization. No production-risk actions were taken.
