# compat_trade_player_scores_current Contract

Migration SQL: [bigquery/migrations/0025__trade_analyzer_score_v0.sql](../migrations/0025__trade_analyzer_score_v0.sql)

View SQL: [bigquery/views/compat_trade_player_scores_current.sql](../views/compat_trade_player_scores_current.sql)

Backing view: [trade_player_scores_current](trade_player_scores_current.md)

Spec: [docs/rebuild/trade-analyzer-scoring-model-v0.md](../../docs/rebuild/trade-analyzer-scoring-model-v0.md)

## Purpose

Safe compatibility view for future Trade Lab and Pigskin-visible Trade Analyzer score reads.

This view is not wired into runtime by default. Future wiring must stay behind default-off flags:

- `USE_TRADE_ANALYZER_SCORE_V0=false`
- `USE_COMPAT_TRADE_PLAYER_SCORE=false`

## Grain

One row per:

- `player_id`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

The view exposes `player_id_internal` as an alias of `player_id` for compatibility with existing identity contracts.

## Required Fields

Identity and context:

- `player_id`
- `player_id_internal`
- `player_name`
- `normalized_name`
- `position`
- `team`
- `season`
- `week`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

Scores:

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

Metadata:

- `source_freshness_json`
- `missing_flags_json`
- `component_json`
- `model_version`
- `model_run_id`
- `ranking_version`
- `feature_config_version_id`
- `score_run_id`
- `created_at`

## Source Rules

`compat_trade_player_scores_current` reads only `trade_player_scores_current`, which reads only `trade_player_scores`.

It must not reference:

- `weekly_metrics`
- `play_by_play`
- `market_values`
- raw NGS, FTN, snap, injury, schedule, roster, or Sleeper source tables
- arbitrary SQL tool paths

## Runtime Rules

- Safe for future Streamlit read helpers after validation.
- Safe for future Pigskin context packets or parameterized helpers after validation.
- Not enabled by default.
- Must not trigger materialization.
- Must not compute scores with an LLM.
- Must expose source freshness and missing-data flags.

## Validation

Validation SQL:

- `157_trade_player_scores_current_grain.sql`
- `158_compat_trade_player_scores_current_exists.sql`
- `159_compat_trade_player_scores_no_raw_source_dependencies.sql`
- `160_trade_player_scores_identity_coverage.sql`

