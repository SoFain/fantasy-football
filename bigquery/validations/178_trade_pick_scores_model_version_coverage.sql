-- Validation helper. Render placeholders before running manually.
-- Expected result: model_version_count should be reviewed

SELECT
    model_version,
    COUNT(*) AS score_rows,
    COUNT(DISTINCT score_run_id) AS score_run_count,
    MIN(created_at) AS first_created_at,
    MAX(created_at) AS latest_created_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_pick_scores`
GROUP BY model_version
ORDER BY latest_created_at DESC;
