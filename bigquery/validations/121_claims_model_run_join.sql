-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_model_run_rows = 0 once claims reference model runs.

SELECT COUNT(*) AS missing_model_run_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claims` claims
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.model_runs` runs
    ON claims.model_run_id_at_claim = runs.model_run_id
WHERE claims.model_run_id_at_claim IS NOT NULL
  AND runs.model_run_id IS NULL;
