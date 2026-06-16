-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_flags_null_count = 0.

SELECT
    'compat_trade_assets_current_missing_flags_exist' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(missing_data_flags IS NULL) AS missing_flags_null_count,
    COUNTIF(NOT STARTS_WITH(missing_data_flags, '[')) AS missing_flags_not_json_array_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current`;
