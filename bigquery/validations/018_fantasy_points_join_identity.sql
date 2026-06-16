-- Validation helper. Render placeholders before running manually.
-- Expected result: important_missing_identity_count should be low after identity bridge is materialized.

WITH latest_week AS (
    SELECT season, week
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile`
    WHERE scoring_profile_id = 'ppr'
    ORDER BY season DESC, week DESC
    LIMIT 1
),
important_rows AS (
    SELECT fp.*
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile` fp
    JOIN latest_week
        USING (season, week)
    WHERE fp.scoring_profile_id = 'ppr'
        AND fp.position IN ('QB', 'RB', 'WR', 'TE')
        AND fp.total_fantasy_points >= 8
)
SELECT
    'fantasy_points_join_identity' AS validation_name,
    COUNT(*) AS important_row_count,
    COUNTIF(player_id_internal IS NULL) AS important_missing_identity_count,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS missing_identity_rate
FROM important_rows;
