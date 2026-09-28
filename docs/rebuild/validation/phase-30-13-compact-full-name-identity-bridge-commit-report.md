# Phase 30.13 Compact/Full-Name Identity Bridge Commit Report

## Final Decision

IDENTITY BRIDGE COMMITTED WITH WARNINGS

The approved Phase 30.12 identity bridge package was committed. No deployment occurred. No BigQuery rows were written. No materialization, Sleeper API call, Pigskin/LLM prompt, Cloud Run Job trigger, Scheduler job, scrape, or Firebase artifact was created.

## Commit

- Commit: `a55dd13 Add Pigskin identity bridge diagnostics`
- Branch observed: `codex/phase-14-validation-footer`
- Previous checkpoint: `52e108f Add lookup merge QA helper`

## Files Committed

Committed exactly the approved Phase 30.12 package:

- `src/pigskin_identity_bridge.py`
- `tests/test_pigskin_identity_bridge.py`
- `src/pigskin_context_qa.py`
- `tests/test_pigskin_context_qa.py`
- `docs/rebuild/validation/phase-30-12-compact-full-name-identity-bridge-design.md`
- `docs/rebuild/validation/phase-30-12-compact-full-name-identity-bridge-report.md`

## Files Excluded

Excluded:

- historical Phase 17 through Phase 30 backlog reports
- owner-review validation artifacts
- deployment artifacts
- logs
- caches
- local output folders
- temporary JSON
- browser evidence
- secrets and environment files

Post-commit status still shows the historical validation backlog as untracked. That backlog was intentionally left out of this commit.

## Gate State

All checked gates were unset:

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

## Implementation Summary

The commit adds an internal identity-resolution bridge for Pigskin QA. It improves stable-ID, full-name, and compact-name diagnostics before any model-visible historical packet exposure decision.

`pigskin_context_qa.py` now attaches `identity_diagnostics` to lookup-plus-merge QA results. The current roster lookup helper remains the current roster source. The bridge does not alter current roster source precedence.

## Identity Bridge Contract

The bridge requires at least one stable ID or name input:

- `player_id_internal`
- `sleeper_player_id`
- `gsis_id`
- `player_name`
- `full_name`
- `display_name`
- `compact_name`

Name and compact-name lookups require an explicit `limit`; the bridge clamps the limit to 25. Team and position are accepted only as narrowing filters.

## Source Precedence

1. `player_identity_bridge`
2. `dim_players_current`
3. `sleeper_players_current`
4. `sleeper_roster_players`, only with league scope
5. `sleeper_available_players`, only with league scope and availability request
6. Historical packet compact names remain historical evidence only

The bridge does not use `compat_viewer_team_context` as global player status. It does not use raw nflverse, staging tables, `weekly_metrics`, or the historical packet compatibility view as identity authority.

## Compact-Name Expansion

Compact variants include forms like:

- `Tyreek Hill` to `t.hill` and `thill`
- `A.J. Brown` to `a.brown`, `abrown`, `aj.brown`, and `ajbrown`

Compact collisions return candidates. The bridge does not silently select one player.

## Full-Name Matching

Full-name matching is normalized and conservative. It may return ambiguity when compact expansion collides. That behavior is intentional until stronger identity remediation is done.

## Stable-ID Reconciliation

Stable IDs are preferred. Source conflicts or packet/current mismatches return diagnostics and `needs_identity_confirmation`.

Mismatch diagnostics include:

- stable ID field
- historical value
- current value
- resolution

## Tyreek Hill Diagnostics

Phase 30.12 read-only smoke documented:

- `player_name=Tyreek Hill`, limit 10: ambiguous, 4 candidates
- `compact_name=T.Hill`, limit 10: ambiguous, 4 candidates
- `player_id_internal=00-0033040`: not found in approved identity/current sources by exact ID
- `sleeper_player_id=1166`: selected Kirk Cousins in approved current-source data, current team `LV`

The packet/current reconciliation returned `needs_identity_confirmation` for the Tyreek historical packet case. Historical `MIA` and current-source `LV` remained separate.

