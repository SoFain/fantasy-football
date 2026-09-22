# Phase 30.12 Compact/Full-Name Identity Bridge Design

## Purpose

Phase 30.12 adds an internal, read-only identity bridge for Pigskin QA. The bridge improves compact-name and full-name candidate handling before any model-visible historical packet exposure decision.

It does not expose a Pigskin tool. It does not write BigQuery rows. It does not call Sleeper, Pigskin, or any LLM.

## Allowed Read-Only Sources

The bridge may read only approved identity and current roster sources:

- `player_identity_bridge`
- `dim_players_current`
- `sleeper_players_current`
- `sleeper_roster_players`, only when league scope is supplied
- `sleeper_available_players`, only when league scope is supplied and available-player context is requested

`compat_pigskin_player_context_current` remains historical evidence only. Its compact display names can be inspected by QA, but they are not identity authority.

## Forbidden Sources And Calls

The bridge must not use:

- `compat_viewer_team_context` as a global current player status source
- raw nflverse tables
- `weekly_metrics`
- historical packet team as current team
- arbitrary SQL supplied by a caller
- Sleeper API or any external roster API
- Pigskin prompt execution
- LLM calls
- BigQuery write APIs

## Input Contract

At least one stable ID or player-name input is required:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`
- `player_name`
- `full_name`
- `display_name`
- `compact_name`

Optional narrowing fields:

- `team`
- `position`
- `league_id`
- `include_available_players`
- `season`
- `week`
- `limit`

Team and position narrow candidates. They are not identity fields by themselves.

Name or compact-name lookup without a stable ID requires an explicit `limit`. The bridge clamps limits to a safe maximum of 25.

## Output Contract

The bridge returns:

- `status`
- `found`
- `needs_identity_confirmation`
- `candidates`
- `selected_identity`
- `identity_sources`
- `stable_ids`
- `full_name`
- `display_name`
- `compact_display_names`
- `current_team`
- `active_status`
- `warnings`
- `provenance`
- `mismatch_diagnostics`

Ambiguous results return candidates and do not select a player. Stable-ID conflicts return `needs_identity_confirmation`.

## Source Precedence

1. Stable IDs in `player_identity_bridge`.
2. Stable IDs in `dim_players_current`.
3. Current roster identity from `sleeper_players_current`.
4. League-scoped roster or availability identity only when league scope is supplied.
5. Historical packet compact display names only as historical evidence.

## Compact-Name Expansion

`build_compact_display_variants` creates compact candidates such as:

- `Tyreek Hill` to `t.hill` and `thill`
- `A.J. Brown` to `a.brown`, `abrown`, `aj.brown`, and `ajbrown`

Compact matches are collision-prone. `T.Hill`, `A.Brown`, `D.Johnson`, and `J.Williams` can refer to multiple players. The bridge must return candidates instead of picking one.

## Full-Name Matching

Full-name matching uses normalized name variants and may also produce compact variants for historical packet compatibility. If expansion creates multiple candidate identities, the bridge returns `ambiguous`.

## Stable-ID Reconciliation

Stable IDs are preferred. If sources agree on stable IDs, the bridge can return one selected identity. If approved sources conflict on any stable ID field inside one candidate group, the result is `needs_identity_confirmation`.

`reconcile_packet_and_current_identity` compares packet and current payload IDs without changing merge behavior. It reports:

- `identity_match`
- `needs_identity_confirmation`
- `weak_identity_match`
- `current_roster_source_gap`
- `historical_packet_unavailable`

## Identity Mismatch Behavior

`explain_identity_mismatch` returns field-level diagnostics:

- stable ID field
- historical value
- current value
- resolution: `needs_identity_confirmation`

The helper does not choose between historical and current IDs. Owner review or a stronger identity source is required.

## Tyreek Hill Example

Historical 2025 packet context may show `T.Hill` with `historical_team=MIA`. Current roster status must come from approved current sources. If the historical packet stable ID and current source stable ID do not reconcile, the bridge returns `needs_identity_confirmation` and preserves both teams as separate facts.

Historical team remains completed-season context only. It is never used as current team.

## Mahomes Unavailable Current Source Example

If `player_id_internal=00-0033873` does not resolve in approved current roster sources, the bridge reports `current_roster_source_gap`. It does not infer current team/status from a historical packet.

## Integration

Phase 30.12 keeps the bridge internal and standalone, then adds diagnostics to `pigskin_context_qa.py` after packet/current lookup results are deterministic enough to merge. The current roster lookup helper remains the authoritative source of current roster payloads.

Next-phase integration can route name-based QA lookups through the bridge before current roster lookup, but only if tests prove it reduces ambiguity without weakening source policy.

## Future Model-Visible Exposure Requirements

Before any historical packet tool becomes model-visible:

- owner approval must explicitly enable the exposure phase
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` must remain default-off
- compact-name collisions must return candidates
- stable-ID mismatches must block with `needs_identity_confirmation`
- current roster status must come only from approved current sources
- no raw/source tables can be visible to Pigskin
