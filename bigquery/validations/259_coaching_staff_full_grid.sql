-- Validation helper. Render placeholders before running manually.
-- The table should hold the full 32-team x 8-role grid.
-- Expected result: row_count = 256

SELECT COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_current`;
