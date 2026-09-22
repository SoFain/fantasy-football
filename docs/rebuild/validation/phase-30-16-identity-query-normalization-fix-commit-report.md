# Phase 30.16 - Identity Query Normalization Fix Commit Report

Final decision: IDENTITY QUERY NORMALIZATION FIX COMMITTED WITH WARNINGS

## Commit

Commit hash: `99c9d00`

Commit message:

`Add identity query normalization for GSIS IDs`

Committed files:

| File | Summary |
| --- | --- |
| `src/pigskin_identity_bridge.py` | Adds raw/prefixed GSIS internal-ID lookup variants using a parameterized BigQuery array. |
| `tests/test_pigskin_identity_bridge.py` | Adds focused tests for raw and prefixed GSIS IDs, exact `gsis_id` and `sleeper_player_id` paths, non-GSIS exact behavior, and `sleeper_player_id=1166` remaining Kirk Cousins. |
| `docs/rebuild/validation/phase-30-15-identity-query-normalization-fix-report.md` | Adds Phase 30.15 implementation and QA evidence. |

No generated artifacts, logs, caches, browser evidence, local output folders, temp JSON, secret files, env files, deployment artifacts, or unrelated historical validation backlog files were committed.

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

## Pre-Commit Review

The staged package contained only:

- `src/pigskin_identity_bridge.py`
- `tests/test_pigskin_identity_bridge.py`
- `docs/rebuild/validation/phase-30-15-identity-query-normalization-fix-report.md`

Staged checks:

| Check | Result |
| --- | --- |
| `git diff --cached --name-only` | exactly the three approved files |
| `git diff --cached --stat` | 3 files changed, 382 insertions, 6 deletions |
| `git diff --cached --check` | pass after removing one trailing blank line from the Phase 30.15 report |

## Implementation Summary

`src/pigskin_identity_bridge.py` now expands `player_id_internal` lookup variants only for GSIS-shaped identifiers:

- Raw `00-\d+` becomes `[raw, gsis:raw]`.
- Already-prefixed `gsis:00-...` becomes `[prefixed, raw]`.
- Non-GSIS internal IDs stay exact only.

The query now uses:

`player_id_internal IN UNNEST(@player_id_internal_variants)`

This keeps the lookup parameterized. It does not rewrite warehouse source data.

`gsis_id` remains a separate exact scalar path. `sleeper_player_id` remains a separate exact scalar path.

The response includes `player_id_internal_lookup_variants` in the request summary and adds a warning when raw/prefixed GSIS matching was used.

## Query-Normalization Behavior

| Input | Behavior |
| --- | --- |
| `player_id_internal=00-0033040` | Searches `00-0033040` and `gsis:00-0033040`. |
| `player_id_internal=gsis:00-0033040` | Searches `gsis:00-0033040` and `00-0033040`. |
| `player_id_internal=00-0033873` | Searches `00-0033873` and `gsis:00-0033873`. |
| `player_id_internal=gsis:00-0033873` | Searches `gsis:00-0033873` and `00-0033873`. |
| `player_id_internal=source:abc123` | Searches exact value only. |
| `gsis_id=00-0033040` | Exact `gsis_id` path only. |
| `sleeper_player_id=1166` | Exact Sleeper path only. |

## Identity Behavior After Fix

Read-only smoke QA from Phase 30.15 confirmed:

| Case | Result |
| --- | --- |
| Raw Tyreek internal ID `00-0033040` | Resolves Tyreek Hill through `gsis:00-0033040`; current team remains unknown in approved current roster sources. |
| Prefixed Tyreek internal ID `gsis:00-0033040` | Still resolves Tyreek Hill. |
| Tyreek `gsis_id=00-0033040` | Still resolves through the separate exact GSIS path. |
| Tyreek `sleeper_player_id=3321` | Resolves Tyreek Hill; current team remains unknown in approved current roster sources. |
| Tyreek full-name lookup | Still ambiguous with the T.Hill candidate family. |
| `sleeper_player_id=1166` | Still resolves Kirk Cousins, not Tyreek Hill. |
| Raw Mahomes internal ID `00-0033873` | Resolves Patrick Mahomes through `gsis:00-0033873`. |
| Prefixed Mahomes internal ID `gsis:00-0033873` | Still resolves Patrick Mahomes. |
| Mahomes `gsis_id=00-0033873` | Still resolves through the separate exact GSIS path. |
| Mahomes `sleeper_player_id=4046` | Resolves Patrick Mahomes. |

Compact-name ambiguity remains conservative. Historical packet team is not used as current roster status.

## No Model-Visible Exposure

