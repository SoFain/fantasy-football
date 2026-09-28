-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_team_week_rows = 0

SELECT COUNT(*) AS duplicate_team_week_rows
FROM (
    SELECT season, week, team, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.stg_team_week_stats`
    GROUP BY 1, 2, 3
    HAVING row_count > 1
);
