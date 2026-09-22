-- Compatibility view for draft-pick score reads.
-- Streamlit and Pigskin-visible helpers should read this view only.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_pick_scores_current` AS
SELECT
    source_pick_key,
    pick_label,
    pick_year,
    pick_class,
    pick_round,
    pick_slot,
    estimated_overall_pick,
    pick_bucket,
    parse_confidence,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    current_market_value,
    risk_adjusted_trade_value,
    market_score,
    slot_capital_score,
    time_discount_score,
    liquidity_certainty_score,
    college_context_score,
    uncertainty_risk_score,
    confidence_score,
    pick_score,
    score_tier,
    component_json,
    missing_flags_json,
    source_freshness_json,
    model_version,
    score_run_id,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores_current`;
