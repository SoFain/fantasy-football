-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_identity_rate should stay low for fantasy-relevant packets.

SELECT
    'llm_player_context_packet_identity_coverage' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(player_id_internal IS NULL) AS missing_identity_count,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS missing_identity_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet`
WHERE position IN ('QB', 'RB', 'WR', 'TE');
