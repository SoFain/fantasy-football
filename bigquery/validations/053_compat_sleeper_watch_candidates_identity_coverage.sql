-- Validation helper. Render placeholders before running manually.
-- Expected result: canonical_identity_rate should rise as player_identity_bridge is populated.

SELECT
    'compat_sleeper_watch_candidates_identity_coverage' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(player_id_internal IS NOT NULL AND NOT STARTS_WITH(player_id_internal, 'source:')) AS canonical_identity_rows,
    SAFE_DIVIDE(
        COUNTIF(player_id_internal IS NOT NULL AND NOT STARTS_WITH(player_id_internal, 'source:')),
        COUNT(*)
    ) AS canonical_identity_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates`;
