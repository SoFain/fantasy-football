-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_count = 0.

SELECT
    'compat_viewer_team_context_grain' AS validation_name,
    COUNT(*) AS duplicate_grain_count
FROM (
    SELECT
        league_id,
        roster_id,
        manager_id,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        snapshot_timestamp,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_viewer_team_context`
    GROUP BY league_id, roster_id, manager_id, season, week, scoring_profile_id, league_type_id, roster_format_id, snapshot_timestamp
    HAVING row_count > 1
);
