-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_identity_rate should stay low for fantasy-relevant rows.

SELECT
    'compat_player_profiles_current_identity_coverage' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(player_id_internal IS NULL) AS missing_identity_count,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS missing_identity_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_player_profiles_current`
WHERE scoring_profile_id = 'ppr'
    AND position IN ('QB', 'RB', 'WR', 'TE')
    AND (
        fantasy_points_per_game_current_season >= 5
        OR pigskin_rank_position <= 100
    );
