-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_column_count = 0

WITH expected_columns AS (
    SELECT 'xfp_score_3yr' AS column_name UNION ALL
    SELECT 'xfp_share_3yr' UNION ALL
    SELECT 'fantasy_points_over_expectation_3yr' UNION ALL
    SELECT 'offensive_snap_share_3yr' UNION ALL
    SELECT 'snap_role_stability_3yr' UNION ALL
    SELECT 'receiving_role_dominance_xfp_3yr' UNION ALL
    SELECT 'high_value_xfp_score_3yr' UNION ALL
    SELECT 'qb_ngs_efficiency_score_3yr' UNION ALL
    SELECT 'injury_risk_score_3yr' UNION ALL
    SELECT 'depth_chart_role_score_3yr'
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
