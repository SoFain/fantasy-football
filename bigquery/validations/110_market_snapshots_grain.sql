-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_snapshot_ids = 0

WITH grain AS (
    SELECT
        snapshot_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_snapshots`
    GROUP BY 1
)
SELECT COUNTIF(row_count > 1) AS duplicate_snapshot_ids
FROM grain;
