# Phase 23.1A Trade Score Accuracy Audit Report

Date: 2026-06-17

## Executive Decision

`ACCURACY AUDIT PASS`

The Trade Analyzer score v0 package is internally consistent after the Phase 23.1B fixes. The documented formula, deterministic builder, BigQuery contract, validation SQL, compatibility view, and Streamlit feature gating now agree on field names, score ranges, and default-off rollout behavior.

No deployment, migration apply, score write, materialization, ingestion, Cloud Run Job trigger, Scheduler job, LLM call, scrape, Firebase artifact creation, feature flag change, or commit was performed.

## Summary

| Category | Status | Result |
| --- | --- | --- |
| Formula accuracy | pass | The implemented weighted formula matches the v0 spec. |
| Risk scale accuracy | pass | `normalized_risk_score` is consistently documented, calculated, and validated as `0.00` to `1.00`. |
| Contract and migration accuracy | pass | Builder output fields match the migration table columns exactly. |
| View accuracy | pass | Current and compatibility views read score outputs only and expose the expected safe fields. |
| Validation SQL accuracy | pass | Trade score, component, confidence, JSON, grain, identity, and compatibility checks are present. |
| Feature flag accuracy | pass | Both Trade Analyzer score flags default false and score UI requires both true. |
| Builder safety and idempotency | pass with note | Dry-run is non-mutating, writes require `--write`, and the MERGE grain is explicit. The builder reads curated marts directly, which is acceptable for this materializer but not for UI or Pigskin-visible paths. |
| UI accuracy | pass | Legacy Trade Lab behavior remains available; score UI reads only the compatibility score view when both flags are true. |
| Test coverage | pass | Formula, clamps, missing flags, dry-run, write guard, flags, UI fallback, and risk validation SQL are covered. |
| Safety checks | pass | Local safety, compile, test, migration dry-run, list-pending, and validation discovery passed. |

## Findings

### Critical Blockers

None.

### Fixed Accuracy Issues

#### 1. `normalized_risk_score` range is now consistent

Decision impact: cleared.

Evidence:

| File | Evidence |
| --- | --- |
| `docs/rebuild/trade-analyzer-scoring-model-v0.md` | Defines `normalized_risk_score` as `0.00` to `1.00` and uses `risk_adjustment = -10 * normalized_risk_score`. |
| `src/trade_player_scores.py` | Clamps `normalized_risk_score` to `0.0` through `1.0` before applying the risk adjustment. |
| `bigquery/contracts/trade_player_scores.md` | Documents `normalized_risk_score` as the score component exception using `0.00` to `1.00`. |
| `bigquery/validations/152_trade_player_scores_component_score_range.sql` | Rejects `normalized_risk_score > 1` and no longer allows values through `100`. |
| `tests/test_trade_player_scores.py` | Includes a regression test that asserts validation `152` checks `normalized_risk_score > 1` and does not check `> 100`. |

#### 2. Legacy proposed contract names are removed from the score spec

Decision impact: cleared.

The score spec now uses implementation names that match the migration and builder:

| Current field | Status |
| --- | --- |
| `model_version` | matches migration and builder |
| `player_id` | matches migration and builder |
| `normalized_risk_score` | matches migration and builder |
| `missing_flags_json` | matches migration and builder |
| `component_json` | matches migration and builder |

The only remaining `player_id_internal` references are intentional compatibility aliases for Streamlit and Pigskin-safe read paths.

## Formula Review

The deterministic formula remains:

```text
base_score =
  0.40 * market_score
+ 0.20 * projection_score
+ 0.15 * recent_production_score
+ 0.10 * role_usage_score
+ 0.10 * positional_scarcity_score
+ 0.05 * efficiency_score

risk_adjustment = -10 * normalized_risk_score
confidence_multiplier = clamp(confidence_score / 100, 0.70, 1.00)
trade_score = clamp((base_score + risk_adjustment) * confidence_multiplier, 0, 100)
```

Score tier thresholds match the implementation:

| Tier | Threshold |
| --- | ---: |
| `elite` | `>= 88` |
| `strong` | `>= 74` |
| `starter` | `>= 60` |
| `flex` | `>= 45` |
| `depth` | `>= 30` |
| `avoid` | `< 30` |

