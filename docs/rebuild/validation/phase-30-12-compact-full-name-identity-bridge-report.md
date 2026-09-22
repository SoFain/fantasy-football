# Phase 30.12 Compact/Full-Name Identity Bridge Report

## Final Decision

IDENTITY BRIDGE READY WITH WARNINGS

The internal identity bridge is implemented, tested, and kept read-only. It is not model-visible. No BigQuery rows were written, no materializations ran, no Sleeper API calls were made, no Pigskin or LLM prompts were submitted, and no deployment occurred.

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

## Git State

- Latest commit: `52e108f Add lookup merge QA helper`
- No files were staged at the start.
- Modified tracked files:
  - `src/pigskin_context_qa.py`
  - `tests/test_pigskin_context_qa.py`
- New Phase 30.12 files:
  - `src/pigskin_identity_bridge.py`
  - `tests/test_pigskin_identity_bridge.py`
  - `docs/rebuild/validation/phase-30-12-compact-full-name-identity-bridge-design.md`
  - `docs/rebuild/validation/phase-30-12-compact-full-name-identity-bridge-report.md`
- Historical validation backlog remains untracked and separate.

## Baseline Checks

Baseline before edits:

- `scripts/check_deployment_safety.py`: pass
- Pigskin module compiles: pass
- `app.py` compile: pass
- `compileall -q src scripts`: pass
- Targeted Pigskin tests: pass
- Full suite: 563 tests passed
- BigQuery migrations pending: none
- BigQuery validation dry-run: discovered through validation 200

## Identity Source Audit

Read-only warehouse audit:

| Object | Row Count | Notes |
|---|---:|---|
| `player_identity_bridge` | 11,212 | Stable ID and canonical name source |
| `dim_players_current` | 11,212 | Stable ID and current dimension source |
| `sleeper_players_current` | 4,254 | Approved global current roster source |
| `sleeper_roster_players` | 636 | League-scoped roster source only |
| `sleeper_available_players` | 3,032 | League-scoped availability source only |
| `sleeper_viewer_team_snapshots` | 3 | Snapshot source, not global status |
| `compat_viewer_team_context` | 10 | Not used as global player status |
| `pigskin_player_context_packet_current` | 4,084 | Historical packet current view |
| `compat_pigskin_player_context_current` | 4,084 | Historical packet compatibility view |

Packet counts:

- 2025 compat Pigskin rows: 510
- 2026+ compat Pigskin rows: 0
- 2026+ Pigskin packet rows: 0
- 2026+ raw nflverse counts checked: 0 across checked raw tables
- 2026+ staging counts checked: 0 across checked `stg_` tables

Warning: `analytics_pigskin_rankings` has 285 rows for 2026+. This is an existing ranking mart, not a Pigskin packet or current roster status source.

## Files Changed

- Added `src/pigskin_identity_bridge.py`
- Added `tests/test_pigskin_identity_bridge.py`
- Added identity diagnostics to `src/pigskin_context_qa.py`
- Updated `tests/test_pigskin_context_qa.py`
- Added the design note

## Identity Bridge Contract Summary

`src/pigskin_identity_bridge.py` adds:

- `normalize_player_name`
- `build_compact_display_variants`
- `build_identity_bridge_query`
- `resolve_player_identity`
- `explain_identity_mismatch`
- `reconcile_packet_and_current_identity`

The bridge requires at least one stable ID or name input. Team and position are narrowing filters only. Name and compact-name lookups require an explicit limit and clamp to 25.

The BigQuery query is parameterized and reads only:

- `player_identity_bridge`
- `dim_players_current`
- `sleeper_players_current`
- `sleeper_roster_players`
- `sleeper_available_players`

It does not read `compat_viewer_team_context`, raw nflverse, `weekly_metrics`, or the historical packet compatibility view as identity authority.

## Source Precedence

1. `player_identity_bridge`
2. `dim_players_current`
3. `sleeper_players_current`
4. `sleeper_roster_players`, only with league scope
5. `sleeper_available_players`, only with league scope and availability request
6. Historical packet compact names remain historical evidence only

