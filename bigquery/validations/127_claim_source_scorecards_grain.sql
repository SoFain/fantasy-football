-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_source_scorecards = 0

WITH grain AS (
    SELECT
        claim_grading_run_id,
        source_id,
        COALESCE(CAST(season AS STRING), 'all') AS season_key,
        COALESCE(CAST(week AS STRING), 'all') AS week_key,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.claim_source_scorecards`
    GROUP BY 1, 2, 3, 4
)
SELECT COUNTIF(row_count > 1) AS duplicate_source_scorecards
FROM grain;
