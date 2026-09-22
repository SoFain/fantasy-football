# Phase 21.8 Trade Analyzer Scoring Model Spec Report

## Purpose

Phase 21.8 drafted the deterministic Trade Analyzer scoring-model specification for a future default-off rollout. This phase did not implement runtime behavior.

## Inputs Reviewed

| Source | Finding |
| --- | --- |
| `app.py` Trade Lab | Current comparison sums `market_value` and an age-retention projected value per selected side |
| `compat_trade_assets_current` contract | Safe future asset source with market value, rankings, risk placeholders, source freshness, and missing-data flags |
| `compat_trade_player_history` contract | Safe recent-history source that avoids direct `weekly_metrics` reads |
| Phase 20 validation report | Current status is staging-only; production is not approved |
| Phase 20.2B Trade Lab QA | Side A and Side B summary cards pass staging QA, with `USE_COMPAT_TRADE_PLAYER_HISTORY=true` staging-only |
| Phase 20.5 mart rebuild report | 2025 marts exist for weekly truth, scoring-profile fantasy points, and Fraud Watch |
| Phase 20.6 Fraud Watch report | Current-season Fraud Watch packets and draft brief exist from real 2025 rows |
| Compatibility and query-debt docs | Raw/source table reads remain prohibited for new UI and Pigskin-visible paths |

## Deliverable Created

Created:

- `docs/rebuild/trade-analyzer-scoring-model-v0.md`

The spec covers:

- current Trade Analyzer behavior;
- allowed and forbidden data sources;
- v0 component weights;
- formula shape;
- normalization rules;
- proposed BigQuery contract;
- feature flags;
- UI behavior;
- Pigskin safety;
- future tests;
- future validation SQL;
- Phase 22 implementation plan.

## Current Behavior Summary

Current Trade Lab behavior remains unchanged:

- The asset board uses legacy `market_values` by default.
- `USE_COMPAT_TRADE_ASSETS` remains default false.
- Side totals use selected asset `market_value`.
- Projected multiyear values use the existing age-retention curve.
- `USE_COMPAT_TRADE_PLAYER_HISTORY=true` is staging-approved only and affects recent-history context for the AI outlook.
- No deterministic score is currently materialized or displayed.

## v0 Model Summary

The proposed v0 formula is deterministic and explainable:

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

The model requires component columns and missing-data flags so admins can audit why a player received a score.

## Proposed Warehouse Contract

The spec proposes:

| Object | Purpose |
| --- | --- |
| `trade_player_scores` | Backing score table |
| `trade_player_scores_current` | Latest current score view |
| `compat_trade_player_scores_current` | Streamlit and Pigskin-readable compatibility view |

Rules:

- UI and Pigskin must read only the compatibility view or helper layer.
- Raw/source tables must not be referenced directly from the compatibility view.
- Score generation must be additive and idempotent.
- Missing identity or stale source data must be flagged.

## Safety Status

| Rule | Status |
| --- | --- |
| No application runtime changes | pass |
| No production feature flag changes | pass |
| No `USE_COMPAT_TRADE_ASSETS` default change | pass |
| No legacy Trade Lab removal | pass |
| No BigQuery mutation | pass |
| No migrations applied | pass |
| No Cloud Run Jobs triggered | pass |
| No deployment | pass |
| No LLM calls | pass |
| No scraping | pass |
| No Firebase artifacts | pass |
| No raw/source table exposure added | pass |

## Warnings

| Warning | Status |
| --- | --- |
| v0 weights are heuristic until backtested | Expected for spec phase |
| Draft pick valuation is not solved in v0 | Open question for Phase 22 |
| Real Trade Review inputs remain blocked | Requires operator-supplied trade sides |
| Production remains not approved | Existing Phase 20 and Phase 21 gate status |

## Recommended Phase 22 Work

1. Add additive BigQuery contracts and migrations for the score table and compatibility view.
2. Implement a bounded `src/trade_player_scores.py` builder with dry-run mode.
3. Add validation SQL for grain, range sanity, freshness, flags, identity coverage, and raw-source dependency checks.
4. Materialize a small 2025 PPR redraft one-QB score run from real marts.
5. Add a default-off Streamlit score display behind `USE_TRADE_ANALYZER_SCORE_V0=false`.
6. Run staging browser QA with only the score flag enabled.
7. Backtest or manually sanity-review v0 weights before any production consideration.

## Final Decision

`TRADE ANALYZER SCORE SPEC READY`

The scoring-model specification is ready for Phase 22 implementation planning. It is not approval to write warehouse objects, enable flags, deploy, or expose the score in production.
