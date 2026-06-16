-- Validation helper. Render placeholders before running manually.
-- Expected result: table_count = 1 after the migration framework has been applied.

SELECT
    'schema_migrations_exists' AS validation_name,
    COUNT(1) AS table_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.TABLES`
WHERE table_name = 'schema_migrations';
