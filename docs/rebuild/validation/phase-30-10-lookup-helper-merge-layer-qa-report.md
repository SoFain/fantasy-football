# Phase 30.10 Lookup Helper Merge-Layer QA Report

## Final Decision

LOOKUP MERGE QA READY WITH WARNINGS

The internal lookup-plus-merge QA path is implemented, tested, and remains read-only. It is not model-visible. Completion audit tightened one guardrail: current roster requests now require a bounded identity field before packet retrieval. The live warehouse smoke found expected source-data caveats: Tyreek Hill current roster lookup resolves through conflicting stable IDs, and `compat_viewer_team_context` currently has 10 rows instead of the older prompt snapshot of 0. The helper handles those conditions by returning `needs_identity_confirmation` or current-roster-unavailable context instead of silently merging.

## Gate State

All checked authorization and exposure gates were unset:

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

No authorization gates were set during this phase.

## Git State

- Latest commit at start and final check: `ab020e2 Add bounded current roster lookup helper`
- No staged files.
- Known historical validation backlog remains untracked.
- Phase 30.10 untracked files:
  - `src/pigskin_context_qa.py`
  - `tests/test_pigskin_context_qa.py`
  - `docs/rebuild/validation/phase-30-10-lookup-merge-qa-design.md`
  - `docs/rebuild/validation/phase-30-10-lookup-helper-merge-layer-qa-report.md`
- Untracked file count before the completion report update: 107.

## Baseline Checks

Baseline checks passed before implementation:

- `scripts/check_deployment_safety.py`
- `py_compile` for `app.py`, Pigskin packet retrieval, current roster lookup, merge, guardrails, context tools, and LLM context packet modules
- `compileall -q src scripts`
- `tests.test_pigskin_current_roster_lookup`: 18 tests passed
- `tests.test_pigskin_current_roster_merge`: 16 tests passed
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests passed
- `tests.test_pigskin_packet_retrieval`: 12 tests passed
- Full suite before changes: 545 tests passed
- No pending migrations
- Validation dry-run discovered through validation 200

## Helper Contract Review

Reviewed modules:

- `src/pigskin_packet_retrieval.py`
- `src/pigskin_current_roster_lookup.py`
- `src/pigskin_current_roster_merge.py`
- `src/pigskin_packet_guardrails.py`
- `src/pigskin_context_tools.py`
- `app.py`

Confirmed:

- Historical packet retrieval reads `compat_pigskin_player_context_current` through parameterized SQL.
- Current roster lookup reads approved current roster and identity sources only.
- Merge preserves `historical_team` and `current_team` separately.
- Packet `current_team` is stripped and never promoted.
- Missing current roster context stays unavailable.
- Ambiguous historical packet and current roster results are not silently selected.
- Blocked metrics, source freshness, missing-data flags, and packet warnings are preserved.

## Files Changed

Created:

- `src/pigskin_context_qa.py`
- `tests/test_pigskin_context_qa.py`
- `docs/rebuild/validation/phase-30-10-lookup-merge-qa-design.md`
- `docs/rebuild/validation/phase-30-10-lookup-helper-merge-layer-qa-report.md`

## Orchestration Contract Summary

New helper:

`build_historical_packet_current_roster_context(packet_request, current_roster_request, client=None, dataset_id=None)`

Behavior:

- Rejects arbitrary SQL keys before calling helper layers.
- Requires explicit historical `season` or `season_start` plus `season_end`.
- Requires bounded current roster identity before packet retrieval: `player_id_internal`, `sleeper_player_id`, `gsis_id`, or `player_name`.
- Calls `retrieve_historical_pigskin_packets` for historical packet evidence.
- Stops before current lookup if the packet request is ambiguous, unavailable, or not deterministic.
- Calls `lookup_current_roster_context` for current roster state.
- Stops before merge if current roster lookup is ambiguous or fails validation.
- Allows `not_found` current roster lookup to merge as current status unavailable.
- Calls `merge_historical_packet_with_current_roster` only for deterministic packet and deterministic or missing current roster context.
- Returns a structured object with source policies, warnings, packet result, current roster result, merged context, teams, current status, source freshness, missing flags, blocked metrics, and provenance.

## Lookup-Plus-Merge Behavior

Unit tests verify:

