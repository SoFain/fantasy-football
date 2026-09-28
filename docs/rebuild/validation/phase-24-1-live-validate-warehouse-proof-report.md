# Phase 24.1 Live Validate-Warehouse Proof Report

Validation date: 2026-06-19

## Final Decision

`LIVE VALIDATE-WAREHOUSE FAIL`

The live proof was authorized, deployed only the `validate-warehouse` Cloud Run Job, and triggered one Cloud Run execution with the narrow `model_runs` validation pattern. The execution failed inside the container because `/app/scripts/run_bigquery_validations.py` is missing from the digest-pinned image.

No production deploy, broad Cloud Run Job deploy, Scheduler job creation, IAM change, LLM call, scrape, ingestion, materialization, or Firebase artifact creation was performed.

## Authorization Gates

The live gates were set only inside the PowerShell command process:

| Gate | Value during proof |
| --- | --- |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | `true` |
| `CLOUD_RUN_JOBS_IMAGE` | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| `CLOUD_RUN_JOB_SERVICE_ACCOUNT` | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| `CLOUD_RUN_PROJECT` | `fantasy-football-498121` |
| `CLOUD_RUN_REGION` | `us-central1` |
| `BQ_PROJECT` | `fantasy-football-498121` |
| `BQ_DATASET` | `fantasy_football_brain` |

After the try/finally blocks, each gate was removed and echoed as empty:

```text
ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=[]
CLOUD_RUN_JOBS_IMAGE=[]
CLOUD_RUN_JOB_SERVICE_ACCOUNT=[]
CLOUD_RUN_PROJECT=[]
CLOUD_RUN_REGION=[]
BQ_PROJECT=[]
BQ_DATASET=[]
```

## Preflight

| Check | Result |
| --- | --- |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 343 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, no pending migrations |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, validation discovery completed |

## gcloud Status

| Item | Result |
| --- | --- |
| SDK | Google Cloud SDK 572.0.0 |
| Active account | `sofain@gmail.com` |
| Active project | `fantasy-football-498121` |

## Dry-Run Preview

Command:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --job-name validate-warehouse --dry-run
```

Preview result:

```text
Project: fantasy-football-498121
Region: us-central1
Dataset: fantasy_football_brain
Image: us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b
Dry run: True
Run after deploy: False
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain --service-account nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Preview assessment:

| Requirement | Result |
| --- | --- |
| only `validate-warehouse` included | pass |
| digest-pinned image used | pass |
| explicit service account used | pass |
| project, region, dataset correct | pass |
| no Scheduler job creation | pass |
| no unrelated jobs deployed | pass |
| no secret values printed | pass |

## Deploy Or Update

The repo PowerShell script preview was valid, but its live invocation was not usable in this local PowerShell environment:

- without a process-local Cloud SDK PATH prepend, the script could not resolve `gcloud`;
- with PATH prepended, the script passed the full command line to `gcloud` in a way that produced `Invalid choice`.

The equivalent direct gcloud command was used for the live update:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run jobs deploy validate-warehouse `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --image=us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b `
  --command=python `
  --args=-m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain `
  --set-env-vars=BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain `
  --service-account=nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --quiet
```

Read-only job describe confirmed the Cloud Run Job exists:

| Field | Value |
| --- | --- |
| Job name | `validate-warehouse` |
| Project | `fantasy-football-498121` |
| Region | `us-central1` |
| Image | `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:b23b67378605068f74e391f6fd21f758033b7f5ff2629778b974d17692ed152b` |
| Command | `python` |
| Args | `-m src.job_runner --job-name validate-warehouse --project fantasy-football-498121 --dataset fantasy_football_brain` |
| Env | `BQ_PROJECT=fantasy-football-498121`, `BQ_DATASET=fantasy_football_brain` |
| Service account | `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com` |
| Max retries | `3` |
| Ready | true |

## Trigger

Exactly one Cloud Run execution was triggered:

