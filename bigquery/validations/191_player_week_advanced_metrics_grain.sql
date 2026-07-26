-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_metric_rows = 0

SELECT COUNT(*) AS duplicate_metric_rows
FROM (
    SELECT metric_version, season, week, player_id_internal, scoring_profile_id, league_type_id, roster_format_id, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_advanced_metrics`
    GROUP BY 1, 2, 3, 4, 5, 6, 7
    HAVING row_count > 1
);
