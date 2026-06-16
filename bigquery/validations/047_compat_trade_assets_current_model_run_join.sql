-- Validation helper. Render placeholders before running manually.
-- Expected result: rows with ranking context should have model_run_id or ranking_version.

SELECT
    'compat_trade_assets_current_model_run_join' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(pigskin_rank_position IS NOT NULL) AS ranked_rows,
    COUNTIF(pigskin_rank_position IS NOT NULL AND model_run_id IS NULL AND ranking_version IS NULL) AS ranked_rows_missing_lineage
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current`;
