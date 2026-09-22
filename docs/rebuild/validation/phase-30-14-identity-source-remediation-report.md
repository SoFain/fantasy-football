# Phase 30.14 - Identity Source Remediation for Tyreek/Mahomes Stable-ID Gaps

Final decision: IDENTITY SOURCE REMEDIATION NEEDS QUERY NORMALIZATION

## Scope

This phase was read-only: warehouse audit, code/test review, identity smoke QA, validation, and remediation planning.

No BigQuery rows were written. No identity materialization, Sleeper refresh, nflverse backfill, staging materialization, advanced metrics materialization, Pigskin packet refresh, rankings run, Cloud Run job trigger, deployment, Pigskin prompt, LLM call, scrape, Firebase artifact, stage, or commit occurred.

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

Latest commit:

`a55dd13 Add Pigskin identity bridge diagnostics`

Tracked files had no modifications at the start of this phase. No files were staged. The historical Phase 17 through Phase 30 validation backlog remains untracked for owner review.

This report is the only file created by this phase.

## Baseline Checks

Baseline checks passed before the audit:

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

## Identity Build and Code Audit

Files inspected:

| File | Finding |
| --- | --- |
| `src/build_player_identity.py` | `_stable_internal_id()` creates prefixed internal IDs. GSIS source rows become `gsis:<gsis_id>`, for example `gsis:00-0033040`. |
| `bigquery/migrations/0005__player_identity_bridge.sql` | `player_id_internal`, `gsis_id`, and `sleeper_player_id` are separate columns. No alternate raw internal ID column exists. |
| `src/pigskin_identity_bridge.py` | `build_identity_bridge_query()` compares `player_id_internal = @player_id_internal` exactly. It does not try `gsis:<raw id>` when a raw GSIS-like ID is supplied as `player_id_internal`. |
| `tests/test_pigskin_identity_bridge.py` | Tests cover parameterization, stable-ID mismatch diagnostics, compact ambiguity, and no Pigskin tool registration. They do not yet cover raw-vs-prefixed GSIS internal ID variants. |

Root-cause classification:

The Tyreek and Mahomes exact `player_id_internal=00-...` failures are query-normalization failures, not missing identity rows. The warehouse stores their internal IDs as `gsis:00-...`. Direct `gsis_id=00-...` lookups work. Direct `player_id_internal=gsis:00-...` lookups work. Direct raw `player_id_internal=00-...` lookups do not.

## Read-Only Identity Diagnostics

All diagnostics used read-only BigQuery queries with neutral aliases such as `matched_row_count` and `row_count`.

| Case | Result |
| --- | --- |
| Tyreek Hill full-name lookup | Found in `player_identity_bridge`, `dim_players_current`, `sleeper_players_current`, and `sleeper_available_players`. Stable IDs: `player_id_internal=gsis:00-0033040`, `gsis_id=00-0033040`, `sleeper_player_id=3321`. |
| Tyreek compact lookup `T.Hill` | Direct source-table compact expression returned no exact rows, but resolver compact expansion returns an ambiguous candidate set. |
| Tyreek `player_id_internal=00-0033040` | 0 matches. |
| Tyreek `player_id_internal=gsis:00-0033040` | 1 match in `player_identity_bridge`, 1 match in `dim_players_current`. |
| Tyreek `gsis_id=00-0033040` | Found in identity, dim, Sleeper global current, and available-player sources. |
| `sleeper_player_id=1166` | Resolves to Kirk Cousins in `player_identity_bridge`, `dim_players_current`, `sleeper_players_current`, and `sleeper_available_players`. Stable IDs: `player_id_internal=gsis:00-0029604`, `gsis_id=00-0029604`, `sleeper_player_id=1166`. |
| Patrick Mahomes full-name lookup | Found in identity, dim, Sleeper global current, and rostered-player sources. Stable IDs: `player_id_internal=gsis:00-0033873`, `gsis_id=00-0033873`, `sleeper_player_id=4046`. |
| Mahomes `player_id_internal=00-0033873` | 0 matches. |
| Mahomes `player_id_internal=gsis:00-0033873` | 1 match in `player_identity_bridge`, 1 match in `dim_players_current`. |
| Mahomes `gsis_id=00-0033873` | Found in identity, dim, Sleeper global current, and rostered-player sources. |

Selected source details:

