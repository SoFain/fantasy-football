-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_claim_grade_rows = 0

WITH grain AS (
    SELECT
        claim_grading_run_id,
        claim_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.claim_grades`
    GROUP BY 1, 2
)
SELECT COUNTIF(row_count > 1) AS duplicate_claim_grade_rows
FROM grain;
