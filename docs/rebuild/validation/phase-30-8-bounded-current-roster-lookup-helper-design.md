# Phase 30.8 Bounded Current Roster Lookup Helper Design

## Purpose

Phase 30.8 adds the first internal lookup helper that can supply current roster payloads to `merge_historical_packet_with_current_roster`.

The helper is intentionally narrow. It retrieves current roster context from already-materialized warehouse sources and returns a structured payload compatible with the Phase 30.6 merge layer. It does not call Sleeper, Pigskin, an LLM, or any external roster API.

## Allowed Read-Only Sources

Allowed sources:

- `player_identity_bridge`
- `dim_players_current`
- `sleeper_players_current`
- `sleeper_roster_players`, only when a `league_id` scope is supplied
- `sleeper_available_players`, only when `league_id` and `include_available_players=true` are supplied

`compat_viewer_team_context` is viewer-team packet context. It is not used as a global current player source.

## Forbidden Sources And Calls

Forbidden:

- arbitrary SQL
- `weekly_metrics`
- raw nflverse tables
- historical Pigskin packet tables as current roster sources
- live Sleeper API calls
- Sleeper ingestion or materialization
- Pigskin prompt calls
- LLM calls
- BigQuery writes
- Cloud Run Jobs
- Scheduler jobs
- model-visible tool registration

## Input Contract

The helper requires at least one bounded identity input:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`
- `player_name`

Optional narrowing inputs:

- `team`
- `position`
- `league_id`
- `include_available_players`
- `limit`

Name-only lookup requires an explicit `limit`. The helper clamps limits to `MAX_LIMIT=25`.

The helper rejects unknown arguments and SQL/query-style keys such as `sql`, `query`, `sql_query`, and `raw_sql`.

## Output Contract

Primary response fields:

- `status`
- `found`
- `source`
- `source_policy`
- `current_roster_context`
- `candidates`
- `candidate_count`
- `needs_identity_confirmation`
- `warnings`
- `request`

`current_roster_context` fields:

- `player_id_internal`
- `gsis_id`
- `sleeper_player_id`
- `full_name`
- `display_name`
- `position`
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
- `warnings`

The payload can be passed directly to `merge_historical_packet_with_current_roster`.

## Identity Strategy

Stable IDs are preferred:

1. `player_id_internal`
2. `sleeper_player_id`
3. `gsis_id`

Name lookup is exact normalized-name matching. It can return candidates and should not be used as final identity confirmation when multiple active records match.

The helper groups rows by stable identity. Rows for the same player from identity and current roster tables are collapsed into one candidate. Multiple identity groups return `status=ambiguous` with candidates.

## Source Precedence

Identity sources are used first for stable mapping:

1. `player_identity_bridge`
2. `dim_players_current`

Current state sources:

1. `sleeper_players_current` for global current player state
2. `sleeper_roster_players` for league-scoped rostered state
3. `sleeper_available_players` for league-scoped available/free-agent state

If league availability data is present, it is preserved separately in `availability_context`. If `sleeper_available_players` supplies the scoped current state, the helper returns available/free-agent status from that current roster source.

## Current Team And Status Rules

Current team, roster status, free-agent status, and availability are sourced only from the approved current roster and identity sources above.

Historical packet team is not an input to the lookup helper. The helper never reads `compat_pigskin_player_context_current` and never uses historical packet `team` as `current_team`.

If approved sources do not include a current team, the helper returns `current_team=None` and a warning. It does not infer from a packet team.

## Snapshot And As-Of Handling

The helper uses latest available snapshots:

- `sleeper_players_current`: latest `snapshot_at`
- `sleeper_roster_players`: latest `snapshot_at` for the supplied `league_id`
- `sleeper_available_players`: latest `snapshot_at` for the supplied `league_id`

Returned payloads include `current_roster_as_of`, source freshness JSON, and provenance entries for each source row used in the candidate.

## Ambiguity Handling

Ambiguity cases return `status=ambiguous`, `found=false`, `needs_identity_confirmation=true`, and a candidate list.

Ambiguity can occur when:

- a name matches multiple stable identities
- a compact or duplicate display name maps to multiple current candidates
- source data cannot be reconciled to one identity group

The helper does not silently select a player in those cases.

## Tyreek Hill Example

A Tyreek Hill historical packet can show `historical_team=MIA` for 2025.

The current lookup helper does not read that packet. It looks up Tyreek in current roster sources only. If `sleeper_players_current` says `current_team=LV`, the helper returns `LV`. If a current source says free agent or available, it returns that current status with source and as-of metadata.

If a name lookup is ambiguous, the helper returns candidates and requires stable ID, team, or position narrowing.

## Integration With Merge Layer

`merge_historical_packet_with_current_lookup` is an internal convenience function:

1. run bounded current roster lookup
2. pass `current_roster_context` to `merge_historical_packet_with_current_roster`
3. attach lookup evidence to the merged response

This function is not wired into Pigskin tools, Streamlit UI, or any model-visible surface in Phase 30.8.

## Failure Modes

- `validation_error`: unbounded request, missing name limit, unknown arguments, or SQL/query-style keys
- `not_found`: approved current roster sources returned no match
- `ambiguous`: multiple candidate identities matched
- `query_error`: BigQuery read failed
- `ok`: exactly one candidate identity resolved

## Future Exposure Requirements

Before model-visible exposure:

- keep `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` default off
- add a staging-only exposure phase
- verify Pigskin cannot see arbitrary SQL
- verify historical packet team remains separate from current team
- verify current roster status comes only from current roster sources
- add browser QA evidence for ambiguity, free-agent status, and Tyreek-style historical/current separation
