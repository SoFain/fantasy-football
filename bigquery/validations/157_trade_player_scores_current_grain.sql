-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_current_rows = 0

WITH duplicate_grain AS (
    SELECT
        player_id,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores_current`
    GROUP BY
        player_id,
        scoring_profile_id,
        league_type_id,
        roster_format_id
    HAVING COUNT(*) > 1
)
SELECT COUNT(*) AS duplicate_current_rows
FROM duplicate_grain;
