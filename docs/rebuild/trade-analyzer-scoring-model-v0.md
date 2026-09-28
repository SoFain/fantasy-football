# Trade Analyzer Scoring Model v0

## Purpose

Define a deterministic, explainable scoring model for the Trade Analyzer before implementation. This is a specification only. It does not change Streamlit behavior, feature flag defaults, BigQuery data, migrations, Cloud Run Jobs, or production runtime.

The model goal is to move the Trade Lab from simple market-value comparison toward a repeatable player trade score that accounts for market value, projections, recent production, role, risk, scarcity, league context, and source confidence.

## Current Trade Analyzer Behavior

The current Trade Lab lives in `app.py` under `render_value_analyzer()`.

Current behavior:

- The asset selector uses the legacy `market_values` path by default.
- The flagged `USE_COMPAT_TRADE_ASSETS=false` path can read `compat_trade_assets_current`, but that flag remains default off.
- Side A and Side B summary cards show selected assets, current market value totals, and projected multiyear totals.
- Current side value is the sum of selected `market_value` values.
- Projected multiyear value uses `project_asset_value(row, years)`, which applies position-specific age-retention curves to current market value.
- Draft picks or rows without a player position receive a simple annual discount.
- The Trade Lab displays a data-path marker for trade player history.
- `USE_COMPAT_TRADE_PLAYER_HISTORY=true` in staging affects only the recent-history context used by the AI outlook section.
- `USE_COMPAT_TRADE_PLAYER_HISTORY` does not change the asset list, current side totals, projected side totals, market values, or deterministic comparison logic.
- The legacy fallback path remains available and must stay available until a separate rollout removes it.

Known limits:

- Current totals are market-price totals, not a model score.
- The multiyear projection is an age-adjusted market-value heuristic.
- League format and roster context are not fully represented.
- Risk, recent usage, and source confidence are not surfaced as first-class deterministic components.
- Real Trade Review packets remain blocked until operator-supplied trade sides exist.

## Safe Source Inputs

The scoring model must use curated marts, projection outputs, compatibility views, or packet tables. It must not read raw/source tables from UI or Pigskin-visible paths.

Allowed source candidates:

| Source | Purpose |
| --- | --- |
| `compat_trade_assets_current` | Market value, identity, rank, tier, source freshness, missing-data flags, Pigskin context, risk placeholders |
| `compat_trade_player_history` | Recent fantasy production, role, usage, scoring-profile-aware history |
| `analytics_player_fantasy_points_by_profile` | Scoring-profile-aware fantasy production foundation |
| `analytics_player_weekly_truth` | Weekly truth and usage foundation |
| `analytics_fraud_watch` | Fraud-risk and overperformance signal foundation |
| `fraud_watch_packets` | Reviewed deterministic fraud-watch packet context |
| `projection_rankings_current` | Current projection and ranking context |
| `projections_player_weekly` | Weekly projection context when available |
| `projections_player_ros` | Rest-of-season projection context when available |
| `projections_player_dynasty` | Long-horizon projection context when available |
| `backtest_result_summary` and `backtest_result_player_week` | Future model calibration and confidence inputs |

Forbidden from UI or Pigskin-visible paths:

- `weekly_metrics`
- `play_by_play`
- `market_values`
- raw NGS, FTN, snap, injury, schedule, roster, and source ingest tables
- arbitrary SQL tool paths

Raw/source tables may be used only inside controlled ingestion or materialization jobs that produce the curated objects above.

## Model Grain

The proposed score should be materialized at this grain:

One row per:

- `player_id`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `season`
- `week`
- `model_version`

Current-view behavior:

- `trade_player_scores_current` should expose only the latest usable score per player and context.
- A compatibility view named `compat_trade_player_scores_current` should be the only Streamlit and Pigskin-readable score object.
- Historical score runs can be stored in `trade_player_scores`.
- `player_id_internal` is exposed only as a compatibility alias in `compat_trade_player_scores_current`; the canonical score key is `player_id`.

## v0 Components

All component scores should be normalized to a `0` to `100` scale unless otherwise noted. `normalized_risk_score` is the exception and uses a `0.00` to `1.00` scale. Missing components must be represented with `missing_flags_json`, not silently fabricated.

