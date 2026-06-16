# Data Ops Cloud Run Jobs Rollout

This guide covers the default-off Cloud Run Jobs path in the Streamlit Data Ops tab.

## Current State

The existing local subprocess buttons remain the active path by default. The Cloud Run Jobs panel is a transition control surface that can list configured jobs, validate args, preview the `gcloud run jobs execute` command, and show recent job metadata.

## Feature Flags

Default values:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
CLOUD_RUN_JOBS_ENABLED=true
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Optional environment:

```text
CLOUD_RUN_REGION=us-central1
CLOUD_RUN_PROJECT=fantasy-football-498121
CLOUD_RUN_JOB_SERVICE_ACCOUNT=<job-service-account>
```

Meaning:

- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS` enables the Streamlit Cloud Run Jobs path.
- `CLOUD_RUN_JOBS_ENABLED` is a global kill switch.
- `DATA_OPS_ALLOW_JOB_TRIGGER` permits an explicit button click to trigger a job.
- The dashboard still requires the user confirmation checkbox for every trigger.

## Local Versus Cloud Run Execution

Local subprocess path:

- Runs Python modules in the Streamlit service process context.
- Uses current local or Cloud Run service credentials.
- Remains available while flags are false.

Cloud Run Jobs path:

- Uses `src/cloud_run_jobs.py` to validate the job and allowed args.
- Builds a `gcloud run jobs execute` command.
- Requires `gcloud` to be available for live triggers in the current wrapper path.
- Returns a clear error when `gcloud` is missing.
- Records trigger metadata in `cloud_run_job_runs`.
- Reads recent status from `cloud_run_job_runs`.
- Refuses unknown job names and ad hoc secret env overrides.
- Writes trigger metadata with BigQuery load jobs when available so immediate status updates are not blocked by streaming buffers.

## Exposed Jobs

The Data Ops Cloud Run panel exposes:

- `ingest-nflverse`
- `ingest-sleeper-news`
- `ingest-sleeper-league`
- `ingest-context-events`
- `ingest-market-values`
- `ingest-college-stats`
- `materialize-analytics`
- `generate-pigskin-rankings`
- `generate-evidence-packets`
- `run-projections`
- `run-backtests`
- `validate-warehouse`
- `verify-external-context`
- `generate-content-briefs`
- `grade-claims`

## Expected Job Args

Use JSON in the dashboard input. Examples:

```json
{"season": 2026, "week": 1}
```

```json
{"league-id": "1314636046436151296", "week": 1, "team-name": "Shartnado"}
```

```json
{"season-start": 2023, "season-end": 2025, "week-start": 1, "week-end": 17, "horizon": "weekly"}
```

```json
{"brief-type": "fraud_watch_show", "season": 2026, "week": 1}
```

```json
{"season": 2026, "week": 1, "claim-id": "claim-123"}
```

The helper rejects args that are not listed for the selected job.

For `validate-warehouse`, use the process in [BigQuery Validation Process](bigquery-validation-process.md). Prefer narrow `--pattern` arguments during rollout and do not combine validation with ingestion, materialization, or LLM calls.

## IAM Requirements

The identity that triggers jobs needs:

- Access to a runtime image or operator shell where `gcloud` is installed, until the wrapper moves to the Cloud Run Jobs client library.
- Cloud Run permission to execute jobs in the configured project and region.
- BigQuery job permission to read and write job metadata.
- BigQuery data editor access on the dataset that contains `cloud_run_job_runs`.

The Cloud Run Job service account needs whatever each job requires, such as BigQuery read/write, Secret Manager secret access, and external API access.

## Safe Rollout

1. Deploy with defaults. Confirm the panel shows disabled status and local buttons still work.
2. Set `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true` only in a controlled environment.
3. Use dry-run previews for each job and verify the args.
4. Confirm `cloud_run_job_runs` status reads work.
5. Set `DATA_OPS_ALLOW_JOB_TRIGGER=true` only for an operator session.
6. Trigger a low-risk job such as `validate-warehouse` with a narrow pattern.
7. Review `cloud_run_job_runs` and Cloud Run logs.
8. Keep local subprocess buttons until repeated Cloud Run runs are reliable.

## Rollback

Set:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

The dashboard will keep showing local subprocess controls. No table migrations or code rollback are required for this feature path.

## Cost Warnings

- `run-backtests`, `run-projections`, `materialize-analytics`, and `generate-pigskin-rankings` can run BigQuery and model work.
- `verify-external-context` can call external search providers.
- Use bounded args such as `limit`, `pattern`, season, week, and horizon before broad runs.
- Do not enable trigger flags as a permanent default during rebuild.

## Logging Behavior

Every actual trigger records:

- job name
- Cloud Run job name
- trigger status
- sanitized args
- command preview
- project and dataset context
- error message when trigger startup fails

Secrets and sensitive env names are redacted or refused.

New metadata rows should be created through load jobs when the real BigQuery client supports it. Streaming inserts can leave rows in a buffer that cannot be updated immediately, which breaks the start-to-finish status lifecycle.

## Manual QA Checklist

- Data Ops local subprocess buttons remain visible with flags false.
- Cloud Run panel shows configured jobs.
- Invalid job args show a clear warning.
- Dry-run command preview renders without live Cloud Run credentials.
- Trigger button is disabled unless both flags are true and the checkbox is checked.
- Live trigger reports missing `gcloud` clearly if the runtime cannot execute the command.
- Recent job status fails gracefully if IAM is missing.
- No Firebase artifacts are created.

## Deployment Safety Check

Before enabling live job triggers in an environment, run:

```powershell
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

