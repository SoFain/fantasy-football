-- Validation helper. Render placeholders before running manually.
-- Expected result: max_snapshot_date should be recent after market ingestion and materialization.

SELECT
    'compat_trade_assets_current_recent_market_snapshot' AS validation_name,
    MAX(market_snapshot_date) AS max_snapshot_date,
    MAX(market_snapshot_timestamp) AS max_snapshot_timestamp,
    COUNT(*) AS row_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current`;
