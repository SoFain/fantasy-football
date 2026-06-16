-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_content_brief_run_ids = 0

WITH grain AS (
    SELECT
        content_brief_run_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_brief_runs`
    GROUP BY 1
)
SELECT COUNTIF(row_count > 1) AS duplicate_content_brief_run_ids
FROM grain;
