# Phase 30.2 Pigskin-Safe Packet Retrieval Layer Report

## Final Decision

PIGSKIN SAFE RETRIEVAL LAYER READY WITH WARNINGS

The safe historical packet retrieval layer exists, is tested, and reads only `compat_pigskin_player_context_current`. It is not yet wired into Pigskin prompt/tool exposure. That is intentional for this phase.

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

No gates were set during this phase.

## Git State

- latest commit at start: `acdb92c Expand nflverse Pigskin packets through 2025`
- staged files: none
- existing untracked backlog: historical validation reports and owner-review artifacts
- new Phase 30.2 untracked files:
  - `src/pigskin_packet_retrieval.py`
  - `tests/test_pigskin_packet_retrieval.py`
  - `docs/rebuild/validation/phase-30-2-pigskin-safe-packet-retrieval-layer-design.md`
  - `docs/rebuild/validation/phase-30-2-pigskin-safe-packet-retrieval-layer-report.md`

No commit was created.

## Baseline Checks

Baseline checks passed before edits:

- `scripts/check_deployment_safety.py`: pass
- `py_compile` for Pigskin context, LLM packets, nflverse packet, advanced metrics, staging, backfill, backfill plan, and `app.py`: pass
- `compileall -q src scripts`: pass
- targeted nflverse tests: pass
- `unittest discover tests`: pass, 487 tests
- `run_bigquery_migrations.py --list-pending`: no pending migrations
- `run_bigquery_validations.py --dry-run`: catalog discovered through validation 200

## Integration Code Audit

Observed current behavior:

- `src/pigskin_context_tools.py` exposes named model-visible tools only. It does not expose arbitrary SQL.
- Existing `get_player_context_packet` and `search_players` still use `src.llm_context_packets`.
- `src.llm_context_packets` reads the older `llm_player_context_packet` surface.
- `compat_pigskin_player_context_current` was not model-visible before this phase.
- `app.py` already contains the prompt rule that historical stat-week team must not be described as current team.

No app prompt wiring was changed in Phase 30.2.

## Retrieval Layer Files Changed

Created:

- `src/pigskin_packet_retrieval.py`
- `tests/test_pigskin_packet_retrieval.py`
- `docs/rebuild/validation/phase-30-2-pigskin-safe-packet-retrieval-layer-design.md`

The new module is an internal read-only API, not a model-visible tool registration.

## Retrieval Request Contract

Required:

- `season`, or both `season_start` and `season_end`

Optional:

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

The layer refuses unbounded historical retrieval. It is currently bounded to 2014-2025.

## Retrieval Response Contract

Responses are dictionaries with:

- `status`: `ok`, `ambiguous`, `not_found`, `validation_error`, or `query_error`
- `found`
- `source`: `compat_pigskin_player_context_current`
- `source_policy`: `historical_nflverse_packet_context_only`
- `historical_context_only`
- `current_roster_status_source_required`
- `current_roster_status_policy`
- `packet` for a single deterministic result
- `packets` for bounded list results
- `candidates` for ambiguous player-name matches
- `warnings`

Normalized packet fields use historical names:

- `historical_team`
- `historical_position`
- `as_of_season`
- `as_of_week`
- `display_name`
- `player_id_internal`

The retrieval layer does not expose packet `team` as `current_team`.

## Source Isolation Confirmation

The retrieval query reads only:

- `compat_pigskin_player_context_current`

It does not read:

- `raw_nflverse_*`
- `stg_*`
- `pigskin_player_context_packet_current`
- `play_by_play`
- `weekly_metrics`
- arbitrary caller-supplied SQL

The query uses BigQuery parameters, including an array parameter for display-name variants. Tests verify that injected player-name text is not rendered into SQL.

Validation `198_compat_pigskin_context_no_raw_dependencies.sql` passed with `raw_source_dependency_count = 0`.

## Identity Disambiguation Behavior

Rules implemented:

- `player_id_internal` is preferred and deterministic.
- Compact display-name collisions return `status=ambiguous`.
- `team` and `position` can disambiguate compact display-name results.
- Full-name support is candidate-only. It maps names such as `Tyreek Hill` to compact variants such as `t.hill`, then still requires uniqueness, team/position, or player ID.

Names that must not be silently selected, such as `T.Hill`, `D.Johnson`, `J.Williams`, `K.Williams`, `A.Brown`, and `J.Jefferson`, are covered by the candidate-return policy.

## Tyreek Hill Historical And Current-Status Handling

Read-only smoke QA:

