-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_metric_count = 0

SELECT COUNT(*) AS invalid_metric_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_week_pbp_opportunity_metrics`
WHERE receiving_xfp_pbp < 0
   OR target_xfp < 0
   OR air_xfp < 0
   OR red_zone_target_xfp < 0
   OR goal_line_target_xfp < 0
   OR high_value_target_xfp < 0
   OR receiving_touchdown_xfp < 0
   OR receiving_xfp_share < 0
   OR receiving_xfp_share > 1
   OR rushing_xfp_pbp < 0
   OR red_zone_rush_xfp < 0
   OR goal_line_rush_xfp < 0
   OR high_value_rush_xfp < 0
   OR rushing_touchdown_xfp < 0
   OR rushing_xfp_share < 0
   OR rushing_xfp_share > 1
   OR high_value_xfp_score < 0
   OR high_value_xfp_score > 100
   OR red_zone_xfp_score < 0
   OR red_zone_xfp_score > 100
   OR goal_line_xfp_score < 0
   OR goal_line_xfp_score > 100
   OR opportunity_quality_score < 0
   OR opportunity_quality_score > 100
   OR receiving_first_down_exp_pbp < 0
   OR rushing_first_down_exp_pbp < 0
   OR passing_first_down_exp_pbp < 0
   OR high_value_first_down_opportunity_score < 0
   OR high_value_first_down_opportunity_score > 100
   OR receiving_chain_mover_score < 0
   OR receiving_chain_mover_score > 100
   OR rushing_chain_mover_score < 0
   OR rushing_chain_mover_score > 100;
