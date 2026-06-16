-- Validation helper. Render placeholders before running manually.
-- Expected result: zero rows.

SELECT
    'duplicate_active_gsis_id_mappings' AS validation_name,
    gsis_id,
    COUNT(DISTINCT player_id_internal) AS mapped_player_count,
    ARRAY_AGG(DISTINCT player_id_internal ORDER BY player_id_internal) AS player_id_internal_values
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_identity_bridge`
WHERE gsis_id IS NOT NULL
GROUP BY gsis_id
HAVING COUNT(DISTINCT player_id_internal) > 1;
