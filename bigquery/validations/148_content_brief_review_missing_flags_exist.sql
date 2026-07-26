-- Validation helper. Render placeholders before running manually.
-- Expected result: rows_missing_flag_column_values = 0

SELECT SUM(rows_missing_flag_column_values) AS rows_missing_flag_column_values
FROM (
    SELECT COUNT(*) AS rows_missing_flag_column_values
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_briefs`
    WHERE missing_data_flags IS NULL
    UNION ALL
    SELECT COUNT(*) AS rows_missing_flag_column_values
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.content_brief_items`
    WHERE missing_data_flags IS NULL
);
