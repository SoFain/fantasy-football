-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_column_count = 0

WITH expected_columns AS (
  SELECT 'receiving_xfp_pbp_3yr' AS column_name UNION ALL
  SELECT 'rushing_xfp_pbp_3yr' UNION ALL
  SELECT 'passing_xfp_pbp_3yr' UNION ALL
  SELECT 'red_zone_xfp_score_3yr' UNION ALL
  SELECT 'goal_line_xfp_score_3yr' UNION ALL
  SELECT 'high_value_target_xfp_score_3yr' UNION ALL
  SELECT 'high_value_rush_xfp_score_3yr' UNION ALL
  SELECT 'receiving_xfp_share_pbp_3yr' UNION ALL
  SELECT 'rushing_xfp_share_pbp_3yr' UNION ALL
  SELECT 'opportunity_quality_score_3yr' UNION ALL
  SELECT 'pbp_xfp_missing_flags_json'
),
actual_columns AS (
  SELECT column_name
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS`
  WHERE table_name = 'ranking_backtest_feature_mart'
)
SELECT COUNT(*) AS missing_column_count
FROM expected_columns
LEFT JOIN actual_columns USING (column_name)
WHERE actual_columns.column_name IS NULL;
