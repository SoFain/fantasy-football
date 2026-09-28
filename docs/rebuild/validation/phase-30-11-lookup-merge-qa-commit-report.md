# Phase 30.11 Lookup Merge QA Commit Report

## Final Decision

LOOKUP MERGE QA COMMITTED WITH WARNINGS

The Phase 30.10 internal lookup-plus-merge QA package was committed as a narrow source and evidence package. No deployment, BigQuery write, materialization, Sleeper API call, Pigskin prompt, LLM call, Cloud Run Job trigger, Scheduler job, scrape, or Firebase action occurred.

## Commit Hash

- Commit: `52e108f Add lookup merge QA helper`
- Branch observed: `codex/phase-14-validation-footer`

## Files Committed Summary

Committed files:

- `src/pigskin_context_qa.py`
- `tests/test_pigskin_context_qa.py`
- `docs/rebuild/validation/phase-30-10-lookup-merge-qa-design.md`
- `docs/rebuild/validation/phase-30-10-lookup-helper-merge-layer-qa-report.md`

Commit stat:

- 4 files changed
- 1,254 insertions

## Files Excluded Summary

Excluded:

- Historical Phase 17 through Phase 30 backlog reports not listed for this package
- Owner-review artifacts
- Logs
- Caches
- Local output folders
- Temporary JSON
- Browser evidence
- Deployment artifacts
- Secret or environment files

After commit, no files were staged. Remaining untracked file count was 104 before this report was created, consisting of the historical validation backlog and owner-review evidence already known from previous cleanup phases.

## Gate State

All checked gates were unset before packaging:

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

The committed helper adds an internal QA path:

`build_historical_packet_current_roster_context(packet_request, current_roster_request, client=None, dataset_id=None)`

It is internal-only and is not registered in Pigskin context tools.

## Orchestration Contract Summary

The helper:

- Rejects arbitrary SQL keys before helper calls.
- Requires explicit historical season or season window.
- Requires current roster identity before packet retrieval.
- Treats team and position only as narrowing filters.
- Retrieves historical packet evidence through `retrieve_historical_pigskin_packets`.
- Retrieves current roster context through `lookup_current_roster_context`.
- Merges through `merge_historical_packet_with_current_roster` only after deterministic helper results.
- Allows missing current roster results to merge as unavailable.
- Preserves historical and current fields separately.

## Lookup-Plus-Merge Behavior

Covered behavior:

- Deterministic packet plus deterministic current roster can merge.
- Ambiguous packet blocks merge and returns candidates.
- Ambiguous current roster result blocks merge and returns candidates.
- Missing current roster result keeps current team/status unavailable.
- Team/position-only current roster request blocks before packet retrieval.
- Unbounded current roster request blocks before packet retrieval.

## Identity Reconciliation Behavior

The helper preserves unresolved identity state. If current roster context maps to a stable ID that does not match the historical packet, the merge returns `needs_identity_confirmation` rather than silently claiming a resolved player.

## Ambiguity Behavior

Ambiguous packet or current roster lookups return candidates and do not silently choose a player. The commit includes tests for both cases.

## Tyreek Hill Historical And Current Status Handling

Phase 30.10 read-only smoke showed Tyreek historical and current context remains separate:

- Historical packet: 2025 week 4, `historical_team=MIA`
- Current roster lookup by `sleeper_player_id=1166`: `current_team=LV`, `current_roster_status=Active`, source `sleeper_players_current`
- Result: `needs_identity_confirmation`, with `team_mismatch=true`

The helper does not infer current team from the historical packet.

## Free-Agent And Available-Player Handling

The committed tests verify available-player context preserves current roster source data:

- current roster status
- current roster source
- current team when present
- free-agent or available flags

Historical packet context remains prior performance context.

## Current Team Mismatch Handling

When historical team and current team differ, the merge preserves both fields and reports `team_mismatch=true` with provenance and a warning.

## Week 22 And Postseason Handling

Week 22 context is preserved only when upstream packet retrieval is explicitly requested with postseason inclusion. Tests verify the postseason policy and week value pass through the merge result.

## Blocked Metric Handling

Blocked metrics remain unavailable. The helper passes through `blocked_metrics`, `missing_data_flags`, and `source_freshness` without converting unavailable metrics to zero.

## Source Provenance And As-Of Handling

