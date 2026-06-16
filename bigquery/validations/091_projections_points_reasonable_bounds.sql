-- Validation helper. Render placeholders before running manually.
-- Expected result: out_of_bounds_rows = 0

WITH checks AS (
    SELECT COUNTIF(projected_points_mean < 0 OR projected_points_mean > 100) AS bad_rows
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_weekly`
    UNION ALL
    SELECT COUNTIF(projected_points_per_game < 0 OR projected_points_per_game > 100 OR projected_points_total < 0 OR projected_points_total > 2000) AS bad_rows
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_ros`
    UNION ALL
    SELECT COUNTIF(total_dynasty_value < 0 OR total_dynasty_value > 10000) AS bad_rows
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_dynasty`
)
SELECT SUM(bad_rows) AS out_of_bounds_rows
FROM checks;