| Player | Source | player_id_internal | gsis_id | sleeper_player_id | current team/status | source as-of |
| --- | --- | --- | --- | --- | --- | --- |
| Tyreek Hill | `player_identity_bridge` | `gsis:00-0033040` | `00-0033040` | `3321` | MIA, Active | 2026-06-16T05:47:32.145903Z |
| Tyreek Hill | `sleeper_players_current` | null | `00-0033040` | `3321` | null, Active | 2026-06-15T19:14:53.601698Z |
| Kirk Cousins | `sleeper_players_current` | null | `00-0029604` | `1166` | LV, Active | 2026-06-15T19:14:53.601698Z |
| Patrick Mahomes | `player_identity_bridge` | `gsis:00-0033873` | `00-0033873` | `4046` | KC, Active | 2026-06-16T05:47:32.145903Z |
| Patrick Mahomes | `sleeper_players_current` | null | `00-0033873` | `4046` | KC, Active | 2026-06-15T19:14:53.601698Z |

## Resolver Smoke QA

| Input | Resolver status | Notes |
| --- | --- | --- |
| `player_name=Tyreek Hill`, limit 10 | `ambiguous` | Candidate names: Tyreek Hill, Taysom Hill, Trey Hill, Tony Hill. This is conservative but over-broad for exact full-name input. |
| `compact_name=T.Hill`, limit 10 | `ambiguous` | Same candidate family as expected. |
| `player_id_internal=00-0033040` | `not_found` | Raw internal ID does not normalize to `gsis:00-0033040`. |
| `player_id_internal=gsis:00-0033040` | `ok` | Resolves Tyreek Hill. Current roster source reports missing current team. |
| `gsis_id=00-0033040` | `ok` | Resolves Tyreek Hill. Current roster source reports missing current team. |
| `sleeper_player_id=1166` | `ok` | Resolves Kirk Cousins. This is current-source evidence, not a hardcoded correction target. |
| `player_name=Patrick Mahomes`, limit 10 | `ok` | Resolves Patrick Mahomes. |
| `player_id_internal=00-0033873` | `not_found` | Raw internal ID does not normalize to `gsis:00-0033873`. |
| `player_id_internal=gsis:00-0033873` | `ok` | Resolves Patrick Mahomes. |
| `gsis_id=00-0033873` | `ok` | Resolves Patrick Mahomes. |

## Tyreek Current-Source Discrepancy

Findings:

- `sleeper_player_id=1166` is Kirk Cousins in approved current-source tables.
- Tyreek Hill is `sleeper_player_id=3321` in `sleeper_players_current`, `player_identity_bridge`, and `dim_players_current`.
- Tyreek Hill appears under `gsis_id=00-0033040` and `player_id_internal=gsis:00-0033040`.
- `sleeper_players_current` reports Tyreek as active but with missing current team. `sleeper_available_players` also contains Tyreek with missing current team.
- The bridge/dim rows carry `current_team=MIA`, sourced from broader identity inputs. The resolver correctly surfaces a warning when approved current roster sources do not provide current team.

Likely remediation:

Do not remap `1166` to Tyreek. The safe next action is query normalization for raw `00-...` inputs plus owner/source review for whether Tyreek current-team status should remain unknown from current roster sources.

## Mahomes Current-Source Gap

Findings:

- Patrick Mahomes appears by name in `player_identity_bridge`, `dim_players_current`, `sleeper_players_current`, and `sleeper_roster_players`.
- His stored internal ID is `gsis:00-0033873`.
- Raw `player_id_internal=00-0033873` misses only because exact internal-ID comparison does not normalize raw GSIS-like values.
- `gsis_id=00-0033873` and `player_id_internal=gsis:00-0033873` both resolve.

Likely remediation:

Query normalization only. No source correction or identity materialization is needed for Mahomes based on this audit.

## Code Change Decision

No code changes were made in this phase.

Reason: this phase was explicitly read-only and the root cause is now well-classified. A safe code-only fix is appropriate, but it should be handled in a separate Phase 30.15 so tests can be added and reviewed without mixing diagnosis and remediation.

Recommended Phase 30.15 implementation:

- Accept raw GSIS-like `player_id_internal` values and search both raw and `gsis:<raw>` variants.
- Continue exact matching for already-prefixed internal IDs.
- Preserve `gsis_id` matching as a separate stable-ID path.
- Add tests for Tyreek and Mahomes raw/prefixed variants.
- Keep `sleeper_player_id=1166` resolving to Kirk Cousins unless source data changes through an authorized current-source workflow.
- Preserve compact-name ambiguity behavior. If full-name exact lookup should be less ambiguous, add a separate ranking rule that prioritizes exact full-name matches without silently selecting compact-only ambiguity.

## Remediation Options

### Option A - Query normalization only

Add raw/prefixed GSIS lookup variants in `src/pigskin_identity_bridge.py`.

Benefits:

- Fixes Tyreek and Mahomes raw internal-ID misses without source writes.
- Keeps historical packet IDs from being treated as current-team evidence.
- Can happen before model-visible exposure.

Risks:

