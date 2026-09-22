-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_metric_range_rows = 0

SELECT COUNT(*) AS invalid_metric_range_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
WHERE target_share < 0
    OR target_share > 1
    OR air_yards_share < 0
    OR air_yards_share > 1
    OR carry_share < 0
    OR carry_share > 1
    OR opportunity_share < 0
    OR opportunity_share > 1
    OR snap_share < 0
    OR snap_share > 1
    OR success_rate < 0
    OR success_rate > 1;
