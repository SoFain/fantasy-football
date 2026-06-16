-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_model_run_join_count should be 0 once rankings use model_run_id.

SELECT
    'llm_player_context_packet_model_run_join' AS validation_name,
    COUNTIF(p.model_run_id IS NOT NULL AND mr.model_run_id IS NULL) AS missing_model_run_join_count,
    COUNTIF(p.model_run_id IS NULL) AS null_model_run_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet` p
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` mr
    ON p.model_run_id = mr.model_run_id;
