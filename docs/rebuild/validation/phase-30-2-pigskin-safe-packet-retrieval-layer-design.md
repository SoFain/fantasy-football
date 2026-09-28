# Phase 30.2 Pigskin-Safe Packet Retrieval Layer Design

## Purpose

`src/pigskin_packet_retrieval.py` is the first internal retrieval layer for the completed 2014-2025 nflverse Pigskin packet warehouse.

It is read-only. It reads only `compat_pigskin_player_context_current`, returns structured dictionaries, and refuses unbounded historical lookups. It is not wired into the model-visible Pigskin tool list in this phase.

## Input Contract

Required:
- `season`, or both `season_start` and `season_end`

Optional filters:
- `week`
- `include_postseason`
- `player_id_internal`
- `player_name`
- `team`
- `position`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `limit`

The layer is bounded to completed historical packet seasons, currently 2014-2025. It never defaults to a current season.

## Output Contract

Responses are structured result dictionaries:
- `status`: `ok`, `ambiguous`, `not_found`, `validation_error`, or `query_error`
- `found`
- `source`: always `compat_pigskin_player_context_current`
- `source_policy`: `historical_nflverse_packet_context_only`
- `historical_context_only`
- `current_roster_status_source_required`
- `current_roster_status_policy`
- `packet` for one deterministic hit
- `packets` for bounded packet lists
- `candidates` for ambiguous player-name lookups
- `warnings`

Packet rows are normalized with historical naming:
- `historical_team`
- `historical_position`
- `as_of_season`
- `as_of_week`
- `display_name`
- `player_id_internal`

The layer does not expose packet `team` as `current_team`.

## Historical Team And Current Roster Separation

nflverse packet rows are historical performance evidence. They do not answer current roster, free-agent, dynasty availability, or 2026 availability questions.

Every response includes:

`Historical nflverse packet context only.`

and:

`Current roster/free-agent status must come from Sleeper/current roster source.`

The retrieval layer does not call Sleeper. Future merge work must combine this historical evidence with a separate current-roster source.

## Tyreek Hill Example

A 2025 lookup for Tyreek Hill can use:
- `player_id_internal`
- compact display name `T.Hill` with `team=MIA` and `position=WR`

If only `Tyreek Hill` or `T.Hill` is supplied and multiple compact-display candidates are present, the layer returns `status=ambiguous` with candidates. It must not infer 2026 free-agent or current-team status from the 2025 Miami packet.

## Display-Name Ambiguity

The compatibility view carries compact display names such as `T.Hill`. These are not globally unique.

The retrieval layer:
- prefers `player_id_internal`
- accepts `team` and `position` as disambiguators
- returns candidates when compact display names collide
- does not silently select among collisions like `D.Johnson`, `J.Williams`, `K.Williams`, `A.Brown`, or `J.Jefferson`

Full-name support is only a safe candidate aid when it can be converted to a compact variant. It is not a reliable identity bridge by itself.

## Postseason Behavior

Default mode is regular-season fantasy analysis and excludes postseason rows.

Because the packet surface has no game-type field, the cutoff is conservative:
- seasons through 2020: weeks 1-17
- seasons 2021 and later: weeks 1-18

`include_postseason=True` allows all available packet weeks through Week 22. No Week 22 rows are deleted or altered.

## Blocked Metrics

Blocked metrics are preserved from `packet_json.blocked_metrics` and returned as unavailable, not zero.

The response includes:
- `blocked_metrics`
- `blocked_metric_policy`: `blocked metrics are unavailable, not zero`
- packet `warnings`
- parsed `source_freshness`
- parsed `missing_data_flags`

## JSON Parsing

The layer safely parses:
- `packet_json`
- `source_freshness_json`
- `missing_data_flags`

If a field contains nested JSON as a string, it attempts one nested parse. Malformed JSON does not crash retrieval. The response includes a parse warning and leaves the affected field empty or unchanged.

## Source Isolation

Allowed source:
- `compat_pigskin_player_context_current`

Forbidden request-time sources:
- `raw_nflverse_*`
- `stg_*`
- `pigskin_player_context_packet_current`
- arbitrary caller-supplied SQL
- Sleeper API
- LLM/Pigskin prompts

## Future Integration Points

Next phases can wire this into Pigskin only after prompt/tool guardrails are added:
- make historical packet context clearly labeled in tool descriptions
- require season/window arguments
- add current-roster merge rules from Sleeper/current roster sources
- preserve ambiguity candidates in UI or tool responses
- keep the compatibility view as the only packet source
