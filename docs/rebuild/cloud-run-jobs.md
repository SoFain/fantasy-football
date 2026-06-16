# Cloud Run Jobs

This document defines the Cloud Run Job-ready path for long-running warehouse work. The Streamlit Cloud Run service remains the admin/UI surface. These jobs use the same container image unless a later cost or dependency split is justified.

No Cloud infrastructure is created by this document. The commands below are operator commands.

## Entry Point

Job runner:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name validate-warehouse --dry-run
```

Container command:

```text
python -m src.job_runner --job-name <job-name> [args]
```

The runner writes execution metadata to `fantasy_football_brain.cloud_run_job_runs`.

## Supported Jobs

| Job | Wrapped path | Required context |
| --- | --- | --- |
| `ingest-nflverse` | `src.pipeline.run_pipeline` | optional `--season` |
| `ingest-sleeper-news` | `src.ingest_news.load_realtime_news` | none |
| `ingest-sleeper-league` | `src.ingest_sleeper_league.ingest_sleeper_league` | `--league-id`, `--week` |
| `ingest-context-events` | `src.ingest_context_events.load_context_events` | optional `--csv` |
| `ingest-market-values` | `src.fetch_market_values` | optional `--league-type` |
| `ingest-college-stats` | `src.ingest_college_data` | `--season` |
| `materialize-analytics` | `src.materialize` plus current mart materializers | optional season/week context |
| `generate-pigskin-rankings` | `src.generate_pigskin_rankings.generate_rankings` | Gemini secret |
| `generate-evidence-packets` | `src.segment_packets`, `src.materialize_llm_packets` | optional season/week/model run context |
| `run-projections` | `src.projection_engine.run_projection` | `--season`, `--week`, `--horizon` |
| `run-backtests` | `src.backtesting.run_backtest` | `--season-start`, `--season-end`, `--horizon` |
| `validate-warehouse` | `scripts/run_bigquery_validations.py` | optional `--pattern` |
| `verify-external-context` | `src.verify_player_context.verify_player_context` | `--player` |

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

Additional job-specific arguments include:

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
```

## Project And Dataset Resolution

Project resolution follows the existing repo pattern from `src/load.py`.

1. `BQ_PROJECT`
2. `GCP_PROJECT`
3. `GOOGLE_CLOUD_PROJECT`
4. repo default, currently `fantasy-football-498121`

Dataset resolution:

1. `BQ_DATASET`
2. `BIGQUERY_DATASET`
3. `DATASET_NAME`
4. `fantasy_football_brain`

Prefer explicit `--project` and `--dataset` in Cloud Run Job definitions so job metadata is unambiguous.

## Local Commands

Validate job wiring without running a validation query:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name validate-warehouse --dry-run --pattern "^096_"
```

Preview a backtest entrypoint:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name run-backtests --season-start 2023 --season-end 2024 --horizon weekly --scoring-profile half_ppr --league-type redraft --roster-format superflex --dry-run
```

Run projection generation in dry-run mode:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name run-projections --season 2026 --week 1 --horizon weekly --dry-run --limit 25
```

Generate Pigskin rankings in dry-run mode:

```powershell
.\venv\Scripts\python.exe -m src.job_runner --job-name generate-pigskin-rankings --dry-run --position-limit 5
```

## Cloud Run Job Commands

Set image variables first:

```powershell
$PROJECT_ID = "fantasy-football-498121"
$REGION = "us-central1"
$IMAGE = "us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app:latest"
$SERVICE_ACCOUNT = "nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com"
```

Create jobs:

```powershell
gcloud run jobs create ingest-nflverse `
  --image $IMAGE `
  --region $REGION `
  --service-account $SERVICE_ACCOUNT `
  --set-env-vars BQ_PROJECT=$PROJECT_ID,BQ_DATASET=fantasy_football_brain `
  --command python `
  --args "-m,src.job_runner,--job-name,ingest-nflverse"
```

```powershell
gcloud run jobs create materialize-analytics `
  --image $IMAGE `
  --region $REGION `
  --service-account $SERVICE_ACCOUNT `
  --set-env-vars BQ_PROJECT=$PROJECT_ID,BQ_DATASET=fantasy_football_brain `
  --command python `
  --args "-m,src.job_runner,--job-name,materialize-analytics"
```

```powershell
gcloud run jobs create generate-pigskin-rankings `
  --image $IMAGE `
  --region $REGION `
  --service-account $SERVICE_ACCOUNT `
  --set-env-vars BQ_PROJECT=$PROJECT_ID,BQ_DATASET=fantasy_football_brain `
  --set-secrets GEMINI_API_KEY=GEMINI_API_KEY:latest `
  --command python `
  --args "-m,src.job_runner,--job-name,generate-pigskin-rankings"
```

```powershell
gcloud run jobs create generate-evidence-packets `
  --image $IMAGE `
  --region $REGION `
  --service-account $SERVICE_ACCOUNT `
  --set-env-vars BQ_PROJECT=$PROJECT_ID,BQ_DATASET=fantasy_football_brain `
  --command python `
  --args "-m,src.job_runner,--job-name,generate-evidence-packets"
```

