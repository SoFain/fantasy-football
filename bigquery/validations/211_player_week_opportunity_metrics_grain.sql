-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_opportunity_rows = 0

SELECT COUNT(*) AS duplicate_opportunity_rows
FROM (
    SELECT
        opportunity_metric_version,
        season,
        week,
        player_id_internal,
        position,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_opportunity_metrics`
    GROUP BY 1, 2, 3, 4, 5
    HAVING row_count > 1
);
