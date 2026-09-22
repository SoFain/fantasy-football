# Phase 30.17 - Current Source Exposure Readiness Report

Final decision: CURRENT SOURCE EXPOSURE READINESS READY WITH GUARDRAILS

## Gate State

All checked gates were unset:

| Gate | State |
| --- | --- |
| `ALLOW_PIGSKIN_PACKET_REFRESH` | unset |
| `ALLOW_ADVANCED_METRICS_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_STAGING_MATERIALIZATION` | unset |
| `ALLOW_NFLVERSE_HISTORICAL_BACKFILL` | unset |
| `ALLOW_NFLVERSE_WEEKLY_REFRESH` | unset |
| `ALLOW_NFLVERSE_WAREHOUSE_MIGRATION_APPLY` | unset |
| `ALLOW_TRADE_PICK_SCORE_MATERIALIZATION` | unset |
| `ALLOW_TRADE_SCORE_MATERIALIZATION` | unset |
| `ALLOW_LIMITED_PRODUCTION_DEPLOY` | unset |
| `DATA_OPS_ALLOW_LOCAL_SUBPROCESS_TRIGGER` | unset |
| `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` | unset |

No deployment, materialization, Sleeper ingestion, Pigskin prompt, LLM call, Cloud Run Job trigger, Scheduler creation, or BigQuery write was run.

## Git State

Starting checkpoint:

- `99c9d00 Add identity query normalization for GSIS IDs`

Phase 30.17 commit:

- `143fd2d Tighten Pigskin current-source exposure readiness`

Committed files:

| File | Summary |
| --- | --- |
| `src/pigskin_current_roster_lookup.py` | Extends current roster lookup to search raw and `gsis:`-prefixed `player_id_internal` variants with a parameterized BigQuery array. |
| `tests/test_pigskin_current_roster_lookup.py` | Adds tests for raw GSIS, prefixed GSIS, non-GSIS exact-only behavior, and null-safe empty-array name lookup. |

The unrelated historical validation backlog remains untracked and was not staged.

## Current Source Review

Approved current roster and identity sources only:

- `player_identity_bridge`
- `dim_players_current`
- `sleeper_players_current`
- `sleeper_roster_players`
- `sleeper_available_players`

`compat_viewer_team_context` was not used as global current player status.

| Input | Status | Candidate count | Identity | Current source | Current team/status | As of | Safe for model-visible use |
| --- | --- | ---: | --- | --- | --- | --- | --- |
| `player_name=Tyreek Hill` | ok | 1 | `player_id_internal=gsis:00-0033040`, `gsis_id=00-0033040`, `sleeper_player_id=3321` | `sleeper_players_current` | `current_team=NULL`, `current_roster_status=Active` | `2026-06-15T19:14:53.601698Z` | Ready with guardrails |
| `player_id_internal=00-0033040` | ok | 1 | same Tyreek identity, resolved through raw/prefixed lookup variants | `sleeper_players_current` | `current_team=NULL`, `current_roster_status=Active` | `2026-06-15T19:14:53.601698Z` | Ready with guardrails |
| `player_name=Patrick Mahomes` | ok | 1 | `player_id_internal=gsis:00-0033873`, `gsis_id=00-0033873`, `sleeper_player_id=4046` | `sleeper_players_current` | `current_team=KC`, `current_roster_status=Active` | `2026-06-15T19:14:53.601698Z` | Ready |
| `player_id_internal=00-0033873` | ok | 1 | same Mahomes identity, resolved through raw/prefixed lookup variants | `sleeper_players_current` | `current_team=KC`, `current_roster_status=Active` | `2026-06-15T19:14:53.601698Z` | Ready |
| `sleeper_player_id=1166` | ok | 1 | `player_id_internal=gsis:00-0029604`, `gsis_id=00-0029604`, `sleeper_player_id=1166` | `sleeper_players_current` | `current_team=LV`, `current_roster_status=Active` | `2026-06-15T19:14:53.601698Z` | Ready |
| `sleeper_player_id=5859`, league `1314636046436151296` | ok | 1 | A.J. Brown, `player_id_internal=gsis:00-0035676` | `sleeper_roster_players` | `current_team=NE`, `current_roster_status=Active`, availability `rostered` | `2026-06-08T18:25:27.387523Z` | Ready with guardrails |
| `sleeper_player_id=830`, league `1314636046436151296`, available included | ok | 1 | A.J. Green, `player_id_internal=gsis:00-0027942` | `sleeper_available_players` | `current_team=NULL`, `current_roster_status=Active`, availability `available` | `2026-06-08T18:25:27.387523Z` | Ready with guardrails |
| `player_name=T.Hill` | not_found | 0 | none | none | none | none | Ready with guardrails |
| `player_name=A.Brown` | not_found | 0 | none | none | none | none | Ready with guardrails |

Warnings observed:

- Current roster/free-agent/current-team status must come from approved current roster or identity sources, never historical packet team.
- Tyreek current team remains unknown in approved current roster sources.
- League availability context is preserved separately from global current player state where league roster or available tables are used.
- Compact-name inputs such as `T.Hill` and `A.Brown` do not silently resolve from current-source lookup. This is conservative and safe.

