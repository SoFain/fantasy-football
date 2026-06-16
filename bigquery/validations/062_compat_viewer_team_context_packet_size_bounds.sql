-- Validation helper. Render placeholders before running manually.
-- Expected result: oversize_packet_text_rows = 0.

SELECT
    'compat_viewer_team_context_packet_size_bounds' AS validation_name,
    MAX(LENGTH(packet_json)) AS max_packet_json_chars,
    MAX(LENGTH(packet_text)) AS max_packet_text_chars,
    COUNTIF(LENGTH(packet_text) > 12000) AS oversize_packet_text_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_viewer_team_context`;
