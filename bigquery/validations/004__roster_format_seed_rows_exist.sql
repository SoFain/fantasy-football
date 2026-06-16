-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_seed_count = 0.

WITH expected AS (
    SELECT 'one_qb' AS roster_format_id
    UNION ALL SELECT 'superflex'
    UNION ALL SELECT 'two_qb'
    UNION ALL SELECT 'best_ball'
),
actual AS (
    SELECT roster_format_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.roster_formats`
)
SELECT
    'roster_format_seed_rows_exist' AS validation_name,
    COUNTIF(actual.roster_format_id IS NULL) AS missing_seed_count
FROM expected
LEFT JOIN actual USING (roster_format_id);
