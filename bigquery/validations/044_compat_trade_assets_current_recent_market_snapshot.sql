-- Validation helper. Render placeholders before running manually.
-- Expected result: freshness_status should be reviewed, not always zero.
--
-- This is warning-level by design. Trade market values are manually or
-- schedule-refreshed external context, not a hard warehouse activation blocker.
-- Freshness policy:
--   - August through January: warn after 2 days.
--   - February through July: warn after 14 days.

WITH freshness AS (
    SELECT
        'compat_trade_assets_current_recent_market_snapshot' AS validation_name,
        MAX(market_snapshot_date) AS max_snapshot_date,
        MAX(market_snapshot_timestamp) AS max_snapshot_timestamp,
        COUNT(*) AS row_count,
        IF(EXTRACT(MONTH FROM CURRENT_DATE()) IN (8, 9, 10, 11, 12, 1), 2, 14) AS allowed_stale_days
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_trade_assets_current`
)
SELECT
    validation_name,
    max_snapshot_date,
    max_snapshot_timestamp,
    row_count,
    allowed_stale_days,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), max_snapshot_timestamp, DAY) AS snapshot_age_days,
    'stale_market_snapshot' AS freshness_status
FROM freshness
WHERE row_count > 0
    AND max_snapshot_timestamp IS NOT NULL
    AND TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), max_snapshot_timestamp, DAY) > allowed_stale_days;
