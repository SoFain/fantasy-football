-- Draft-pick deterministic score v0 contract.
-- Additive schema-only migration. No pick scores are generated, backfilled, renamed, or removed.

CREATE TABLE IF NOT EXISTS `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores` (
    model_version STRING NOT NULL,
    score_run_id STRING NOT NULL,
    source_pick_key STRING NOT NULL,
    pick_label STRING NOT NULL,
    pick_year INT64 NOT NULL,
    pick_class STRING NOT NULL,
    pick_round INT64 NOT NULL,
    pick_slot INT64,
    estimated_overall_pick INT64,
    pick_bucket STRING NOT NULL,
    parse_confidence STRING NOT NULL,
    scoring_profile_id STRING NOT NULL,
    league_type_id STRING NOT NULL,
    roster_format_id STRING NOT NULL,
    current_market_value FLOAT64,
    risk_adjusted_trade_value FLOAT64,
    market_score FLOAT64,
    slot_capital_score FLOAT64,
    time_discount_score FLOAT64,
    liquidity_certainty_score FLOAT64,
    college_context_score FLOAT64,
    uncertainty_risk_score FLOAT64,
    confidence_score FLOAT64,
    pick_score FLOAT64,
    score_tier STRING,
    component_json STRING,
    missing_flags_json STRING,
    source_freshness_json STRING,
    created_by STRING,
    created_at TIMESTAMP NOT NULL
)
PARTITION BY RANGE_BUCKET(pick_year, GENERATE_ARRAY(2020, 2050, 1))
CLUSTER BY model_version, scoring_profile_id, league_type_id, roster_format_id;

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