```powershell
gcloud run jobs create run-projections `
  --image $IMAGE `
  --region $REGION `
  --service-account $SERVICE_ACCOUNT `
  --set-env-vars BQ_PROJECT=$PROJECT_ID,BQ_DATASET=fantasy_football_brain `
  --command python `
  --args "-m,src.job_runner,--job-name,run-projections"
```

```powershell
gcloud run jobs create run-backtests `
  --image $IMAGE `
  --region $REGION `
  --service-account $SERVICE_ACCOUNT `
  --set-env-vars BQ_PROJECT=$PROJECT_ID,BQ_DATASET=fantasy_football_brain `
  --command python `
  --args "-m,src.job_runner,--job-name,run-backtests"
```

```powershell
gcloud run jobs create validate-warehouse `
  --image $IMAGE `
  --region $REGION `
  --service-account $SERVICE_ACCOUNT `
  --set-env-vars BQ_PROJECT=$PROJECT_ID,BQ_DATASET=fantasy_football_brain `
  --command python `
  --args "-m,src.job_runner,--job-name,validate-warehouse"
```

Execute a job with overrides:

```powershell
gcloud run jobs execute run-projections `
  --region $REGION `
  --args "-m,src.job_runner,--job-name,run-projections,--season,2026,--week,1,--horizon,weekly"
```

```powershell
gcloud run jobs execute run-backtests `
  --region $REGION `
  --args "-m,src.job_runner,--job-name,run-backtests,--season-start,2023,--season-end,2024,--horizon,weekly,--scoring-profile,half_ppr,--league-type,redraft,--roster-format,superflex"
```

```powershell
gcloud run jobs execute run-backtests `
  --region $REGION `
  --args "-m,src.job_runner,--job-name,run-backtests,--season-start,2024,--season-end,2024,--horizon,weekly,--scoring-profile,ppr,--market-source-id,manual_ecr"
```

## IAM Expectations

The job service account needs:

- Project: `roles/bigquery.jobUser`
- Dataset `fantasy_football_brain`: `roles/bigquery.dataEditor`
- Secret access for required secrets such as `GEMINI_API_KEY`

Read-only operators who only inspect pending migrations or validations need:

- Project: `roles/bigquery.jobUser`
- Dataset: `roles/bigquery.dataViewer`

## Secret Manager Expectations

Secrets should be provided by Cloud Run secret bindings or environment variables.

Current required secret for LLM ranking generation:

- `GEMINI_API_KEY`

Future external adapters should follow the same pattern.

## Failure Behavior

The runner:

- Inserts a `running` row before dispatch.
- Marks `success` with result metadata when the wrapped job completes.
- Marks `failed` with the original error message when the wrapped job raises.
- Exits nonzero on failure.
- Does not silently swallow exceptions.

If failure metadata cannot be written, the runner logs that secondary metadata problem and preserves the original job exception.

## Retry Strategy

Use Cloud Run Job retry settings only for idempotent jobs or jobs that safely overwrite by version.

Recommended starting point:

- Ingestion: low retry count, explicit inspection after repeated failure.
- Materialization: one retry if queries are idempotent.
- Ranking generation: manual retry unless the failure is clearly transient.
- External verification: strict quota guardrails and low retry count.
- Validation: one retry is acceptable.

## Cost Controls

- Prefer `--dry-run` during setup.
- Use `--limit` for projections, rankings, and packet generation tests.
- Use validation `--pattern` when checking a narrow area.
- Keep external verification behind explicit player/query inputs.
- Keep scheduled jobs conservative until warehouse freshness and row counts are visible.
- Store only metadata in `cloud_run_job_runs`; put large logs or artifacts in Cloud Storage if needed.

## Streamlit Data Ops Compatibility

Do not remove current Streamlit subprocess buttons yet.

Streamlit now has a default-off Cloud Run Jobs preview and trigger panel in Data Ops.

Feature flags:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
CLOUD_RUN_JOBS_ENABLED=true
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Optional configuration:

```text
CLOUD_RUN_REGION=us-central1
CLOUD_RUN_PROJECT=fantasy-football-498121
CLOUD_RUN_JOB_SERVICE_ACCOUNT=<job-service-account>
```

Behavior:

- With the default flags, Streamlit shows configured jobs and dry-run previews only.
- Actual triggering requires `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true` and `DATA_OPS_ALLOW_JOB_TRIGGER=true`.
- The user must confirm the trigger in the dashboard before any job is started.
- Unknown job names and unsupported args are rejected by `src/cloud_run_jobs.py`.
- Trigger metadata is written to `cloud_run_job_runs`.
- Secrets are refused as ad hoc environment overrides and are not logged.
- Local subprocess controls remain available during rollout.

The safe rollout guide lives in [data-ops-cloud-run-jobs-rollout.md](data-ops-cloud-run-jobs-rollout.md).
