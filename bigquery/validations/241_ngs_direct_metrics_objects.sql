-- Expected result: missing_object_or_column_count = 0

WITH expected_columns AS (
  SELECT 'player_week_ngs_metrics' AS table_name, column_name
  FROM UNNEST([
    'source_version',
    'season',
    'week',
    'player_id_internal',
    'position',
    'ngs_receiving_efficiency_score',
    'ngs_rushing_efficiency_score',
    'ngs_passing_efficiency_score',
    'ngs_missing_flags_json',
    'source_provenance_json'
  ]) AS column_name
  UNION ALL
  SELECT 'ranking_backtest_feature_mart' AS table_name, column_name
  FROM UNNEST([
    'ngs_receiving_efficiency_score_3yr',
    'ngs_yac_over_expected_score_3yr',
    'ngs_separation_score_3yr',
    'ngs_catch_over_expected_score_3yr',
    'ngs_rushing_efficiency_score_3yr',
    'ngs_rush_yards_over_expected_score_3yr',
    'ngs_box_resilience_score_3yr',
    'ngs_qb_passing_efficiency_score_3yr',
    'ngs_missing_flags_json'
  ]) AS column_name
)
SELECT COUNT(*) AS missing_object_or_column_count
FROM expected_columns expected
WHERE NOT EXISTS (
  SELECT 1
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS` columns_info
  WHERE columns_info.table_name = expected.table_name
    AND columns_info.column_name = expected.column_name
);
