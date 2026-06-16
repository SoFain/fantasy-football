-- Validation helper. Render placeholders before running manually.
-- Expected result: oversized_packet_count = 0.

SELECT
    'llm_player_context_packet_size_bounds' AS validation_name,
    COUNTIF(LENGTH(packet_text) > 8000 OR token_estimate > 2200) AS oversized_packet_count,
    MAX(LENGTH(packet_text)) AS max_packet_text_length,
    MAX(token_estimate) AS max_token_estimate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet`;