## Compact-Name Expansion

The bridge builds compact variants such as:

- `Tyreek Hill` to `t.hill` and `thill`
- `A.J. Brown` to `a.brown`, `abrown`, `aj.brown`, and `ajbrown`

Compact collisions return candidates and do not select a player.

## Full-Name Matching

Full-name inputs are normalized and matched against display, full, and stored normalized names. Compact expansion is included for packet compatibility, so full-name inputs can return ambiguity when compact expansion collides. This is intentional for now because silent selection is riskier than owner confirmation.

## Stable-ID Reconciliation

Stable IDs are preferred. If a single candidate has conflicting stable IDs across approved sources, `resolve_player_identity` returns `needs_identity_confirmation`.

`reconcile_packet_and_current_identity` compares packet and current roster payloads. It returns `needs_identity_confirmation` for stable-ID mismatch and `current_roster_source_gap` when current source data is unavailable.

## Ambiguity Behavior

Ambiguous names return candidate lists:

- `T.Hill`: 4 candidates, including Tyreek Hill, Taysom Hill, Trey Hill, Tony Hill
- `A.Brown`: 5 candidates in the bounded smoke result
- `J.Jefferson`: 4 candidates in the bounded smoke result
- `D.Johnson`: 5 candidates in the bounded smoke result
- `J.Williams`: 5 candidates in the bounded smoke result

No compact collision silently selected an identity.

## Identity Mismatch Behavior

Mismatch diagnostics include:

- stable ID field
- historical value
- current value
- resolution: `needs_identity_confirmation`

The bridge does not choose which source is right.

## Tyreek Hill Diagnostics

Read-only smoke:

- `player_name=Tyreek Hill`, `limit=10`: ambiguous, 4 candidates due compact expansion
- `compact_name=T.Hill`, `limit=10`: ambiguous, 4 candidates
- historical packet identity `player_id_internal=00-0033040`: not found in approved identity/current sources
- `sleeper_player_id=1166`: selected `Kirk Cousins`, stable IDs `player_id_internal=gsis:00-0029604`, `gsis_id=00-0029604`, `sleeper_player_id=1166`, current team `LV`

Synthetic reconciliation of packet `T.Hill`, `player_id_internal=00-0033040`, historical team `MIA` against the approved current-source result for sleeper `1166` returned:

- status: `needs_identity_confirmation`
- blocked reason: `stable_id_mismatch`
- historical team: `MIA`
- current team: `LV`
- mismatch: `player_id_internal` historical `00-0033040` versus current `gsis:00-0029604`

The bridge preserved historical/current separation and did not infer current team from the packet.

## Mahomes Diagnostics

Read-only smoke:

- `player_name=Patrick Mahomes`, `limit=10`: ok, selected Patrick Mahomes, current team `KC`
- `player_id_internal=00-0033873`: not found by that internal ID in approved sources

`reconcile_packet_and_current_identity` with a Mahomes historical packet and no current payload returned:

- status: `current_roster_source_gap`
- blocked reason: `approved_current_roster_source_unavailable`
- warning: current roster state was not inferred from historical packet team

## Integration With Current Roster Lookup And QA Helper

The current roster lookup helper remains unchanged. It is still the source of current roster payloads.

`pigskin_context_qa.py` now adds `identity_diagnostics` after deterministic packet/current lookup and before returning the merged QA result. The merge behavior remains conservative:

- missing current roster state remains unavailable
- historical team is not treated as current team
- stable-ID mismatch still requires confirmation

## Tests Added Or Updated

Added `tests/test_pigskin_identity_bridge.py` with 20 tests.

Updated `tests/test_pigskin_context_qa.py` to assert diagnostics are carried in the QA result.

Coverage includes:

