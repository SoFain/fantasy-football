-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_market_value_count = 0 when market source is populated.

SELECT
    'compat_trade_assets_current_market_value_not_null' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(market_value IS NULL) AS missing_market_value_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current`;
