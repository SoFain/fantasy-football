-- Validation helper. Render placeholders before running manually.
-- Expected result: raw_market_values_reference_count = 0 for the compatibility view.

SELECT
    'compat_trade_assets_current_no_raw_ui_dependency' AS validation_name,
    COUNTIF(REGEXP_CONTAINS(LOWER(view_definition), r'\bmarket_values\b')) AS raw_market_values_reference_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.VIEWS`
WHERE table_name = 'compat_trade_assets_current';
