-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_top_ranked_count = 0 after profile mart materialization.

WITH top_ranked AS (
    SELECT
        COALESCE(player_id, sleeper_player_id, player_name) AS ranking_key,
        player_id,
        sleeper_player_id,
        position,
        rank
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings`
    WHERE COALESCE(is_active, TRUE)
        AND rank <= 100
),
profiles AS (
    SELECT DISTINCT
        source_player_key,
        gsis_id,
        sleeper_player_id,
        position
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_player_profiles_current`
    WHERE scoring_profile_id = 'ppr'
)
SELECT
    'compat_player_profiles_current_top_ranked_players_present' AS validation_name,
    COUNT(*) AS missing_top_ranked_count
FROM top_ranked tr
LEFT JOIN profiles p
    ON tr.position = p.position
    AND (
        tr.player_id IN (p.source_player_key, p.gsis_id)
        OR tr.sleeper_player_id = p.sleeper_player_id
    )
WHERE p.source_player_key IS NULL
    AND p.gsis_id IS NULL
    AND p.sleeper_player_id IS NULL;
