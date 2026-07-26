# Cloud Scheduler Plan

Status: the daily player watch is **deployed and live** as of 2026-07-24. Cloud Scheduler runs `ingest-sleeper-news-daily` at 07:00 America/New_York and `detect-player-changes-daily` at 07:15, triggering Cloud Run Jobs built from this branch (image tag `pigskin-jobs-*`). `generate-pigskin-rankings` is deliberately NOT scheduled: it truncates `analytics_pigskin_rankings`, which the public feed publisher reads for the fable positional boards. The 07:30 America/New_York leg (`PigskinDailyPublishImport`, this machine) now runs the full chain via `scripts/daily_pigskin_chain.ps1`: automated board refresh (`scripts/run_daily_board_refresh.py --apply`, the production runbook as a fail-closed chain re-running approved formulas on fresh data), then `publish_public_rankings.py --publish --gcloud-auth`, then the IONOS site import via `run_remote_php`. A pre-write guardrail trip (exit 1, e.g. the QB24 cutline) republishes the last-approved boards and surfaces an owner-review item in the log; a post-write failure (exit 3) skips publication per the runbook Recovery section. The publisher carries manifest `datasets` entries forward, so coaching staff stays listed without a `--dataset-entry` flag. See the main checkout's `docs/rankings-production-runbook.md`.

The weekly `archive-sleeper-player-snapshot` trigger (Tuesday 09:00 UTC) has been enabled since 2026-07-11. The remainder of this plan describes triggers not yet created.

## Scheduler Principles

- Trigger Cloud Run Jobs directly.
- Use least-privilege service accounts.
- Keep early schedules conservative.
- Prefer explicit job args over hidden defaults.
- Record all job status in `cloud_run_job_runs`.
- Add cost caps before increasing frequency.

## Proposed Schedules

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
| `archive-sleeper-player-snapshot` | weekly, Tuesday 09:00 UTC | **Enabled 2026-07-11.** Digest-pinned narrow image runs `build_sleeper_current_player_context.py --apply --refresh --archive` into the advanced-metrics dataset. |

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

Do not create a `generate-pigskin-rankings` scheduler trigger: it truncates `analytics_pigskin_rankings`, which the publisher reads for the live fable positional boards. The 07:30 America/New_York leg is the local `PigskinDailyPublishImport` task, not a Cloud Scheduler job.

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
  --oauth-service-account-email scheduler-invoker-sa@fantasy-football-498121.iam.gserviceaccount.com `
  --attempt-deadline 1800s
```

Pause immediately after creation during rollout:

```powershell
gcloud scheduler jobs pause validate-warehouse-daily --location us-central1
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

## Deferred Operator Tooling

Local CLI execution stays the default for now.

Future UI triggering should be guarded by:

```text
USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false
DATA_OPS_ALLOW_JOB_TRIGGER=false
```

When enabled, operator tooling should call a narrow job trigger helper and read recent `cloud_run_job_runs` rows instead of waiting for long subprocesses.

## Rollback

Pause or delete Scheduler jobs first, then disable the operator trigger flags above. Local subprocess controls remain available while the scheduler path is paused.
