-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_count = 0.

SELECT
    'compat_sleeper_watch_candidates_grain' AS validation_name,
    COUNT(*) AS duplicate_grain_count
FROM (
    SELECT
        COALESCE(player_id_internal, source_player_key, sleeper_player_id, normalized_name) AS player_key,
        COALESCE(league_id, 'GLOBAL') AS league_context,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        season,
        week,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates`
    GROUP BY player_key, league_context, scoring_profile_id, league_type_id, roster_format_id, season, week
    HAVING row_count > 1
);
