-- Validation helper. Render placeholders before running manually.
-- Expected result: null_model_run_rows = 0

WITH projection_rows AS (
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_weekly`
    UNION ALL
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_ros`
    UNION ALL
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_dynasty`
    UNION ALL
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current`
)
SELECT COUNTIF(model_run_id IS NULL) AS null_model_run_rows
FROM projection_rows;
