-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_rows = 0

WITH grain AS (
    SELECT snapshot_at, sleeper_player_id, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_history`
    GROUP BY snapshot_at, sleeper_player_id
)
SELECT COUNTIF(row_count > 1) AS duplicate_grain_rows
FROM grain;
