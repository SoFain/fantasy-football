# Phase 30.7 Sleeper Current Roster Merge Rules Commit Report

Final decision: SLEEPER CURRENT ROSTER MERGE RULES COMMITTED WITH WARNINGS

## Commit

- commit: `82098ce Add Sleeper current roster merge rules`
- previous checkpoint: `859ad96 Add Pigskin historical packet guardrails`
- branch: `codex/phase-14-validation-footer`

Committed files:

- `src/pigskin_current_roster_merge.py`
- `tests/test_pigskin_current_roster_merge.py`
- `docs/rebuild/validation/phase-30-6-sleeper-current-roster-merge-rules-design.md`
- `docs/rebuild/validation/phase-30-6-sleeper-current-roster-merge-rules-report.md`

Excluded files:

- historical Phase 17 through Phase 30 validation backlog
- owner-review reports, including Phase 30.3 and Phase 30.5 commit evidence
- generated output, logs, env files, browser evidence, temp JSON, caches, deployment artifacts, and secrets

No generated or secret-like artifact was committed. The targeted untracked scan found no `output/`, logs, env files, screenshots, Playwright evidence, JSON temp files, cookies, sessions, or secret-looking files.

## Gate State

All checked authorization and exposure gates were empty or unset:

- `ALLOW_PIGSKIN_PACKET_REFRESH`
- `ALLOW_ADVANCED_METRICS_MATERIALIZATION`
- `ALLOW_NFLVERSE_STAGING_MATERIALIZATION`
- `ALLOW_NFLVERSE_HISTORICAL_BACKFILL`
- `ALLOW_NFLVERSE_WEEKLY_REFRESH`
- `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY`
- `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION`
- `ALLOW_TRADE_SCORE_MATERIALIZATION`
- `ALLOW_LIMITED_PRODUCTION_DEPLOY`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`

## Implementation Summary

Phase 30.6 added an internal pure merge layer for historical Pigskin packet results plus caller-supplied current roster payloads. The layer does not run a current roster lookup, call Sleeper, call BigQuery, call Pigskin, call an LLM, write data, or register a model-visible tool.

The merge contract keeps historical packet evidence as completed-season context. Packet `team` stays `historical_team`. Current roster, current team, roster availability, and free-agent status come only from the supplied current roster payload.

## Merge Contract

The merge response preserves:

- `historical_team` from packet context
- `current_team` from current roster payload only
- `current_roster_status`
- `current_roster_source`
- `current_roster_as_of`
- `team_mismatch`
- `provenance`
- `packet_as_of_season`
- `packet_as_of_week`
- `blocked_metrics`
- `packet_warnings`
- `source_freshness`
- `missing_data_flags`

Packet `current_team` fields are stripped before output. Missing current roster payload returns `current_roster_unavailable` and does not infer current status from historical team.

## Identity And Ambiguity

Stable IDs are compared across `player_id_internal`, `gsis_id`, and `sleeper_player_id` when available. Shared ID mismatch returns `needs_identity_confirmation`.

Ambiguous packet results and multiple current roster candidates also return `needs_identity_confirmation`. Compact names are not silently resolved to a selected player.

## Tyreek And Free-Agent Handling

The Tyreek Hill test path preserves 2025 Miami packet context as `historical_team=MIA`. Current free-agent status is accepted only from the current roster payload. If current roster data says free agent, the output keeps the current status as free agent and warns that the packet shows prior usage only.

If historical team and current team differ, both are returned with provenance and `team_mismatch=true`.

## Packet Guardrails

The package preserves:

- blocked metrics as unavailable, not zero
- packet warnings
- source freshness
- missing-data flags
- Week 22 and postseason context
- no arbitrary SQL input
- no model-visible historical packet tool registration

SQL/query-style input keys are rejected with `blocked_reason=arbitrary_sql_not_allowed`.

## Source Inventory

Read-only inventory from Phase 30.6 remains the source context:

- `sleeper_players_current`: 4,254 rows
- `sleeper_roster_players`: 636 rows
- `sleeper_available_players`: 3,032 rows
- `sleeper_viewer_team_snapshots`: 3 rows
- `compat_viewer_team_context`: 10 rows
- `player_identity_bridge`: 11,212 rows
- `dim_players_current`: 11,212 rows

No source table was modified in Phase 30.7.

## Checks Run

Local checks passed:

- `scripts/check_deployment_safety.py`
- `py_compile src\pigskin_current_roster_merge.py`
- `py_compile src\pigskin_packet_guardrails.py`
- `py_compile src\pigskin_packet_retrieval.py`
- `py_compile src\pigskin_context_tools.py`
- `py_compile src\llm_context_packets.py`
- `py_compile app.py`
- `compileall -q src scripts`
- `tests.test_pigskin_current_roster_merge`: 16 tests
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests
- `tests.test_pigskin_packet_retrieval`: 12 tests
- `unittest discover tests`: 527 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: catalog discovered through validation 200

The full-suite log includes existing mocked unit-test fixture messages from load and pipeline paths. They did not run live ingestion or materialization.

## Validation Results

Read-only validation patterns passed:

- `raw_nflverse`: 3 passed, 0 failed, informational coverage warning
- `stg_`: 7 passed, 0 failed
- `advanced_metrics`: 4 passed, 0 failed
- `compat_pigskin`: 2 passed, 0 failed
- `trade_player_scores`: 12 passed, 0 failed
- `trade_pick_scores`: 17 passed, 0 failed, informational model-version warning

Known informational warnings:

- `181_raw_nflverse_season_week_coverage.sql` returned review rows, first row `raw_nflverse_pbp` with `row_count=580005`, min season 2014, max season 2025, and 257 season-week values.
- `178_trade_pick_scores_model_version_coverage.sql` returned `trade_pick_score_v0_2026_001` with 64 score rows.

## Warehouse Read-Only State

Read-only confirmation:

- `pigskin_player_context_packet_current`: 4,084 rows
- `compat_pigskin_player_context_current`: 4,084 rows
- 2025 compat packet rows: 510
- 2026+ compat packet rows: 0

Category confirmation:

| Category | Table count | Row count | 2026+ rows |
| --- | ---: | ---: | ---: |
| raw_nflverse | 18 | 1,757,357 | 0 |
| staging | 6 | 2,462,109 | 0 |
| advanced_metrics | 7 | 252,568 | 0 |

The first advanced-metrics table metadata total was stale. Direct `COUNT(*)` per advanced table reconciled the expected total of 252,568.

## Service Untouched Confirmation

Production remained unchanged:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: `nfl-studio-dashboard-00077-2jp:100`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=false`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` absent/unset

Staging remained unchanged:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- traffic: `nfl-studio-dashboard-staging-00029-jtb:100`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- `USE_COMPAT_TRADE_PLAYER_HISTORY=true`
- `USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=false`
- `DATA_OPS_ALLOW_JOB_TRIGGER=false`
- `USE_DATA_OPS_LOCAL_SUBPROCESS_CONTROLS=false`
- `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER=false`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` absent/unset

No deployment occurred.

## Post-Commit State

- no tracked diff after commit
- no staged files after commit
- remaining untracked file count before this report: 102
- remaining untracked files are historical validation backlog and owner-review reports

This Phase 30.7 report is intentionally left uncommitted for owner review.

## Remaining Warnings

- A bounded current roster lookup helper still needs a separate phase before any model-visible use.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` remains unset and no tool exposure was added.
- Historical validation backlog remains untracked by owner decision.
- Git reported LF-to-CRLF working-copy warnings during staging for the four committed files. `git diff --cached --check` passed.

## Recommended Next Phase

Recommended next phase: Phase 30.8, build a bounded current roster lookup helper.

Alternative future phases:

- owner exposure decision for model-visible historical packet tool
- staging-only exposure test for historical packet tool
- read-only QA UI for historical packet lookup
