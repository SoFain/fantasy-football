-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_required_json = 0

SELECT COUNT(*) AS rows_missing_required_json
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_candidates`
WHERE formula_json IS NULL
   OR feature_allowlist_json IS NULL
   OR target_definition_json IS NULL
   OR source_requirements_json IS NULL
   OR JSON_VALUE(formula_json, '$.score_expression') IS NULL
   OR JSON_VALUE(formula_json, '$.position') IS NULL;
