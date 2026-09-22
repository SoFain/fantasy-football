-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_source_dependency_count = 0

SELECT COUNT(*) AS raw_source_dependency_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name IN (
        'player_recent_advanced_metrics_current',
        'player_role_usage_metrics_current',
        'compat_pigskin_player_context_current'
    )
    AND REGEXP_CONTAINS(
        LOWER(view_definition),
        r'\b(from|join)\s+`?[^`\s]*(raw_nflverse_[a-z0-9_]*|play_by_play|weekly_metrics|ngs_passing|ngs_rushing|ngs_receiving|ftn_charting|weekly_snap_counts|injury_reports|depth_charts|source_[a-z0-9_]*|raw_[a-z0-9_]*)\b'
    );
