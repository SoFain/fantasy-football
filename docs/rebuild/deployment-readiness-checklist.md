# Deployment Readiness Checklist

Use this checklist before enabling Cloud Run Jobs or Scheduler in a real environment. This document does not authorize live deployment by itself.

## Local Safety

- Run `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`.
- Confirm `app.py`, `src`, and `scripts` compile.
- Confirm no tracked secrets, service account JSON, private keys, `.env` files, or local caches are present.
- Confirm no Firebase artifacts were introduced.
- Confirm Pigskin arbitrary SQL tooling remains removed.

## Migration And Validation

- Run `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run`.
- Run `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`.
- Inspect unexpected pending migrations before applying anything.
- Run validation dry-run.
- Run only narrow live validation patterns during rollout.

## Cloud Run Job Definitions

- Confirm job names match the allowlist in [Cloud Run Jobs](cloud-run-jobs.md).
- Use explicit `--project` and `--dataset` in job args.
- Deploy with the dry-run script preview first.
- Use job-specific service accounts.
- Do not use the deploy identity as the runtime identity.
- Do not set secrets as plain environment variables.

## Feature Flags

Defaults must remain:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Enable only during a controlled operator session:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true
DATA_OPS_ALLOW_JOB_TRIGGER=true
```

Every live trigger still requires user confirmation in the dashboard.

## Secret Manager

- Confirm required secrets exist in Secret Manager.
- Bind secrets only to the service or job that needs them.
- Confirm `GEMINI_API_KEY` is available only where Gemini is called.
- Confirm missing-secret behavior fails clearly before partial output is written.

## IAM

- Runtime service accounts have project `roles/bigquery.jobUser`.
- Dataset grants are scoped by job class.
- Secret Manager grants are per secret.
- Scheduler identity has invoke access only.
- Deploy identity is separate from runtime identities.

## Scheduler

- Create Scheduler jobs paused during rollout.
- Start with `validate-warehouse`.
- Keep external verification, ranking generation, backtests, content briefs, and claim grading manual until cost and quality gates are stable.
- Review `cloud_run_job_runs` before enabling the next schedule.

## Rollback

- Disable Streamlit trigger flags.
- Pause Scheduler jobs.
- Keep local subprocess controls available.
- Revert only the Cloud Run Job or Scheduler definition that caused the issue.
- Do not drop BigQuery tables as part of rollback unless a separate migration plan is approved.
