-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_score_rows = 0

WITH duplicate_grain AS (
    SELECT
        model_version,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        player_id,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.trade_player_scores`
    GROUP BY
        model_version,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        player_id
    HAVING COUNT(*) > 1
)
SELECT COUNT(*) AS duplicate_score_rows
FROM duplicate_grain;
