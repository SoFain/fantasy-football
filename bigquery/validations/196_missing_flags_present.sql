-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_flags = 0

SELECT COUNT(*) AS rows_missing_flags
FROM (
    SELECT missing_data_flags FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
    UNION ALL
    SELECT missing_data_flags FROM `{{PROJECT_ID}}.{{DATASET_ID}}.team_week_context_metrics`
    UNION ALL
    SELECT missing_data_flags FROM `{{PROJECT_ID}}.{{DATASET_ID}}.qb_week_environment_metrics`
    UNION ALL
    SELECT missing_data_flags FROM `{{PROJECT_ID}}.{{DATASET_ID}}.pigskin_player_context_packet_current`
)
WHERE missing_data_flags IS NULL;
