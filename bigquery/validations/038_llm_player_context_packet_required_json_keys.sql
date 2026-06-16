-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_required_keys = 0.

SELECT
    'llm_player_context_packet_required_json_keys' AS validation_name,
    COUNT(*) AS rows_missing_required_keys
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.llm_player_context_packet`
WHERE JSON_QUERY(packet_json, '$.identity') IS NULL
    OR JSON_QUERY(packet_json, '$.ranking_context') IS NULL
    OR JSON_QUERY(packet_json, '$.recent_fantasy_summary') IS NULL
    OR JSON_QUERY(packet_json, '$.usage_summary') IS NULL
    OR JSON_QUERY(packet_json, '$.efficiency_summary') IS NULL
    OR JSON_QUERY(packet_json, '$.fraud_watch_context') IS NULL
    OR JSON_QUERY(packet_json, '$.trade_context') IS NULL
    OR JSON_QUERY(packet_json, '$.external_context') IS NULL
    OR JSON_QUERY(packet_json, '$.counterarguments') IS NULL
    OR JSON_QUERY(packet_json, '$.source_metadata') IS NULL;