```powershell
& 'C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin\gcloud.cmd' run jobs execute validate-warehouse `
  --project=fantasy-football-498121 `
  --region=us-central1 `
  --args=-m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain,--pattern,model_runs `
  --wait `
  --format=json
```

Trigger details:

| Field | Value |
| --- | --- |
| Execution ID | `validate-warehouse-qhwkq` |
| Validation pattern | `model_runs` |
| Start time | `2026-06-19T15:53:08.110457Z` |
| Completion time | `2026-06-19T15:58:38.936261Z` |
| Status | failed |
| Failure reason | `NonZeroExitCode` |
| Failure message | `Task validate-warehouse-qhwkq-task0 failed with exit code: 1 and message: The container exited with an error.` |

Although only one execution was triggered, Cloud Run retried the failed task because the job has `maxRetries=3`. That produced four failed `cloud_run_job_runs` rows for the same execution ID.

## Logs Summary

Cloud Run logs showed no secret values.

Relevant failure:

```text
/usr/local/bin/python: can't open file '/app/scripts/run_bigquery_validations.py': [Errno 2] No such file or directory
```

`src.job_runner` then recorded the subprocess failure:

```text
Command '['/usr/local/bin/python', 'scripts/run_bigquery_validations.py', '--project', 'fantasy-football-498121', '--dataset', 'fantasy_football_brain', '--run', '--pattern', 'model_runs']' returned non-zero exit status 2.
```

Root cause: the digest-pinned image used for this proof can run `src.job_runner`, but it does not contain the `scripts/run_bigquery_validations.py` file at the path expected by `dispatch_validate_warehouse`.

## BigQuery Metadata

Latest metadata row:

| Field | Value |
| --- | --- |
| `job_run_id` | `validate-warehouse-20260619T155828Z-0e14d143` |
| `job_name` | `validate-warehouse` |
| `cloud_run_job_name` | `validate-warehouse` |
| `cloud_run_execution_name` | `validate-warehouse-qhwkq` |
| `status` | `failed` |
| `started_at` | `2026-06-19T15:58:28.735924Z` |
| `finished_at` | `2026-06-19T15:58:31.703374Z` |
| `duration_seconds` | `2.96745` |
| `error_message` | `Command '['/usr/local/bin/python', 'scripts/run_bigquery_validations.py', '--project', 'fantasy-football-498121', '--dataset', 'fantasy_football_brain', '--run', '--pattern', 'model_runs']' returned non-zero exit status 2.` |
| `metadata_json` | `{"error_type": "CalledProcessError"}` |

Other rows from the same execution:

| Job run ID | Status | Duration seconds |
| --- | --- | --- |
| `validate-warehouse-20260619T155718Z-f09cfde9` | failed | `3.763663` |
| `validate-warehouse-20260619T155624Z-46176f6c` | failed | `4.677807` |
| `validate-warehouse-20260619T155431Z-8cde1757` | failed | `3.533303` |

These are task retry rows from the same `validate-warehouse-qhwkq` execution, not separate manual triggers.

## Metadata Validation

Command:

```powershell
.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern cloud_run_job
```

Result: pass, 8 passed, 0 failed.

## Production Impact

| Item | Result |
| --- | --- |
| Production service deploy | not run |
| Staging service deploy | not run |
| Broad Cloud Run Job deploy | not run |
| Scheduler job creation | not run |
| IAM change | not run |
| Cloud Run Job touched | only `validate-warehouse` |
| Cloud Run execution triggered | exactly one execution, `validate-warehouse-qhwkq` |
| LLM call | not run |
| Scrape | not run |
| Firebase artifacts | none created |

## Next Step

Fix the Cloud Run image or job runner path so `validate-warehouse` can invoke validations inside the container. Options:

1. Include `scripts/run_bigquery_validations.py` in the production-candidate image build context.
2. Change `dispatch_validate_warehouse` to call a packaged module path that exists in the container.
3. Add a container smoke test that runs `python scripts/run_bigquery_validations.py --dry-run` or the replacement module path before the next live proof.

Do not retry the live proof until the image/path issue is fixed and a new explicit authorization is supplied.
