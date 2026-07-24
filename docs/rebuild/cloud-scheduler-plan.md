# Cloud Scheduler Plan

This plan describes Cloud Scheduler triggers for Cloud Run Jobs. The Sleeper refresh schedule is active; all other schedules remain plans until separately authorized.

## Scheduler Principles

- Trigger Cloud Run Jobs, not Streamlit request handlers.
- Use `scheduler-invoker-sa` or an equivalent least-privilege invoker identity.
- Keep schedules disabled by default during rollout.
- Prefer explicit job args over hidden defaults.
- Record all job status in `cloud_run_job_runs`.
- Add cost caps before increasing frequency.

## Proposed Schedules

| Job | Cadence | Seasonality | Triggering identity | Dependencies | Cost caution | Retry policy | Rollout |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `ingest-sleeper-news` | daily at 10:00 America/New_York | active season higher frequency only after review | `scheduler-invoker-sa` | Sleeper API available | API quota and rate limit | 2 retries, exponential backoff | enabled 2026-07-10 |
| `ingest-nflverse` | after game days | active season plus manual offseason refresh | `scheduler-invoker-sa` | nflverse source refresh | BigQuery load cost | 1 retry | disabled by default |
| `materialize-analytics` | after successful ingestion | active season daily or weekly | `scheduler-invoker-sa` | source tables refreshed | BigQuery processing | 1 retry | disabled by default |
| `generate-pigskin-rankings` | weekly or manual | active draft and season windows | `scheduler-invoker-sa` | analytics materialized, Gemini secret available | LLM cost | no automatic retry until quality gates exist | disabled by default |
| `generate-evidence-packets` | after rankings and projections | show prep days | `scheduler-invoker-sa` | rankings and projections current | BigQuery processing | 1 retry | disabled by default |
| `run-projections` | weekly, then daily during active season | active season | `scheduler-invoker-sa` | analytics current | BigQuery processing | 1 retry | disabled by default |
| `run-backtests` | manual or weekly after model changes | all season windows but bounded | `scheduler-invoker-sa` | projections and actuals available | can be expensive over large windows | no automatic retry for large windows | disabled by default |
| `validate-warehouse` | after materialization and daily in active season | all year | `scheduler-invoker-sa` | migrations applied | low to moderate, depends on pattern | 2 retries | first candidate for enablement |
| `grade-claims` | weekly after games | active season and offseason review batches | `scheduler-invoker-sa` | claim ledger and actuals current | BigQuery processing | 1 retry | disabled by default |
| `generate-content-briefs` | show prep days | active season and draft season | `scheduler-invoker-sa` | evidence packets, rankings, claims current | BigQuery processing, no LLM by default | 1 retry | disabled by default |
| `verify-external-context` | manual or queued only | player-specific | `scheduler-invoker-sa` | external provider configured | external search cost and quota | no automatic retry | disabled by default |
| `archive-sleeper-player-snapshot` | weekly, Tuesday 09:00 UTC | all year | `scheduler-invoker-sa` | digest-pinned archive image and BigQuery writer identity | Sleeper API availability | 2 retries, exponential backoff | enabled 2026-07-11 |

## Example Commands

Create a disabled daily validation trigger:

```powershell
gcloud scheduler jobs create http validate-warehouse-daily `
  --location us-central1 `
  --schedule "30 9 * * *" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/validate-warehouse:run" `
  --http-method POST `
  --oauth-service-account-email scheduler-invoker-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --attempt-deadline 1800s
```

Pause immediately after creation during rollout:

```powershell
gcloud scheduler jobs pause validate-warehouse-daily --location us-central1
```

The active Sleeper status refresh trigger is:

```powershell
gcloud scheduler jobs create http ingest-sleeper-news-daily `
  --location us-central1 `
  --schedule "0 10 * * *" `
  --time-zone "America/New_York" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/ingest-sleeper-news:run" `
  --http-method POST `
  --oauth-service-account-email scheduler-invoker-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Do not create or unpause any additional scheduler job without a separately authorized rollout.

## Sleeper Player Snapshot Archive Preview

The weekly archive uses a narrow derivative of the reviewed application image because the shared image does not package this script. Build it with `cloudbuild-sleeper-archive.yaml`, then deploy the resulting digest:

```powershell
gcloud run jobs deploy archive-sleeper-player-snapshot `
  --project fantasy-football-498121 `
  --region us-central1 `
  --image <digest-pinned-sleeper-archive-image> `
  --command python `
  --args scripts/build_sleeper_current_player_context.py,--apply,--refresh,--archive,--project,fantasy-football-498121,--dataset,fantasy_football_advanced_metrics `
  --service-account <least-privilege-job-service-account>
```

After one successful manual execution, create the enabled scheduler:

```powershell
gcloud scheduler jobs create http archive-sleeper-player-snapshot-weekly `
  --project fantasy-football-498121 `
  --location us-central1 `
  --schedule "0 9 * * 2" `
  --time-zone UTC `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/archive-sleeper-player-snapshot:run" `
  --http-method POST `
  --oauth-service-account-email scheduler-invoker-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --max-retry-attempts 2
```

Verify one successful manual execution before enabling the scheduler. Do not replace the service account placeholder without a reviewed deployment phase.

## Staged Rollout

1. Deploy Cloud Run Job definitions with dry-run script previews first.
2. Run `validate-warehouse` manually with a narrow pattern.
3. Run one low-risk non-dry job manually and verify `cloud_run_job_runs`.
4. Create Scheduler jobs paused.
5. Unpause only `validate-warehouse` first.
6. Add Sleeper news only after API limits are confirmed.
7. Add materialization and projections after validation is stable.
8. Keep ranking generation, external verification, backtests, claim grading, and content briefs manual until cost and quality gates are stable.

## Cost Controls

- Start daily or weekly, not hourly.
- Use narrow validation patterns during rollout.
- Keep external verification manual until quotas are visible.
- Keep backtest windows bounded.
- Review `cloud_run_job_runs` weekly for repeated failures and duration spikes.
- Do not schedule LLM-backed jobs until budget controls and review gates are in place.

## Rollback

Pause or delete Scheduler jobs first. Then disable Streamlit trigger flags:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

Local subprocess controls remain available while the scheduler path is paused.
