-- Expected result: target_season_leak_count = 0

SELECT COUNT(*) AS target_season_leak_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE source_window_end_season >= target_season
  AND (
    ngs_receiving_efficiency_score_3yr IS NOT NULL
    OR ngs_rushing_efficiency_score_3yr IS NOT NULL
    OR ngs_qb_passing_efficiency_score_3yr IS NOT NULL
  );
