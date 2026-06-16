-- Validation helper. Render placeholders before running manually.
-- Expected result: bad_rank_rows = 0

WITH expected AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY model_run_id, projection_horizon, scoring_profile_id, league_type_id, roster_format_id
            ORDER BY projected_points_or_value DESC, display_name
        ) AS expected_overall,
        ROW_NUMBER() OVER (
            PARTITION BY model_run_id, projection_horizon, scoring_profile_id, league_type_id, roster_format_id, position
            ORDER BY projected_points_or_value DESC, display_name
        ) AS expected_position
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current`
)
SELECT
    COUNTIF(rank_overall != expected_overall OR rank_position != expected_position) AS bad_rank_rows
FROM expected;
