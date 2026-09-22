-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_required_json_keys = 0

SELECT COUNT(*) AS rows_missing_required_json_keys
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
WHERE component_json IS NULL
    OR NOT REGEXP_CONTAINS(component_json, r'"market_score"')
    OR NOT REGEXP_CONTAINS(component_json, r'"projection_score"')
    OR NOT REGEXP_CONTAINS(component_json, r'"recent_production_score"')
    OR NOT REGEXP_CONTAINS(component_json, r'"role_usage_score"')
    OR NOT REGEXP_CONTAINS(component_json, r'"positional_scarcity_score"')
    OR NOT REGEXP_CONTAINS(component_json, r'"efficiency_score"')
    OR NOT REGEXP_CONTAINS(component_json, r'"normalized_risk_score"')
    OR NOT REGEXP_CONTAINS(component_json, r'"confidence_score"');
