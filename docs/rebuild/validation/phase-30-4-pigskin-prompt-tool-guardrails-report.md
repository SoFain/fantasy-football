# Phase 30.4 Pigskin Prompt And Tool Guardrails Report

## Final Decision

PIGSKIN PROMPT TOOL GUARDRAILS READY WITH WARNINGS

The historical packet retrieval layer remains safe and internal. Phase 30.4 added a default-disabled guardrail wrapper, future tool declaration policy, Pigskin prompt guardrail text, and tests. No model-visible historical packet tool was registered.

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

No authorization gates were set.

## Git State

- latest commit: `6380d27 Add Pigskin-safe packet retrieval layer`
- staged files: none
- unrelated historical validation backlog remains untracked
- new/modified Phase 30.4 files:
  - `app.py`
  - `src/pigskin_packet_guardrails.py`
  - `tests/test_pigskin_packet_tool_guardrails.py`
  - `docs/rebuild/validation/phase-30-4-pigskin-prompt-tool-guardrails-design.md`
  - `docs/rebuild/validation/phase-30-4-pigskin-prompt-tool-guardrails-report.md`

No commit was created.

## Completion Check Rerun

The Phase 30.4 completion pass reran the requested checks after the report prompt:

- safety checker: pass
- requested `py_compile` commands: pass
- `compileall -q src scripts`: pass
- targeted nflverse tests: pass
- `tests.test_pigskin_packet_retrieval`: pass, 12 tests
- `tests.test_pigskin_packet_tool_guardrails`: pass, 12 tests
- `unittest discover tests`: pass, 511 tests
- no pending migrations
- validation dry-run discovered through validation 200

## Pigskin Tool And Prompt Audit

Current model-visible tool declarations live in `src.pigskin_context_tools.get_pigskin_context_tool_declarations`.

Active Pigskin tools remain:

- `get_player_context_packet`
- `search_players`
- `get_rankings_slice`
- `get_fraud_watch_candidates`
- `get_trade_player_history`
- `compare_players`
- `get_context_event_leads`

The new future historical packet tool is not added to this list.

The Pigskin system prompt is assembled in `app.py`. Existing prompt language already warned not to describe a historical stat-week team as current team. Phase 30.4 adds a more specific historical nflverse packet guardrail block.

## Files Changed

Added:

- `src/pigskin_packet_guardrails.py`
- `tests/test_pigskin_packet_tool_guardrails.py`
- `docs/rebuild/validation/phase-30-4-pigskin-prompt-tool-guardrails-design.md`
- `docs/rebuild/validation/phase-30-4-pigskin-prompt-tool-guardrails-report.md`

Updated:

- `app.py`

## Guardrail Policy Summary

`src.pigskin_packet_guardrails` defines:

- historical packet source policy
- current roster deferral policy
- historical-team naming rule
- compact-name ambiguity rule
- blocked metric unavailable-not-zero rule
- Week 22/postseason rule
- safe future tool description
- safe prompt guardrail text
- blocked request reasons

No live external call path was added.

## Wrapper And Tool Contract Summary

Internal wrapper:

`execute_historical_packet_context_lookup(args, client=None, dataset_id=None)`

Behavior:

- requires `season`, or both `season_start` and `season_end`
- rejects SQL-style arguments such as `sql_query`
- ignores unsupported non-SQL args with warning
- calls `pigskin_packet_retrieval.retrieve_historical_pigskin_packets`
- does not query BigQuery directly
- preserves ambiguity candidates
- strips any exact `current_team` field from packet/candidate output
- adds current roster deferral policy
- preserves blocked metric policy

Future declaration builder:

`get_historical_packet_tool_declarations(enabled=None)`

Default behavior:

- returns `[]`
- checks `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`
- remains disabled unless explicitly enabled by caller or environment

This builder is not wired into `src.pigskin_context_tools.py`.

## Prompt Guardrail Summary

`app.py` now includes `PIGSKIN_HISTORICAL_PACKET_PROMPT_GUARDRAIL` in the Pigskin system prompt.

The guardrail says:

- historical nflverse packet context is completed-season evidence only
- packet context does not answer current roster, free-agent, dynasty availability, injury/status, or current-team questions
- 2026-facing roster/status questions require Sleeper/current roster source
- packet season/week must be labeled when packet context is provided
- packet team is historical team, never current team
- ambiguous player lookups require player ID, team, or position
- blocked metrics are unavailable, not zero
- Week 22 is postseason/historical unless explicitly requested

The prompt does not tell Pigskin to call a historical packet retrieval tool before such a tool is enabled.

## Feature Flag And Default Disabled Summary

Default-disabled switch:

`USE_PIGSKIN_HISTORICAL_PACKET_TOOL`

It was not set in any local, staging, or production runtime by this phase.

## Identity Disambiguation Behavior

The wrapper preserves retrieval-layer ambiguity behavior.

Compact display-name collisions return candidates instead of selected packets. Future UI/tool exposure must require disambiguators such as:

- player ID
- team
- position

