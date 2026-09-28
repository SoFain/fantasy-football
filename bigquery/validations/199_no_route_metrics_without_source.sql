-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_route_metric_rows = 0

SELECT COUNT(*) AS invalid_route_metric_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_role_usage_metrics_current`
WHERE route_share IS NOT NULL
    AND (
        missing_data_flags IS NULL
        OR NOT REGEXP_CONTAINS(LOWER(missing_data_flags), r'true_route_source')
    );
