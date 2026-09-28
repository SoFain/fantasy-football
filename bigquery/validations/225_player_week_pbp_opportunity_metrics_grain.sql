-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_duplicate_count = 0

WITH grain_counts AS (
  SELECT
    source_version,
    season,
    week,
    player_id_internal,
    COUNT(*) AS row_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_pbp_opportunity_metrics`
  GROUP BY source_version, season, week, player_id_internal
)
SELECT COUNT(*) AS invalid_duplicate_count
FROM grain_counts
WHERE row_count > 1;