- empty/unbounded rejection
- arbitrary SQL key rejection
- explicit limit required for name lookup
- team/position not treated as identity
- parameterized BigQuery query
- approved source allowlist
- forbidden source exclusion
- stable ID deterministic paths
- full-name ambiguity
- compact-name collisions
- stable-ID conflicts
- Tyreek mismatch diagnostics
- Mahomes current-source gap
- source/as-of provenance
- no Sleeper API, BigQuery write, Pigskin, LLM, or tool registration path

## Optional Read-Only Smoke QA

Bounded smoke cases ran through `resolve_player_identity`:

| Case | Result |
|---|---|
| `player_name=Tyreek Hill`, limit 10 | ambiguous, 4 candidates |
| `compact_name=T.Hill`, limit 10 | ambiguous, 4 candidates |
| `player_id_internal=00-0033040` | not found in approved identity/current sources |
| `sleeper_player_id=1166` | ok, selected Kirk Cousins, current team LV |
| `player_name=Patrick Mahomes`, limit 10 | ok, current team KC |
| `player_id_internal=00-0033873` | not found by that internal ID |
| `compact_name=A.Brown`, limit 10 | ambiguous, 5 candidates |
| `compact_name=J.Jefferson`, limit 10 | ambiguous, 4 candidates |
| `compact_name=D.Johnson`, limit 10 | ambiguous, 5 candidates |
| `compact_name=J.Williams`, limit 10 | ambiguous, 5 candidates |

## No Model-Visible Exposure Confirmation

Search confirmed:

- no identity bridge helper is registered as a Pigskin tool
- no lookup-plus-merge QA helper is registered as a Pigskin tool
- future historical packet declaration remains default-disabled
- no prompt text was changed to call unavailable historical packet tools

## No State Change Confirmation

- No BigQuery write command was run.
- No materialization command was run.
- No Sleeper API call was made.
- No Pigskin or LLM call was made.
- No Cloud Run Job was triggered.
- No deployment occurred.

## Validation Results

Read-only validation patterns:

- `raw_nflverse`: pass, with informational coverage warning
- `stg_`: pass
- `advanced_metrics`: pass
- `compat_pigskin`: pass
- `trade_player_scores`: pass
- `trade_pick_scores`: pass, with informational model-version coverage warning

## Final Local Checks

Final checks:

- `scripts/check_deployment_safety.py`: pass
- `py_compile` for new and touched Pigskin modules: pass
- `py_compile app.py`: pass
- `compileall -q src scripts`: pass
- `tests.test_pigskin_identity_bridge`: 20 tests pass
- `tests.test_pigskin_context_qa`: 18 tests pass
- `tests.test_pigskin_current_roster_lookup`: 18 tests pass
- `tests.test_pigskin_current_roster_merge`: 16 tests pass
- `tests.test_pigskin_packet_retrieval`: 12 tests pass
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests pass
- Full test suite: 583 tests pass
- BigQuery migrations pending: none
- BigQuery validation dry-run: discovered through validation 200

## Staging And Production Untouched

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- image: `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: unset
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- Trade score flags: false
- Trade history compat: false

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- image: `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: unset
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- staging Trade Score and Trade History flags remain as previously configured

## Remaining Warnings

- Compact-name expansion is intentionally conservative and can make full-name lookups ambiguous when compact aliases collide.
- `sleeper_player_id=1166` currently resolves to Kirk Cousins in approved current-source data, not Tyreek Hill.
- `player_id_internal=00-0033040` and `00-0033873` do not resolve by those exact IDs in approved identity/current sources, even though name-based lookup can find Tyreek Hill and Patrick Mahomes.
- `analytics_pigskin_rankings` has 2026+ rows. This was not changed in this phase and is not a historical packet exposure source.
- Historical validation backlog remains untracked.

## Recommended Next Phase

Phase 30.13 - Package and commit identity bridge improvements.

After that, a separate owner decision should choose whether to integrate the identity bridge into lookup-plus-merge QA resolution flow more deeply or keep it as a diagnostic layer until model-visible historical packet exposure is explicitly approved.
