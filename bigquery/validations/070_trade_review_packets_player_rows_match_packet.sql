-- Validation helper. Render placeholders before running manually.
-- Expected result: mismatched_packet_rows = 0

WITH packet_counts AS (
    SELECT
        trade_review_id,
        COALESCE(ARRAY_LENGTH(JSON_QUERY_ARRAY(packet_json, '$.side_a_evidence.player_rows')), 0)
        + COALESCE(ARRAY_LENGTH(JSON_QUERY_ARRAY(packet_json, '$.side_b_evidence.player_rows')), 0) AS expected_player_rows
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets`
),
player_counts AS (
    SELECT
        trade_review_id,
        COUNT(*) AS actual_player_rows
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packet_players`
    GROUP BY trade_review_id
)
SELECT
    COUNTIF(COALESCE(packet_counts.expected_player_rows, 0) != COALESCE(player_counts.actual_player_rows, 0)) AS mismatched_packet_rows
FROM packet_counts
LEFT JOIN player_counts
    USING (trade_review_id);
