-- Validation helper. Render placeholders before running manually.
-- Expected result: review

SELECT
    COUNT(*) AS player_week_rows,
    COUNTIF(player_id_internal IS NULL) AS missing_internal_id_rows,
    SAFE_DIVIDE(COUNTIF(player_id_internal IS NULL), COUNT(*)) AS missing_internal_id_rate
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.stg_player_week_stats`;
