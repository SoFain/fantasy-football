-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_source_ids = 0

WITH grain AS (
    SELECT
        source_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_sources`
    GROUP BY 1
)
SELECT COUNTIF(row_count > 1) AS duplicate_source_ids
FROM grain;
