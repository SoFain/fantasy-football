-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_player_week_rows = 0

SELECT COUNT(*) AS duplicate_player_week_rows
FROM (
    SELECT season, week, player_id_internal, team, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.stg_player_week_stats`
    GROUP BY 1, 2, 3, 4
    HAVING row_count > 1
);
