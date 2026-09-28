# Phase 30.9 Bounded Current Roster Lookup Helper Commit Report

Final decision: CURRENT ROSTER LOOKUP HELPER COMMITTED WITH WARNINGS

## Commit

- commit: `ab020e2 Add bounded current roster lookup helper`
- previous checkpoint: `82098ce Add Sleeper current roster merge rules`
- branch: `codex/phase-14-validation-footer`

Committed files:

- `src/pigskin_current_roster_lookup.py`
- `tests/test_pigskin_current_roster_lookup.py`
- `docs/rebuild/validation/phase-30-8-bounded-current-roster-lookup-helper-design.md`
- `docs/rebuild/validation/phase-30-8-bounded-current-roster-lookup-helper-report.md`

Excluded files:

- `docs/rebuild/validation/phase-30-7-sleeper-current-roster-merge-rules-commit-report.md`
- historical Phase 17 through Phase 30 validation backlog
- unrelated owner-review artifacts
- generated output, logs, env files, browser evidence, temp JSON, caches, deployment artifacts, and secrets

No generated or secret-like artifact was committed. The targeted untracked scan found no `output/`, logs, env files, screenshots, Playwright evidence, JSON temp files, cookies, sessions, or secret-looking files.

## Gate State

All authorization and exposure gates were empty or unset:

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

No gate was set during this phase.

## Implementation Summary

Phase 30.8 added an internal bounded current roster lookup helper. The helper reads approved current roster and identity sources through parameterized BigQuery queries and returns payloads compatible with `merge_historical_packet_with_current_roster`.

The helper does not:

- call the live Sleeper API
- run Sleeper ingestion or materialization
- write BigQuery rows
- call Pigskin
- call an LLM
- register a model-visible tool
- deploy staging or production

## Lookup Contract Summary

Primary helper functions:

- `lookup_current_roster_context`
- `build_current_roster_lookup_query`
- `merge_historical_packet_with_current_lookup`

Required bounded identity input:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`
- `player_name`

Name-only lookup requires explicit `limit`, clamped to `MAX_LIMIT=25`.

Rejected inputs:

- empty/unbounded lookup
- unknown arguments
- arbitrary SQL keys: `sql`, `query`, `sql_query`, `raw_sql`

Returned payload fields include:

- `current_team`
- `current_roster_status`
- `current_roster_source`
- `current_roster_as_of`
- `fantasy_availability`
- `free_agent`
- `source_freshness_json`
- `missing_data_flags`
- `availability_context`
- `identity_sources`
- `provenance`

## Source Precedence Summary

Identity mapping:

1. `player_identity_bridge`
2. `dim_players_current`

Current roster state:

1. `sleeper_players_current`
2. `sleeper_roster_players`, when `league_id` is supplied
3. `sleeper_available_players`, when `league_id` and `include_available_players=true` are supplied

`compat_viewer_team_context` is not used as global current player status.

## Identity And Ambiguity Behavior

Stable IDs are preferred over names:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`

Rows from multiple approved sources are collapsed into one candidate when they share stable identity. Multiple candidate identities return:

- `status=ambiguous`
- `found=false`
- `needs_identity_confirmation=true`
- candidate rows

Exact normalized-name lookup is supported. Compact-name expansion remains future work.

## Tyreek Hill Current-Status Handling

Phase 30.8 read-only smoke showed:

- input: `sleeper_player_id=1166`
- status: `ok`
- current team: `LV`
- current roster status: `Active`
- source: `sleeper_players_current`
- as-of: `2026-06-15T19:14:53.601698+00:00`

This is current roster source evidence, not hardcoded truth. The helper does not read 2025 historical packet context and does not infer Miami from a historical packet team.

## Free-Agent And Available-Player Handling

Phase 30.8 read-only available-player smoke used:

- source table: `sleeper_available_players`
- seed player: `A.J. Green`
- `league_id=1314636046436151296`
- `sleeper_player_id=830`
- status: `ok`
- current roster source: `sleeper_available_players`
- availability context: `available`
- current roster as-of: `2026-06-08T18:25:27.387523+00:00`

