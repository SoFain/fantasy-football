# trade_pick_scores Contract

Migration SQL: [bigquery/migrations/0026__trade_pick_score_v0.sql](../migrations/0026__trade_pick_score_v0.sql)

Planner: [src/trade_pick_scores.py](../../src/trade_pick_scores.py)

## Purpose

Stores deterministic draft-pick score rows for the pick-score lane. This is not a player-score table. Generic draft picks are not player rows, do not have player identity, and must not be forced into `trade_player_scores`.

The v0 pick lane is market-led. College context is neutral and unavailable in v0 until a future college or rookie identity bridge is contracted and validated.

## Grain

One row per:

- `model_version`
- `source_pick_key`
- `pick_year`
- `pick_class`
- `pick_round`
- `pick_slot`
- `scoring_profile_id`
- `league_type_id`
- `roster_format_id`

`pick_slot` is nullable for round-only picks. The grain remains deterministic because `source_pick_key`, `pick_class`, `pick_round`, and the scoring context are still required.

## Required Fields

Identity and context:

- `model_version`
- `score_run_id`
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

Value inputs:

- `current_market_value`
- `risk_adjusted_trade_value`

Component scores:

- `market_score`
- `slot_capital_score`
- `time_discount_score`
- `liquidity_certainty_score`
- `college_context_score`
- `uncertainty_risk_score`
- `confidence_score`
- `pick_score`
- `score_tier`

Explainability:

- `component_json`
- `missing_flags_json`
- `source_freshness_json`

Metadata:

- `created_by`
- `created_at`

## Score Range Rules

- Component scores use a `0` to `100` range.
- `confidence_score` uses a `0` to `100` range.
- `pick_score` uses a `0` to `100` range.
- `college_context_score` is neutral at `50` in v0 and must be flagged with `college_context_unavailable`.
- `uncertainty_risk_score` uses `0` to `100`, where higher means more uncertainty penalty.
- Missing or stale inputs must be represented in `missing_flags_json` and `source_freshness_json`.

## Source Rules

The v0 builder may read:

- `compat_trade_assets_current`

The v0 builder must not read:

- `draft_picks`
- `college_player_stats`
- `rookie_scouting_metrics`
- raw or source tables

The compatibility view must not expose direct dependencies on raw/source tables. Future college or rookie context requires a separate identity bridge and curated mart before it can affect pick scores.

## Runtime Rules

- Streamlit must not write this table from request-time UI.
- Phase 28.2 and Phase 28.3 include dry-run and schema work only.
- Production exposure remains default-off and requires a separate rollout decision.
- No LLM calls are required or allowed to compute deterministic pick scores.
- Pick scores should be displayed as pick scores, not player trade scores, until product language is explicitly approved.

## Validation

Validation SQL:

- `161_trade_pick_scores_exists.sql`
- `162_trade_pick_scores_grain.sql`
- `163_trade_pick_scores_pick_score_range.sql`
- `164_trade_pick_scores_component_score_range.sql`
- `165_trade_pick_scores_confidence_range.sql`
- `166_trade_pick_scores_required_identity_fields.sql`
- `167_trade_pick_scores_exact_slot_fields.sql`
- `168_trade_pick_scores_round_only_fields.sql`
- `169_trade_pick_scores_source_freshness_exists.sql`
- `170_trade_pick_scores_missing_flags_exist.sql`
- `171_trade_pick_scores_component_json_exists.sql`
- `175_trade_player_scores_no_pick_rows.sql`
- `176_trade_pick_scores_no_player_columns.sql`
- `177_trade_pick_scores_parseability_warning.sql`
- `178_trade_pick_scores_model_version_coverage.sql`