- `Tyreek Hill`, season 2025: `status=ambiguous`, 2 candidates
- `T.Hill`, season 2025: `status=ambiguous`, 2 candidates
- `T.Hill`, season 2025, `team=MIA`, `position=WR`: `status=ok`, `player_id_internal=00-0033040`, `historical_team=MIA`, `as_of_week=4`
- player ID lookup for `00-0033040`: `status=ok`, `historical_team=MIA`

Every result includes:

`Current roster/free-agent status must come from Sleeper/current roster source.`

No 2026 free-agent or current-team claim is returned from the packet retrieval layer.

## Sleeper And Current Roster Deferral Rule

The module does not call Sleeper, current roster APIs, Pigskin prompts, or LLMs.

Current roster/free-agent/current-team facts must come from a separate current roster source in a future merge phase. The historical nflverse packet can only provide completed-season evidence.

## Postseason Handling

Default behavior excludes postseason rows by season-era cutoff:

- seasons through 2020: weeks 1-17
- seasons 2021 and later: weeks 1-18

`include_postseason=True` permits Week 22.

Read-only smoke QA:

- actual Week 22 seed: `A.Barner`, 2025 Week 22, `player_id_internal=00-0039793`, `team=SEA`, `position=TE`
- Week 22 with `include_postseason=False`: `status=not_found`
- Week 22 with `include_postseason=True`: `status=ok`, `historical_team=SEA`, `as_of_week=22`

No Week 22 rows were deleted or altered.

## Blocked Metric Presentation

The retrieval layer parses `packet_json.blocked_metrics` and returns:

- `blocked_metrics`
- `blocked_metric_policy`: `blocked metrics are unavailable, not zero`

Tests verify blocked metrics are preserved and not converted to zero.

## Packet JSON Parsing Behavior

The module safely parses:

- `packet_json`
- `source_freshness_json`
- `missing_data_flags`

Malformed JSON does not crash retrieval. The affected field is left empty or unchanged and a parse warning is returned.

## Tests Added And Updated

Added `tests/test_pigskin_packet_retrieval.py` with coverage for:

- explicit season/window requirement
- compatibility-view-only query
- no raw/staging/base packet table references
- parameterized query behavior
- player ID deterministic lookup
- compact-name ambiguity
- Tyreek Hill current-status deferral
- team/position disambiguation
- historical team naming
- regular-season cutoff
- Week 22 inclusion
- blocked metric preservation
- malformed JSON safety
- no Sleeper, LLM, or Pigskin prompt call path

## Optional Read-Only Smoke QA Results

Packet counts:

| Check | Result |
| --- | ---: |
| `pigskin_player_context_packet_current` | 4,084 |
| `compat_pigskin_player_context_current` | 4,084 |
| 2025 compat packet rows | 510 |
| Week 22 compat packet rows | 57 |
| 2026+ packet rows | 0 |

Category-level 2026+ separation:

| Category | Table count | Row count | 2026+ rows |
| --- | ---: | ---: | ---: |
| raw_nflverse | 18 | 1,757,357 | 0 |
| staging | 6 | 2,462,109 | 0 |
| advanced_metrics | 3 | 229,768 | 0 |
| packet | 2 | 8,168 | 0 |

## No-State-Change Confirmation

No BigQuery writes were run.

Not run:

- raw backfill
- prepare-only
- nflreadpy loaders
- staging materialization
- advanced metrics materialization
- Pigskin packet refresh
- packet-display repair
- rankings
- Sleeper API
- LLM/Pigskin prompt calls
- Cloud Run Jobs
- Scheduler jobs
- deployments

Packet and 2026+ row counts remained consistent with Phase 30.1.

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
- `unittest tests.test_pigskin_packet_retrieval`: 12 tests
- `unittest tests.test_nflverse_pigskin_packets`: 15 tests
- `unittest tests.test_nflverse_advanced_metrics`: 12 tests
- `unittest tests.test_nflverse_staging`: 11 tests
- `unittest tests.test_nflverse_backfill_executor`: 18 tests
- `unittest tests.test_nflverse_backfill_plan`: 15 tests
- `unittest discover tests`: 499 tests
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

No deployment occurred.

## Remaining Warnings

- Full-name identity resolution is still not a reliable identity bridge because the compatibility surface stores compact display names.
- The retrieval layer is not yet model-visible. Prompt/tool guardrails are still needed before Pigskin can use it safely.
- Current roster/free-agent/current-team state still requires a separate Sleeper/current roster merge phase.
- Expected informational validation warnings remain for raw nflverse coverage and trade-pick score model-version coverage.
- The historical validation backlog remains untracked for owner review.

## Recommended Next Phase

Phase 30.3 should package and commit the Pigskin-safe retrieval layer, or add Pigskin prompt/tool guardrails for this retrieval layer before any model-visible use.
