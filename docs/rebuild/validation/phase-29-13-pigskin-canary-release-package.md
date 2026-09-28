# Phase 29.13 Pigskin Canary Release Package

Date: 2026-06-29

Package status: ready for commit review

## Final Canary State

The Phase 29 canary proves the 2014 nflverse historical path from raw source tables through Pigskin-safe context packets.

Current warehouse state:

- 2014 raw nflverse tables populated.
- 2014 staging tables populated.
- 2014 base advanced metrics populated.
- 2014 current derived metric views populated.
- `pigskin_player_context_packet_current` populated with 482 rows.
- `compat_pigskin_player_context_current` returns 482 rows through the view.
- Packet version: `nflverse_pigskin_packet_v0_2014_001`
- Source metric version: `nflverse_adv_metrics_v0_2014_001`
- Production and staging services were not changed during Phase 29.12.

## Source Files Added

- `src/nflverse_backfill_plan.py`
- `src/nflverse_backfill.py`
- `src/nflverse_staging.py`
- `src/nflverse_advanced_metrics.py`
- `src/nflverse_pigskin_packets.py`

These modules cover the source-family registry, bounded raw backfill executor, staging transforms, advanced metrics materialization logic, and deterministic Pigskin packet generation.

## Tests Added

- `tests/test_nflverse_backfill_plan.py`
- `tests/test_nflverse_backfill_executor.py`
- `tests/test_nflverse_staging.py`
- `tests/test_nflverse_advanced_metrics.py`
- `tests/test_nflverse_pigskin_packets.py`
- `tests/test_nflverse_historical_contracts.py`
- `tests/test_pigskin_advanced_metrics_contracts.py`

The tests cover fail-closed gates, bounded planner behavior, optional source mapping, staging transforms, metric bounds, packet write gating, Pigskin-safe view contracts, and raw/source dependency controls.

## Migration Added And Applied

- `bigquery/migrations/0027__nflverse_historical_feature_warehouse.sql`

Migration 0027 creates the raw nflverse warehouse, staging layer, advanced metric marts, current metric views, Pigskin packet table, and Pigskin compatibility view. Phase 29.4 applied it before later authorized data phases.

## Contracts Added

Raw nflverse source contracts:

- `bigquery/contracts/raw_nflverse_depth_charts.md`
- `bigquery/contracts/raw_nflverse_draft_picks.md`
- `bigquery/contracts/raw_nflverse_ff_playerids.md`
- `bigquery/contracts/raw_nflverse_ftn_charting.md`
- `bigquery/contracts/raw_nflverse_injuries.md`
- `bigquery/contracts/raw_nflverse_ngs_passing.md`
- `bigquery/contracts/raw_nflverse_ngs_receiving.md`
- `bigquery/contracts/raw_nflverse_ngs_rushing.md`
- `bigquery/contracts/raw_nflverse_participation.md`
- `bigquery/contracts/raw_nflverse_pbp.md`
- `bigquery/contracts/raw_nflverse_players.md`
- `bigquery/contracts/raw_nflverse_rosters.md`
- `bigquery/contracts/raw_nflverse_rosters_weekly.md`
- `bigquery/contracts/raw_nflverse_schedules.md`
- `bigquery/contracts/raw_nflverse_snap_counts.md`
- `bigquery/contracts/raw_nflverse_team_stats.md`
- `bigquery/contracts/raw_nflverse_teams.md`
- `bigquery/contracts/raw_nflverse_weekly.md`

Staging contracts:

- `bigquery/contracts/stg_game_context.md`
- `bigquery/contracts/stg_participation_context.md`
- `bigquery/contracts/stg_play_player_events.md`
- `bigquery/contracts/stg_player_identity.md`
- `bigquery/contracts/stg_player_week_stats.md`
- `bigquery/contracts/stg_team_week_stats.md`

Metric and packet contracts:

- `bigquery/contracts/player_week_advanced_metrics.md`
- `bigquery/contracts/team_week_context_metrics.md`
- `bigquery/contracts/qb_week_environment_metrics.md`
- `bigquery/contracts/player_recent_advanced_metrics_current.md`
- `bigquery/contracts/player_role_usage_metrics_current.md`
- `bigquery/contracts/pigskin_player_context_packet_current.md`
- `bigquery/contracts/compat_pigskin_player_context_current.md`

## Views Added

- `bigquery/views/player_recent_advanced_metrics_current.sql`
- `bigquery/views/player_role_usage_metrics_current.sql`
- `bigquery/views/compat_pigskin_player_context_current.sql`

The Pigskin compatibility view reads only from `pigskin_player_context_packet_current`. It does not expose raw or source tables.

## Validations Added

Validation files 179 through 200 cover:

- raw nflverse table existence, metadata, and coverage review;
- staging table existence and grain;
- player identity coverage review;
- advanced metrics existence, grain, range sanity, denominator flags, rolling windows, source freshness, and missing flags;
- Pigskin compatibility view existence and raw/source dependency exclusion;
- route and pressure metric blocking.

## Reports Included

- `docs/rebuild/validation/phase-29-1-pigskin-advanced-metrics-source-audit-report.md`
- `docs/rebuild/validation/phase-29-2-nflverse-historical-backfill-design-report.md`
- `docs/rebuild/validation/phase-29-3-nflverse-warehouse-contracts-report.md`
- `docs/rebuild/validation/phase-29-4-nflverse-warehouse-migration-apply-report.md`
- `docs/rebuild/validation/phase-29-5-nflverse-backfill-planner-report.md`
- `docs/rebuild/validation/phase-29-6-nflverse-raw-backfill-smoke-report.md`
- `docs/rebuild/validation/phase-29-6a-nflverse-optional-schema-mapping-report.md`
- `docs/rebuild/validation/phase-29-6b-nflverse-optional-raw-repair-smoke-report.md`
- `docs/rebuild/validation/phase-29-7-nflverse-staging-dry-run-report.md`
- `docs/rebuild/validation/phase-29-8-nflverse-staging-materialization-report.md`
- `docs/rebuild/validation/phase-29-9-nflverse-advanced-metrics-dry-run-report.md`
- `docs/rebuild/validation/phase-29-10-nflverse-base-advanced-metrics-materialization-report.md`
- `docs/rebuild/validation/phase-29-11-pigskin-current-packet-dry-run-report.md`
- `docs/rebuild/validation/phase-29-12-pigskin-packet-materialization-report.md`

## Documentation Included

- `docs/rebuild/nflverse-historical-backfill-plan.md`
- `docs/rebuild/pigskin-advanced-metrics-warehouse.md`
- `docs/rebuild/nflverse-backfill-planner.md`
- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/table-classification.md`

## Known Warnings

- Some packet rows carry expected missing-data warnings, mostly missing snap share or sample-size flags.
- Route share, yards per route run, first-read share, red-zone usage, true pressure, contact yards, and alignment metrics remain blocked or null until true sources are verified.
- The raw nflverse coverage validation is informational by design.
- Trade pick model-version coverage validation remains informational and unrelated to the Phase 29 package.
- Phase 29 is a 2014 canary. It is not a 2025 or 2026 current-season content rollout.

## Deliberately Not Included

- Historical validation backlog from Phases 17 through 28.
- Local output folders, browser evidence, logs, cache files, environment files, secret-looking files, or deployment artifacts.
- New data writes, materializations, deployments, rankings, Cloud Run Jobs, Scheduler jobs, Pigskin prompts, LLM calls, scraping, or Firebase artifacts.

## Next Expansion Plan

Recommended next phase: Phase 29.14, authorized historical expansion planner for 2015 through 2025 batches.

That phase should stay planner-first, use bounded season windows, preserve the same fail-closed authorization gates, and continue proving raw/source data never reaches Pigskin-facing compatibility surfaces.

