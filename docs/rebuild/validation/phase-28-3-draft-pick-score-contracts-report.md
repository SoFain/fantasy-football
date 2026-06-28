# Phase 28.3 Draft-Pick Score Contracts Report

Timestamp: 2026-06-28T03:31Z

## Final Decision

DRAFT PICK SCORE CONTRACTS READY WITH WARNINGS

The draft-pick score warehouse contract is ready for review. Migration `0026__trade_pick_score_v0.sql` remains pending by design. No migration was applied, no BigQuery rows were written, no deployment happened, and no authorization gates were set.

## Scope

Phase 28.3 added schema, contract, view, validation, and documentation scaffolding for the draft-pick score lane:

- `trade_pick_scores`
- `trade_pick_scores_current`
- `compat_trade_pick_scores_current`

This work is separate from `trade_player_scores`. Generic draft picks are not player rows and must not be materialized into the player-score lane.

## Files Created

| File | Purpose |
| --- | --- |
| `bigquery/migrations/0026__trade_pick_score_v0.sql` | Additive schema migration for draft-pick score table and current/compat views. |
| `bigquery/contracts/trade_pick_scores.md` | Output table contract. |
| `bigquery/contracts/trade_pick_scores_current.md` | Current view contract. |
| `bigquery/contracts/compat_trade_pick_scores_current.md` | Compatibility view contract for future safe read paths. |
| `bigquery/views/trade_pick_scores_current.sql` | Standalone current view definition. |
| `bigquery/views/compat_trade_pick_scores_current.sql` | Standalone compatibility view definition. |
| `bigquery/validations/161_trade_pick_scores_exists.sql` through `178_trade_pick_scores_model_version_coverage.sql` | Draft-pick score validation set. |
| `docs/rebuild/trade-pick-score-rollout.md` | Draft-pick score rollout plan. |
| `tests/test_trade_pick_score_contracts.py` | Local tests for migration, contracts, views, validations, and write-mode gating. |

## Files Updated

| File | Change |
| --- | --- |
| `docs/rebuild/table-classification.md` | Classified the draft-pick score objects as output/compat objects, not raw/source tables. |
| `docs/rebuild/compatibility-contracts.md` | Added the draft-pick score contracts to the compatibility contract index and rollout section. |

## Migration Summary

Migration: `0026__trade_pick_score_v0.sql`

The migration is additive only:

- Creates `trade_pick_scores` if it does not exist.
- Creates or replaces `trade_pick_scores_current`.
- Creates or replaces `compat_trade_pick_scores_current`.
- Does not alter, insert into, merge into, or backfill `trade_player_scores`.
- Does not include destructive `DROP`, `DELETE`, or `TRUNCATE` operations.

Recommended grain for `trade_pick_scores`:

- `model_version`
- `source_pick_key`
- `pick_year`
- `pick_class`
- `pick_round`
- `pick_slot`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

`trade_pick_scores_current` chooses one latest row per pick/context using `created_at`, `model_version`, and `score_run_id`.

## Contract Summary

The contracts define a draft-pick score lane with these boundaries:

- Draft picks are not player rows.
- Exact-slot and round-only picks are both supported.
- Round-only rows keep uncertainty explicit through `pick_class`, null slot fields, confidence, and missing flags.
- College context is neutral and unavailable in v0 unless a future audited source is approved.
- The compatibility view reads only from `trade_pick_scores_current`.
- Raw/source tables such as `draft_picks`, `college_player_stats`, and `rookie_scouting_metrics` are not exposed through the compatibility view.
- Production feature exposure remains default-off.

## View Summary

`trade_pick_scores_current` reads from `trade_pick_scores` and returns the latest row per pick/profile/context.

`compat_trade_pick_scores_current` reads from `trade_pick_scores_current` only. It exposes pick identity, market value, component scores, confidence, missing flags, freshness, model version, and created timestamp. It does not expose player columns such as `player_id`, `player_name`, `position`, or `team`.

## Validation Summary

Added validations cover:

- Object existence.
- Grain uniqueness.
- Score ranges.
- Component score ranges.
- Confidence range.
- Required pick identity fields.
- Exact-slot field requirements.
- Round-only uncertainty requirements.
- Source freshness JSON presence.
- Missing flags JSON presence.
- Component JSON presence.
- Current view grain.
- Compatibility view existence.
- Compatibility view raw/source dependency guard.
- Player-score lane separation.
- No player columns on pick-score objects.
- Parseability warning coverage.
- Model version coverage.

Validation discovery now includes `161` through `178`.

## Dry-Run Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.trade_pick_scores --model-version trade_pick_score_v0_2026_001 --dry-run
```

Result:

- `wrote`: false
- source pick asset rows: 192
- parsed pick rows: 192
- unparsed pick rows: 0
- exact-slot rows: 144
- round-only rows: 48
- rows by pick year: 2026=156, 2027=12, 2028=12, 2029=12
- rows by scoring profile: half_ppr=64, ppr=64, standard=64
- pick score range: min=18.0143, max=96.7, avg=43.6848, stddev=13.8831
- confidence range: min=62.0, max=88.0, avg=83.0, stddev=8.9443
- tier distribution: elite=3, solid=21, speculative=48, deep=96, avoid=24
- top pick example: `2026 Pick 1.01`, score 96.7, confidence 88.0, tier `elite`

Expected warning flags:

- `college_context_unavailable`: 192
- `draft_outcome_prior_insufficient`: 192
- `pick_market_source_only`: 192
- `pick_score_staging_only`: 192
- `pick_round_only_uncertainty`: 48
- `pick_future_year_discount`: 36

No write path was executed.

## Checks Run

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_score_contracts` | Pass, 6 tests. |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_pick_scores` | Pass, 13 tests. |
| `.\venv\Scripts\python.exe -m unittest discover tests` | Pass, 386 tests. |
| `.\venv\Scripts\python.exe -m py_compile src\trade_pick_scores.py` | Pass. |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | Pass. |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | Pass. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run` | Pass. Discovered migrations through 0026. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | Pass. Pending migration: 0026 only. |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | Pass. Discovered validations through 178. |

## Migration Apply Status

Migration `0026__trade_pick_score_v0.sql` was not applied. This is expected for Phase 28.3.

## Safety Confirmation

- No production deployment.
- No staging deployment.
- No BigQuery write.
- No score materialization.
- No ingestion.
- No Cloud Run Job trigger.
- No Scheduler job.
- No LLM action.
- No Pigskin prompt.
- No scraping or external data fetch.
- No Firebase artifact.
- No authorization gates set.
- No production feature flags changed.

## Warnings

- Migration `0026` is pending until a future explicitly authorized phase applies it.
- The new validation SQL is discovered but cannot fully pass in live mode until the migration is applied.
- Draft-pick score materialization remains dry-run only. The write path is still fail-closed.
- College context remains neutral and unavailable in v0.

## Recommended Next Phase

Run a migration-apply phase only if explicitly authorized. After `0026` is applied, verify the three objects exist, then run the pick-score validations. Materialize pick-score rows only in a separate bounded staging phase with an explicit write authorization gate.
