# Phase 30.6 Sleeper Current Roster Merge Rules Report

## Final Decision

SLEEPER CURRENT ROSTER MERGE RULES READY WITH WARNINGS

Phase 30.6 added an internal pure merge layer for combining historical nflverse Pigskin packet evidence with caller-supplied Sleeper/current roster payloads. It does not run a lookup, write BigQuery rows, call Sleeper, call Pigskin, call an LLM, or expose a new model-visible tool.

The remaining warning is real: a bounded current roster lookup helper still needs a separate phase before model-visible use.

## Gate State

All requested gates were empty or unset:

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

No authorization or exposure gate was set.

## Git State

- latest commit: `859ad96 Add Pigskin historical packet guardrails`
- staged files at start: none
- staged files at end: none
- unrelated historical validation backlog remains untracked
- new Phase 30.6 files:
  - `src/pigskin_current_roster_merge.py`
  - `tests/test_pigskin_current_roster_merge.py`
  - `docs/rebuild/validation/phase-30-6-sleeper-current-roster-merge-rules-design.md`
  - `docs/rebuild/validation/phase-30-6-sleeper-current-roster-merge-rules-report.md`

No commit was created.

## Baseline Checks

Baseline checks passed before implementation:

- `scripts/check_deployment_safety.py`: pass
- requested `py_compile` commands: pass
- `compileall -q src scripts`: pass
- `tests.test_pigskin_packet_tool_guardrails`: pass
- `tests.test_pigskin_packet_retrieval`: pass
- `unittest discover tests`: pass
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: validation catalog discovered through validation 200

## Current Roster Source Audit

Repo search found existing current roster/Sleeper surfaces:

- `sleeper_players_current`
- `sleeper_roster_players`
- `sleeper_available_players`
- `sleeper_viewer_team_snapshots`
- `compat_viewer_team_context`
- `player_identity_bridge`
- `dim_players_current`
- viewer-team helper module: `src/viewer_team_context.py`
- viewer-team materializer: `src/materialize_viewer_team_context.py`

Important finding: no safe standalone current-player status lookup helper exists for this specific merge use yet. The new merge layer therefore accepts current roster payloads as inputs and does not invent a table query or live API call.

## Files Changed

Added:

- `src/pigskin_current_roster_merge.py`
- `tests/test_pigskin_current_roster_merge.py`
- `docs/rebuild/validation/phase-30-6-sleeper-current-roster-merge-rules-design.md`
- `docs/rebuild/validation/phase-30-6-sleeper-current-roster-merge-rules-report.md`

No existing runtime UI or Pigskin tool registration was changed.

## Merge Contract Summary

New internal function:

`merge_historical_packet_with_current_roster(historical_result, current_roster_payload=None)`

Behavior:

- accepts a historical packet retrieval or guardrail result
- accepts a current roster payload supplied by caller
- rejects SQL/query-style input keys
- never queries BigQuery
- never calls Sleeper or external roster APIs
- never calls Pigskin or an LLM
- never writes data
- preserves packet context as historical-only evidence
- returns current status only from the current roster payload

Output includes:

- `historical_context`
- `current_roster_context`
- `provenance`
- `warnings`
- `status`
- `needs_identity_confirmation`
- `historical_team`
- `current_team`
- `current_roster_status`
- `current_roster_source`
- `current_roster_as_of`
- `packet_as_of_season`
- `packet_as_of_week`
- `current_status_policy`

## Identity Mapping And Ambiguity Behavior

Stable ID comparison uses:

- `player_id_internal`
- `gsis_id`
- `sleeper_player_id`

If shared stable IDs disagree, the response is `needs_identity_confirmation`.

If the packet lookup is ambiguous, the merge does not select a player. It returns historical candidates and requires confirmation.

If the current roster payload has multiple candidates, the merge returns current roster candidates and requires confirmation.

If no stable ID can be compared, the merge can return payload context but adds a warning that identity lacks a stable ID match.

## Tyreek Hill Historical And Current-Status Handling

Tests prove the required split:

- 2025 packet context can return `historical_team=MIA`
- current free-agent status comes only from current roster payload
- if current payload says `free_agent`, merged output returns `current_roster_status=free_agent`
- if current payload is missing, merged output does not infer current team or free-agent status from Miami packet context

## Free-Agent Handling

The merge layer treats `free_agent=true`, `roster_status=free_agent`, or availability text containing free-agent/available language as current roster state from the current roster payload.

When current source says free agent, the output warns that the historical packet shows prior usage only.

## Historical And Current Team Mismatch Handling

The output preserves both:

- `historical_team` from packet context
- `current_team` from current roster payload

