# Phase 30.8 Bounded Current Roster Lookup Helper Report

Final decision: CURRENT ROSTER LOOKUP HELPER READY WITH WARNINGS

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

## Git State

- latest commit: `82098ce Add Sleeper current roster merge rules`
- no tracked diff at phase start
- no staged files at phase start
- unrelated historical validation backlog remained untracked

Phase 30.8 changed files, but did not stage or commit them:

- `src/pigskin_current_roster_lookup.py`
- `tests/test_pigskin_current_roster_lookup.py`
- `docs/rebuild/validation/phase-30-8-bounded-current-roster-lookup-helper-design.md`
- `docs/rebuild/validation/phase-30-8-bounded-current-roster-lookup-helper-report.md`

Existing untracked evidence remains:

- `docs/rebuild/validation/phase-30-7-sleeper-current-roster-merge-rules-commit-report.md`
- historical owner-review validation backlog

## Baseline Checks

Baseline checks passed before code changes:

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

## Current Roster Source Audit

Repo audit found existing identity and viewer-team patterns in:

- `src/build_player_identity.py`
- `src/viewer_team_context.py`
- `src/pigskin_packet_retrieval.py`
- `tests/test_viewer_team_context.py`
- `tests/test_pigskin_packet_retrieval.py`

The closest existing pattern is `src/pigskin_packet_retrieval.py`: parameterized BigQuery query, identifier validation, explicit byte cap, bounded limit, no raw-source exposure, and ambiguity responses.

Approved current roster and identity source schema state:

| Source | Row count | Relevant fields |
| --- | ---: | --- |
| `player_identity_bridge` | 11,212 | `player_id_internal`, `gsis_id`, `sleeper_player_id`, `full_name`, `display_name`, `normalized_name`, `position`, `current_team`, `active_status`, `source_freshness_json`, `missing_data_flags`, `updated_at` |
| `dim_players_current` | 11,212 | `player_id_internal`, `display_name`, `full_name`, `normalized_name`, `position`, `current_team`, `active_status`, `sleeper_player_id`, `gsis_id`, `source_freshness_json`, `missing_data_flags`, `updated_at` |
| `sleeper_players_current` | 4,254 | `snapshot_at`, `sleeper_player_id`, `gsis_id`, `player_name`, `position`, `team`, `active`, `status`, `injury_status` |
| `sleeper_roster_players` | 636 | `snapshot_at`, `league_id`, `season`, `week`, `roster_id`, `sleeper_player_id`, `player_name`, `position`, `team`, `gsis_id`, `status`, `is_starter`, `is_taxi`, `is_reserve` |
| `sleeper_available_players` | 3,032 | `snapshot_at`, `league_id`, `season`, `week`, `sleeper_player_id`, `player_name`, `position`, `team`, `gsis_id`, `status` |
| `sleeper_viewer_team_snapshots` | 3 | viewer-team snapshot metadata |
| `compat_viewer_team_context` | 0 | viewer-team context packet fields |

No live Sleeper API path was used or added.

## Files Changed

Created:

- `src/pigskin_current_roster_lookup.py`
- `tests/test_pigskin_current_roster_lookup.py`
- `docs/rebuild/validation/phase-30-8-bounded-current-roster-lookup-helper-design.md`
- `docs/rebuild/validation/phase-30-8-bounded-current-roster-lookup-helper-report.md`

No existing runtime UI or Pigskin tool registration was changed.

## Lookup Contract Summary

The new helper is internal and read-only:

- `lookup_current_roster_context(...)`
- `build_current_roster_lookup_query(...)`
- `merge_historical_packet_with_current_lookup(...)`

It requires at least one bounded identity input:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`
- `player_name`

Name-only lookup requires explicit `limit`, clamped to `MAX_LIMIT=25`.

It rejects:

- empty/unbounded lookup
- unknown lookup arguments
- `sql`, `query`, `sql_query`, and `raw_sql`

Output is compatible with `merge_historical_packet_with_current_roster` and includes:

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
2. `sleeper_roster_players` when `league_id` is supplied
3. `sleeper_available_players` when `league_id` and `include_available_players=true` are supplied

League roster and availability context is preserved separately in `availability_context`.

## Identity And Ambiguity Behavior

Stable IDs are preferred over names:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`

Rows from multiple approved sources are collapsed into one candidate when they share a stable identity. Multiple candidate identities return:

- `status=ambiguous`
- `found=false`
- `needs_identity_confirmation=true`
- `candidates=[...]`

Exact normalized-name lookup is supported. Compact-name expansion is not part of this helper yet.

## Tyreek Hill Current-Status Handling

Read-only smoke by stable Sleeper ID:

- input: `sleeper_player_id=1166`
- status: `ok`
- current team: `LV`
- current roster status: `Active`
- source: `sleeper_players_current`
- as-of: `2026-06-15T19:14:53.601698+00:00`

This comes from current roster data only. The helper does not read 2025 historical packet context and cannot infer Miami from a historical packet team.

Read-only name smoke:

