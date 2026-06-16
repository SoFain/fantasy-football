-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_flags = 0

SELECT COUNT(*) AS rows_missing_flags
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_briefs`
WHERE missing_data_flags IS NULL;
