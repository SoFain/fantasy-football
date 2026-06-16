-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_context_id_rows = 0

WITH projection_rows AS (
    SELECT scoring_profile_id, league_type_id, roster_format_id, projection_horizon, rank_source
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_weekly`
    UNION ALL
    SELECT scoring_profile_id, league_type_id, roster_format_id, projection_horizon, rank_source
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_ros`
    UNION ALL
    SELECT scoring_profile_id, league_type_id, roster_format_id, projection_horizon, rank_source
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_dynasty`
    UNION ALL
    SELECT scoring_profile_id, league_type_id, roster_format_id, projection_horizon, rank_source
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current`
)
SELECT
    COUNTIF(
        scoring_profile_id IS NULL
        OR league_type_id IS NULL
        OR roster_format_id IS NULL
        OR projection_horizon IS NULL
        OR rank_source IS NULL
    ) AS missing_context_id_rows
FROM projection_rows;
