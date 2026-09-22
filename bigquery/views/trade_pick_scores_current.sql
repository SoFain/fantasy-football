-- Current deterministic draft-pick score rows.
-- Reads only the draft-pick score output table.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores_current` AS
SELECT
    model_version,
    score_run_id,
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
    created_by,
    created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY
        source_pick_key,
        pick_year,
        pick_class,
        pick_round,
        pick_slot,
        scoring_profile_id,
        league_type_id,
        roster_format_id
    ORDER BY
        created_at DESC,
        model_version DESC,
        score_run_id DESC
) = 1;
