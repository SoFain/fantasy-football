-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_feature_count = 0

SELECT COUNT(*) AS invalid_feature_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE receiving_xfp_pbp_3yr < 0
   OR rushing_xfp_pbp_3yr < 0
   OR red_zone_xfp_score_3yr < 0
   OR red_zone_xfp_score_3yr > 100
   OR goal_line_xfp_score_3yr < 0
   OR goal_line_xfp_score_3yr > 100
   OR high_value_target_xfp_score_3yr < 0
   OR high_value_rush_xfp_score_3yr < 0
   OR receiving_xfp_share_pbp_3yr < 0
   OR receiving_xfp_share_pbp_3yr > 1
   OR rushing_xfp_share_pbp_3yr < 0
   OR rushing_xfp_share_pbp_3yr > 1
   OR opportunity_quality_score_3yr < 0
   OR opportunity_quality_score_3yr > 100;
