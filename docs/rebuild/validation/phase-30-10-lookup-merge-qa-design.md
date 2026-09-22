# Phase 30.10 Lookup Merge QA Design

## Purpose

This phase adds an internal QA path that retrieves one historical Pigskin packet, retrieves bounded current roster context, and merges them into one structured object for review. The helper is not registered as a Pigskin tool and is not exposed in Streamlit.

The design keeps the two evidence lanes separate:

- Historical nflverse packets are completed-season performance context.
- Current team, roster status, free-agent status, and availability come only from approved current roster sources.

## Allowed Inputs

`build_historical_packet_current_roster_context(packet_request, current_roster_request, client=None, dataset_id=None)` accepts two dictionaries.

`packet_request` must include an explicit historical window:

- `season`, or
- `season_start` and `season_end`

It may include bounded packet fields already supported by `retrieve_historical_pigskin_packets`, such as `week`, `include_postseason`, `player_id_internal`, `player_name`, `team`, `position`, `scoring_profile_id`, `league_type_id`, `roster_format_id`, and `limit`.

`current_roster_request` may include bounded identity and narrowing fields already supported by `lookup_current_roster_context`, such as `player_id_internal`, `sleeper_player_id`, `gsis_id`, `player_name`, `team`, `position`, `league_id`, `include_available_players`, and `limit`.

Stable IDs should be preferred whenever they are available.

At least one current roster identity field is required before packet retrieval:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`
- `player_name`

## Forbidden Inputs

The QA helper rejects arbitrary SQL keys before either BigQuery helper is called:

- `sql`
- `query`
- `sql_query`
- `raw_sql`

The helper does not accept table names, raw SQL fragments, unbounded warehouse scans, model prompts, Sleeper API requests, or write controls.

## Output Contract

The helper returns a dictionary with these stable top-level fields:

- `status`
- `found`
- `source`
- `source_policy`
- `qa_policy`
- `warnings`
- `merge_blocked`
- `blocked_reason`
- `packet_request`
- `current_roster_request`
- `packet_result`
- `current_roster_result`
- `merged_context`
- `historical_team`
- `current_team`
- `current_roster_status`
- `current_roster_source`
- `current_roster_as_of`
- `team_mismatch`
- `packet_as_of_season`
- `packet_as_of_week`
- `source_freshness`
- `missing_data_flags`
- `blocked_metrics`
- `provenance`

When ambiguity or validation blocks the merge, `merge_blocked` is true and `merged_context` is null. Candidate lists are returned in `historical_candidates` or `current_roster_candidates` when available.

## Packet Retrieval Contract

Historical packets come only from `retrieve_historical_pigskin_packets`, which reads `compat_pigskin_player_context_current` with parameterized BigQuery SQL and bounded limits.

The packet result must be deterministic before merge:

- `status=ok`
- exactly one selected `packet`

If packet lookup is ambiguous, not found, or returns multiple packet rows without a selected packet, the QA helper stops before current roster merge.

## Current Roster Lookup Contract

Current roster context comes only from `lookup_current_roster_context`, which reads approved current roster and identity sources:

- `player_identity_bridge`
- `dim_players_current`
- `sleeper_players_current`
- `sleeper_roster_players`
- `sleeper_available_players`

The current roster result must be deterministic before merge, except `not_found` is allowed. A missing current roster result is merged as unavailable, and the merge layer must not infer current team or roster status from the historical packet.

Unbounded current roster requests block before historical packet retrieval. Team and position may narrow the lookup, but they are not identity fields by themselves.

## Merge Contract

The helper calls `merge_historical_packet_with_current_roster` only after packet lookup is deterministic and current roster lookup is deterministic or not found.

The merge layer strips any packet `current_team`, preserves `historical_team`, and fills `current_team` only from current roster context. It also preserves:

- provenance
- source freshness
- missing-data flags
- packet warnings
- blocked metrics
- current roster source/as-of metadata

## Source Precedence

For current status fields, current roster sources always win. Historical packet team is never a fallback for current team.

Source priority is:

1. Current roster lookup for current team/status/free-agent/available state.
2. Historical packet for completed-season team, week, and performance context.
3. Missing/unavailable status when current roster source cannot resolve the player.

## Identity Reconciliation

Stable ID mismatch returns `needs_identity_confirmation`. The helper preserves both contexts and warnings, but it does not claim that identity is safely reconciled.

Name-only lookups that return multiple current roster or historical candidates block before merge. They return candidates for human review.

## Tyreek Hill Example

The expected behavior for a Tyreek Hill historical Miami packet is:

- `historical_team=MIA` from the 2025 historical packet.
- `current_team` only from current roster lookup source data.
- If the current roster source maps the lookup to a different stable ID, return `needs_identity_confirmation`.
- Never promote `MIA` from the packet as current team.

## Free-Agent And Available-Player Handling

If `sleeper_available_players` supplies the current context, the merge preserves:

- `current_roster_status`
- `fantasy_availability`
- `free_agent`
- `current_roster_source=sleeper_available_players`
- `current_roster_as_of`

Historical packet data remains prior usage context.

## Current Team Mismatch

If `historical_team` and `current_team` differ, the merged result sets `team_mismatch=true` and adds a warning. This is not an error by itself. It is expected for trades, free agency, and offseason status changes.

## Week 22 And Postseason Context

Week 22 is explicit postseason or historical context. It is only retrieved when the packet request explicitly includes `include_postseason=True` and a postseason week. The helper preserves `packet_as_of_week=22` and the merge layer postseason policy.

## Blocked Metrics

Blocked metrics remain unavailable. They are passed through as `blocked_metrics` and `missing_data_flags`; the helper never converts missing or blocked metrics to zero.

## Source Provenance And As-Of Handling

Historical packet provenance includes packet version, feature run, metric version, packet season/week, and packet creation time.

Current roster provenance includes the current roster source, snapshot ID when available, and `current_roster_as_of`.

The helper exposes both in `provenance` and does not overwrite one lane with the other.

## Future Model-Visible Exposure Requirements

This phase does not expose the helper to Pigskin. Future exposure requires owner approval and a separate staging-only validation phase.

Before any model-visible exposure, the project must verify:

- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` remains default-off.
- Prompt text does not instruct Pigskin to call unavailable tools.
- The tool declaration is bounded and does not accept raw SQL.
- Ambiguity and missing-current-status behavior remains visible to the model and user.
