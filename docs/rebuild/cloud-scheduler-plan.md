# Cloud Scheduler Plan

Status: the daily player watch is **deployed and live** as of 2026-07-24. Cloud Scheduler runs `ingest-sleeper-news-daily` at 07:00 America/New_York and `detect-player-changes-daily` at 07:15, triggering Cloud Run Jobs built from this branch (image tag `pigskin-jobs-*`). `generate-pigskin-rankings` is deliberately NOT scheduled: it truncates `analytics_pigskin_rankings`, which the public feed publisher reads for the fable positional boards. Daily site publication is the 07:30 America/New_York leg: the scheduled task `PigskinDailyPublishImport` (this machine, local time = Eastern) runs `scripts/publish_public_rankings.py --publish --gcloud-auth` in the main checkout, then triggers the IONOS site import via `run_remote_php`. The publisher carries manifest `datasets` entries forward, so coaching staff stays listed without a `--dataset-entry` flag. See the main checkout's `docs/rankings-production-runbook.md`.

The remainder of this plan describes triggers not yet created.

## Scheduler Principles

- Trigger Cloud Run Jobs directly.
- Use least-privilege service accounts.
- Keep early schedules conservative.
- Prefer explicit job args over hidden defaults.
- Record all job status in `cloud_run_job_runs`.
- Add tighter cost caps before increasing frequency.

## Suggested Cadence

| Job | Suggested cadence | Notes |
| --- | --- | --- |
| `ingest-sleeper-news` | daily at 07:00 America/New_York | Snapshots the Sleeper player map (`/v1/players/?active=true`) and appends to `sleeper_players_history`. This is the only caller of `/v1/players/`, which Sleeper limits to once per day; the job skips if today's snapshot already exists. Other jobs read the saved snapshot. |
| `detect-player-changes` | daily at 07:15 America/New_York | Runs after the snapshot. Diffs the two most recent snapshots and pulls team news for injury, team, depth-chart, and deactivation changes. |
| `ingest-coaching-staff` | weekly, and on coaching changes | Loads the curated coaching CSV. Small and cheap; refresh after editing the CSV. |
| `coaching-staff-feed` | after ingest-coaching-staff | Emits the JSON dataset object and manifest entry for the ranking publisher to merge. |
| `ingest-nflverse` | after game days | Run by explicit season. Avoid repeated full truncation during live show prep unless intended. |
| `materialize-analytics` | after successful ingestion | Use after source tables are refreshed. |
| `generate-pigskin-rankings` | **do not schedule yet** | Truncates `analytics_pigskin_rankings`, which the publisher reads for the live fable positional boards. Blocked until the LLM path is reconciled with the fable pipeline. Its Sleeper-pool precondition remains in force for manual runs against a non-production dataset. |
| `generate-evidence-packets` | after rankings and projections | Use for show prep and segment packets. |
| `validate-warehouse` | after materialization | Use a validation pattern when checking a narrow sprint. |
| `run-projections` | weekly or daily during active season | Start with weekly projection horizon, then add ROS and dynasty cadence. |
| `run-backtests` | weekly or after projection changes | Start manual or narrow. Use dry-run first and keep season windows bounded. |
| `verify-external-context` | manual or queued by player | Keep quota use explicit and auditable. |

## Time Zones

Always pass `--time-zone`. Cloud Scheduler defaults to UTC, so a schedule written as a bare UTC offset silently drifts by an hour twice a year when US daylight saving changes. A 7:00 AM Eastern job is `--schedule "0 7 * * *" --time-zone "America/New_York"`, never `"0 11 * * *"` or `"0 12 * * *"`.

## Example Commands

Create the daily 7:00 AM Eastern Sleeper snapshot:

```powershell
gcloud scheduler jobs create http ingest-sleeper-news-daily `
  --location us-central1 `
  --schedule "0 7 * * *" `
  --time-zone "America/New_York" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/ingest-sleeper-news:run" `
  --http-method POST `
  --oauth-service-account-email nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

Create the change detection and news pass that follows it:

```powershell
gcloud scheduler jobs create http detect-player-changes-daily `
  --location us-central1 `
  --schedule "15 7 * * *" `
  --time-zone "America/New_York" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/detect-player-changes:run" `
  --http-method POST `
  --oauth-service-account-email nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

The 15 minute gap is a deliberate buffer, not a dependency. Cloud Scheduler cannot express "run after that job succeeded", so if the snapshot is slow or fails, the detector simply finds no new snapshot to diff and exits without writing. It does not produce wrong results; it produces none.

Create the daily 7:30 AM Eastern rankings run, after the snapshot:

```powershell
gcloud scheduler jobs create http generate-pigskin-rankings-daily `
  --location us-central1 `
  --schedule "30 7 * * *" `
  --time-zone "America/New_York" `
  --uri "https://us-central1-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/fantasy-football-498121/jobs/generate-pigskin-rankings:run" `
  --http-method POST `
  --oauth-service-account-email nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com
```

The rankings job enforces its own precondition: it materializes candidates only from a current-day Sleeper pool and raises if the snapshot is missing or stale. The 30 minute offset from the 07:00 snapshot is the same soft-buffer pattern, but here a failure is loud rather than silent — a stale pool stops the run instead of ranking yesterday's players. If the snapshot job is ever slowed, widen the offset rather than letting rankings fail. For a manual run that should also refresh Sleeper first, pass `--refresh-sleeper` (the once-per-day guard still applies).

If an existing trigger needs to move to Eastern time:

```powershell
gcloud scheduler jobs update http ingest-sleeper-news-daily `
  --location us-central1 `
  --schedule "0 7 * * *" `
  --time-zone "America/New_York"
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

## Deferred Operator Tooling

Local CLI execution stays the default for now.

Future UI triggering should be guarded by:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
```

When enabled, operator tooling should call a narrow job trigger helper and read recent `cloud_run_job_runs` rows instead of waiting for long subprocesses.
