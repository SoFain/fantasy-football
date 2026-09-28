-- Validation: injury context features use seasons strictly before the target season.
-- Expected result: leaked_feature_count = 0

SELECT COUNT(1) AS leaked_feature_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE source_window_end_season >= target_season
  AND (
    injury_status_score_3yr IS NOT NULL
    OR injury_burden_score_3yr IS NOT NULL
    OR missed_time_risk_score_3yr IS NOT NULL
    OR availability_score_3yr IS NOT NULL
  );