- Must not silently coerce unrelated non-GSIS internal IDs.
- Must keep ambiguous name lookups conservative.

Required gates:

- None, if implemented as code/test only.

Tests required:

- Raw `00-0033040` resolves through `gsis:00-0033040`.
- Raw `00-0033873` resolves through `gsis:00-0033873`.
- Already-prefixed IDs still work.
- `sleeper_player_id=1166` remains Kirk Cousins.
- No Pigskin tool registration is added.

Recommendation: use this as Phase 30.15.

### Option B - Identity bridge materialization fix

Adjust the future identity build to populate alternate stable-ID helper fields or a normalized lookup column.

Benefits:

- Makes ID lookup intent explicit in the warehouse.
- Reduces query-side complexity over time.

Risks:

- Requires authorized write/materialization.
- Could accidentally broaden identity joins if not bounded.

Required gates:

- Future identity materialization/write authorization, not set in this phase.

Tests required:

- Bridge grain validation.
- Raw/prefixed ID coverage.
- No current-team inference from historical packet team.

Recommendation: defer unless query normalization is insufficient.

### Option C - Current Sleeper snapshot/source refresh

Refresh approved current roster/source snapshots if the owner wants current-team evidence updated.

Benefits:

- Could resolve Tyreek current-team unknown status if current source now carries team data.

Risks:

- External data refresh is outside this phase.
- Refresh must not rewrite source evidence without authorization.

Required gates:

- Future current-source refresh authorization.

Tests required:

- Snapshot row-count checks.
- Identity conflict checks.
- Current-team provenance checks.

Recommendation: separate owner-approved phase only. Do not use it to rewrite `1166`.

### Option D - Manual review/owner-confirmed correction

Use an owner-approved correction workflow only if source data is internally contradictory after refresh or query normalization.

Benefits:

- Keeps corrections explicit and auditable.

Risks:

- Manual overrides can hide source drift if used too early.

Required gates:

- Owner correction approval and future write authorization.

Tests required:

- Override precedence tests.
- Conflict diagnostics.
- Reversibility documentation.

Recommendation: not needed for Mahomes. Only consider for Tyreek current-team/source status after a separate current-source review.

## No Model-Visible Exposure

Search confirmed:

- `resolve_player_identity` is not registered as a Pigskin tool.
- Lookup-plus-merge QA helpers are not registered as Pigskin tools.
- `get_historical_pigskin_packet_context` remains default-disabled.
- `USE_PIGSKIN_HISTORICAL_PACKET_TOOL` is unset in both staging and production.
- Pigskin tool declaration tests still assert that `execute_bigquery_sql` is absent.

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

Raw/staging 2026+ checks:

- All `raw_nflverse_*` tables with a season column returned 0 rows for `season >= 2026`.
- All staging tables `stg_game_context`, `stg_participation_context`, `stg_play_player_events`, `stg_player_identity`, `stg_player_week_stats`, and `stg_team_week_stats` returned 0 rows for `season >= 2026`.
- `analytics_pigskin_rankings` has 285 rows for `season >= 2026`. This is the known unrelated rankings mart warning and is not historical packet exposure data.

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
| `tests.test_pigskin_identity_bridge` | 20 tests passed |
| `tests.test_pigskin_context_qa` | 18 tests passed |
| `tests.test_pigskin_current_roster_lookup` | 18 tests passed |
| `tests.test_pigskin_current_roster_merge` | 16 tests passed |
| `tests.test_pigskin_packet_retrieval` | 12 tests passed |
| `tests.test_pigskin_packet_tool_guardrails` | 12 tests passed |
| `unittest discover tests` | 583 tests passed |
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

- Raw `player_id_internal=00-...` misses are expected until query normalization is implemented.
- Tyreek full-name lookup is ambiguous because compact expansion broadens the candidate family to T.Hill names.
- Tyreek current-team evidence differs by source role: identity/dim rows carry MIA, while approved Sleeper global current reports missing current team. The resolver surfaces this as a warning rather than inferring from historical context.
- `sleeper_player_id=1166` is Kirk Cousins in approved current-source data. Do not use it for Tyreek.
- `analytics_pigskin_rankings` has 2026+ rows, but this is not model-visible historical packet exposure.

## Recommended Next Phase

Phase 30.15 - Implement safe query-normalization fix.

Recommended scope:

- Code/test only.
- Add raw and `gsis:`-prefixed lookup variants for `player_id_internal`.
- Keep `gsis_id` and `sleeper_player_id` as separate exact identity paths.
- Add tests for Tyreek and Mahomes raw/prefixed variants.
- Add a test proving `sleeper_player_id=1166` still resolves to current-source Kirk Cousins.
- Preserve no model-visible Pigskin historical packet exposure.

