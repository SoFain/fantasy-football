-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_model_run_id_count = 0 for rows generated after migration 0004.
-- Historical rows generated before this migration may have NULL model_run_id.

WITH migration AS (
    SELECT MIN(applied_at) AS applied_at
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.schema_migrations`
    WHERE migration_id = '0004'
),
recent_active AS (
    SELECT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings`, migration
    WHERE generated_at >= migration.applied_at
),
recent_history AS (
    SELECT model_run_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings_history`, migration
    WHERE generated_at >= migration.applied_at
)
SELECT
    'pigskin_rankings_model_run_id_present' AS validation_name,
    COUNTIF(model_run_id IS NULL) AS missing_model_run_id_count
FROM (
    SELECT model_run_id FROM recent_active
    UNION ALL
    SELECT model_run_id FROM recent_history
);
