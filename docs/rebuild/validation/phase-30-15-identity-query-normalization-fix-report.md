# Phase 30.15 - Identity Query Normalization Fix

Final decision: IDENTITY QUERY NORMALIZATION FIX READY WITH WARNINGS

## Scope

This phase implemented the safe code-only query-normalization fix identified in Phase 30.14.

No BigQuery rows were written. No identity materialization, Sleeper ingestion, Sleeper materialization, live Sleeper API call, raw backfill, prepare-only run, nflreadpy loader, staging materialization, advanced metrics materialization, Pigskin packet refresh, Pigskin call, LLM call, ranking run, Cloud Run job trigger, Scheduler job, scrape, Firebase artifact, deployment, stage, or commit occurred.

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

## Git State

Latest commit at start:

`a55dd13 Add Pigskin identity bridge diagnostics`

Tracked changes after this phase:

| File | Status |
| --- | --- |
| `src/pigskin_identity_bridge.py` | modified |
| `tests/test_pigskin_identity_bridge.py` | modified |
| `docs/rebuild/validation/phase-30-15-identity-query-normalization-fix-report.md` | new |

Unrelated historical validation backlog remains untracked. No files were staged or committed.

## Baseline Checks

Baseline checks passed before code changes:

| Check | Result |
| --- | --- |
| `scripts/check_deployment_safety.py` | pass |
| Targeted `py_compile` for Pigskin identity/context modules and `app.py` | pass |
| `compileall -q src scripts` | pass |
| `tests.test_pigskin_identity_bridge` | 20 tests passed |
| `tests.test_pigskin_context_qa` | 18 tests passed |
| `tests.test_pigskin_current_roster_lookup` | 18 tests passed |
| `tests.test_pigskin_current_roster_merge` | 16 tests passed |
| `tests.test_pigskin_packet_retrieval` | 12 tests passed |
| `tests.test_pigskin_packet_tool_guardrails` | 12 tests passed |
| `unittest discover tests` | 583 tests passed |
| `run_bigquery_migrations.py --list-pending` | no pending migrations |
| `run_bigquery_validations.py --dry-run` | catalog discovered through validation 200 |

## Code Changes Made

### `src/pigskin_identity_bridge.py`

Added a bounded helper:

`_player_id_internal_lookup_variants(player_id_internal)`

Behavior:

- Empty input returns an empty array.
- Raw GSIS-like internal IDs matching `00-\d+` expand to `[raw, gsis:raw]`.
- Already-prefixed `gsis:00-...` inputs expand to `[prefixed, raw]`.
- Non-GSIS internal IDs keep exact lookup behavior and are not blindly prefixed.

Query behavior changed from:

`player_id_internal = @player_id_internal`

to:

`player_id_internal IN UNNEST(@player_id_internal_variants)`

using a BigQuery array parameter.

`gsis_id` remains a separate exact scalar parameter. `sleeper_player_id` remains a separate exact scalar parameter. No source data is rewritten or coerced.

The response now includes request-level `player_id_internal_lookup_variants` and a warning when raw/prefixed GSIS lookup variants were used for read-only matching.

### `tests/test_pigskin_identity_bridge.py`

Added tests covering:

- Raw Tyreek internal ID `00-0033040` includes `gsis:00-0033040`.
- Raw Mahomes internal ID `00-0033873` includes `gsis:00-0033873`.
- Already-prefixed Tyreek and Mahomes IDs still include the exact prefixed value.
- Non-GSIS internal IDs are not prefixed.
- `sleeper_player_id` and `gsis_id` paths keep empty internal-ID variants.
- `sleeper_player_id=1166` remains Kirk Cousins and is not remapped to Tyreek.
- Raw GSIS-like lookup reports variants and a normalization warning.

## Query-Normalization Behavior

| Input | Lookup variants | Expected behavior |
| --- | --- | --- |
| `player_id_internal=00-0033040` | `00-0033040`, `gsis:00-0033040` | resolves Tyreek if prefixed warehouse row exists |
| `player_id_internal=gsis:00-0033040` | `gsis:00-0033040`, `00-0033040` | still resolves Tyreek |
| `player_id_internal=00-0033873` | `00-0033873`, `gsis:00-0033873` | resolves Mahomes if prefixed warehouse row exists |
| `player_id_internal=gsis:00-0033873` | `gsis:00-0033873`, `00-0033873` | still resolves Mahomes |
| `player_id_internal=source:abc123` | `source:abc123` | exact only |
| `gsis_id=00-0033040` | none | exact `gsis_id` path |
| `sleeper_player_id=1166` | none | exact Sleeper path |

## Read-Only Smoke QA

Smoke checks used `src.pigskin_identity_bridge.resolve_player_identity` only. They did not write data.

