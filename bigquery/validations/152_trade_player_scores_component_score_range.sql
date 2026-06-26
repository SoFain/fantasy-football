-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_component_score_rows = 0

SELECT COUNT(*) AS invalid_component_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
WHERE market_score IS NULL
    OR market_score < 0
    OR market_score > 100
    OR projection_score IS NULL
    OR projection_score < 0
    OR projection_score > 100
    OR recent_production_score IS NULL
    OR recent_production_score < 0
    OR recent_production_score > 100
    OR role_usage_score IS NULL
    OR role_usage_score < 0
    OR role_usage_score > 100
    OR positional_scarcity_score IS NULL
    OR positional_scarcity_score < 0
    OR positional_scarcity_score > 100
    OR efficiency_score IS NULL
    OR efficiency_score < 0
    OR efficiency_score > 100
    OR normalized_risk_score IS NULL
    OR normalized_risk_score < 0
    OR normalized_risk_score > 1
    OR fraud_score IS NULL
    OR fraud_score < 0
    OR fraud_score > 100;
