-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_flag_count = 0

SELECT COUNT(*) AS invalid_flag_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_pbp_opportunity_metrics`
WHERE missing_flags_json IS NULL
   OR source_provenance_json IS NULL
   OR JSON_VALUE(missing_flags_json, '$.xfp_proxy_policy') IS NULL
   OR JSON_VALUE(source_provenance_json, '$.leakage_policy') IS NULL;