## Mahomes Current-Source Gap

Phase 30.12 read-only smoke documented:

- `player_name=Patrick Mahomes`, limit 10: ok, current team `KC`
- `player_id_internal=00-0033873`: not found by exact ID in approved current roster sources

The bridge reports this as a current-source gap, not as a current team inference from historical packet data.

## No Model-Visible Exposure

Search and tests confirmed:

- no identity bridge helper is registered as a Pigskin tool
- no lookup-plus-merge QA helper is registered as a Pigskin tool
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` remains unset in production and staging
- no prompt text was changed to call unavailable historical packet tools

## Source Inventory Summary

Read-only counts:

| Object | Row Count |
|---|---:|
| `pigskin_player_context_packet_current` | 4,084 |
| `compat_pigskin_player_context_current` | 4,084 |
| 2025 compat Pigskin rows | 510 |
| 2026+ compat Pigskin rows | 0 |
| `player_identity_bridge` | 11,212 |
| `dim_players_current` | 11,212 |
| `sleeper_players_current` | 4,254 |
| `sleeper_roster_players` | 636 |
| `sleeper_available_players` | 3,032 |
| `sleeper_viewer_team_snapshots` | 3 |
| `compat_viewer_team_context` | 10 |

2026+ raw nflverse and staging checked counts were 0. `analytics_pigskin_rankings` has 285 2026+ rows and remains a known unrelated ranking mart warning, not packet exposure data.

## Test Results

Final checks before commit:

- `scripts/check_deployment_safety.py`: pass
- `py_compile src\pigskin_identity_bridge.py`: pass
- `py_compile src\pigskin_context_qa.py`: pass
- `py_compile src\pigskin_current_roster_lookup.py`: pass
- `py_compile src\pigskin_current_roster_merge.py`: pass
- `py_compile src\pigskin_packet_retrieval.py`: pass
- `py_compile src\pigskin_packet_guardrails.py`: pass
- `py_compile src\pigskin_context_tools.py`: pass
- `py_compile src\llm_context_packets.py`: pass
- `py_compile app.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_pigskin_identity_bridge`: 20 tests passed
- `tests.test_pigskin_context_qa`: 18 tests passed
- `tests.test_pigskin_current_roster_lookup`: 18 tests passed
- `tests.test_pigskin_current_roster_merge`: 16 tests passed
- `tests.test_pigskin_packet_retrieval`: 12 tests passed
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests passed
- full suite: 583 tests passed

## Migration And Validation Results

- BigQuery migrations pending: none
- BigQuery validation dry-run: discovered through validation 200

Read-only validation patterns:

- `raw_nflverse`: pass with informational coverage warning
- `stg_`: pass
- `advanced_metrics`: pass
- `compat_pigskin`: pass
- `trade_player_scores`: pass
- `trade_pick_scores`: pass with informational model-version coverage warning

## Service Untouched Confirmation

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- image digest: `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: unset
- Data Ops trigger flags: false
- local subprocess flags: false
- Trade Analyzer score flags: false
- Trade History compat: false

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- image digest: `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: unset
- Data Ops trigger flags: false
- local subprocess flags: false

No deployment occurred in Phase 30.13.

## Remaining Warnings

- Compact-name expansion is intentionally conservative and can make full-name lookups ambiguous.
- `sleeper_player_id=1166` resolves to Kirk Cousins in approved current-source data, not Tyreek Hill.
- `player_id_internal=00-0033040` and `00-0033873` do not resolve by exact ID in approved identity/current sources.
- `analytics_pigskin_rankings` has 2026+ rows but is not historical packet exposure data.
- Historical validation backlog remains untracked.
- This Phase 30.13 report is new evidence and was created after the commit.

## Recommended Next Phase

Phase 30.14 - Identity source remediation for Tyreek/Mahomes stable ID gaps.

After source remediation, the owner can make a separate exposure decision for any model-visible historical packet tool or staging-only exposure test.
