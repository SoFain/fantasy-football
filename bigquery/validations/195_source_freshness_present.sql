-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_source_freshness = 0

SELECT COUNT(*) AS rows_missing_source_freshness
FROM (
    SELECT source_freshness_json FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
    UNION ALL
    SELECT source_freshness_json FROM `{{PROJECT_ID}}.{{DATASET_ID}}.team_week_context_metrics`
    UNION ALL
    SELECT source_freshness_json FROM `{{PROJECT_ID}}.{{DATASET_ID}}.qb_week_environment_metrics`
    UNION ALL
    SELECT source_freshness_json FROM `{{PROJECT_ID}}.{{DATASET_ID}}.pigskin_player_context_packet_current`
)
WHERE source_freshness_json IS NULL;
