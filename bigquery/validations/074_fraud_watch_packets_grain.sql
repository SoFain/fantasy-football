-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_grain_rows = 0

WITH grain AS (
    SELECT
        COALESCE(player_id_internal, source_player_key, display_name) AS player_key,
        COALESCE(model_run_id, 'missing-run') AS model_run_key,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        season,
        week,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.fraud_watch_packets`
    GROUP BY 1, 2, 3, 4, 5, 6, 7
)
SELECT COUNTIF(row_count > 1) AS duplicate_grain_rows
FROM grain;
