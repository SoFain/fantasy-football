-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_profile_count = 0 after materialization.

WITH expected_profiles AS (
    SELECT 'standard' AS scoring_profile_id
    UNION ALL SELECT 'half_ppr'
    UNION ALL SELECT 'ppr'
),
latest_week AS (
    SELECT season, week
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_weekly_truth`
    WHERE season_type = 'REG'
    ORDER BY season DESC, week DESC
    LIMIT 1
),
actual_profiles AS (
    SELECT DISTINCT scoring_profile_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile` fp
    JOIN latest_week
        USING (season, week)
)
SELECT
    'fantasy_points_profile_seed_coverage' AS validation_name,
    COUNTIF(actual_profiles.scoring_profile_id IS NULL) AS missing_profile_count,
    ARRAY_AGG(expected_profiles.scoring_profile_id IGNORE NULLS ORDER BY expected_profiles.scoring_profile_id) AS expected_profiles
FROM expected_profiles
LEFT JOIN actual_profiles
    USING (scoring_profile_id);