The merge result preserves:

- historical source
- packet version
- feature run ID
- source metric version
- packet season/week
- current roster source
- current roster as-of timestamp
- source freshness
- missing-data flags

## No Model-Visible Exposure Confirmation

Repository search confirmed:

- `src/pigskin_context_qa.py` is not imported by `app.py`.
- The QA helper is not in `get_pigskin_context_tool_declarations`.
- `get_historical_pigskin_packet_context` remains absent from active model-visible tools.
- The historical packet declaration remains guarded and default-disabled.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` is absent or unset in both production and staging.

## Source Inventory Summary

The committed source package does not add:

- Sleeper API path
- Pigskin prompt path
- LLM path
- BigQuery write path
- Cloud Run Job trigger path
- Scheduler creation path
- Firebase artifact path

## Test Results

Final checks before staging and commit passed:

- `scripts/check_deployment_safety.py`
- `py_compile` for `src/pigskin_context_qa.py`
- `py_compile` for current roster lookup, merge, packet retrieval, packet guardrails, context tools, LLM context packets, and `app.py`
- `compileall -q src scripts`
- `tests.test_pigskin_context_qa`: 18 tests passed
- `tests.test_pigskin_current_roster_lookup`: 18 tests passed
- `tests.test_pigskin_current_roster_merge`: 16 tests passed
- `tests.test_pigskin_packet_retrieval`: 12 tests passed
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests passed
- Full suite: 563 tests passed

## Validation Results

Validation dry-run:

- Discovered validation catalog through validation 200.

Read-only validation patterns:

- `raw_nflverse`: 3 passed, 0 failed, with informational coverage warning.
- `stg_`: 7 passed, 0 failed.
- `advanced_metrics`: 4 passed, 0 failed.
- `compat_pigskin`: 2 passed, 0 failed.
- `trade_player_scores`: 12 passed, 0 failed.
- `trade_pick_scores`: 17 passed, 0 failed, with informational model-version coverage warning.

## Warehouse Read-Only State

Read-only counts:

- `pigskin_player_context_packet_current`: 4,084
- `compat_pigskin_player_context_current`: 4,084
- 2025 compat packet rows: 510
- 2026+ compat packet rows: 0
- `raw_nflverse_pbp` 2026+ rows: 0
- `raw_nflverse_weekly` 2026+ rows: 0
- staging nflverse 2026+ rows: 0 across checked staging tables
- advanced metrics 2026+ rows: 0 across checked advanced tables
- `sleeper_players_current`: 4,254
- `sleeper_roster_players`: 636
- `sleeper_available_players`: 3,032
- `sleeper_viewer_team_snapshots`: 3
- `compat_viewer_team_context`: 10
- `player_identity_bridge`: 11,212
- `dim_players_current`: 11,212

No warehouse data was modified.

## Service Untouched Confirmation

Production:

- Service: `nfl-studio-dashboard`
- Revision: `nfl-studio-dashboard-00077-2jp`
- Traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- Image digest: `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset
- Data Ops trigger flags false
- Data Ops local subprocess flags false
- Trade Analyzer score flags false
- Trade History compatibility false

Staging:

- Service: `nfl-studio-dashboard-staging`
- Revision: `nfl-studio-dashboard-staging-00029-jtb`
- Traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- Image digest: `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset
- Data Ops trigger flags false
- Data Ops local subprocess flags false

No staging or production deployment occurred.

## Remaining Warnings

- Tyreek current lookup by `sleeper_player_id=1166` preserves current LV source data but still returns `needs_identity_confirmation` due stable ID mismatch against the historical packet.
- Mahomes current roster lookup by `player_id_internal=00-0033873` returned unavailable in approved current roster sources.
- `compat_viewer_team_context` has 10 rows. The QA helper does not use that table.
- `raw_nflverse` season/week coverage and `trade_pick_scores` model-version coverage validations retain informational warnings.
- Historical validation backlog remains untracked and intentionally excluded from this commit.

## Recommended Next Phase

Recommended:

- Phase 30.12 - Compact/full-name identity bridge improvements

Other valid owner decisions:

- Phase 30.12 - Owner exposure decision for model-visible historical packet tool
- Phase 30.12 - Staging-only exposure test for historical packet tool
- Phase 30.12 - Read-only QA UI for historical packet plus current roster context
