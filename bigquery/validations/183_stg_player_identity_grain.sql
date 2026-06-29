-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_identity_rows = 0

SELECT COUNT(*) AS duplicate_identity_rows
FROM (
    SELECT player_id_internal, season, week, team, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.stg_player_identity`
    GROUP BY 1, 2, 3, 4
    HAVING row_count > 1
);