| Case | Status | Result |
| --- | --- | --- |
| `player_id_internal=00-0033040` | ok | Tyreek Hill, `player_id_internal=gsis:00-0033040`, `gsis_id=00-0033040`, `sleeper_player_id=3321`; normalization warning present; current team unknown in approved current roster sources. |
| `player_id_internal=gsis:00-0033040` | ok | Tyreek Hill; exact prefixed ID still works; normalization warning present. |
| `gsis_id=00-0033040` | ok | Tyreek Hill through separate GSIS path; no internal-ID variant warning. |
| `player_name=Tyreek Hill`, limit 10 | ambiguous | Candidates remain Tyreek Hill, Taysom Hill, Trey Hill, Tony Hill. Conservative ambiguity preserved. |
| `compact_name=T.Hill`, limit 10 | ambiguous | Same conservative T.Hill candidate family. |
| `sleeper_player_id=1166` | ok | Kirk Cousins, `player_id_internal=gsis:00-0029604`, `gsis_id=00-0029604`, `sleeper_player_id=1166`, current team LV. |
| `sleeper_player_id=3321` | ok | Tyreek Hill, current team unknown in approved current roster sources. |
| `player_id_internal=00-0033873` | ok | Patrick Mahomes, `player_id_internal=gsis:00-0033873`, `gsis_id=00-0033873`, `sleeper_player_id=4046`; normalization warning present. |
| `player_id_internal=gsis:00-0033873` | ok | Patrick Mahomes; exact prefixed ID still works. |
| `gsis_id=00-0033873` | ok | Patrick Mahomes through separate GSIS path. |
| `sleeper_player_id=4046` | ok | Patrick Mahomes through separate Sleeper path. |
| `player_name=Patrick Mahomes`, limit 10 | ok | Patrick Mahomes resolves by name. |

## Preserved Safety Rules

- `sleeper_player_id=1166` was not remapped to Tyreek. It still resolves to Kirk Cousins.
- `gsis_id` matching remains exact and separate.
- `sleeper_player_id` matching remains exact and separate.
- Compact-name ambiguity remains conservative.
- Historical packet team is not used as current roster status.
- Current-team status still comes only from approved current roster or identity sources.
- No arbitrary SQL input is accepted.
- No model-visible identity bridge tool was registered.

## No Model-Visible Exposure

Search confirmed:

- `resolve_player_identity` remains internal.
- No identity bridge helper is registered as a Pigskin tool.
- No lookup-plus-merge QA helper is registered as a Pigskin tool.
- `get_historical_pigskin_packet_context` remains default-disabled.
- Prompt tests still assert the unavailable historical packet tool is not advertised.
- Pigskin tool declaration tests still assert `execute_bigquery_sql` is absent.

## No-State-Change Confirmation

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

Raw/staging checks:

- Season-scoped `raw_nflverse_*` tables checked for `season >= 2026`: all returned 0 rows.
- Staging tables checked for `season >= 2026`: all returned 0 rows.
- `analytics_pigskin_rankings` has 285 rows for `season >= 2026`. This is the known unrelated rankings mart warning and is not packet exposure data.

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

## Final Local Checks

Final checks passed:

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

## Staging and Production Untouched

Read-only Cloud Run describes:

| Service | Revision | Image | Traffic | Relevant flags |
| --- | --- | --- | --- | --- |
| `nfl-studio-dashboard` | `nfl-studio-dashboard-00077-2jp` | `sha256:5b4bf9a2fcf6285bb5aa04b7e34b3ced67a366202b29451a81b981ee19a0816f` | 100% to current revision | `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset, job triggers false, local subprocess false, score flags false, Trade History compat false |
| `nfl-studio-dashboard-staging` | `nfl-studio-dashboard-staging-00029-jtb` | `sha256:3a661d2c5137be774c5f206cffb0262e16b55a0832d4741b8eb1edeb7574d7d8` | 100% to current revision | `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` unset, job triggers false, local subprocess false |

No deployment occurred.

## Remaining Warnings

- Tyreek current team remains unknown in approved current roster sources for current-source lookups. The bridge surfaces that warning and does not infer current team from historical packet team.
- Tyreek full-name lookup remains ambiguous because compact expansion intentionally keeps the T.Hill family conservative.
- `analytics_pigskin_rankings` still has unrelated 2026+ rows. This is not packet exposure data.
- Git printed line-ending warnings for touched files. No functional issue was observed.

## Recommended Next Phase

Phase 30.16 - Package and commit identity query-normalization fix.

Optional later work, separate from packaging:

- Current-source review for Tyreek current-team status.
- Owner exposure decision for model-visible historical packet tool.
- Staging-only exposure test for historical packet tool, only after explicit owner approval.
