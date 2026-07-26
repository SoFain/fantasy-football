-- Validation: role context injury features are bounded and explainable.
-- Expected result: invalid_injury_feature_count = 0

SELECT COUNT(1) AS invalid_injury_feature_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_role_context_metrics`
WHERE injury_status_score < 0
   OR injury_status_score > 100
   OR injury_burden_score < 0
   OR injury_burden_score > 100
   OR missed_time_risk_score < 0
   OR missed_time_risk_score > 100
   OR availability_score < 0
   OR availability_score > 100
   OR injury_context_missing_flags_json IS NULL
   OR source_provenance_json IS NULL;
