# compat_trade_pick_scores_current Contract

Migration SQL: [bigquery/migrations/0026__trade_pick_score_v0.sql](../migrations/0026__trade_pick_score_v0.sql)

View SQL: [bigquery/views/compat_trade_pick_scores_current.sql](../views/compat_trade_pick_scores_current.sql)

## Purpose

Provides the future UI-safe and Pigskin-safe read contract for draft-pick score rows. This compatibility view is separate from player scores. It is not a player contract, and generic draft picks are not player rows.

The v0 view is market-led. College context remains neutral and unavailable until future source contract work adds a curated college or rookie identity bridge.

## Grain

One current row per:

- `source_pick_key`
- `pick_year`
- `pick_class`
- `pick_round`
- `pick_slot`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

## UI Fields

The view includes:

- `source_pick_key`
- `pick_label`
- `pick_year`
- `pick_class`
- `pick_round`
- `pick_slot`
- `estimated_overall_pick`
- `pick_bucket`
- `parse_confidence`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`
- `current_market_value`
- `risk_adjusted_trade_value`
- `market_score`
- `slot_capital_score`
- `time_discount_score`
- `liquidity_certainty_score`
- `college_context_score`
- `uncertainty_risk_score`
- `confidence_score`
- `pick_score`
- `score_tier`
- `component_json`
- `missing_flags_json`
- `source_freshness_json`
- `model_version`
- `score_run_id`
- `created_at`

## Source Rules

Allowed source:

- `trade_pick_scores_current`

Forbidden direct dependencies:

- `draft_picks`
- `college_player_stats`
- `rookie_scouting_metrics`
- `source_*`
- `raw_*`
- raw market tables

## Runtime Rules

- This view does not enable production score UI.
- Production exposure remains default-off.
- The view must not trigger materialization, ingestion, LLM calls, or Cloud Run Jobs.
- If no pick score row exists, UI should keep the existing market-only behavior and show a clear unavailable state.

## Validation

Validation SQL:

- `173_compat_trade_pick_scores_current_exists.sql`
- `174_compat_trade_pick_scores_no_raw_source_dependencies.sql`