## Tyreek Hill Historical And Current-Status Handling

Read-only wrapper smoke:

- missing season: `validation_error`
- `T.Hill`, 2025, no disambiguation: `ambiguous`, 2 candidates
- `T.Hill`, 2025, `team=MIA`, `position=WR`: `ok`, `historical_team=MIA`

No 2026 free-agent or current-team claim is produced by the wrapper.

## Sleeper And Current Roster Deferral Rule

Every guarded result includes:

`Current roster/free-agent status must come from Sleeper/current roster source.`

No Sleeper API call or external roster call was added.

## Postseason Handling

Read-only wrapper smoke:

- 2025 Week 22 packet lookup without `include_postseason`: `not_found`
- 2025 Week 22 packet lookup with `include_postseason=True`: `ok`, `historical_team=SEA`

Week 22 remains explicit postseason/historical context.

## Blocked Metric Handling

The wrapper carries:

`Blocked metrics are unavailable, not zero.`

Tests verify the policy and that blocked metrics remain visible.

## Tests Added And Updated

Added `tests/test_pigskin_packet_tool_guardrails.py` with coverage for:

- future tool exposure default disabled
- enabled declaration contains safe bounded arguments
- model-visible Pigskin tools do not include the future historical packet tool
- missing season/window validation
- arbitrary SQL argument rejection
- wrapper calls retrieval layer with mocks, not BigQuery directly
- `historical_team` preserved
- exact `current_team` field removed from packet/candidate data
- ambiguity candidates preserved
- Tyreek Hill historical/current-status separation
- blocked metrics unavailable-not-zero policy
- Week 22 explicit postseason behavior
- no Sleeper/LLM/Pigskin prompt call path
- prompt guardrail historical/current separation language

## Optional Smoke QA Results

Read-only wrapper smoke against the warehouse:

| Scenario | Result |
| --- | --- |
| missing season | `validation_error` |
| `T.Hill`, 2025 | `ambiguous`, 2 candidates |
| `T.Hill`, 2025, `team=MIA`, `position=WR` | `ok`, `historical_team=MIA` |
| 2025 Week 22 default | `not_found` |
| 2025 Week 22 with `include_postseason=True` | `ok`, `historical_team=SEA` |

No `current_team` packet field was returned.

## No-State-Change Confirmation

No BigQuery rows were written.

Not run:

- raw backfill
- prepare-only
- nflreadpy loaders
- staging materialization
- advanced metrics materialization
- Pigskin packet refresh
- rankings
- Sleeper API
- Pigskin prompt calls
- LLM calls
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
- `py_compile src\pigskin_packet_guardrails.py`
- `py_compile src\pigskin_packet_retrieval.py`
- `py_compile src\pigskin_context_tools.py`
- `py_compile src\llm_context_packets.py`
- `py_compile src\nflverse_pigskin_packets.py`
- `py_compile src\nflverse_advanced_metrics.py`
- `py_compile src\nflverse_staging.py`
- `py_compile src\nflverse_backfill.py`
- `py_compile src\nflverse_backfill_plan.py`
- `py_compile app.py`
- `compileall -q src scripts`
- `tests.test_pigskin_packet_retrieval`: 12 tests
- `tests.test_pigskin_packet_tool_guardrails`: 12 tests
- `tests.test_nflverse_pigskin_packets`: 15 tests
- `tests.test_nflverse_advanced_metrics`: 12 tests
- `tests.test_nflverse_staging`: 11 tests
- `tests.test_nflverse_backfill_executor`: 18 tests
- `tests.test_nflverse_backfill_plan`: 15 tests
- `unittest discover tests`: 511 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: catalog discovered through validation 200

## Staging And Production Untouched

Production:

- service: `nfl-studio-dashboard`
- revision: `nfl-studio-dashboard-00077-2jp`
- traffic: 100 percent to `nfl-studio-dashboard-00077-2jp`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f`
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- Trade Analyzer score flags: false
- Trade History compatibility: false

Staging:

- service: `nfl-studio-dashboard-staging`
- revision: `nfl-studio-dashboard-staging-00029-jtb`
- traffic: 100 percent to `nfl-studio-dashboard-staging-00029-jtb`
- image: `us-central1-docker.pkg.dev/fantasy-football-498121/nfl-studio-repo/nfl-studio-app@sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8`
- Data Ops trigger flags: false
- Data Ops local subprocess flags: false
- staging score/history flags remain as previously configured
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL`: absent/unset

No deployment occurred.

## Remaining Warnings

- The future historical packet tool remains disabled and non-model-visible. Owner exposure decision is still required.
- Full-name identity resolution still needs a stronger identity bridge because the packet surface stores compact names.
- 2026 current roster/free-agent/current-team answers still require Sleeper/current roster merge work.
- Expected informational validation warnings remain for raw nflverse coverage and trade-pick score model-version coverage.
- Historical validation backlog remains untracked for owner review.

## Recommended Next Phase

Phase 30.5: Package and commit Pigskin prompt/tool guardrails.
