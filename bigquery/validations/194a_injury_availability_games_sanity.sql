-- Validation helper. Verify injury direction, NGS coverage, games logic, and metadata structures.
-- Expected result: invalid_rows = 0

SELECT COUNT(*) AS invalid_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_season_advanced_metrics`
WHERE metric_version = 'advanced_player_metrics_v1'
  AND (
    -- Availability Direction check: higher is healthier (max 100)
    availability_score < 0.0 OR availability_score > 100.0
    OR injury_burden_score < 0.0 OR injury_burden_score > 100.0
    
    -- Healthy players should have 100% availability and 0 burden
    OR (injury_burden_score = 0.0 AND availability_score != 100.0)
    
    -- Missed time risk score check (total weeks out must be non-negative)
    OR missed_time_risk_score < 0.0
    
    -- NGS season-level rules: 2014-2015 must be UNAVAILABLE and NGS fields null
    OR (season < 2016 AND (
         ngs_source_status != 'UNAVAILABLE' 
         OR ngs_avg_separation IS NOT NULL 
         OR ngs_rush_yards_over_expected IS NOT NULL 
         OR ngs_qb_cpoe IS NOT NULL
       ))
       
    -- NGS 2016+ rules: must be AVAILABLE
    OR (season >= 2016 AND ngs_source_status != 'AVAILABLE')
    
    -- Metadata columns check (must be present and populated)
    OR source_coverage_json IS NULL
    OR missing_flags_json IS NULL
    OR proxy_flags_json IS NULL
    OR blocked_flags_json IS NULL
  );
