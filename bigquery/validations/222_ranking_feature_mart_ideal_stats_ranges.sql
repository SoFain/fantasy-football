-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_feature_rows = 0

SELECT COUNT(*) AS invalid_feature_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE xfp_score_3yr < 0
   OR xfp_score_3yr > 100
   OR xfp_share_3yr < 0
   OR xfp_share_3yr > 1
   OR offensive_snap_share_3yr < 0
   OR offensive_snap_share_3yr > 1
   OR snap_role_stability_3yr < 0
   OR snap_role_stability_3yr > 100
   OR receiving_role_dominance_xfp_3yr < 0
   OR receiving_role_dominance_xfp_3yr > 100
   OR high_value_xfp_score_3yr < 0
   OR high_value_xfp_score_3yr > 100
   OR qb_ngs_efficiency_score_3yr < 0
   OR qb_ngs_efficiency_score_3yr > 100
   OR injury_risk_score_3yr < 0
   OR injury_risk_score_3yr > 100
   OR depth_chart_role_score_3yr < 0
   OR depth_chart_role_score_3yr > 100;
