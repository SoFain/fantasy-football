-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_rows = 0

WITH grain AS (
    SELECT team_abbr, role, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.coaching_staff_current`
    GROUP BY team_abbr, role
)
SELECT COUNTIF(row_count > 1) AS duplicate_grain_rows
FROM grain;