## Safe Improvements Made

The read-only current roster helper now mirrors the Phase 30.15 identity bridge normalization for `player_id_internal` lookup only:

- Raw GSIS-shaped values such as `00-0033040` search both `00-0033040` and `gsis:00-0033040`.
- Already-prefixed values such as `gsis:00-0033873` search both `gsis:00-0033873` and `00-0033873`.
- Non-GSIS internal IDs remain exact only.
- `gsis_id` remains a separate exact scalar path.
- `sleeper_player_id` remains a separate exact scalar path.
- The BigQuery query remains parameterized and read-only.
- Empty internal-ID searches remain name-safe through `COALESCE(ARRAY_LENGTH(@player_id_internal_variants), 0) = 0`.

No source data is rewritten. No hardcoded player remap was added.

## Exposure Readiness Matrix

| Exposure target | Status | Notes |
| --- | --- | --- |
| Internal QA use | Ready | Current roster lookup, packet retrieval, guardrails, and identity diagnostics are test-covered and read-only. |
| Read-only admin UI use | Ready with guardrails | Safe if it labels historical packet evidence and current roster context separately. |
| Staging-only model-visible historical packet tool | Needs owner decision | Tool declaration exists only behind explicit guardrails and remains default-disabled. A staging-only exposure test should be separate. |
| Production model-visible historical packet tool | Needs owner decision | Production exposure should wait for owner approval, staging evidence, and prompt wording review. |
| 2026 current roster/status answers | Ready with guardrails | Approved current-source rows support bounded answers, but Tyreek current team is unknown and must stay labeled unknown. |
| Dynasty/keeper forward-looking answers | Needs owner decision | Requires explicit policy for how historical packet context may inform future-looking claims. |
| Trade analyzer enrichment | Ready with guardrails | Current-source identity and roster context can enrich internal QA. Model-visible use should stay behind a separate approval gate. |

## No Model-Visible Exposure

Search confirmed:

- Normal Pigskin tool declarations still come from `get_pigskin_context_tool_declarations`.
- `get_historical_pigskin_packet_context` remains absent from the default Pigskin tool set.
- `pigskin_packet_guardrails.get_historical_packet_tool_declarations()` still returns no declarations unless explicitly enabled.
- Prompt tests still assert the unavailable historical packet tool is not advertised.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` is unset in the local process, production, and staging.

## Warehouse Read-Only State

Targeted row confirmations:

| Object | Row count |
| --- | ---: |
| `pigskin_player_context_packet_current` | 4,084 |
| `compat_pigskin_player_context_current` | 4,084 |
| `pigskin_player_context_packet_current` 2025 rows | 510 |
| `pigskin_player_context_packet_current` 2026+ rows | 0 |
| `player_identity_bridge` | 11,212 |
| `dim_players_current` | 11,212 |
| `sleeper_players_current` | 4,254 |
| `sleeper_roster_players` | 636 |
| `sleeper_available_players` | 3,032 |

No warehouse state changed.

## Service Untouched Confirmation

Read-only Cloud Run describes:

| Service | Revision | Traffic | Image | Relevant flags |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | 100% | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | historical packet tool unset, job triggers false, local subprocess false, score flags false, Trade History compat false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | 100% | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | historical packet tool unset, job triggers false, local subprocess false |

Production and staging were not deployed.

## Tests And Checks

Baseline and final checks:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| `python -m compileall -q src scripts` | pass |
| `python -m unittest tests.test_pigskin_identity_bridge` | 25 tests pass |
| `python -m unittest tests.test_pigskin_context_qa` | 18 tests pass |
| `python -m unittest tests.test_pigskin_current_roster_lookup` | 21 tests pass after Phase 30.17 changes |
| `python -m unittest tests.test_pigskin_current_roster_merge` | 16 tests pass |
| `python -m unittest tests.test_pigskin_packet_retrieval` | 12 tests pass |
| `python -m unittest tests.test_pigskin_packet_tool_guardrails` | 12 tests pass |
| `python -m unittest discover tests` | 591 tests pass |
| `scripts/run_bigquery_migrations.py --list-pending` | no pending migrations |
| `scripts/run_bigquery_validations.py --dry-run` | catalog discovered through validation 200 |

Validation policy used: targeted tests and bounded read-only BigQuery smoke queries, plus one full suite at the end. Broad validation patterns were not run because this phase did not change warehouse SQL, materializers, packet SQL, or compatibility views.

## Remaining Warnings

- Tyreek current team remains unknown in approved current roster sources.
- Compact-name inputs remain conservative and do not silently resolve.
- Historical packet evidence remains completed-season context only. It is not current roster status.
- The model-visible historical packet tool still needs an explicit owner exposure decision before any staging or production registration.
- The historical validation backlog remains untracked for owner review.

## Recommended Next Phase

Recommended next phase: Owner exposure decision for model-visible historical packet tool.

Other valid follow-ups:

- Staging-only exposure test for historical packet tool, only with explicit owner approval.
- Read-only QA UI for historical packet plus current roster context.
- Current-source remediation for Tyreek current-team status.
