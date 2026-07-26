# Phase 30.5 Pigskin Prompt Tool Guardrails Commit Report

## Final Decision

PIGSKIN PROMPT TOOL GUARDRAILS COMMITTED WITH WARNINGS

Phase 30.5 committed the approved Phase 30.4 Pigskin historical packet prompt/tool guardrails package. No deployment occurred. No BigQuery rows were written. No Pigskin, LLM, Sleeper, Cloud Run Job, Scheduler, backfill, materialization, ranking, or packet refresh action was run.

## Commit Hash

`859ad96 Add Pigskin historical packet guardrails`

## Files Committed

- `app.py`
- `src/pigskin_packet_guardrails.py`
- `tests/test_pigskin_packet_tool_guardrails.py`
- `docs/rebuild/validation/phase-30-4-pigskin-prompt-tool-guardrails-design.md`
- `docs/rebuild/validation/phase-30-4-pigskin-prompt-tool-guardrails-report.md`

## Files Excluded

The historical validation backlog and owner-review artifacts remain untracked. No logs, caches, browser evidence, output folders, temporary JSON, environment files, secrets, deployment artifacts, or unrelated source files were staged or committed.

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

## Implementation Summary

The committed package adds `src.pigskin_packet_guardrails` with policy constants, defensive prompt text, a default-disabled future tool declaration, and an internal wrapper around `src.pigskin_packet_retrieval.retrieve_historical_pigskin_packets`.

The active Pigskin tool registry in `src.pigskin_context_tools.py` was not changed. No model-visible historical packet tool was registered.

## Prompt Guardrail Summary

`app.py` now injects `PIGSKIN_HISTORICAL_PACKET_PROMPT_GUARDRAIL` into the Pigskin system prompt. The text says historical nflverse packet context is completed-season evidence only, must label packet season/week, treats packet team as historical team, and does not answer current roster, free-agent, dynasty availability, injury/status, or current-team questions.

The prompt explicitly says not to call historical packet lookup unless a future enabled tool is present in the provided tool list.

## Wrapper And Default-Disabled Summary

`execute_historical_packet_context_lookup(args, client=None, dataset_id=None)`:

- requires `season`, or `season_start` plus `season_end`
- rejects SQL-style arguments such as `sql_query`
- does not call BigQuery directly
- does not call Sleeper
- does not call Pigskin or an LLM
- maps allowed args into the retrieval layer
- strips exact `current_team` fields from packet/candidate output
- preserves `historical_team`
- preserves ambiguity candidates
- preserves blocked metrics as unavailable, not zero

`get_historical_packet_tool_declarations(enabled=None)` returns `[]` by default and only returns the future declaration when explicitly enabled by caller or by `USE_PIGSKIN_HISTORICAL_PACKET_TOOL=true`.

## Future Tool Exposure Summary

The future declaration name is `get_historical_pigskin_packet_context`. It remains non-model-visible. Owner approval and a separate exposure phase are still required before wiring it into Pigskin tools.

## Identity Disambiguation Summary

Compact display-name collisions return candidates. The wrapper does not silently choose between players. Future exposure should require player ID, team, or position when names collide.

## Tyreek Hill Historical And Current-Status Handling

Phase 30.4 smoke coverage confirmed:

- `T.Hill`, 2025 with no disambiguation returns `ambiguous`, 2 candidates
- `T.Hill`, 2025, `team=MIA`, `position=WR` returns historical Miami packet context
- no 2026 roster/free-agent/current-team claim is produced from packet retrieval

## Sleeper And Current Roster Deferral Rule

Current roster/free-agent status must come from Sleeper/current roster source. The guardrail package adds this rule to prompt text and guarded wrapper results, but does not call Sleeper.

## Postseason Handling

Week 22 remains postseason/historical context. The wrapper and prompt keep it excluded from regular-season fantasy analysis unless explicitly requested.

## Blocked Metric Handling

Blocked metrics remain unavailable, not zero. The wrapper and tests preserve the distinction.

## Source Isolation Confirmation

Historical packet retrieval remains bound to `compat_pigskin_player_context_current`. The wrapper rejects arbitrary SQL and does not expose raw/staging/source tables to Pigskin.

## Test Results

Final checks passed before commit:

- `scripts/check_deployment_safety.py`: pass
- requested `py_compile` commands: pass
- `compileall -q src scripts`: pass
- `tests.test_pigskin_packet_tool_guardrails`: pass, 12 tests
- `tests.test_pigskin_packet_retrieval`: pass, 12 tests
- `tests.test_nflverse_pigskin_packets`: pass, 15 tests
- `tests.test_nflverse_advanced_metrics`: pass, 12 tests
- `tests.test_nflverse_staging`: pass, 11 tests
- `tests.test_nflverse_backfill_executor`: pass, 18 tests
- `tests.test_nflverse_backfill_plan`: pass, 15 tests
- `unittest discover tests`: pass, 511 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: validation catalog discovered through validation 200

## Validation Results

Read-only validation patterns passed:

- `raw_nflverse`: 3 passed, 0 failed, informational coverage warning
- `stg_`: 7 passed, 0 failed
- `advanced_metrics`: 4 passed, 0 failed
- `compat_pigskin`: 2 passed, 0 failed
- `trade_player_scores`: 12 passed, 0 failed
- `trade_pick_scores`: 17 passed, 0 failed, informational model-version warning

## Warehouse Read-Only State

Read-only row confirmations:

| Check | Result |
| --- | ---: |
| `pigskin_player_context_packet_current` | 4,084 rows |
| `compat_pigskin_player_context_current` | 4,084 rows |
| 2025 compat packet rows | 510 |
| 2026+ packet rows | 0 |

Category future-row confirmation:

| Category | Table count | Row count | 2026+ rows |
| --- | ---: | ---: | ---: |
| raw_nflverse | 18 | 1,757,357 | 0 |
| staging | 6 | 2,462,109 | 0 |
| advanced_metrics | 7 | 252,568 | 0 |

## Service Untouched Confirmation

Production remained untouched:

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

Staging remained untouched:

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

## Remaining Warnings

- The future historical packet tool remains disabled and non-model-visible. Owner exposure decision is still required.
- Full-name identity resolution still needs a stronger identity bridge because the packet surface stores compact names.
- 2026 current roster/free-agent/current-team answers still require Sleeper/current roster merge work.
- Expected informational validation warnings remain for raw nflverse coverage and trade-pick score model-version coverage.
- Historical validation backlog remains untracked for owner review.

## Recommended Next Phase

Phase 30.6: Add Sleeper/current roster merge rules, or make an owner exposure decision for the model-visible historical packet tool.
