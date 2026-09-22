-- Validation helper. Render placeholders before running manually.
-- Expected result: table_count = 7

SELECT COUNT(*) AS table_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
WHERE table_name IN (
    'player_week_advanced_metrics',
    'team_week_context_metrics',
    'qb_week_environment_metrics',
    'pigskin_player_context_packet_current',
    'player_recent_advanced_metrics_current',
    'player_role_usage_metrics_current',
    'compat_pigskin_player_context_current'
);
