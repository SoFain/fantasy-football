-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_column_count = 0

WITH expected_columns AS (
    SELECT 'qb_rushing_leverage_index' AS column_name UNION ALL
    SELECT 'rb_high_value_opportunity_score' UNION ALL
    SELECT 'receiving_role_dominance_score' UNION ALL
    SELECT 'red_zone_usage_score' UNION ALL
    SELECT 'goal_line_usage_score' UNION ALL
    SELECT 'team_environment_score' UNION ALL
    SELECT 'spike_week_rate_3yr' UNION ALL
    SELECT 'bust_week_rate_3yr' UNION ALL
    SELECT 'elite_week_rate_3yr'
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
