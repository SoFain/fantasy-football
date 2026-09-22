# Phase 29.3 nflverse Warehouse Contracts Report

Date: 2026-06-29

Final decision: NFLVERSE WAREHOUSE CONTRACTS READY WITH WARNINGS

## Scope

Phase 29.3 created additive contract, migration, view, validation, test, and rollout documentation scaffolding for the nflverse historical feature warehouse.

No BigQuery rows were written. No migration was applied. No table was created live. No nflverse ingestion, historical backfill, weekly refresh, advanced metric materialization, Pigskin packet refresh, deploy, feature flag change, Cloud Run Job trigger, Scheduler job, LLM-backed action, Pigskin prompt, scraping, external fetch, ranking build, Firebase artifact, staging action, or production action occurred.

## Authorization Gate State

Checked gates:

| Gate | State |
| --- | --- |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_PROJECTION_CONTEXT_REFRESH` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `ALLOW_VALIDATE_WAREHOUSE_CLOUD_RUN_TEST` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |

No gate was set during this phase.

## Git State

Latest commit at phase start:

`a73656c Document draft pick score release package`

Recent Phase 28 commits are present:

- `a73656c Document draft pick score release package`
- `6e4b565 Draft pick score lane and staging UI`

Phase 29.1 and Phase 29.2 reports remain untracked owner-review artifacts:

- `docs/rebuild/validation/phase-29-1-pigskin-advanced-metrics-source-audit-report.md`
- `docs/rebuild/validation/phase-29-2-nflverse-historical-backfill-design-report.md`

There were no staged files.

## Files Created or Changed

### Migration

- `bigquery/migrations/0027__nflverse_historical_feature_warehouse.sql`

### Raw Contracts

- `bigquery/contracts/raw_nflverse_pbp.md`
- `bigquery/contracts/raw_nflverse_weekly.md`
- `bigquery/contracts/raw_nflverse_rosters.md`
- `bigquery/contracts/raw_nflverse_rosters_weekly.md`
- `bigquery/contracts/raw_nflverse_players.md`
- `bigquery/contracts/raw_nflverse_ff_playerids.md`
- `bigquery/contracts/raw_nflverse_schedules.md`
- `bigquery/contracts/raw_nflverse_teams.md`
- `bigquery/contracts/raw_nflverse_team_stats.md`
- `bigquery/contracts/raw_nflverse_injuries.md`
- `bigquery/contracts/raw_nflverse_depth_charts.md`
- `bigquery/contracts/raw_nflverse_snap_counts.md`
- `bigquery/contracts/raw_nflverse_participation.md`
- `bigquery/contracts/raw_nflverse_ngs_passing.md`
- `bigquery/contracts/raw_nflverse_ngs_rushing.md`
- `bigquery/contracts/raw_nflverse_ngs_receiving.md`
- `bigquery/contracts/raw_nflverse_ftn_charting.md`
- `bigquery/contracts/raw_nflverse_draft_picks.md`

### Staging Contracts

- `bigquery/contracts/stg_player_identity.md`
- `bigquery/contracts/stg_game_context.md`
- `bigquery/contracts/stg_player_week_stats.md`
- `bigquery/contracts/stg_team_week_stats.md`
- `bigquery/contracts/stg_play_player_events.md`
- `bigquery/contracts/stg_participation_context.md`

### Feature and Compatibility Contracts

- `bigquery/contracts/player_week_advanced_metrics.md`
- `bigquery/contracts/player_recent_advanced_metrics_current.md`
- `bigquery/contracts/team_week_context_metrics.md`
- `bigquery/contracts/qb_week_environment_metrics.md`
- `bigquery/contracts/player_role_usage_metrics_current.md`
- `bigquery/contracts/pigskin_player_context_packet_current.md`
- `bigquery/contracts/compat_pigskin_player_context_current.md`

### View SQL

- `bigquery/views/player_recent_advanced_metrics_current.sql`
- `bigquery/views/player_role_usage_metrics_current.sql`
- `bigquery/views/compat_pigskin_player_context_current.sql`

### Validation SQL

- `bigquery/validations/179_raw_nflverse_tables_exist.sql`
- `bigquery/validations/180_raw_nflverse_load_metadata.sql`
- `bigquery/validations/181_raw_nflverse_season_week_coverage.sql`
- `bigquery/validations/182_stg_nflverse_tables_exist.sql`
- `bigquery/validations/183_stg_player_identity_grain.sql`
- `bigquery/validations/184_stg_game_context_grain.sql`
- `bigquery/validations/185_stg_player_week_stats_grain.sql`
- `bigquery/validations/186_stg_team_week_stats_grain.sql`
- `bigquery/validations/187_stg_play_player_events_grain.sql`
- `bigquery/validations/188_stg_participation_context_sanity.sql`
- `bigquery/validations/189_player_identity_coverage.sql`
- `bigquery/validations/190_advanced_metrics_tables_exist.sql`
- `bigquery/validations/191_player_week_advanced_metrics_grain.sql`
- `bigquery/validations/192_advanced_metrics_range_sanity.sql`
- `bigquery/validations/193_advanced_metrics_denominator_flags.sql`
- `bigquery/validations/194_rolling_window_consistency.sql`
- `bigquery/validations/195_source_freshness_present.sql`
- `bigquery/validations/196_missing_flags_present.sql`
- `bigquery/validations/197_compat_pigskin_context_exists.sql`
- `bigquery/validations/198_compat_pigskin_context_no_raw_dependencies.sql`
- `bigquery/validations/199_no_route_metrics_without_source.sql`
- `bigquery/validations/200_no_pressure_metrics_without_source.sql`

### Docs

- `docs/rebuild/table-classification.md`
- `docs/rebuild/compatibility-contracts.md`
- `docs/rebuild/nflverse-historical-backfill-plan.md`
- `docs/rebuild/pigskin-advanced-metrics-warehouse.md`

### Tests

- `tests/test_nflverse_historical_contracts.py`
- `tests/test_pigskin_advanced_metrics_contracts.py`

## Migration Summary

Migration number: `0027`

Migration file:

`bigquery/migrations/0027__nflverse_historical_feature_warehouse.sql`

The migration is additive. It creates empty raw, staging, feature, packet, and compatibility objects. It does not alter existing production-facing tables or score tables.

Objects created by the migration:

- 18 raw `raw_nflverse_*` tables;
- 6 canonical staging tables;
- 3 base feature or packet tables;
- 3 current or compatibility views.

The migration contains no `DROP`, `DELETE`, `TRUNCATE`, `INSERT`, `MERGE`, or destructive `ALTER TABLE` statement.

## Raw Contract Summary

Raw contracts define purpose, nflreadpy loader, grain, idempotency key, required known source columns, passthrough policy, load metadata, partitioning, clustering, refresh strategy, replacement note, and safety boundary.

Common load metadata required across raw tables:

- `source_system`
- `source_loader`
- `source_version`
- `source_season`
- `source_week`
- `source_refresh_id`
- `loaded_at`
- `loaded_by`
- `row_hash`

Each raw contract explicitly states that the raw table is not Pigskin safe and not UI safe.

## Staging Contract Summary

Staging contracts cover:

- `stg_player_identity`;
- `stg_game_context`;
- `stg_player_week_stats`;
- `stg_team_week_stats`;
- `stg_play_player_events`;
- `stg_participation_context`.

`stg_play_player_events` normalizes play-level passer, receiver, rusher, target, rush, reception, touchdown, and team events for later metric construction.

`stg_participation_context` keeps `route_share` nullable and requires `has_true_route_source` before any route metric can be populated.

## Feature Mart Contract Summary

Feature contracts cover:

- player-week advanced metrics;
- recent player advanced metrics current view;
- team-week context metrics;
- QB week environment metrics;
- player role usage metrics current view;
- Pigskin player context packet current table;
- Pigskin compatibility context view.

Feature contracts include `metric_version`, `feature_run_id`, `packet_version` where needed, source freshness, missing-data flags, and current as-of season/week fields.

## Compatibility View Summary

Created standalone view SQL files:

- `player_recent_advanced_metrics_current.sql`
- `player_role_usage_metrics_current.sql`
- `compat_pigskin_player_context_current.sql`

Compatibility rules:

- current views read derived feature marts;
- compatibility view reads `pigskin_player_context_packet_current`;
- compatibility view does not read raw/source tables;
- no request-time write path is added.

Forbidden direct dependencies for the compatibility view:

- `raw_nflverse_*`
- `play_by_play`
- `weekly_metrics`
- `ngs_*`
- `ftn_charting`
- `weekly_snap_counts`
- `injury_reports`
- `depth_charts`
- `source_*`
- `raw_*`

## Validation Summary

Validation files `179` through `200` were added. They cover:

- raw object existence;
- raw metadata columns;
- raw season/week coverage review;
- staging object existence;
- staging grain checks;
- participation sanity;
- identity coverage review;
- advanced metrics object existence;
- player-week metric grain;
- metric range checks;
- denominator and missing-flag handling;
- rolling-window review;
- source freshness;
- compatibility view existence;
- compatibility view raw/source dependency guard;
- route metrics blocked without true route source;
- pressure metrics blocked without true pressure source.

Validation discovery now reports `Total validation files: 200`.

## Tests Added

`tests/test_nflverse_historical_contracts.py` verifies:

- migration exists and is additive;
- raw contracts exist and are marked not Pigskin/UI safe;
- staging and feature contracts exist;
- validation files exist;
- route and pressure metrics remain blocked until true source fields exist.

`tests/test_pigskin_advanced_metrics_contracts.py` verifies:

- compatibility view SQL does not read raw/source tables;
- the compatibility contract forbids raw dependencies;
- Pigskin tool declarations do not expose SQL or raw/source tables;
- Streamlit does not reference new request-time write targets.

## Check Results

Baseline before edits:

- `scripts/check_deployment_safety.py`: pass
- targeted `py_compile` commands: pass
- `compileall -q src scripts`: pass
- `run_bigquery_migrations.py --list-pending`: no pending migrations before Phase 29.3 files
- `run_bigquery_validations.py --dry-run`: 178 validation files before Phase 29.3 files

After scaffolding:

- `scripts/check_deployment_safety.py`: pass
- `python -m unittest tests.test_nflverse_historical_contracts`: pass
- `python -m unittest tests.test_pigskin_advanced_metrics_contracts`: pass
- `python -m unittest discover tests`: pass, 416 tests
- `run_bigquery_migrations.py --dry-run`: pass, discovers `0027`
- `run_bigquery_migrations.py --list-pending`: pass, pending migration is `0027` only
- `run_bigquery_validations.py --dry-run`: pass, discovers 200 validation files

No migration apply command was run.

## Pending Migration State

Ledger-aware pending migration list:

`0027: nflverse historical feature warehouse`

This is expected. Phase 29.3 created migration scaffolding only.

## Safety Exclusions

Confirmed exclusions:

- no BigQuery writes;
- no migration apply;
- no table creation live;
- no ingestion;
- no historical backfill;
- no weekly refresh;
- no advanced metric materialization;
- no Pigskin packet refresh;
- no staging deploy;
- no production deploy;
- no feature flag changes;
- no Cloud Run Job triggers;
- no Scheduler jobs;
- no LLM-backed actions;
- no Pigskin prompts;
- no scraping or external fetch;
- no Firebase artifacts;
- no rankings.

## Remaining Warnings

- Migration `0027` is pending by design and must not be applied until a separate apply phase authorizes it.
- The schema is intentionally conservative. Real nflreadpy schema inspection is still required before any source write path is implemented.
- Route share, first-read share, true pressure, alignment splits, and contact yards remain blocked until true sources are identified.
- Current pipeline still rejects week bounds and writes legacy table names. A future pipeline lane is needed before any backfill.
- Existing `ingest-nflverse` Cloud Run Job remains too coarse for this Phase 29 design.
- Phase 29.1 and Phase 29.2 reports remain untracked owner-review artifacts.

## Recommended Next Phase

Phase 29.4 should be a migration-apply gate only:

1. confirm no data-write gates are set;
2. confirm pending migration set is exactly `0027`;
3. review the migration for additive-only behavior;
4. apply only `0027` if explicitly authorized;
5. verify object existence and zero-row state;
6. do not backfill nflverse data.

Backfill, weekly refresh, advanced metric materialization, and Pigskin packet refresh should remain separate later phases with explicit gates.

## Final Decision

NFLVERSE WAREHOUSE CONTRACTS READY WITH WARNINGS
