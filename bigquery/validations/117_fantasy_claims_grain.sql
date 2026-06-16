-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_claim_ids = 0

WITH grain AS (
    SELECT
        claim_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fantasy_claims`
    GROUP BY 1
)
SELECT COUNTIF(row_count > 1) AS duplicate_claim_ids
FROM grain;
