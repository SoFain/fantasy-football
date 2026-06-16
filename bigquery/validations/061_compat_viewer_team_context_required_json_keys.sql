-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_required_keys = 0.

SELECT
    'compat_viewer_team_context_required_json_keys' AS validation_name,
    COUNTIF(
        JSON_QUERY(packet_json, '$.league_context') IS NULL
        OR JSON_QUERY(packet_json, '$.team_context') IS NULL
        OR JSON_QUERY(packet_json, '$.roster_rows') IS NULL
        OR JSON_QUERY(packet_json, '$.lineup_rows') IS NULL
        OR JSON_QUERY(packet_json, '$.bench_rows') IS NULL
        OR JSON_QUERY(packet_json, '$.waiver_rows') IS NULL
        OR JSON_QUERY(packet_json, '$.team_strengths') IS NULL
        OR JSON_QUERY(packet_json, '$.team_weaknesses') IS NULL
        OR JSON_QUERY(packet_json, '$.recommended_actions') IS NULL
        OR JSON_QUERY(packet_json, '$.evidence_metadata') IS NULL
    ) AS rows_missing_required_keys
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_viewer_team_context`;
