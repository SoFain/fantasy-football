-- Validation helper. Render placeholders before running manually.
-- Expected result: row_count > 0 after materialization.

SELECT
    'compat_viewer_team_context_recent_rows_exist' AS validation_name,
    MAX(snapshot_timestamp) AS latest_snapshot_timestamp,
    MAX(season) AS max_season,
    MAX(week) AS max_week,
    COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_viewer_team_context`;
