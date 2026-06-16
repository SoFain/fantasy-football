-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_column_count = 0.

WITH expected AS (
    SELECT 'model_run_id' AS column_name
    UNION ALL SELECT 'run_type'
    UNION ALL SELECT 'model_name'
    UNION ALL SELECT 'model_version'
    UNION ALL SELECT 'prompt_version'
    UNION ALL SELECT 'code_version'
    UNION ALL SELECT 'season'
    UNION ALL SELECT 'week'
    UNION ALL SELECT 'scoring_profile_id'
    UNION ALL SELECT 'league_type_id'
    UNION ALL SELECT 'roster_format_id'
    UNION ALL SELECT 'feature_config_version_id'
    UNION ALL SELECT 'source_freshness_snapshot_id'
    UNION ALL SELECT 'status'
    UNION ALL SELECT 'created_by'
    UNION ALL SELECT 'created_at'
    UNION ALL SELECT 'completed_at'
    UNION ALL SELECT 'error_message'
    UNION ALL SELECT 'notes'
),
actual AS (
    SELECT column_name
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS`
    WHERE table_name = 'model_runs'
)
SELECT
    'model_runs_required_columns' AS validation_name,
    COUNTIF(actual.column_name IS NULL) AS missing_column_count
FROM expected
LEFT JOIN actual USING (column_name);
