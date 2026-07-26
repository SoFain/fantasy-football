-- Validation: ranking feature mart has injury context columns.
-- Expected result: missing_column_count = 0

WITH expected_columns AS (
  SELECT 'injury_status_score_3yr' AS column_name UNION ALL
  SELECT 'injury_burden_score_3yr' UNION ALL
  SELECT 'missed_time_risk_score_3yr' UNION ALL
  SELECT 'availability_score_3yr' UNION ALL
  SELECT 'injury_context_missing_flags_json'
),
actual_columns AS (
  SELECT column_name
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.INFORMATION_SCHEMA.COLUMNS`
  WHERE table_name = 'ranking_backtest_feature_mart'
)
SELECT COUNT(1) AS missing_column_count
FROM expected_columns
LEFT JOIN actual_columns USING (column_name)
WHERE actual_columns.column_name IS NULL;
