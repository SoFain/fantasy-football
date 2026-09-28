-- Validation: RB weighted-opportunity diagnostic columns exist and remain bounded.
-- Expected result: invalid_feature_count = 0.

WITH required_columns AS (
  SELECT column_name
  FROM UNNEST([
    'red_zone_carries',
    'outside_red_zone_targets',
    'outside_red_zone_carries',
    'gemini31_rb_weighted_opportunity_ppr'
  ]) AS column_name
),
missing_columns AS (
  SELECT required_columns.column_name
  FROM required_columns
  LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS` columns_meta
    ON columns_meta.table_name = 'ranking_backtest_feature_mart'
   AND columns_meta.column_name = required_columns.column_name
  WHERE columns_meta.column_name IS NULL
),
invalid_values AS (
  SELECT COUNT(*) AS invalid_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
  WHERE scoring_profile_id = 'ppr'
    AND position = 'RB'
    AND target_season BETWEEN 2017 AND 2025
    AND (
      red_zone_carries < 0
      OR outside_red_zone_targets < 0
      OR outside_red_zone_carries < 0
      OR gemini31_rb_weighted_opportunity_ppr < 0
    )
)
SELECT
  (SELECT COUNT(*) FROM missing_columns) + (SELECT invalid_count FROM invalid_values) AS invalid_feature_count;
