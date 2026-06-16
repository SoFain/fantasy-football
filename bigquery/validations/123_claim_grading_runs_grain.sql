-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_claim_grading_run_ids = 0

WITH grain AS (
    SELECT
        claim_grading_run_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.claim_grading_runs`
    GROUP BY 1
)
SELECT COUNTIF(row_count > 1) AS duplicate_claim_grading_run_ids
FROM grain;
