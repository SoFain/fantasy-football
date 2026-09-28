-- Validation: role context identity mapping is deterministic and populated.
-- Expected result: missing_identity_count = 0

SELECT COUNT(1) AS missing_identity_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_role_context_metrics`
WHERE player_id_internal IS NULL
   OR identity_mapping_method IS NULL
   OR identity_mapping_confidence IS NULL
   OR identity_mapping_confidence < 0
   OR identity_mapping_confidence > 1;
