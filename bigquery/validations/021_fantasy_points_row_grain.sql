-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows.

SELECT
    'fantasy_points_row_grain' AS validation_name,
    COALESCE(player_id_internal, source_player_key) AS player_key,
    source_player_key,
    season,
    week,
    scoring_profile_id,
    COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile`
GROUP BY player_key, source_player_key, season, week, scoring_profile_id
HAVING COUNT(*) > 1;
