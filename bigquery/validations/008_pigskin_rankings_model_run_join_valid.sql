-- Validation helper. Render placeholders before running manually.
-- Expected result: orphan_model_run_id_count = 0.
-- NULL model_run_id values from historical pre-migration rows are ignored.

WITH ranking_ids AS (
    SELECT DISTINCT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings`
    WHERE model_run_id IS NOT NULL

    UNION DISTINCT

    SELECT DISTINCT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings_history`
    WHERE model_run_id IS NOT NULL
)
SELECT
    'pigskin_rankings_model_run_join_valid' AS validation_name,
    COUNTIF(model_runs.model_run_id IS NULL) AS orphan_model_run_id_count
FROM ranking_ids
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` model_runs
    USING (model_run_id);
