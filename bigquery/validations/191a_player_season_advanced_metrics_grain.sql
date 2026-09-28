-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_metric_rows = 0

SELECT COUNT(*) AS duplicate_metric_rows
FROM (
    SELECT metric_version, season, season_type, player_id_internal, position, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_season_advanced_metrics`
    GROUP BY 1, 2, 3, 4, 5
    HAVING row_count > 1
);
