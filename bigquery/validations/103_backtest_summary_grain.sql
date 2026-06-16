-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_summary_rows = 0

WITH grain AS (
    SELECT
        backtest_run_id,
        model_run_id,
        projection_horizon,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        COALESCE(position, 'ALL') AS position_key,
        COALESCE(season, -1) AS season_key,
        COALESCE(week, -1) AS week_key,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_summary`
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8, 9
)
SELECT COUNTIF(row_count > 1) AS duplicate_summary_rows
FROM grain;
