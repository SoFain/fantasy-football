# Cloud Run Operating Model

This is the long-term operating model for the Pigskin fantasy football platform.

The platform runs on Cloud Run Jobs, BigQuery, Cloud Scheduler, Cloud Storage, and Secret Manager. Firebase is not part of the target architecture unless the project explicitly reopens that decision.

## No Cloud Run Service

There is no Cloud Run service. The Streamlit admin/UI app that occupied that role was retired, and nothing replaced it.

This is the intended end state of the transition this document originally described, reached by deleting the UI rather than by migrating it. Consequences:

- There is no HTTP listener, no request path, and no request-time work to bound.
- The image has a single entrypoint, `src/job_runner.py`, invoked per execution with a job name.
- Adding a service back is a platform decision that needs an explicit ADR, not an incremental change.

If a consumer surface is needed later, it reads the compatibility objects and packets documented in [ui-query-debt-register.md](ui-query-debt-register.md). It does not query raw tables, and it does not re-embed job execution.

## Cloud Run Jobs Responsibilities

Cloud Run Jobs are the target runtime for Python tasks that mutate warehouse state or perform expensive analysis.

Target job categories:

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

Each job should be idempotent where possible, accept explicit project and dataset parameters, write status to BigQuery admin tables, and fail loudly when required inputs are missing.

Warehouse validation jobs should follow [BigQuery Validation Process](bigquery-validation-process.md). The `validate-warehouse` job should call `scripts/run_bigquery_validations.py` with explicit patterns and should not trigger ingestion, materialization, Cloud Run production jobs, or LLM calls.

## BigQuery Responsibilities

BigQuery is the analytical source of truth.

Responsibilities:

- Raw/source tables.
- Staging tables.
- Feature-like marts.
- Compatibility views and marts.
- Projection outputs.
- Ranking outputs.
- Evidence packets.
- Backtest outputs.
- Claim tracking.
- Operational metadata such as `schema_migrations`, `dashboard_job_runs`, and `cloud_run_job_runs`.

BigQuery tables should be partitioned and clustered where appropriate. User-facing UI and LLM paths should read precomputed marts or internal APIs, not raw source tables.

## Cloud Scheduler Responsibilities

Cloud Scheduler should trigger recurring Cloud Run Jobs.

Target scheduled triggers:

- Sleeper player/news refresh.
- Weekly or daily nflverse ingestion during active season.
- Materialization after successful ingestion.
- Pigskin ranking generation on explicit cadence.
- Evidence packet generation for show prep.
- Backtests and validation jobs.
- Claim grading and content brief generation.
- External verification refreshes with cost caps.

Scheduler should trigger jobs through least-privilege service accounts.

## Cloud Storage Responsibilities

Cloud Storage is used when a file artifact is too large or awkward for BigQuery.

Examples:

- Run logs beyond short status metadata.
- Exported evidence packets.
- CSV or Parquet exports.
- Large model prompts or responses when storing them in BigQuery is too costly.
- Backtest artifacts.
- Show-prep packet exports.

BigQuery should store metadata and pointers to Cloud Storage artifacts.

## Secret Manager Responsibilities

Secret Manager stores runtime secrets.

Current and future examples:

- `GEMINI_API_KEY`
- External API keys.
- Service tokens.
- Search provider configuration that should not live in code.

Cloud Run services and jobs should receive secrets through environment bindings or mounted secrets, not checked-in files.

## Completed: Streamlit Retirement

Everything this document previously listed as "temporarily in Streamlit" or "must eventually move out of Streamlit" is done. Ingestion, Sleeper refreshes, viewer-team ingestion, college and market ingestion, materialization, ranking generation, evidence packets, projections, backtests, warehouse validations, and external verification are all named jobs in `src/job_runner.py`.

One item did not migrate. The Pigskin chat interface was deleted with the UI; the curated tool layer survives in `src/pigskin_context_tools.py` and can back a future surface.

The rookie scouting CSV upload became the `ingest-rookie-scouting` job rather than disappearing with the UI.

## Job Naming Conventions

Use short, action-first names:

