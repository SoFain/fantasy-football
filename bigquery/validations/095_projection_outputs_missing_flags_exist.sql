-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_flags_null_rows = 0

WITH projection_rows AS (
    SELECT missing_data_flags FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_weekly`
    UNION ALL
    SELECT missing_data_flags FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_ros`
    UNION ALL
    SELECT missing_data_flags FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projections_player_dynasty`
)
SELECT COUNTIF(missing_data_flags IS NULL) AS missing_flags_null_rows
FROM projection_rows;
