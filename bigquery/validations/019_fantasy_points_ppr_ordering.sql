-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows.

WITH profile_rows AS (
    SELECT
        COALESCE(player_id_internal, source_player_key) AS player_key,
        season,
        week,
        source_player_key,
        MAX(IF(scoring_profile_id = 'standard', total_fantasy_points, NULL)) AS standard_points,
        MAX(IF(scoring_profile_id = 'half_ppr', total_fantasy_points, NULL)) AS half_ppr_points,
        MAX(IF(scoring_profile_id = 'ppr', total_fantasy_points, NULL)) AS ppr_points,
        MAX(IF(scoring_profile_id = 'ppr', source_stat_json, NULL)) AS ppr_source_stat_json,
        STRING_AGG(COALESCE(missing_data_flags, ''), ',') AS missing_flags
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_fantasy_points_by_profile`
    GROUP BY player_key, season, week, source_player_key
),
with_receptions AS (
    SELECT
        *,
        SAFE_CAST(JSON_VALUE(ppr_source_stat_json, '$.receptions') AS FLOAT64) AS receptions
    FROM profile_rows
)
SELECT
    'fantasy_points_ppr_ordering' AS validation_name,
    player_key,
    season,
    week,
    standard_points,
    half_ppr_points,
    ppr_points,
    receptions,
    missing_flags
FROM with_receptions
WHERE receptions >= 0
    AND standard_points IS NOT NULL
    AND half_ppr_points IS NOT NULL
    AND ppr_points IS NOT NULL
    AND (
        ppr_points < half_ppr_points
        OR half_ppr_points < standard_points
    )
    AND NOT REGEXP_CONTAINS(missing_flags, r'"missing_receptions"');
