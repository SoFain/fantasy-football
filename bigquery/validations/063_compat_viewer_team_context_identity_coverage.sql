-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_identity_packet_rows = 0

SELECT
    'compat_viewer_team_context_identity_coverage' AS validation_name,
    COUNT(*) AS packet_rows,
    COUNTIF(REGEXP_CONTAINS(missing_data_flags, r'missing_player_identity_rows')) AS missing_identity_packet_rows,
    SAFE_DIVIDE(
        COUNTIF(NOT REGEXP_CONTAINS(missing_data_flags, r'missing_player_identity_rows')),
        COUNT(*)
    ) AS packet_identity_coverage_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_viewer_team_context`;
