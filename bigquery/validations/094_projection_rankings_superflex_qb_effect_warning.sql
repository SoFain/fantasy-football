-- Validation helper. Render placeholders before running manually.
-- Expected result: superflex_qb_effect_rows should be reviewed

WITH superflex_runs AS (
    SELECT DISTINCT model_run_id, projection_horizon, scoring_profile_id, league_type_id, roster_format_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current`
    WHERE roster_format_id = 'superflex'
),
qb_top_24 AS (
    SELECT
        model_run_id,
        projection_horizon,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        COUNTIF(position = 'QB' AND rank_overall <= 24) AS qb_top_24_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.projection_rankings_current`
    WHERE roster_format_id = 'superflex'
    GROUP BY 1, 2, 3, 4, 5
)
SELECT
    COUNTIF(COALESCE(q.qb_top_24_count, 0) = 0) AS superflex_qb_effect_rows
FROM superflex_runs s
LEFT JOIN qb_top_24 q
    USING (model_run_id, projection_horizon, scoring_profile_id, league_type_id, roster_format_id);
