-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_candidate_rows = 0

SELECT COUNT(*) AS invalid_candidate_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_formula_candidates`
WHERE position NOT IN ('QB', 'RB', 'WR', 'TE')
   OR status NOT IN ('draft', 'reviewed', 'active', 'retired', 'rejected');
