-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_total_count = 0.

SELECT
    'fantasy_points_no_invalid_totals' AS validation_name,
    COUNT(*) AS invalid_total_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile`
WHERE total_fantasy_points IS NULL
    OR IS_NAN(total_fantasy_points)
    OR ABS(total_fantasy_points) > 200;
