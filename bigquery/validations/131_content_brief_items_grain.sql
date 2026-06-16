-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_content_brief_items = 0

WITH grain AS (
    SELECT
        content_brief_id,
        item_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_brief_items`
    GROUP BY 1, 2
)
SELECT COUNTIF(row_count > 1) AS duplicate_content_brief_items
FROM grain;
