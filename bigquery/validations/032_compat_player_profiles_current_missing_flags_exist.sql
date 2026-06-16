-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_flags_null_count = 0.

SELECT
    'compat_player_profiles_current_missing_flags_exist' AS validation_name,
    COUNTIF(missing_data_flags IS NULL OR missing_data_flags = '') AS missing_flags_null_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_player_profiles_current`;
