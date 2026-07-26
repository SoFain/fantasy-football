# Phase 30.6 Sleeper Current Roster Merge Rules Design

## Purpose

Phase 30.6 defines the first internal merge policy for combining completed-season nflverse Pigskin packet evidence with current roster status from Sleeper/current roster sources.

The merge layer is internal and pure. It does not query BigQuery, call Sleeper, call Pigskin, call an LLM, or write data. It accepts an already-retrieved historical packet result plus an already-supplied current roster payload.

## Allowed Current Roster Sources

Allowed current roster sources are curated warehouse or caller-supplied payloads derived from:

- `sleeper_players_current`
- `sleeper_roster_players`
- `sleeper_available_players`
- `compat_viewer_team_context`
- `player_identity_bridge`
- `dim_players_current`

These are source candidates for a future lookup helper. Phase 30.6 does not implement that lookup helper.

## Forbidden Sources And Calls

Forbidden in this phase:

- live Sleeper API calls
- external roster APIs
- arbitrary SQL input
- raw nflverse table access from the merge layer
- Pigskin prompt calls
- LLM calls
- BigQuery writes
- BigQuery reads from the merge module
- ingestion, staging materialization, advanced metric materialization, packet refresh, ranking generation, or deployment

## Input Contract

Historical input:

- a safe retrieval result from `src.pigskin_packet_retrieval` or guarded result from `src.pigskin_packet_guardrails`
- selected packet under `packet`, or a single-entry `packets` list
- ambiguity represented as `status=ambiguous` plus `candidates`

Current roster input:

- a caller-supplied payload from a curated current roster source
- stable IDs where available: `player_id_internal`, `gsis_id`, `sleeper_player_id`
- current status fields where available: `current_team`, `roster_status`, `fantasy_availability`, `free_agent`
- source metadata: `current_roster_source`, `snapshot_id`, `current_roster_as_of`

## Output Contract

`src.pigskin_current_roster_merge.merge_historical_packet_with_current_roster` returns:

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

Current-team terminology is used only for current roster source data. Packet team stays `historical_team`.

## Identity Mapping Strategy

The merge layer compares stable IDs when both sources provide them:

- `player_id_internal`
- `gsis_id`
- `sleeper_player_id`

If any shared stable ID conflicts, the merge returns `needs_identity_confirmation`.

If no stable ID can be compared, the merge may return an `ok` payload but includes a warning that identity lacks a stable ID match. It does not pretend compact-name matching is reliable.

## Precedence Rules

Sleeper/current roster source is authoritative for:

- current team
- free-agent status
- current roster state
- current fantasy availability
- 2026-facing status

nflverse packets are authoritative only for historical completed-season usage, role, efficiency, packet warnings, source freshness, and missing-data flags.

If historical and current sources disagree, the output preserves both and labels provenance.

## Historical Packet And Current Roster Separation

The merge layer strips exact `current_team` fields from historical packet data before returning it. It never promotes packet `historical_team` to `current_team`.

If current roster data is missing, current team/status remains unavailable. Historical team is still shown as completed-season context.

## Tyreek Hill Example

A 2025 `T.Hill` packet can resolve to Miami historical evidence:

- `historical_team=MIA`
- `packet_as_of_season=2025`

Current status must come only from current roster payload:

- if current payload says free agent, merged output says current status is free agent and the Miami packet is prior usage context
- if current payload is missing, merged output says current status unavailable and does not infer it from Miami

## Free-Agent Handling

If current roster payload says `free_agent=true`, `roster_status=free_agent`, or availability contains free-agent/available language, the merge returns that as current roster state and adds a warning that the packet only shows prior usage.

## Current Team Mismatch Handling

If `historical_team` differs from current payload `current_team`, the merge returns:

- `historical_team`
- `current_team`
- `team_mismatch=true`
- provenance for both
- warning to preserve both values

## Ambiguity Handling

Ambiguous historical packet results are not merged into a selected player. The response returns `needs_identity_confirmation` and preserves historical candidates.

Current roster payloads with multiple candidates also return `needs_identity_confirmation`.

## Missing Current Roster Source Behavior

If no current roster payload is available, merge status is `current_roster_unavailable`. Current team and current status are null. The response explicitly warns that current status was not inferred from packet team.

## Week 22 And Postseason Behavior

The merge layer preserves upstream packet `as_of_week` and `postseason_policy`. It does not expand the packet window. Week 22 remains postseason/historical and requires explicit upstream inclusion.

## Blocked Metric Behavior

Blocked metrics remain unavailable, not zero. The merge output preserves:

- `blocked_metrics`
- `blocked_metric_policy`
- packet warnings
- source freshness
- missing-data flags

## Future Model-Visible Exposure Requirements

Before model-visible exposure:

- implement a bounded current roster lookup helper if owner approves
- require stable identity reconciliation where possible
- keep historical packet tool default-disabled until an explicit exposure phase
- run staging-only QA proving historical team and current team are labeled separately
- keep production flags false until an approved deploy phase
