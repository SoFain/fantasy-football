# Cloud Run Jobs

This document defines the Cloud Run Job path for long-running warehouse work. The Streamlit Cloud Run service remains the admin and control surface. These jobs should use the shared app container image unless a later dependency split is justified.

No Cloud infrastructure is created by this document.

## Entry Point

Local runner:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name validate-warehouse --dry-run
```

Container command:

```text
python -m src.job_runner --job-name <job-name> [args]
```

The runner writes execution metadata to `fantasy_football_brain.cloud_run_job_runs`. Real BigQuery clients should write new metadata rows with load jobs, not streaming inserts, because the runner updates the same row at job finish time.

## Supported Jobs

Code and docs must agree on this allowlist:

| Job | Wrapped path | Required context | Notes |
| --- | --- | --- | --- |
| `ingest-nflverse` | `src.pipeline.run_pipeline` | optional `--season` | Mutates warehouse. |
| `ingest-sleeper-news` | `src.ingest_news.load_realtime_news` | none | External API call. |
| `ingest-sleeper-league` | `src.ingest_sleeper_league.ingest_sleeper_league` | `--league-id`, `--week` | External API call. |
| `ingest-context-events` | `src.ingest_context_events.load_context_events` | optional `--csv` | Curated context event import. |
| `ingest-market-values` | `src.fetch_market_values` | optional `--league-type` | External source, refresh cadence controlled manually at first. |
| `ingest-college-stats` | `src.ingest_college_data` | `--season` | Prospect and college context. |
| `materialize-analytics` | `src.materialize` plus mart materializers | optional season/week context | Runs marts and compatibility objects. |
| `generate-pigskin-rankings` | `src.generate_pigskin_rankings.generate_rankings` | optional position context | Requires Gemini only when not dry-run. |
| `generate-evidence-packets` | `src.segment_packets`, `src.materialize_llm_packets` | optional season/week/model context | Creates curated evidence packets. |
| `run-projections` | `src.projection_engine.run_projection` | `--season`, `--week`, `--horizon` | Versioned outputs. |
| `run-backtests` | `src.backtesting.run_backtest` | `--season-start`, `--season-end`, `--horizon` | Keep windows bounded. |
| `validate-warehouse` | `scripts/run_bigquery_validations.py` | optional `--pattern` | Prefer narrow validation patterns. |
| `verify-external-context` | `src.verify_player_context.verify_player_context` | `--player` | Cost and quota controlled. |
| `generate-content-briefs` | `src.content_briefs` | `--brief-type`, `--season` | Deterministic brief generation. |
| `grade-claims` | `src.claim_grading.run_claim_grading` | optional claim or season/week context | Claim accountability scoring. |

## Common Arguments

```text
--job-name
--project
--dataset
--season
--week
--season-start
--season-end
--week-start
--week-end
--league-id
--scoring-profile
--league-type
--roster-format
--model-run-id
--market-source-id
--dry-run
--limit
--fail-fast
--backtest-name
--allow-large-backtest
```

Additional job-specific arguments:

```text
--horizon
--pattern
--player
--query
--team
--max-results
--csv
--roster-id
--username
--display-name
--team-name
--positions
--position-limit
--refresh-sleeper
--write-disposition
--brief-type
--claim-id
```

## Project And Dataset Resolution

Prefer explicit `--project` and `--dataset` in Cloud Run Job definitions.

Project resolution follows the existing repo pattern:

1. `BQ_PROJECT`
2. `GCP_PROJECT`
3. `GOOGLE_CLOUD_PROJECT`
4. repo default, currently `fantasy-football-498121`

Dataset resolution:

1. `BQ_DATASET`
2. `BIGQUERY_DATASET`
3. `DATASET_NAME`
4. `fantasy_football_brain`

## Local Dry-Run Examples

Validate job wiring:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name validate-warehouse --dry-run --pattern "^096_"
```

Preview projections:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name run-projections --season 2026 --week 1 --horizon weekly --dry-run --limit 25
```

Preview backtests:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name run-backtests --season-start 2023 --season-end 2024 --horizon weekly --scoring-profile half_ppr --league-type redraft --roster-format superflex --dry-run
```

Preview content briefs:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name generate-content-briefs --brief-type fraud_watch_show --season 2026 --week 1 --dry-run
```

Preview claim grading:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name grade-claims --season 2026 --week 1 --dry-run
```

## Deployment Scripts

Dry-run all job deploy commands:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --dry-run --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest
```

Dry-run one job:

```powershell
.\scripts\deploy_cloud_run_jobs.ps1 --dry-run --job-name validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest
```

Bash equivalent:

```bash
scripts/deploy_cloud_run_jobs.sh --dry-run --job-name validate-warehouse --project fantasy-football-498121 --region us-central1 --image us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest
```

The scripts:

- Support `--dry-run`.
- Support `--project`, `--region`, `--image`, `--service-account`, `--job-name`, and `--dataset`.
- Print commands before execution.
- Do not run jobs after deploy unless `--run-after-deploy` is explicitly passed.
- Do not embed secrets.

## Streamlit Trigger Path

`src/cloud_run_jobs.py` powers the default-off Data Ops control surface.

Live trigger requirements:

- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true`
- `CLOUD_RUN_JOBS_ENABLED=true`
- `DATA_OPS_ALLOW_JOB_TRIGGER=true`
- User confirmation checkbox checked
- `gcloud` available in the runtime path

Dry-run previews do not require live credentials or `gcloud`.

If `gcloud` is missing for a live trigger, the helper returns a clear error and keeps dry-run previews available.

## Metadata And Status

Actual trigger attempts record sanitized metadata in `cloud_run_job_runs`.

Metadata includes:

- job name
- Cloud Run job name
- trigger status
- sanitized args
- command preview
- project and dataset
- error message when trigger startup fails

Secrets and sensitive env names are redacted or refused.

Metadata write behavior:

- `src.job_runner.start_job_run()` uses `load_table_from_json()` when the real BigQuery client supports it.
- `src.cloud_run_jobs.record_cloud_run_job_trigger()` uses `load_table_from_json()` when the real BigQuery client supports it.
- Test doubles without load-job support still use `insert_rows_json`.
- Avoid streaming inserts for rows that need immediate status updates because BigQuery can reject `UPDATE` statements while rows are still in the streaming buffer.

## IAM And Secrets

See:

- [IAM Hardening Plan](iam-hardening-plan.md)
- [Secret Manager Plan](secret-manager-plan.md)

Runtime identities should have the minimum BigQuery, Secret Manager, and Cloud Run permissions needed for their job class. Deploy identities can have Cloud Run developer permissions. Runtime identities should not.

## Failure Behavior

The runner:

- Rejects unknown job names.
- Rejects unsupported args.
- Records failed status with `error_message`.
- Preserves the original exception when metadata updates fail.
- Exits nonzero on failure.
- Does not hide retries from logs.

## Validation

Run:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_cloud_run_jobs
.\venv\Scripts\python.exe -m unittest tests.test_job_runner
.\venv\Scripts\python.exe scripts\check_deployment_safety.py
```

## Phase 14.7 Validate Warehouse Gate

Phase 14.7 produced a dry-run deployment preview for only `validate-warehouse`. Live deployment was not run because `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST=true` was not set and `gcloud` was not installed locally.

See [phase-14-7-cloud-run-validate-warehouse-test.md](validation/phase-14-7-cloud-run-validate-warehouse-test.md).
