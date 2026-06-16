-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_flags_null_rows = 0.

SELECT
    'compat_sleeper_watch_candidates_missing_flags_exist' AS validation_name,
    COUNTIF(missing_data_flags IS NULL) AS missing_flags_null_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates`;