If they differ, `team_mismatch=true` and the warning says both values must be preserved with provenance.

Packet `current_team` fields are stripped before output. Packet team is never promoted to current team.

## Source Provenance Handling

Merged output includes provenance for:

- historical source: `compat_pigskin_player_context_current`
- historical source policy: `historical_nflverse_packet_context_only`
- packet version
- feature run ID
- source metric version
- packet as-of season/week
- packet creation timestamp
- current roster source
- current roster snapshot ID
- current roster as-of timestamp
- merge policy

Packet `created_at` is not treated as current roster freshness.

## Packet Guardrail Preservation

The merge layer preserves:

- packet warnings
- blocked metrics
- `Blocked metrics are unavailable, not zero.`
- source freshness
- missing-data flags
- upstream Week 22/postseason context
- ambiguity candidates

The merge layer does not expand the packet window or include postseason rows itself.

## Tests Added

Added `tests/test_pigskin_current_roster_merge.py` with 16 tests:

- historical team and current team are separate fields
- current team comes only from current roster payload
- packet `current_team` is stripped and not promoted
- free-agent current status is preserved from current source
- missing current roster payload does not infer current team from packet
- Tyreek Hill Miami 2025 packet plus current free-agent payload returns both with provenance
- identity mismatch returns `needs_identity_confirmation`
- ambiguous packet result is not merged as a selected player
- current roster multiple candidates returns candidates and needs confirmation
- blocked metrics remain unavailable
- packet warnings and source freshness are preserved
- Week 22/postseason context is preserved
- missing current roster payload keeps current status unavailable
- arbitrary SQL is rejected
- weak identity adds a warning
- no Sleeper API, LLM, Pigskin, BigQuery query, or write path exists

## Optional Read-Only Source Inventory QA

Read-only inventory results:

| Table/View | Row Count | Relevant Fields |
| --- | ---: | --- |
| `sleeper_players_current` | 4,254 | `snapshot_at`, `sleeper_player_id`, `gsis_id`, `player_name`, `team`, `status` |
| `sleeper_roster_players` | 636 | `snapshot_at`, `sleeper_player_id`, `player_name`, `team`, `gsis_id`, `status` |
| `sleeper_available_players` | 3,032 | `snapshot_at`, `sleeper_player_id`, `player_name`, `team`, `gsis_id`, `status` |
| `sleeper_viewer_team_snapshots` | 3 | `snapshot_at` |
| `compat_viewer_team_context` | 10 | `snapshot_timestamp`, `created_at`, `updated_at` |
| `player_identity_bridge` | 11,212 | `player_id_internal`, `gsis_id`, `sleeper_player_id`, `full_name`, `display_name`, `current_team`, `active_status`, `created_at`, `updated_at` |
| `dim_players_current` | 11,212 | `player_id_internal`, `display_name`, `full_name`, `current_team`, `active_status`, `sleeper_player_id`, `gsis_id`, `updated_at` |

This confirms there are usable future lookup sources, but Phase 30.6 intentionally did not add a live lookup or query helper.

## No-State-Change Confirmation

No BigQuery rows were written.

Not run:

- raw backfill
- prepare-only
- nflreadpy loaders
- staging materialization
- advanced metrics materialization
- Pigskin packet refresh
- Sleeper ingestion
- Sleeper API
- Pigskin prompts
- LLM calls
- rankings
- Cloud Run Jobs
- Scheduler jobs
- deployment

Warehouse read-only confirmation:

| Check | Result |
| --- | ---: |
| `pigskin_player_context_packet_current` | 4,084 rows |
| `compat_pigskin_player_context_current` | 4,084 rows |
| 2025 compat packet rows | 510 |
| 2026+ packet rows | 0 |

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

## Final Local Checks

Final checks passed:

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

The full-suite log includes existing unit-test fixture messages that simulate load/job paths. They did not run live ingestion or materialization.

## Staging And Production Untouched

Production:

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

Staging:

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

- A bounded current roster lookup helper is still missing. Phase 30.6 added pure merge rules only.
- Full-name and compact-name identity still need a stronger bridge before model-visible exposure.
- The future historical packet tool remains disabled and non-model-visible.
- Expected informational validation warnings remain for raw nflverse coverage and trade-pick score model-version coverage.
- Historical validation backlog remains untracked for owner review.

## Recommended Next Phase

Phase 30.7: Package and commit Sleeper/current roster merge rules.

Alternate Phase 30.7 options:

- Build current roster lookup helper.
- Owner exposure decision for model-visible historical packet tool.
- Staging-only exposure test for historical packet tool.
