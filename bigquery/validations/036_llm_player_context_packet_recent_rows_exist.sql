-- Validation helper. Render placeholders before running manually.
-- Expected result: recent_row_count > 0 after packet materialization.

SELECT
    'llm_player_context_packet_recent_rows_exist' AS validation_name,
    COUNT(*) AS recent_row_count,
    MAX(as_of_season) AS max_as_of_season,
    MAX(as_of_week) AS max_as_of_week
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet`
WHERE as_of_season >= EXTRACT(YEAR FROM CURRENT_DATE()) - 2;
