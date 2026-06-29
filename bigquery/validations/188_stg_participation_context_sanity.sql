-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_participation_rows = 0

SELECT COUNT(*) AS invalid_participation_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.stg_participation_context`
WHERE offense_pct < 0
    OR offense_pct > 1
    OR (route_share IS NOT NULL AND has_true_route_source IS NOT TRUE);
