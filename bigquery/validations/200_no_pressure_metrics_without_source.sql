-- Validation helper. Render placeholders before running manually.
-- Expected result: pressure_metric_column_count = 0

SELECT COUNT(*) AS pressure_metric_column_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name IN (
        'player_week_advanced_metrics',
        'team_week_context_metrics',
        'qb_week_environment_metrics',
        'pigskin_player_context_packet_current',
        'compat_pigskin_player_context_current'
    )
    AND REGEXP_CONTAINS(LOWER(column_name), r'pressure|pass_rush_win|pressure_rate');