The checker verifies the local hardening prerequisites:

- no tracked Firebase artifacts
- no tracked secret or service account files
- `app.py`, `src`, and `scripts` compile
- deploy scripts exist
- Secret Manager, IAM, and scheduler plans exist
- live Cloud Run Data Ops feature flags default off
- Pigskin arbitrary SQL tooling remains removed

## Phase 14.7 Validate Warehouse Dry Run

Phase 14.7 tested only the `validate-warehouse` rollout path.

Result:

- Safety checks passed.
- Full tests passed.
- Dry-run deployment preview passed.
- Dry-run Data Ops trigger preview passed.
- Live deployment was not run because `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` was not set.
- Live trigger was not run.
- No scheduler jobs were created.
- Local `gcloud` was not installed, so a future live test must run from an environment with `gcloud` or move the trigger path to a Cloud Run Jobs client library.

See [phase-14-7-cloud-run-validate-warehouse-test.md](validation/phase-14-7-cloud-run-validate-warehouse-test.md).

## Phase 15.1 Cleanup Note

The local dry-run Data Ops metadata row `validate-warehouse-20260616T133114Z-5e7c51a8` remains a known cleanup warning.

Phase 15.1 confirmed:

- the row is a dry-run metadata artifact;
- no Cloud Run execution name exists;
- no live Cloud Run Job was triggered;
- cleanup is still blocked by BigQuery streaming-buffer mutation limits.

Keep live triggers gated by `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true`, `DATA_OPS_ALLOW_JOB_TRIGGER=true`, and explicit user confirmation.

## Phase 15.4 Validate Warehouse Live-Test Result

Phase 15.4 did not deploy or trigger a live Cloud Run Job.

Blocking gates:

- `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` was not set.
- `CLOUD_RUN_JOBS_IMAGE` was not set.
- `CLOUD_RUN_JOB_SERVICE_ACCOUNT` was not set.
- `gcloud` was not installed in the local shell.

Dry-run preview remained available and produced the expected `validate-warehouse` deploy command shape. `cloud_run_job` validations passed after the attempt.

Live trigger rollout remains blocked until those gates are satisfied. See [phase-15-4-live-validate-warehouse-job-report.md](validation/phase-15-4-live-validate-warehouse-job-report.md).
