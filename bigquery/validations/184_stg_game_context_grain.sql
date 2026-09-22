-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_game_rows = 0

SELECT COUNT(*) AS duplicate_game_rows
FROM (
    SELECT season, week, game_id, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.stg_game_context`
    GROUP BY 1, 2, 3
    HAVING row_count > 1
);
