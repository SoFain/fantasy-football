# Phase 30.4 Pigskin Prompt And Tool Guardrails Design

## Purpose

Phase 30.4 adds guardrails around the historical nflverse Pigskin packet retrieval layer before any model-visible exposure.

The retrieval layer remains safe and internal. The new guardrail layer defines policy text, a default-disabled future tool declaration, and a wrapper that maps future tool arguments into `src.pigskin_packet_retrieval` without exposing BigQuery or current-roster claims.

## What Was Added

New module:

- `src/pigskin_packet_guardrails.py`

New tests:

- `tests/test_pigskin_packet_tool_guardrails.py`

Prompt update:

- `app.py` now imports `PIGSKIN_HISTORICAL_PACKET_PROMPT_GUARDRAIL` and includes it in the Pigskin system prompt.

The prompt text is defensive only. It does not tell Pigskin to call the historical packet retrieval layer.

## What Remains Disabled

The historical packet retrieval wrapper is not registered in `src.pigskin_context_tools.py`.

`get_historical_packet_tool_declarations()` returns an empty list by default. The future declaration is returned only when explicitly enabled by caller or by `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`.

No runtime environment was changed. No feature flag was enabled.

## Safe Wrapper Contract

Function:

`execute_historical_packet_context_lookup(args, client=None, dataset_id=None)`

Rules:

- requires `season`, or both `season_start` and `season_end`
- rejects arbitrary SQL arguments such as `sql_query`
- ignores unsupported non-SQL args with a warning
- calls `pigskin_packet_retrieval.retrieve_historical_pigskin_packets`
- preserves ambiguity candidates
- strips any exact `current_team` field from returned packet data
- adds historical/current separation policy metadata
- returns blocked metrics as unavailable, not zero
- does not call BigQuery directly
- does not call Sleeper
- does not call Pigskin or an LLM

## Future Tool Declaration Contract

Future declaration name:

`get_historical_pigskin_packet_context`

Required guardrails in description:

- bounded historical nflverse packet context
- explicit season or season window required
- returns `historical_team`
- returns source freshness and missing-data flags
- returns ambiguity candidates
- does not answer current roster, free-agent, or current-team status

The declaration is not model-visible in this phase.

## Prompt Guardrail Language

The Pigskin prompt now includes:

- historical nflverse packet context is completed-season evidence only
- it does not answer current roster, free-agent, dynasty availability, injury/status, or current-team questions
- 2026-facing roster/status questions must use Sleeper/current roster source
- packet season/week must be labeled when packet context is provided
- packet team is historical team, never current team
- if historical team and current roster team differ, state both with provenance
- if current roster source says free agent, packet context shows prior historical usage only
- ambiguous player lookup requires player ID, team, or position
- blocked metrics are unavailable, not zero
- Week 22 is postseason/historical and excluded from regular-season analysis unless requested

The text does not instruct Pigskin to call a historical packet tool before that tool is enabled.

## Historical Packet And Current Roster Separation

nflverse packets are historical performance/context evidence. They can support completed-season usage, role, efficiency, and source-freshness analysis.

They cannot answer:

- current team
- free-agent status
- dynasty availability
- injury/status
- current roster state
- 2026 player availability

Current status must come from Sleeper/current roster sources.

## Tyreek Hill Example

Tyreek Hill’s 2025 packet context can resolve to Miami historical evidence when the lookup is disambiguated by player ID or `T.Hill` plus `team=MIA` and `position=WR`.

That packet does not prove any 2026 roster or free-agent status.

If the lookup is `Tyreek Hill` or `T.Hill` without disambiguators, compact display-name collisions return candidates instead of a selected player.

## Display-Name Ambiguity

The guardrail wrapper preserves ambiguity results from the retrieval layer.

Examples that must not silently select:

- `T.Hill`
- `D.Johnson`
- `J.Williams`
- `K.Williams`
- `A.Brown`
- `J.Jefferson`

Future UI or tool exposure should show the candidate list and require player ID, team, or position.

## Week 22 And Postseason Handling

Default regular-season mode excludes postseason rows by the retrieval layer cutoff:

- seasons through 2020: weeks 1-17
- seasons 2021 and later: weeks 1-18

Week 22 can be included only with explicit `include_postseason=True`.

## Blocked Metric Presentation

Blocked metrics are unavailable, not zero.

The wrapper and prompt guardrails preserve this distinction so route-share or pressure metrics absent from the source version cannot be treated as numeric zeros.

## Source Isolation

Allowed packet source:

- `compat_pigskin_player_context_current`

Forbidden:

- `raw_nflverse_*`
- `stg_*`
- `pigskin_player_context_packet_current`
- arbitrary SQL
- Sleeper API calls
- LLM/Pigskin prompt calls from the wrapper

## Future Exposure Requirements

Before model-visible use:

- owner must approve exposure
- the future declaration must be explicitly wired into `src.pigskin_context_tools.py`
- staging QA must prove the tool is visible only when intended
- prompt text must not encourage historical packet use for current roster state
- Sleeper/current roster merge rules should exist for 2026-facing questions
- production flags must remain false until an approved deploy phase
