-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_rows = 0

WITH grain AS (
    SELECT
        model_run_id,
        projection_horizon,
        COALESCE(player_id_internal, display_name) AS player_key,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current`
    GROUP BY 1, 2, 3, 4, 5, 6
)
SELECT COUNTIF(row_count > 1) AS duplicate_grain_rows
FROM grain;