- input: `player_name=Tyreek Hill`, `limit=5`
- status: `ok`
- current roster source: `sleeper_players_current`
- warning: current team was unknown in the matched approved source row

Stable ID is the recommended path for Tyreek-style cases.

## Free-Agent And Available-Player Handling

Read-only available-player smoke used a real `sleeper_available_players` row:

- seed player: `A.J. Green`
- `league_id=1314636046436151296`
- `sleeper_player_id=830`
- source table: `sleeper_available_players`
- status: `ok`
- current roster source: `sleeper_available_players`
- availability context: `available`
- current roster as-of: `2026-06-08T18:25:27.387523+00:00`

The helper preserved league-scoped available-player context without calling Sleeper or writing data.

## Merge-Layer Integration

`merge_historical_packet_with_current_lookup` is internal only. It:

1. runs the bounded current roster lookup
2. passes `current_roster_context` into `merge_historical_packet_with_current_roster`
3. attaches lookup evidence to `current_roster_lookup`

It is not wired into Pigskin tools, Streamlit, or any model-visible surface.

## Source Provenance And As-Of Handling

Returned contexts include:

- `current_roster_source`
- `current_roster_as_of`
- `source_freshness_json`
- `missing_data_flags`
- `provenance`
- `identity_sources`
- `availability_context`

Latest snapshot rules:

- `sleeper_players_current`: latest `snapshot_at`
- `sleeper_roster_players`: latest `snapshot_at` for the supplied `league_id`
- `sleeper_available_players`: latest `snapshot_at` for the supplied `league_id`

## Tests Added

Added `tests/test_pigskin_current_roster_lookup.py` with 18 tests covering:

- empty/unbounded lookup rejection
- arbitrary SQL key rejection
- explicit limit requirement for name lookup
- parameterized SQL
- approved source usage
- stable ID lookups by `player_id_internal`, `sleeper_player_id`, and `gsis_id`
- name ambiguity and candidates
- team/position narrowing parameters
- available/free-agent status
- missing current team stays unknown
- Tyreek current-status separation
- merge-layer compatibility
- source metadata preservation
- deterministic source precedence
- no Sleeper API, Pigskin, LLM, or BigQuery write path

## Optional Read-Only Smoke QA

Smoke calls performed read-only BigQuery queries through the helper:

| Case | Result |
| --- | --- |
| Stable Sleeper ID `1166` | `ok`, `current_team=LV`, `current_roster_status=Active`, `source=sleeper_players_current` |
| Name `Tyreek Hill`, `limit=5` | `ok`, warning for missing current team in matched row |
| Available-player scoped lookup | `ok`, `source=sleeper_available_players`, availability preserved |
| Name `Josh Johnson`, `limit=10` | `ambiguous`, 3 candidates |

No write path was called.

## No-State-Change Confirmation

Warehouse confirmation after the helper smoke:

- `pigskin_player_context_packet_current`: 4,084 rows
- `compat_pigskin_player_context_current`: 4,084 rows
- 2025 compat packet rows: 510
- 2026+ compat packet rows: 0

Current roster source counts:

- `sleeper_players_current`: 4,254
- `sleeper_roster_players`: 636
- `sleeper_available_players`: 3,032
- `sleeper_viewer_team_snapshots`: 3
- `compat_viewer_team_context`: 0
- `player_identity_bridge`: 11,212
- `dim_players_current`: 11,212

Category 2026+ confirmation:

| Category | Table count | Row count | 2026+ rows |
| --- | ---: | ---: | ---: |
| raw_nflverse | 18 | 1,757,357 | 0 |
| staging | 6 | 2,462,109 | 0 |
| advanced_metrics | 7 | 252,568 | 0 |

## Validation Results

Read-only validation patterns:

- `raw_nflverse`: pass, 3 passed, 0 failed, informational coverage warning
- `stg_`: pass, 7 passed, 0 failed
- `advanced_metrics`: pass, 4 passed, 0 failed
- `compat_pigskin`: pass, 2 passed, 0 failed
- `trade_player_scores`: pass, 12 passed, 0 failed
- `trade_pick_scores`: pass, 17 passed, 0 failed, informational model-version warning

Known informational warnings:

- `181_raw_nflverse_season_week_coverage.sql` returned review rows, first row `raw_nflverse_pbp` with `row_count=580005`.
- `178_trade_pick_scores_model_version_coverage.sql` returned `trade_pick_score_v0_2026_001` with 64 score rows.

## Final Local Checks

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

## Staging And Production Untouched

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

## Remaining Warnings

- Name lookup is exact normalized-name matching. Compact-name expansion remains future work.
- `compat_viewer_team_context` currently has 0 rows and is not used as global current player status.
- The helper is internal only. No model-visible tool exposure was added.
- Phase 30.7 commit evidence and historical validation backlog remain untracked.

## Recommended Next Phase

Recommended next phase: Phase 30.9, package and commit current roster lookup helper.

Alternative next phases:

- Wire lookup helper into merge-layer QA.
- Owner exposure decision for model-visible historical packet tool.
- Staging-only exposure test for historical packet tool.
