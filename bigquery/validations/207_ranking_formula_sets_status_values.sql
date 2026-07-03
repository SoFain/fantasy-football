-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_formula_set_rows = 0

SELECT COUNT(*) AS invalid_formula_set_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_sets`
WHERE status NOT IN ('draft', 'reviewed', 'active', 'retired');
