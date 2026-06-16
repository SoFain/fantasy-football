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
- Records trigger metadata in `cloud_run_job_runs`.
- Reads recent status from `cloud_run_job_runs`.
- Refuses unknown job names and ad hoc secret env overrides.

## Exposed Jobs

The Data Ops Cloud Run panel exposes:

- `ingest-nflverse`
- `ingest-sleeper-news`
- `ingest-sleeper-league`
- `ingest-market-values`
- `materialize-analytics`
- `generate-pigskin-rankings`
- `generate-evidence-packets`
- `run-projections`
- `run-backtests`
- `validate-warehouse`
- `verify-external-context`

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

The helper rejects args that are not listed for the selected job.

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

## Manual QA Checklist

- Data Ops local subprocess buttons remain visible with flags false.
- Cloud Run panel shows configured jobs.
- Invalid job args show a clear warning.
- Dry-run command preview renders without live Cloud Run credentials.
- Trigger button is disabled unless both flags are true and the checkbox is checked.
- Recent job status fails gracefully if IAM is missing.
- No Firebase artifacts are created.