No model-visible identity bridge or historical packet tool exposure was added.

Confirmed by code/test review:

- `resolve_player_identity` remains internal.
- `get_historical_pigskin_packet_context` remains default-disabled.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` remains absent/unset in staging and production.
- Pigskin tool declaration tests still assert `execute_bigquery_sql` is absent.
- Prompt tests still avoid instructing Pigskin to call unavailable historical packet tools.

## Source Inventory Summary

The identity bridge query still reads only approved sources:

- `player_identity_bridge`
- `dim_players_current`
- `sleeper_players_current`
- `sleeper_roster_players`, only under league scope
- `sleeper_available_players`, only under league and availability scope

It does not read raw nflverse tables, staging tables, `weekly_metrics`, `compat_viewer_team_context`, or the historical packet compatibility view as identity authority.

## Tests and Checks

Pre-commit checks passed:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| Targeted `py_compile` | pass |
| `compileall -q src scripts` | pass |
| `tests.test_pigskin_identity_bridge` | 25 tests passed |
| `tests.test_pigskin_context_qa` | 18 tests passed |
| `tests.test_pigskin_current_roster_lookup` | 18 tests passed |
| `tests.test_pigskin_current_roster_merge` | 16 tests passed |
| `tests.test_pigskin_packet_retrieval` | 12 tests passed |
| `tests.test_pigskin_packet_tool_guardrails` | 12 tests passed |
| `unittest discover tests` | 588 tests passed |
| `run_bigquery_migrations.py --list-pending` | no pending migrations |
| `run_bigquery_validations.py --dry-run` | catalog discovered through validation 200 |

## Warehouse Read-Only State

Read-only row counts:

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
| `sleeper_viewer_team_snapshots` | 3 |
| `compat_viewer_team_context` | 10 |
| Season-scoped raw nflverse 2026+ total | 0 |
| Staging 2026+ total | 0 |
| `analytics_pigskin_rankings` 2026+ rows | 285 |

The `analytics_pigskin_rankings` 2026+ rows are the known unrelated rankings mart warning and are not packet exposure data.

No BigQuery data was written.

## Validation Results

Read-only validation runs:

| Pattern | Result |
| --- | --- |
| `raw_nflverse` | 3 passed, 0 failed. Informational coverage warning remains. |
| `stg_` | 7 passed, 0 failed. |
| `advanced_metrics` | 4 passed, 0 failed. |
| `compat_pigskin` | 2 passed, 0 failed. |
| `trade_player_scores` | 12 passed, 0 failed. |
| `trade_pick_scores` | 17 passed, 0 failed. Informational model-version coverage warning remains. |

Known informational warnings:

- `181_raw_nflverse_season_week_coverage.sql`: first row `raw_nflverse_pbp`, `row_count=580005`, `min_season=2014`, `max_season=2025`, `season_week_count=257`.
- `178_trade_pick_scores_model_version_coverage.sql`: `trade_pick_score_v0_2026_001`, `score_rows=64`, `score_run_count=64`, `first_created_at=2026-06-28T18:10:29.515354Z`, `latest_created_at=2026-06-28T18:10:29.515354Z`.

## Service Untouched Confirmation

Read-only Cloud Run describes:

| Service | Revision | Image | Traffic | Relevant flags |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | 100% to current revision | `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset, job triggers false, local subprocess false, score flags false, Trade History compat false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | 100% to current revision | `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset, job triggers false, local subprocess false |

No deployment occurred.

## Files Excluded

Excluded intentionally:

- Phase 17 through Phase 30 historical validation backlog reports not explicitly approved for this commit.
- `docs/rebuild/validation/phase-30-14-identity-source-remediation-report.md`, left untracked with the broader backlog.
- Logs, caches, browser evidence, local output folders, temporary JSON, secret files, env files, and deployment artifacts.

Post-commit status contains only untracked validation backlog and owner-review artifacts.

## Remaining Warnings

- Tyreek current team remains unknown in approved current roster sources for current-source lookups.
- Tyreek full-name lookup remains ambiguous because compact expansion intentionally keeps the T.Hill family conservative.
- `analytics_pigskin_rankings` has unrelated 2026+ rows. This is not packet exposure data.
- Git printed line-ending warnings for touched files. No functional issue was observed.

## Recommended Next Phase

Recommended next phase: Phase 30.17 - Current-source review for Tyreek current-team status.

Other valid follow-ups:

- Phase 30.17 - Owner exposure decision for model-visible historical packet tool.
- Phase 30.17 - Staging-only exposure test for historical packet tool, only with explicit owner approval.
- Phase 30.17 - Package historical validation backlog cleanup.
