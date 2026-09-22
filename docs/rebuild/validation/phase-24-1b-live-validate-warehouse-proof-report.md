# Phase 24.1B Live Validate-Warehouse Proof Report

Validation date: 2026-06-19

## Final Decision

`LIVE VALIDATE-WAREHOUSE PASS WITH WARNINGS`

The live `validate-warehouse` Cloud Run Job proof was rerun with the fixed digest-pinned image from Phase 24.1A. The job was deployed/updated only for `validate-warehouse` and triggered exactly once with the narrow `model_runs` validation pattern.

The execution completed successfully. The previous missing path issue for `/app/scripts/run_bigquery_validations.py` is resolved in the fixed image.

Warning: the repository PowerShell deploy script produced a valid dry-run preview, but its live invocation handed the full gcloud command to `gcloud.ps1` as one invalid choice in this local shell. To avoid broad changes and still preserve the reviewed command shape, the live deploy/update used the equivalent full-path `gcloud.cmd run jobs deploy validate-warehouse` command for only this job. No broad job deploy was run.

## Authorization Gates

The following gates were set only inside the live PowerShell execution process:

| Gate | Value |
| --- | --- |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | `true` |
| `CLOUD_RUN_JOBS_IMAGE` | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| `CLOUD_RUN_PROJECT` | `fantasy-football-498121` |
| `CLOUD_RUN_REGION` | `us-central1` |
| `BQ_PROJECT` | `fantasy-football-498121` |
| `BQ_DATASET` | `fantasy_football_brain` |

The gates were removed afterward. Post-run environment checks were empty for:

- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST`
- `CLOUD_RUN_JOBS_IMAGE`
- `CLOUD_RUN_JOB_SERVICE_ACCOUNT`
- `CLOUD_RUN_PROJECT`
- `CLOUD_RUN_REGION`
- `BQ_PROJECT`
- `BQ_DATASET`

## Preflight Results

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 346 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass |

## GCloud Context

| Item | Result |
| --- | --- |
| Google Cloud SDK | `572.0.0` |
| Active account | `sofain@gmail.com` |
| Active project | `fantasy-football-498121` |

## Fixed Image

| Field | Value |
| --- | --- |
| Digest-pinned image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Old failed digest avoided | `sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |

## Dry-Run Preview

Command:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --dry-run
```

Preview result:

- only `validate-warehouse` was included;
- fixed digest-pinned image was used;
- project was `fantasy-football-498121`;
- region was `us-central1`;
- dataset was `fantasy_football_brain`;
- service account was `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`;
- no `--run-after-deploy` path was used;
- no unrelated jobs were included;
- no Scheduler job was created;
- no secret values were printed.

Dry-run command preview:

```text
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29 --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain --service-account nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

## Deploy/Update Command

The live deploy/update used the equivalent single-job full-path gcloud command:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run jobs deploy validate-warehouse `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29 `
  --command=python `
  --args='-m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain' `
  --set-env-vars='BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain' `
  --service-account='nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com' `
  --quiet
```

Post-deploy job state:

| Field | Value |
| --- | --- |
| Job name | `validate-warehouse` |
| Generation | `2` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Command | `python` |
| Args | `-m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Ready condition | `Ready=True` |

## Trigger Command

Exactly one live execution was triggered:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run jobs execute validate-warehouse `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --args='-m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain,--pattern,model_runs' `
  --wait `
  --format=json
```

## Execution Result

| Field | Value |
| --- | --- |
| Cloud Run Job | `validate-warehouse` |
| Execution ID | `validate-warehouse-gwbpg` |
| Status | completed successfully |
| Completion message | `Execution completed successfully in 58.34s.` |
| Started | `2026-06-19T17:26:46.358348Z` |
| Completed | `2026-06-19T17:27:44.706610Z` |
| Succeeded count | `1` |
| Validation pattern | `model_runs` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:24c71dd29ea6796d27e8958f6882c209a68114b95a720ffe5586c2a2f798ca29` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |

The execution args included:

```text
-m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain,--pattern,model_runs
```

## Log Summary

Cloud Run logs for `validate-warehouse-gwbpg` showed:

- job started as `validate-warehouse-20260619T172733Z-e1070248`;
- validation runner used `Validations dir: /app/bigquery/validations`;
- exactly one validation file ran: `005__model_runs_required_columns.sql`;
- validation result was `Validation Run Completed: 1 passed, 0 failed.`;
- job result was `{"pattern":"model_runs","returncode":0,"row_count":0}`;
- container exited with code `0`.

No `/app/scripts/run_bigquery_validations.py` missing-file error appeared. No secret values appeared in the inspected logs or metadata.

## BigQuery Metadata Row

Latest metadata row for this execution:

```json
{
  "job_run_id": "validate-warehouse-20260619T172733Z-e1070248",
  "job_name": "validate-warehouse",
  "cloud_run_job_name": "validate-warehouse",
  "cloud_run_execution_name": "validate-warehouse-gwbpg",
  "status": "success",
  "started_at": "2026-06-19T17:27:33.735808+00:00",
  "finished_at": "2026-06-19T17:27:38.611873+00:00",
  "duration_seconds": 4.876065,
  "error_message": null,
  "metadata_json": "{\"pattern\": \"model_runs\", \"returncode\": 0, \"row_count\": 0}"
}
```

Secret scan of the execution metadata returned:

- failed rows: `0`;
- suspicious error rows: `0`;
- suspicious metadata rows: `0`.

## Metadata Validation

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result:

```text
Validation Run Completed: 8 passed, 0 failed.
```

## Scheduler Status

A read-only Cloud Scheduler list command returned `SERVICE_DISABLED` for `cloudscheduler.googleapis.com`. The API was not enabled and no Scheduler job was created by this phase.

## Production Impact

| Item | Result |
| --- | --- |
| Production deploy | not run |
| Staging deploy | not run |
| Broad Cloud Run Jobs deploy | not run |
| Cloud Run Job touched | only `validate-warehouse` |
| Live executions triggered | exactly one |
| Scheduler job creation | not run |
| IAM change | not run |
| LLM call | not run |
| Scrape | not run |
| Firebase artifacts | none created |
| Production feature flags | unchanged |

## Remaining Warning

The live proof passed, but `scripts/deploy_cloud_run_jobs.ps1` still has a local live invocation issue in this PowerShell environment. Its dry-run preview is correct, but the non-dry-run path failed before the direct gcloud fallback because gcloud progress output and argument passing through `gcloud.ps1` produced an invalid-choice error. This should be hardened before relying on the script for future live deploys.

## Next Step

Phase 24.2 can be rerun against the fixed proof state. The production candidate gate can now treat the live validate-warehouse proof blocker as resolved, subject to the deploy-script warning above.
