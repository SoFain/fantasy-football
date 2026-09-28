-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_flag_rows = 0

SELECT COUNT(*) AS invalid_flag_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_ideal_opportunity_metrics`
WHERE missing_flags_json IS NULL
   OR source_provenance_json IS NULL
   OR source_updated_at IS NULL
   OR JSON_VALUE(missing_flags_json, '$.true_route_share_missing_flag') IS NULL
   OR JSON_VALUE(source_provenance_json, '$.expected_fantasy_source') IS NULL;
