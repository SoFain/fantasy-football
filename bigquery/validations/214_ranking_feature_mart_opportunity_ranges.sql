-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_feature_rows = 0

SELECT COUNT(*) AS invalid_feature_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE qb_rushing_leverage_index < 0
   OR qb_rushing_leverage_index > 100
   OR rb_high_value_opportunity_score < 0
   OR rb_high_value_opportunity_score > 100
   OR receiving_role_dominance_score < 0
   OR receiving_role_dominance_score > 100
   OR red_zone_usage_score < 0
   OR red_zone_usage_score > 100
   OR goal_line_usage_score < 0
   OR goal_line_usage_score > 100
   OR team_environment_score < 0
   OR team_environment_score > 100
   OR spike_week_rate_3yr < 0
   OR spike_week_rate_3yr > 1
   OR bust_week_rate_3yr < 0
   OR bust_week_rate_3yr > 1
   OR elite_week_rate_3yr < 0
   OR elite_week_rate_3yr > 1;
