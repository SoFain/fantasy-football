-- Validation: injury risk is bounded and depth remains explicitly unavailable.
-- Expected result: invalid_role_context_count = 0.

SELECT COUNT(1) AS invalid_role_context_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_role_context_metrics`
WHERE injury_risk_score < 0
   OR injury_risk_score > 100
   OR missing_flags_json IS NULL
   OR source_provenance_json IS NULL
   OR depth_chart_role_score IS NOT NULL;
