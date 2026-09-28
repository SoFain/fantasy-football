-- Validation helper. Render placeholders before running manually.
-- Expected result: claim_source_count should be reviewed

SELECT
    COUNT(*) AS claim_source_count,
    COUNTIF(active) AS active_claim_source_count,
    MAX(updated_at) AS latest_source_update_at
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.claim_sources`;
