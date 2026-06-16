-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_required_keys = 0

SELECT
    COUNTIF(
        packet_json IS NULL
        OR JSON_QUERY(packet_json, '$.trade_summary') IS NULL
        OR JSON_QUERY(packet_json, '$.verdict') IS NULL
        OR JSON_QUERY(packet_json, '$.side_a_evidence') IS NULL
        OR JSON_QUERY(packet_json, '$.side_b_evidence') IS NULL
        OR JSON_QUERY(packet_json, '$.player_evidence') IS NULL
        OR JSON_QUERY(packet_json, '$.roster_context') IS NULL
        OR JSON_QUERY(packet_json, '$.counterarguments') IS NULL
        OR JSON_QUERY(packet_json, '$.show_framing') IS NULL
        OR JSON_QUERY(packet_json, '$.metadata') IS NULL
    ) AS rows_missing_required_keys
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets`;