## Field Alignment

The builder `OUTPUT_FIELDS` list and `trade_player_scores` migration table contain the same 33 fields. No missing or extra fields were found in either direction.

Required score fields are present:

- `player_id`
- `player_name`
- `position`
- `team`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `current_market_value`
- `projected_3_year_value`
- `market_score`
- `projection_score`
- `recent_production_score`
- `role_usage_score`
- `positional_scarcity_score`
- `efficiency_score`
- `normalized_risk_score`
- `fraud_score`
- `confidence_score`
- `trade_score`
- `score_tier`
- `source_freshness_json`
- `missing_flags_json`
- `component_json`
- `model_version`
- `created_at`

Additional implementation metadata fields are also aligned:

- `score_run_id`
- `season_type`
- `player_id_internal`
- `source_snapshot_week`
- `score_inputs_json`
- `updated_at`

## View And UI Safety

`trade_player_scores_current` reads from `trade_player_scores` and keeps one latest row per player, profile, context, and model version.

`compat_trade_player_scores_current` reads from `trade_player_scores_current`, exposes `player_id_internal`, score fields, freshness JSON, missing flags, and component JSON, and does not read raw or source tables.

Streamlit score UI remains gated behind both default-off flags:

- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`

The Trade Lab score path uses the compatibility view only when both flags are true. Legacy Trade Lab behavior remains available when either flag is false.

## Validation Coverage

The validation catalog dry-run discovered 160 files, including the Trade Analyzer score validations:

- `150_trade_player_scores_grain.sql`
- `151_trade_player_scores_trade_score_range.sql`
- `152_trade_player_scores_component_score_range.sql`
- `153_trade_player_scores_confidence_range.sql`
- `154_trade_player_scores_required_json_fields.sql`
- `155_trade_player_scores_missing_flags_exist.sql`
- `156_trade_player_scores_source_freshness_exists.sql`
- `157_trade_player_scores_current_grain.sql`
- `158_compat_trade_player_scores_current_exists.sql`
- `159_compat_trade_player_scores_no_raw_source_dependencies.sql`
- `160_trade_player_scores_identity_coverage.sql`

Live `trade_score` validations were not run because migration `0025__trade_analyzer_score_v0.sql` is still pending and was not applied in this audit.

## Local Checks

| Command | Result |
| --- | --- |
| `.\venv\Scripts\python.exe -m unittest tests.test_trade_player_scores` | pass, 10 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_streamlit_compat_rollout` | pass, 10 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_pipeline_plan` | pass, 13 tests |
| `.\venv\Scripts\python.exe -m unittest tests.test_staging_ui_warning_fixes` | pass, 13 tests |
| `.\venv\Scripts\python.exe -m unittest discover tests` | pass, 328 tests |
| `.\venv\Scripts\python.exe -m py_compile app.py` | pass |
| `.\venv\Scripts\python.exe -m compileall -q src scripts` | pass |
| `.\venv\Scripts\python.exe scripts\check_deployment_safety.py` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --dry-run` | pass |
| `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending` | pass, pending migration `0025` only |
| `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run` | pass, 160 validation files discovered |

## Remaining Warnings

1. Migration `0025__trade_analyzer_score_v0.sql` remains pending. Applying it still requires explicit operator authorization.
2. No bounded score write was performed. Materialization still requires explicit operator authorization.
3. Live `trade_score` validations should be run after migration `0025` is applied.
4. Formula quality still needs empirical review after the first bounded 2025 PPR redraft one-QB materialization, but no blocking contract or implementation mismatch remains.

## Recommendation

The Trade Analyzer score v0 package is accurate enough to proceed to the next gated step.

Approved next steps from this audit standpoint:

1. Apply migration `0025` only if `ALLOW_TRADE_SCORE_MIGRATION_APPLY=true`.
2. Verify `trade_player_scores`, `trade_player_scores_current`, and `compat_trade_player_scores_current` exist after migration.
3. Run the bounded score builder dry-run for 2025 week 18 PPR redraft one-QB.
4. Materialize scores only if `ALLOW_TRADE_SCORE_MATERIALIZATION=true`.
5. Run live `trade_score`, `market`, and `content_brief` validations after materialization.

Final decision: `ACCURACY AUDIT PASS`.