- SQL-like keys are rejected in packet and current roster requests.
- Missing historical bounds are rejected.
- Missing current roster identity is rejected before packet retrieval or roster lookup.
- Team and position alone are treated only as narrowing filters and are not accepted as current roster identity.
- Historical packet retrieval receives explicit bounds.
- Current roster lookup receives bounded identity inputs.
- Merge is called only after deterministic helper results.
- Ambiguous packet and current roster outputs return candidates and do not merge.
- Missing current roster context merges as unavailable without using historical team as current team.

## Identity Reconciliation Behavior

The helper preserves identity warnings. If current roster lookup maps to a different stable ID than the packet, the merge returns `needs_identity_confirmation` instead of silently claiming the contexts belong to one resolved identity.

Live smoke showed this for Tyreek Hill:

- Historical packet: `season=2025`, `week=4`, `player_id_internal=00-0033040`, `historical_team=MIA`
- Current lookup by `sleeper_player_id=1166`: `current_team=LV`, `current_roster_status=Active`, `current_roster_source=sleeper_players_current`, `current_roster_as_of=2026-06-15T19:14:53.601698+00:00`
- Result: `needs_identity_confirmation`, `team_mismatch=true`

This is expected guardrail behavior.

## Ambiguity Behavior

Live smoke confirmed a current roster name lookup can block before merge:

- Packet request: Tyreek Hill 2025 week 4 historical packet
- Current roster request: `player_name=Josh Johnson`, `limit=10`
- Current roster result: `ambiguous`, 3 candidates
- QA result: `needs_identity_confirmation`
- Merge was blocked before a selected current roster context was created.

## Tyreek Hill Historical And Current Status Handling

The unit tests and live smoke preserve these fields separately:

- `historical_team=MIA` from historical packet context.
- `current_team=LV` from `sleeper_players_current` when lookup uses `sleeper_player_id=1166`.
- Identity mismatch is not hidden.
- Historical Miami context is not treated as current team.

## Free-Agent And Available-Player Handling

Unit tests verify available-player status is preserved from current roster source data:

- `current_roster_status=available`
- `current_roster_source=sleeper_available_players`
- `current_team=None`

Live smoke using A.J. Green and `sleeper_available_players` returned source `sleeper_available_players`, `current_roster_as_of=2026-06-08T18:25:27.387523+00:00`, and preserved the historical Cincinnati packet context. It also returned `needs_identity_confirmation`, which should be resolved through identity bridge review before any model-visible exposure.

## Current Team Mismatch Handling

Mismatch behavior is preserved:

- `historical_team` comes from the packet.
- `current_team` comes from current roster lookup only.
- Differing teams set `team_mismatch=true`.
- The warning says to preserve both with provenance.

## Week 22 And Postseason Handling

Unit tests verify `week=22` is preserved when the packet request explicitly includes `include_postseason=True`.

Live smoke for Tyreek week 22 returned no packet in the compatibility view, so no merge occurred. That is data availability, not a code failure.

## Blocked Metric Handling

Unit tests verify blocked metrics remain unavailable:

- `blocked_metrics` remain lists such as `["route_share", "pressure_rate"]`
- `source_freshness` is passed through
- `missing_data_flags` is passed through
- No blocked metric is converted to zero

## Source Provenance And As-Of Handling

The helper returns provenance from the merge layer:

- Historical source: `compat_pigskin_player_context_current`
- Packet version and feature run ID where present
- Packet season and week
- Current roster source
- Current roster snapshot/as-of when present

## Tests Added

Added `tests/test_pigskin_context_qa.py` with 18 tests covering:

- SQL key rejection
- Missing historical bounds
- Missing current roster identity
- Team/position-only current roster request blocking
- Bounded packet retrieval call
- Bounded current roster lookup call
- Merge call gating
- Ambiguous packet handling
- Ambiguous current roster handling
- Missing current roster handling
- Tyreek historical/current separation
- Current team source precedence
- Historical team source precedence
- Available-player status
- Team mismatch warnings and provenance
- Blocked metrics
- Week 22 postseason preservation
- Absence of Sleeper API, Pigskin tool, LLM, BigQuery write, and model-visible registration paths

## Optional Read-Only Smoke QA

All smoke calls used the new helper with existing BigQuery clients and no writes.

Warehouse counts:

- `pigskin_player_context_packet_current`: 4,084
- `compat_pigskin_player_context_current`: 4,084
- `compat_pigskin_player_context_current` 2025 rows: 510
- `compat_pigskin_player_context_current` 2026+ rows: 0
- `sleeper_players_current`: 4,254
- `sleeper_roster_players`: 636
- `sleeper_available_players`: 3,032
- `sleeper_viewer_team_snapshots`: 3
- `compat_viewer_team_context`: 10
- `player_identity_bridge`: 11,212
- `dim_players_current`: 11,212