| Component | Weight | Description | Candidate inputs |
| --- | ---: | --- | --- |
| Market score | `0.40` | Current market consensus value by format and scoring profile | `compat_trade_assets_current.market_value`, market rank, tier |
| Projection score | `0.20` | Forward-looking player value | `projection_rankings_current`, `projections_player_weekly`, `projections_player_ros`, `projections_player_dynasty` |
| Recent production score | `0.15` | Scoring-profile-aware recent fantasy output | `compat_trade_player_history`, `analytics_player_fantasy_points_by_profile` |
| Role and usage score | `0.10` | Snap share, target share, rush share, high-value touches, red-zone work | `compat_trade_player_history`, `analytics_player_weekly_truth` |
| Positional scarcity score | `0.10` | Replacement gap by position and roster format | `compat_trade_assets_current.position_scarcity_score`, projection ranks |
| Efficiency score | `0.05` | Production quality signals adjusted by position | yards per target, yards per carry, catch rate, EPA summaries where available |
| Risk adjustment | `-10` to `0` points | Injury, volatility, fraud risk, missing-data risk, confidence penalties | `analytics_fraud_watch`, `fraud_watch_packets`, missing flags, freshness |
| Confidence multiplier | `0.70` to `1.00` | Caps score when inputs are stale, sparse, or identity coverage is weak | source freshness, missing flags, identity status, backtest calibration |

## Formula Shape

Initial deterministic formula:

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

Notes:

- `normalized_risk_score` is `0.00` to `1.00`.
- A higher `normalized_risk_score` means more downside risk.
- The `risk_adjustment` can reduce the score by up to 10 points.
- The confidence multiplier should never increase a score.
- The model must emit component columns so admins can explain the final result.
- v0 weights are intentionally simple. They should be backtested and tuned later.

## Score Tier Thresholds

Current v0 thresholds:

- `elite` when `trade_score >= 88`
- `strong` when `trade_score >= 74`
- `starter` when `trade_score >= 60`
- `flex` when `trade_score >= 45`
- `depth` when `trade_score >= 30`
- `avoid` otherwise

These thresholds are v0 heuristics and may be tuned after backtesting.

## Normalization Rules

Recommended v0 normalization:

- Normalize market value by percentile within `position`, `scoring_profile_id`, `league_type_id`, and `roster_format_id`.
- Normalize projection score by expected fantasy points or ranking percentile within the same context.
- Normalize recent production by rolling 3 to 5 week fantasy points per game within position and scoring profile.
- Normalize role by position-specific usage features:
  - QB: dropbacks, attempts, rush attempts, rushing share, red-zone usage.
  - RB: carries, target share, snap share, high-value touches, red-zone work.
  - WR and TE: target share, receptions, air-yards share, routes proxy when available, red-zone work.
- Normalize scarcity by replacement gap for the target roster format.
- Normalize efficiency with position-specific caps to avoid small-sample spikes.
- Compute confidence from row availability, source freshness, identity coverage, and missing-data flags.

Do not use unsafe fuzzy identity matching inside score generation. If identity cannot be resolved deterministically, leave the score null or emit a low-confidence row with explicit flags.

## Proposed BigQuery Contract

The authoritative warehouse contracts are the files in `bigquery/contracts/*`. This section is aligned with the Phase 22 implementation and should be treated as a summary of those contracts.

Proposed backing table:

- `trade_player_scores`

Proposed current view:

- `trade_player_scores_current`

Proposed compatibility view for UI and Pigskin:

- `compat_trade_player_scores_current`

Required fields:

| Field | Type intent | Notes |
| --- | --- | --- |
| `score_run_id` | string | Deterministic run ID |
| `model_version` | string | Example: `trade_score_v0` |
| `player_id` | string | Canonical score identity key |
| `player_name` | string | Display only |
| `normalized_name` | string | Identity diagnostics |
| `position` | string | Required |
| `team` | string | Nullable |
| `season` | integer | Required |
| `week` | integer | Required for current-season context |
| `scoring_profile_id` | string | Required |
| `league_type_id` | string | Required |
| `roster_format_id` | string | Required |
| `current_market_value` | numeric | Current market value |
| `projected_3_year_value` | numeric | Long-horizon projection or fallback value |
| `market_score` | numeric | `0` to `100` |
| `projection_score` | numeric | `0` to `100` |
| `recent_production_score` | numeric | `0` to `100` |
| `role_usage_score` | numeric | `0` to `100` |
| `positional_scarcity_score` | numeric | `0` to `100` |
| `efficiency_score` | numeric | `0` to `100` |
| `normalized_risk_score` | numeric | `0.00` to `1.00`, higher means riskier |
| `fraud_score` | numeric | `0` to `100`, higher means more fraud or overperformance risk |
| `confidence_score` | numeric | `0` to `100` |
| `trade_score` | numeric | Final `0` to `100` score |
| `score_tier` | string | Example: elite, strong, starter, flex, depth, avoid |
| `source_freshness_json` | JSON or string | Input freshness by source |
| `missing_flags_json` | JSON array text | Explicit missing or low-confidence inputs |
| `component_json` | JSON or string | Input values, normalized components, formula details, and fallbacks |
| `model_run_id` | string | Optional projection or ranking model run |
| `ranking_version` | string | Optional ranking lineage |
| `feature_config_version_id` | string | Scoring feature configuration identifier |
| `created_by` | string | Materializer or operator identifier |
| `created_at` | timestamp | Run creation time |

Compatibility view fields:

| Field | Type intent | Notes |
| --- | --- | --- |
| `player_id` | string | Canonical score identity key |
| `player_id_internal` | string | Alias of canonical `player_id` for compatibility with existing UI identity helpers |
| `player_name` | string | Display only |
| `normalized_name` | string | Identity diagnostics |
| `position` | string | Player position |
| `team` | string | Nullable |
| `season` | integer | Latest score season for the player and context |
| `week` | integer | Latest score week for the player and context |
| `scoring_profile_id` | string | Score context |
| `league_type_id` | string | Score context |
| `roster_format_id` | string | Score context |
| `current_market_value` | numeric | Current market value |
| `projected_3_year_value` | numeric | Long-horizon projection or fallback value |
| `trade_score` | numeric | Final `0` to `100` score |
| `score_tier` | string | v0 tier label |
| `confidence_score` | numeric | Confidence `0` to `100` |
| `normalized_risk_score` | numeric | Risk `0.00` to `1.00` |
| `fraud_score` | numeric | Fraud or overperformance risk `0` to `100` |
| `model_version` | string | Same model version as the backing score row |
| `source_freshness_json` | JSON or string | Input freshness by source |
| `missing_flags_json` | JSON array text | Explicit missing or low-confidence inputs |
| `component_json` | JSON or string | Input values, normalized components, formula details, and fallbacks |
| `score_run_id` | string | Deterministic run ID |
| `created_at` | timestamp | Run creation time |

Contract rules:

- `compat_trade_player_scores_current` must not reference raw/source tables directly.
- The scoring builder can reference curated marts, projection outputs, compatibility views, and packet tables.
- UI and Pigskin must read only the compatibility view or a helper module that reads that view.
- Score rows that use a source key because canonical identity is missing must be flagged in `missing_flags_json`.
- Score rows with stale market or projection context must be warning-level, not silently accepted.
- Score generation must be additive and idempotent.

## UI Behavior Proposal

Future Trade Lab behavior when `USE_TRADE_ANALYZER_SCORE_V0=true`:

- Keep the current selector and side-summary workflow.
- Add a visible score block per selected asset:
  - Trade score
  - Score tier
  - Top positive components
  - Risk flags
  - Confidence score
  - Source freshness summary
- Add side-level score totals:
  - Sum of trade scores
  - Weighted score by lineup value or market share
  - Current market total
  - Projected multiyear total
  - Fairness delta
- Show an explicit label such as `Trade score source: compat_trade_player_scores_current`.
- If the score object is unavailable, show a warning and fall back to the existing value-only behavior.
- Do not trigger score materialization from Streamlit.
- Do not run long warehouse mutations from request-time UI.
- Do not call an LLM to compute deterministic score values.

Future Pigskin behavior:

- Pigskin can see the score only through bounded context packets or a parameterized helper.
- Pigskin must not receive raw/source table names or arbitrary SQL tools.
- Score explanations should come from component columns, not hidden prompt logic.

## Feature Flags

Recommended future flags:

| Flag | Default | Purpose |
| --- | --- | --- |
| `USE_TRADE_ANALYZER_SCORE_V0` | `false` | Show deterministic trade scores in Trade Lab |
| `USE_COMPAT_TRADE_PLAYER_SCORE` | `false` | Route score reads through `compat_trade_player_scores_current` |
| `USE_COMPAT_TRADE_ASSETS` | `false` | Existing asset selector compatibility path |
| `USE_COMPAT_TRADE_PLAYER_HISTORY` | `false` production, `true` staging-approved | Existing recent-history compatibility path |

Rollout rule:

- Stage `USE_TRADE_ANALYZER_SCORE_V0=true` only after the score view exists, validation passes, and browser QA confirms the legacy value-only path remains available.
- Do not enable `USE_COMPAT_TRADE_ASSETS` by default as part of the score spec.
- Production must remain all-risk-flags-off until separately approved.

## Tests For Future Implementation

Future unit tests:

- Formula produces deterministic output for fixed inputs.
- Component weights sum to `1.00` before risk and confidence.
- Risk adjustment only lowers scores.
- Confidence multiplier never increases scores.
- Missing required identity emits missing-data flags.
- Missing market value produces null or low-confidence score, not fabricated value.
- Position-specific normalization handles QB, RB, WR, TE.
- Roster format changes scarcity score.
- Stale source freshness lowers confidence or flags the row.
- Helper queries use parameters and read only `compat_trade_player_scores_current`.
- Feature flags default false.
- Legacy Trade Lab value path remains available.

Future UI tests:

- Score widgets remain hidden when the flag is false.
- Score widgets render when the flag is true and score rows exist.
- Missing score rows show clean empty state.
- Side A and Side B score summaries render selected assets consistently.
- Pigskin-visible paths do not expose raw/source table names.
- `execute_bigquery_sql` remains absent.

## Validation SQL For Future Implementation

Proposed validation files:

- `15X_trade_player_scores_current_grain.sql`
- `15X_trade_player_scores_required_fields.sql`
- `15X_trade_player_scores_range_sanity.sql`
- `15X_trade_player_scores_missing_flags_exist.sql`
- `15X_trade_player_scores_source_freshness_exists.sql`
- `15X_trade_player_scores_identity_coverage.sql`
- `15X_trade_player_scores_no_raw_source_dependencies.sql`
- `15X_trade_player_scores_current_rows_exist.sql`
- `15X_trade_player_scores_component_weights.sql`

Validation expectations:

- Grain failures are blockers.
- Score range failures are blockers.
- Raw/source dependency failures are blockers.
- Missing current rows can be warning-level during offseason or before a score run exists.
- Identity coverage above a configured threshold should be warning first, blocker only above a higher threshold.
- Stale market source should be warning-level in offseason/manual contexts.

## Phase 22 Implementation Plan

Suggested follow-up phases:

1. Phase 22.1: Add BigQuery contracts and additive migrations for `trade_player_scores`, `trade_player_scores_current`, and `compat_trade_player_scores_current`.
2. Phase 22.2: Build `src/trade_player_scores.py` with dry-run, bounded context controls, and parameterized reads.
3. Phase 22.3: Add validation SQL and dry-run validation coverage.
4. Phase 22.4: Materialize a small v0 score run for 2025 PPR redraft one-QB using real 2025 current-season marts.
5. Phase 22.5: Add default-off Streamlit score display behind `USE_TRADE_ANALYZER_SCORE_V0=false`.
6. Phase 22.6: Run staging browser QA with the score flag on and all other risk flags unchanged.
7. Phase 22.7: Backtest or sanity-review component weights before any production consideration.

## Open Questions

- Should the first score be redraft-only, or should dynasty and keeper contexts be modeled in v0?
- Should side totals use simple sum, market-share weighting, or starter-slot weighting?
- Should a draft pick value model be part of v0 or left as a placeholder?
- Which projection output should be authoritative when weekly, rest-of-season, and dynasty scores disagree?
- What identity coverage threshold should block production score display?
- Should the UI expose component weights to admins for review, or keep weights in docs and score metadata only?

## Decision

`TRADE ANALYZER SCORE SPEC READY`

The v0 model is ready for implementation planning. It is not approved for runtime use, warehouse writes, production flags, or production UI exposure.