- `ingest-nflverse`
- `ingest-sleeper-news`
- `ingest-sleeper-league`
- `materialize-analytics`
- `generate-pigskin-rankings`
- `generate-evidence-packets`
- `run-projections`
- `run-backtests`
- `validate-warehouse`
- `generate-content-briefs`
- `grade-claims`

Use the same job name in:

- Cloud Run Job name.
- BigQuery job-run metadata.
- Dashboard labels.
- Logs.
- Documentation.

The detailed job entrypoint and operator commands live in [cloud-run-jobs.md](cloud-run-jobs.md). Recurring trigger planning lives in [cloud-scheduler-plan.md](cloud-scheduler-plan.md).

For job-specific variants, use suffixes:

- `generate-evidence-packets-fraud-watch`
- `run-backtests-rankings`
- `validate-warehouse-partitions`

## Environment Variable Conventions

Project and dataset:

- `BQ_PROJECT`: primary BigQuery project override.
- `GCP_PROJECT`: fallback project.
- `GOOGLE_CLOUD_PROJECT`: fallback project.
- `BQ_DATASET`: primary dataset override for jobs and migrations.
- `BIGQUERY_DATASET`: fallback dataset.
- `DATASET_NAME`: legacy fallback dataset.

Model and AI:

- `GEMINI_API_KEY`: Gemini API secret.
- `GEMINI_MODEL`: model name for generation.

External verification:

- `EXTERNAL_SEARCH_PROVIDER`
- `EXTERNAL_SEARCH_DAILY_LIMIT`
- `EXTERNAL_SEARCH_MAX_RESULTS`
- `VERTEX_AI_SEARCH_LOCATION`
- `VERTEX_AI_SEARCH_ENGINE_ID`
- `VERTEX_AI_SEARCH_SERVING_CONFIG`

Job metadata:

- `APP_VERSION`
- `APP_COMMIT`
- `K_REVISION`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS`: default false. Enables live Cloud Run Job dispatch instead of local execution.
- `CLOUD_RUN_JOBS_ENABLED`: optional global Cloud Run Jobs switch.
- `DATA_OPS_ALLOW_JOB_TRIGGER`: default false. Required before a Cloud Run Job can actually be triggered.
- `CLOUD_RUN_REGION`: Cloud Run Jobs region. Defaults to `us-central1`.
- `CLOUD_RUN_PROJECT`: Cloud Run Jobs project override.
- `CLOUD_RUN_JOB_SERVICE_ACCOUNT`: deployment-time service account hint for job definitions.
- Future: `JOB_RUN_ID`, `MODEL_RUN_ID`, `FEATURE_CONFIG_VERSION`, `SCORING_PROFILE`

## Deployment Assumptions

- Python jobs are packaged from the same repo image unless a later split is justified.
- Cloud Build can build the shared image.
- Cloud Run Jobs use the same image with job-specific commands.
- Service accounts should use least privilege once migrations stabilize.
- Secrets are injected through Secret Manager.
- BigQuery project defaults should continue to follow `src/load.py`.
- Job triggers should remain explicit operator actions and should be logged to `cloud_run_job_runs`.

## Cost-Control Assumptions

- Precompute marts instead of running repeated raw scans.
- Partition and cluster large BigQuery tables.
- Require partition filters in ad hoc diagnostic queries.
- Keep external verification behind daily and per-query limits.
- Store large artifacts in Cloud Storage instead of duplicating them in BigQuery.
- Prefer scheduled incremental jobs over full rebuilds when source data supports it.
- Keep `DATA_OPS_ALLOW_JOB_TRIGGER=false` outside controlled operator sessions.
- Use dry-run previews before enabling live Cloud Run Job triggers.
- Keep Cloud Run Job memory, CPU, and timeout settings job-specific.
- Keep LLM calls tied to evidence packets and ranking runs.

## Future Sprint Guidance

Future sprint docs should reference this file for platform placement decisions.

Default placement:

- Long-running Python work: Cloud Run Jobs.
- Schedules: Cloud Scheduler.
- Analytical state: BigQuery.
- Large files and exports: Cloud Storage.
- Secrets: Secret Manager.
- Optional internal APIs: a Cloud Run service, likely FastAPI, only with an explicit ADR reopening the no-service decision.
