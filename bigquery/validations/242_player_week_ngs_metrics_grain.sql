-- Expected result: duplicate_grain_count = 0

SELECT COUNT(*) AS duplicate_grain_count
FROM (
  SELECT
    source_version,
    season,
    week,
    player_id_internal,
    COALESCE(position, '') AS position_value,
    COUNT(*) AS record_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_ngs_metrics`
  GROUP BY source_version, season, week, player_id_internal, position_value
  HAVING COUNT(*) > 1
);
