-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows.

SELECT
    'compat_player_profiles_current_grain' AS validation_name,
    COALESCE(player_id_internal, source_player_key) AS player_key,
    scoring_profile_id,
    as_of_season,
    as_of_week,
    COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_player_profiles_current`
GROUP BY player_key, scoring_profile_id, as_of_season, as_of_week
HAVING COUNT(*) > 1;
