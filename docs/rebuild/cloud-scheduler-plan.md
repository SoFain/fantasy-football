# Cloud Scheduler Plan

This plan describes future Cloud Scheduler triggers for Cloud Run Jobs. It does not create live scheduler resources.

## Scheduler Principles

- Trigger Cloud Run Jobs, not Streamlit request handlers.
- Use least-privilege service accounts.
- Keep early schedules conservative.
- Prefer explicit job args over hidden defaults.
- Record all job status in `cloud_run_job_runs`.
- Add tighter cost caps before increasing frequency.

## Suggested Cadence

| Job | Suggested cadence | Notes |
| --- | --- | --- |
| `ingest-sleeper-news` | daily, more often during active season | Keep Sleeper calls below API safety limits. |
| `ingest-nflverse` | after game days | Run by explicit season. Avoid repeated full truncation during live show prep unless intended. |
| `materialize-analytics` | after successful ingestion | Use after source tables are refreshed. |
| `generate-pigskin-rankings` | explicit cadence | Start manual or weekly. Do not overrun Gemini budget. |
| `generate-evidence-packets` | after rankings and projections | Use for show prep and segment packets. |
| `validate-warehouse` | after materialization | Use a validation pattern when checking a narrow sprint. |
| `run-projections` | weekly or daily during active season | Start with weekly projection horizon, then add ROS and dynasty cadence. |
| `run-backtests` | weekly or after projection changes | Start manual or narrow. Use dry-run first and keep season windows bounded. |
| `verify-external-context` | manual or queued by player | Keep quota use explicit and auditable. |

## Example Commands

Create a daily Sleeper news refresh trigger:

```powershell
gcloud scheduler jobs create http ingest-sleeper-news-daily `
  --location us-central1 `
  --schedule "0 8 * * *" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/ingest-sleeper-news:run" `
  --http-method POST `
  --oauth-service-account-email nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Create an after-game-day nflverse trigger:

```powershell
gcloud scheduler jobs create http ingest-nflverse-weekly `
  --location us-central1 `
  --schedule "0 9 * * MON,TUE" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/ingest-nflverse:run" `
  --http-method POST `
  --oauth-service-account-email nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Create a post-materialization validation trigger:

```powershell
gcloud scheduler jobs create http validate-warehouse-daily `
  --location us-central1 `
  --schedule "30 9 * * *" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/validate-warehouse:run" `
  --http-method POST `
  --oauth-service-account-email nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

## Staged Rollout

1. Create Cloud Run Job definitions manually.
2. Run each job manually with `--dry-run` or tight `--limit` where supported.
3. Apply the `cloud_run_job_runs` migration.
4. Run one manual non-dry execution per job type.
5. Verify `cloud_run_job_runs` status rows.
6. Enable the lowest-risk schedules first: `validate-warehouse`, then `ingest-sleeper-news`.
7. Add materialization and projection schedules after validation is stable.
8. Keep ranking generation manual until LLM cost and output quality are understood.

## Cost Controls

- Start with daily or weekly schedules, not hourly.
- Use job-specific `--limit` in test jobs.
- Keep external verification manual until quotas are visible.
- Store large logs in Cloud Storage only when needed.
- Review `cloud_run_job_runs` weekly for failures, duration spikes, and repeated reruns.

## Deferred Streamlit Wiring

The Streamlit Data Ops buttons stay in place for now.

Future UI triggering should be guarded by:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
```

When enabled, Streamlit should call a narrow job trigger helper and display recent `cloud_run_job_runs` rows instead of waiting for long subprocesses.
