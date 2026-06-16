-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_seed_count = 0.

WITH expected AS (
    SELECT 'redraft' AS league_type_id
    UNION ALL SELECT 'keeper'
    UNION ALL SELECT 'dynasty'
    UNION ALL SELECT 'best_ball'
),
actual AS (
    SELECT league_type_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.league_types`
)
SELECT
    'league_type_seed_rows_exist' AS validation_name,
    COUNTIF(actual.league_type_id IS NULL) AS missing_seed_count
FROM expected
LEFT JOIN actual USING (league_type_id);
