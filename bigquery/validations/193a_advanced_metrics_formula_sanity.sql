-- Validation helper. Verify mathematical correctness and opportunity bounds in seasonal table.
-- Expected result: invalid_formula_rows = 0

SELECT COUNT(*) AS invalid_formula_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_season_advanced_metrics`
WHERE metric_version = 'advanced_player_metrics_v1'
  AND (
    -- Opportunities sum check
    ABS(red_zone_opportunities - (red_zone_targets + red_zone_carries)) > 0.001
    OR ABS(goal_line_opportunities - (goal_line_targets + goal_line_carries)) > 0.001
    
    -- WOPR formula consistency
    OR ABS(wopr - (1.5 * COALESCE(target_share, 0.0) + 0.7 * COALESCE(air_yards_share, 0.0))) > 0.001
    
    -- standard weighted opportunity check
    OR ABS(
         weighted_opportunity_standard - (
           (COALESCE(red_zone_targets, 0.0) * 1.47) + 
           (GREATEST(0.0, COALESCE(targets, 0.0) - COALESCE(red_zone_targets, 0.0)) * 0.67) + 
           (COALESCE(red_zone_carries, 0.0) * 1.28) + 
           (GREATEST(0.0, COALESCE(carries, 0.0) - COALESCE(red_zone_carries, 0.0)) * 0.47)
         )
       ) > 0.001
       
    -- ppr weighted opportunity check
    OR ABS(
         weighted_opportunity_ppr - (
           (COALESCE(red_zone_targets, 0.0) * 2.39) + 
           (GREATEST(0.0, COALESCE(targets, 0.0) - COALESCE(red_zone_targets, 0.0)) * 1.54) + 
           (COALESCE(red_zone_carries, 0.0) * 1.28) + 
           (GREATEST(0.0, COALESCE(carries, 0.0) - COALESCE(red_zone_carries, 0.0)) * 0.47)
         )
       ) > 0.001
  );
