-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_metric_rows = 0

SELECT COUNT(*) AS invalid_metric_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_ideal_opportunity_metrics`
WHERE xfp_share < 0
   OR xfp_share > 1
   OR xfp_score < 0
   OR xfp_score > 100
   OR high_value_xfp_score < 0
   OR high_value_xfp_score > 100
   OR offensive_snap_share < 0
   OR offensive_snap_share > 1
   OR role_stability_from_snaps < 0
   OR role_stability_from_snaps > 100
   OR receiving_role_dominance_xfp < 0
   OR receiving_role_dominance_xfp > 100
   OR goal_line_usage_score < 0
   OR goal_line_usage_score > 100
   OR red_zone_usage_score < 0
   OR red_zone_usage_score > 100
   OR qb_ngs_efficiency_score < 0
   OR qb_ngs_efficiency_score > 100
   OR injury_risk_score < 0
   OR injury_risk_score > 100
   OR depth_chart_role_score < 0
   OR depth_chart_role_score > 100;
