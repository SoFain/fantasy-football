-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_evaluation_windows = 0

WITH grain AS (
    SELECT
        claim_id,
        evaluation_window_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.claim_evaluation_windows`
    GROUP BY 1, 2
)
SELECT COUNTIF(row_count > 1) AS duplicate_evaluation_windows
FROM grain;
