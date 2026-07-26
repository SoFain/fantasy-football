# Phase 34.9 Sleeper Snapshot Retention Rollout Report

## Final Decision

`WEEKLY SLEEPER SNAPSHOT RETENTION ENABLED`

The RB Fable formula champion remains unchanged. Current Sleeper context stays outside `rb_fable_01_score` and continues to supply team, injury, and depth-order review evidence. Weekly dated snapshots now accumulate the missing historical evidence needed to test a future role-change modifier honestly.

## Deployment

- Cloud Run Job: `archive-sleeper-player-snapshot`, region `us-central1`.
- Image: `sleeper-snapshot-archive@sha256:905b5b04ff6f84d8157f3d2c93ed860d6dd1407815fd604621980ccb0a180512`.
- Base image: reviewed application digest `sha256:11cdd1928773fc7eccc5a2e9dfabf9f47e41c0bc2f344a7398e962d719bc74b0`.
- Runtime identity: `nfl-studio-sa@fantasy-football-498121.iam.gserviceaccount.com`.
- Successful execution: `archive-sleeper-player-snapshot-9j5n9`.
- Scheduler: `archive-sleeper-player-snapshot-weekly`, enabled.
- Schedule: Tuesday at 09:00 UTC. Next scheduled run after rollout: `2026-07-14T09:00:00Z`.
- Scheduler identity: `scheduler-invoker-sa@fantasy-football-498121.iam.gserviceaccount.com`.
- Retry count: 2.

## First Snapshot

- Snapshot date: `2026-07-11`.
- Sleeper rows fetched: 12,200.
- RB rows: 926.
- Current table: `fantasy_football_advanced_metrics.sleeper_current_player_context`.
- History table: `fantasy_football_advanced_metrics.sleeper_player_snapshot_history`.
- Change view: `fantasy_football_advanced_metrics.v_sleeper_player_status_changes`.
- RB review view refreshed: `fantasy_football_advanced_metrics.v_rb_fable_v1_current_context_review`.

The history write is idempotent at `snapshot_date + sleeper_player_id`; a retry on the same date replaces that date rather than appending duplicates.

## Packaging Fix

The shared application image did not contain the archiver or its SQL template. A narrow derivative image was used instead of rebuilding the dirty application tree. It adds only:

- `scripts/build_sleeper_current_player_context.py`
- `bigquery/views/v_rb_fable_v1_current_context_review.sql`

Build definition: `cloudbuild-sleeper-archive.yaml` with `Dockerfile.sleeper-archive`.

## Safety

- No formula weight changed.
- No champion record changed.
- No active ranking order changed.
- No model was trained.
- No application service was deployed.
- The only recurring writes are the current context table, dated history table, and their review views in the isolated advanced-metrics dataset.

## Future Evaluation Gate

Do not add Sleeper depth order to the validated formula until dated preseason snapshots cover enough future outcome seasons for a forward test. Snapshot history can support operational change alerts immediately, but it is not yet historical backtest evidence.
