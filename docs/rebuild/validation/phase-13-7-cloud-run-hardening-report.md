# Phase 13.7 Cloud Run Hardening Report

Final decision: GO WITH WARNINGS

## Scope

Phase 13.7 hardened the Cloud Run Jobs deployment and scheduler path without creating live Cloud Run Jobs, Scheduler jobs, IAM grants, or Firebase artifacts.

## Job Support Matrix

Code and docs now agree on these supported jobs:

| Job | Status |
| --- | --- |
| `ingest-nflverse` | supported |
| `ingest-sleeper-news` | supported |
| `ingest-sleeper-league` | supported |
| `ingest-context-events` | supported |
| `ingest-market-values` | supported |
| `ingest-college-stats` | supported |
| `materialize-analytics` | supported |
| `generate-pigskin-rankings` | supported |
| `generate-evidence-packets` | supported |
| `run-projections` | supported |
| `run-backtests` | supported |
| `validate-warehouse` | supported |
| `verify-external-context` | supported |
| `generate-content-briefs` | supported |
| `grade-claims` | supported |

## Current State

- `src/job_runner.py` rejects unknown job names through the parser allowlist and dispatcher map.
- `src/job_runner.py` records success and failure metadata in `cloud_run_job_runs`.
- Failure metadata preserves `error_message` and does not mask the original exception if metadata update fails.
- `src/cloud_run_jobs.py` validates job names, project, region, allowed args, and safe env overrides.
- Dry-run command previews work without live credentials.
- Live triggers require feature flags, trigger allow flag, user confirmation, and `gcloud`.
- `app.py` Data Ops still keeps local subprocess controls available.
- Streamlit live Cloud Run triggering remains default off.
- Recent job status reads from job metadata tables only.

## Dry-Run Command Examples

Runner preview:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name validate-warehouse --dry-run --pattern "^096_"
```

Deployment preview:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --dry-run --job-name validate-warehouse --project fantasy-football-498121 --region us-central1 --image example.com/test/image:latest
```

Observed deployment preview:

```text
gcloud run jobs deploy validate-warehouse --project fantasy-football-498121 --region us-central1 --image example.com/test/image:latest --command python --args -m,src.job_runner,--job-name,validate-warehouse,--project,fantasy-football-498121,--dataset,fantasy_football_brain --set-env-vars BQ_PROJECT=fantasy-football-498121,BQ_DATASET=fantasy_football_brain
```

## Gcloud Dependency Status

Dry-run previews do not require `gcloud`.

Live Streamlit triggers still use the `gcloud run jobs execute` wrapper. The helper now checks for `gcloud` before attempting a live trigger and raises a clear error when it is unavailable.

## IAM Plan Status

Created:

- `docs/rebuild/iam-hardening-plan.md`

The plan defines separate runtime identities for the dashboard, ingestion, materialization, ranking, evidence, validation, backtesting, claim grading, and scheduler invocation. No live IAM changes were applied.

## Secret Manager Plan Status

Created:

- `docs/rebuild/secret-manager-plan.md`

The plan documents `GEMINI_API_KEY`, future external API keys, local ADC guidance, Cloud Run service and job secret binding, rotation, and missing-secret behavior. No secrets were added or changed.

## Scheduler Plan Status

Updated:

- `docs/rebuild/cloud-scheduler-plan.md`

The plan defines disabled-by-default schedules for ingestion, materialization, rankings, evidence packets, projections, backtests, validation, claim grading, and content briefs. No live Scheduler jobs were created.

## Deployment Safety Check

Added:

- `scripts/check_deployment_safety.py`
- `docs/rebuild/deployment-readiness-checklist.md`

The checker verifies:

- no tracked Firebase artifacts
- no tracked secret or service-account files
- no tracked secret-shaped content
- required hardening files exist
- live Cloud Run trigger flags default off
- Pigskin arbitrary SQL tooling remains removed
- `app.py`, `src`, and `scripts` compile

The checker was adjusted to avoid flagging its own regex definitions and prose references to private-key patterns while still detecting real PEM headers, JSON `private_key` fields, and API-key shaped values.

## Validation Results

Commands run with `.\venv\Scripts\python.exe`:

| Command | Result |
| --- | --- |
| `-m unittest tests.test_cloud_run_jobs` | passed, 12 tests |
| `-m unittest tests.test_job_runner` | passed, 17 tests |
| `-m unittest tests.test_deployment_safety` | passed, 5 tests |
| `-m unittest discover tests` | passed, 266 tests |
| `-m py_compile app.py` | passed |
| `-m compileall -q src scripts` | passed |
| `scripts\check_deployment_safety.py` | passed |
| `scripts\run_bigquery_migrations.py --dry-run` | passed |
| `scripts\run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts\deploy_cloud_run_jobs.ps1 --dry-run --job-name validate-warehouse ...` | passed |

## Remaining Warnings

- No live Cloud Run Jobs were deployed, per instruction.
- No live Scheduler jobs were created, per instruction.
- No live IAM changes were applied, per instruction.
- Live Streamlit job execution still depends on `gcloud` being available until a future phase moves to the Cloud Run Jobs client library.
- The deploy scripts preview and deploy job definitions, but operator review is still required before running them outside dry-run mode.

## Blockers

None.

## Readiness

Phase 13.7 is ready for the next controlled rollout step. The next step should be either a dry-run deployment review with the real image or a narrowly authorized live deployment of one low-risk job such as `validate-warehouse`.
