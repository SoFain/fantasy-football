-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_seed_count = 0.

WITH expected AS (
    SELECT 'standard' AS scoring_profile_id
    UNION ALL SELECT 'half_ppr'
    UNION ALL SELECT 'ppr'
),
actual AS (
    SELECT scoring_profile_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.scoring_profiles`
)
SELECT
    'scoring_profile_seed_rows_exist' AS validation_name,
    COUNTIF(actual.scoring_profile_id IS NULL) AS missing_seed_count
FROM expected
LEFT JOIN actual USING (scoring_profile_id);
