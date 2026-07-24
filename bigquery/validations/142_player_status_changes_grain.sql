-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_rows = 0

WITH grain AS (
    SELECT detected_at, sleeper_player_id, field_name, COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_status_changes`
    GROUP BY detected_at, sleeper_player_id, field_name
)
SELECT COUNTIF(row_count > 1) AS duplicate_grain_rows
FROM grain;
