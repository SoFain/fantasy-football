-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_current_baseline_rows = 0

WITH grain AS (
    SELECT
        source_id,
        COALESCE(player_id_internal, source_player_key, display_name) AS player_key,
        season,
        COALESCE(week, -1) AS week_key,
        COALESCE(scoring_profile_id, 'none') AS scoring_profile_key,
        COALESCE(league_type_id, 'none') AS league_type_key,
        COALESCE(roster_format_id, 'none') AS roster_format_key,
        baseline_type,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.market_consensus_baseline_current`
    GROUP BY 1, 2, 3, 4, 5, 6, 7, 8
)
SELECT COUNTIF(row_count > 1) AS duplicate_current_baseline_rows
FROM grain;
