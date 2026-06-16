-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows.

WITH required_profiles AS (
    SELECT 'standard' AS scoring_profile_id
    UNION ALL SELECT 'half_ppr'
    UNION ALL SELECT 'ppr'
),
available_profiles AS (
    SELECT DISTINCT scoring_profile_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_player_profiles_current`
)
SELECT
    'compat_player_profiles_current_scoring_profiles_exist' AS validation_name,
    required_profiles.scoring_profile_id
FROM required_profiles
LEFT JOIN available_profiles USING (scoring_profile_id)
WHERE available_profiles.scoring_profile_id IS NULL;
