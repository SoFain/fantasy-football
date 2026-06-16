-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_player_week_rows = 0

WITH grain AS (
    SELECT
        backtest_run_id,
        model_run_id,
        COALESCE(player_id_internal, source_player_key, display_name) AS player_key,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        projection_horizon,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_player_week`
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
)
SELECT COUNTIF(row_count > 1) AS duplicate_player_week_rows
FROM grain;