2026+ row checks:

- `raw_nflverse_pbp`: 0
- `raw_nflverse_weekly`: 0
- `stg_game_context`: 0
- `stg_player_week_stats`: 0
- `stg_team_week_stats`: 0
- `stg_play_player_events`: 0
- `stg_participation_context`: 0
- `player_week_advanced_metrics`: 0
- `team_week_context_metrics`: 0
- `qb_week_environment_metrics`: 0
- `pigskin_player_context_packet_current`: 0
- `compat_pigskin_player_context_current`: 0

Smoke case summary:

| Case | Result |
| --- | --- |
| Tyreek 2025 week 4 MIA plus current Sleeper ID 1166 | `needs_identity_confirmation`, historical MIA and current LV preserved |
| Mahomes 2025 week 15 KC plus current internal ID | `current_roster_unavailable`, historical KC preserved and current team not inferred |
| Josh Johnson current name lookup after deterministic packet | `needs_identity_confirmation`, 3 current roster candidates, merge blocked |
| A.J. Green historical packet plus available source context | Available source/as-of preserved, identity confirmation still required |
| Tyreek week 22 with explicit postseason | Historical packet unavailable, merge blocked before roster lookup |
| Team/position-only current roster request | `validation_error`, `blocked_reason=missing_current_roster_identity`, blocked before packet retrieval or roster lookup |

## No Model-Visible Exposure Confirmation

Confirmed:

- `src/pigskin_context_tools.py` still declares the existing model-visible tools only.
- `src/pigskin_context_qa.py` is not imported by `app.py`.
- `get_historical_pigskin_packet_context` is absent from active declarations while the gate is unset.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` is unset locally, in production, and in staging.
- No prompt text was added instructing Pigskin to call this helper.

## No State Change Confirmation

No write, ingest, materialization, refresh, deployment, Cloud Run Job trigger, Scheduler creation, Sleeper API call, Pigskin prompt, LLM call, scrape, or Firebase action was run.

Only read-only BigQuery queries and Cloud Run service describes were run.

## Validation Results

Read-only validation patterns:

- `raw_nflverse`: 3 passed, 0 failed. Informational warning from `181_raw_nflverse_season_week_coverage.sql`.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed. Informational warning from `178_trade_pick_scores_model_version_coverage.sql`.

## Final Local Checks

Final checks passed after implementation:

- `scripts/check_deployment_safety.py`
- `py_compile` for `src/pigskin_context_qa.py`
- `py_compile` for current roster lookup, merge, packet guardrails, packet retrieval, context tools, LLM context packets, and `app.py`
- `compileall -q src scripts`
- `tests.test_pigskin_context_qa`: 18 tests passed
- `tests.test_pigskin_current_roster_lookup`: 18 tests passed
- `tests.test_pigskin_current_roster_merge`: 16 tests passed
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests passed
- `tests.test_pigskin_packet_retrieval`: 12 tests passed
- Full suite: 563 tests passed
- `scripts/run_bigquery_migrations.py --list-pending`: no pending migrations
- `scripts/run_bigquery_validations.py --dry-run`: discovered through validation 200

## Staging And Production Untouched Confirmation

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: `nfl-studio-dashboard-00077-2jp:100`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset
- Data Ops trigger flags false
- Data Ops local subprocess flags false
- Trade Analyzer score flags false
- Trade History compatibility false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: `nfl-studio-dashboard-staging-00029-jtb:100`
- Image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset
- Data Ops trigger flags false
- Data Ops local subprocess flags false
- Staging score and Trade History flags remain as previously configured

## Remaining Warnings

- Live Tyreek current lookup by `sleeper_player_id=1166` resolves to current LV context but with a stable ID mismatch against the historical packet ID. The helper correctly returns `needs_identity_confirmation`.
- Mahomes current roster lookup by `player_id_internal=00-0033873` returned not found in the approved current roster sources.
- `compat_viewer_team_context` currently has 10 rows, while the prompt snapshot listed 0. The helper does not use that table.
- `raw_nflverse` and `trade_pick_scores` validations include existing informational review warnings.
- The helper is internal only. Owner approval is still required before any model-visible exposure.

## Recommended Next Phase

Phase 30.11 should package and commit lookup merge QA.

Secondary follow-up:

Phase 30.11 or later can address compact/full-name identity bridge improvements for Tyreek and available-player examples before any model-visible exposure decision.
