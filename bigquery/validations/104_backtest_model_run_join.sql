-- Validation helper. Render placeholders before running manually.
-- Expected result: orphan_model_run_rows = 0

WITH model_run_refs AS (
    SELECT DISTINCT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_runs`
    WHERE model_run_id IS NOT NULL
    UNION DISTINCT
    SELECT DISTINCT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_player_week`
    WHERE model_run_id IS NOT NULL
    UNION DISTINCT
    SELECT DISTINCT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_result_summary`
    WHERE model_run_id IS NOT NULL
    UNION DISTINCT
    SELECT DISTINCT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.backtest_calibration_bins`
    WHERE model_run_id IS NOT NULL
)
SELECT COUNTIF(mr.model_run_id IS NULL) AS orphan_model_run_rows
FROM model_run_refs refs
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` mr
    ON refs.model_run_id = mr.model_run_id;
