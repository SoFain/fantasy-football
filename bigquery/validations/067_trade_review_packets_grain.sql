-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_trade_review_ids = 0

SELECT
    COUNT(*) - COUNT(DISTINCT trade_review_id) AS duplicate_trade_review_ids
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_review_packets`;
