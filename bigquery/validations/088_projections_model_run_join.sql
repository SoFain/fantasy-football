-- Validation helper. Render placeholders before running manually.
-- Expected result: orphaned_model_run_rows = 0

WITH projection_rows AS (
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_weekly`
    UNION ALL
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_ros`
    UNION ALL
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_dynasty`
    UNION ALL
    SELECT model_run_id FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current`
)
SELECT
    COUNTIF(p.model_run_id IS NOT NULL AND mr.model_run_id IS NULL) AS orphaned_model_run_rows
FROM projection_rows p
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` mr
    ON p.model_run_id = mr.model_run_id;