League-scoped roster and available-player context is preserved in `availability_context`.

## Merge-Layer Integration

`merge_historical_packet_with_current_lookup` is an internal API that:

1. runs bounded current roster lookup
2. passes `current_roster_context` into `merge_historical_packet_with_current_roster`
3. attaches lookup evidence under `current_roster_lookup`

This phase did not wire the helper into Pigskin tools, Streamlit UI, or any model-visible surface.

## Source Provenance And As-Of Handling

Returned contexts preserve:

- `current_roster_source`
- `current_roster_as_of`
- `source_freshness_json`
- `missing_data_flags`
- `provenance`
- `identity_sources`
- `availability_context`

Latest snapshot rules:

- `sleeper_players_current`: latest `snapshot_at`
- `sleeper_roster_players`: latest `snapshot_at` for supplied `league_id`
- `sleeper_available_players`: latest `snapshot_at` for supplied `league_id`

## Source Inventory Summary

Read-only current roster and identity counts:

| Source | Row count |
| --- | ---: |
| `sleeper_players_current` | 4,254 |
| `sleeper_roster_players` | 636 |
| `sleeper_available_players` | 3,032 |
| `sleeper_viewer_team_snapshots` | 3 |
| `compat_viewer_team_context` | 0 |
| `player_identity_bridge` | 11,212 |
| `dim_players_current` | 11,212 |

No current roster source rows were written.

## Test Results

Final local checks passed:

- `scripts/check_deployment_safety.py`
- `py_compile src\pigskin_current_roster_lookup.py`
- `py_compile src\pigskin_current_roster_merge.py`
- `py_compile src\pigskin_packet_guardrails.py`
- `py_compile src\pigskin_packet_retrieval.py`
- `py_compile src\pigskin_context_tools.py`
- `py_compile src\llm_context_packets.py`
- `py_compile app.py`
- `compileall -q src scripts`
- `tests.test_pigskin_current_roster_lookup`: 18 tests
- `tests.test_pigskin_current_roster_merge`: 16 tests
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests
- `tests.test_pigskin_packet_retrieval`: 12 tests
- `unittest discover tests`: 545 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: catalog discovered through validation 200

The full-suite log includes existing mocked fixture messages for load and pipeline paths. They did not run live ingestion or materialization.

## Validation Results

Read-only validation patterns passed:

- `raw_nflverse`: 3 passed, 0 failed, informational coverage warning
- `stg_`: 7 passed, 0 failed
- `advanced_metrics`: 4 passed, 0 failed
- `compat_pigskin`: 2 passed, 0 failed
- `trade_player_scores`: 12 passed, 0 failed
- `trade_pick_scores`: 17 passed, 0 failed, informational model-version warning

Known informational warnings:

- `181_raw_nflverse_season_week_coverage.sql` returned review rows, first row `raw_nflverse_pbp` with `row_count=580005`.
- `178_trade_pick_scores_model_version_coverage.sql` returned `trade_pick_score_v0_2026_001` with 64 score rows.

## Warehouse Read-Only State

Read-only packet confirmation:

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
- remaining untracked file count before this report: 103
- remaining untracked files are historical validation backlog and owner-review reports

This Phase 30.9 report is intentionally left uncommitted for owner review.

## Remaining Warnings

- Compact-name expansion remains future work.
- `compat_viewer_team_context` currently has 0 rows and is not used as global current player status.
- The helper remains internal only. No model-visible tool exposure was added.
- Phase 30.7 commit evidence and historical validation backlog remain untracked.
- Git reported LF-to-CRLF working-copy warnings during staging for the four committed files. `git diff --cached --check` passed.

## Recommended Next Phase

Recommended next phase: Phase 30.10, wire lookup helper into merge-layer QA.

Alternative next phases:

- Compact/full-name identity bridge improvements.
- Owner exposure decision for model-visible historical packet tool.
- Staging-only exposure test for historical packet tool.
