-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_required_keys = 0

SELECT
    COUNTIF(
        packet_json IS NULL
        OR JSON_QUERY(packet_json, '$.identity') IS NULL
        OR JSON_QUERY(packet_json, '$.ranking_context') IS NULL
        OR JSON_QUERY(packet_json, '$.breakout_claim') IS NULL
        OR JSON_QUERY(packet_json, '$.evidence') IS NULL
        OR JSON_QUERY(packet_json, '$.counterargument') IS NULL
        OR JSON_QUERY(packet_json, '$.what_would_change_the_take') IS NULL
        OR JSON_QUERY(packet_json, '$.show_framing') IS NULL
        OR JSON_QUERY(packet_json, '$.snark_hooks') IS NULL
        OR JSON_QUERY(packet_json, '$.source_metadata') IS NULL
    ) AS rows_missing_required_keys
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_breakout_packets`;
