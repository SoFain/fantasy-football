-- Expected result: invalid_feature_count = 0

SELECT COUNT(*) AS invalid_feature_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE (ngs_receiving_efficiency_score_3yr IS NOT NULL AND ngs_receiving_efficiency_score_3yr NOT BETWEEN 0 AND 100)
   OR (ngs_yac_over_expected_score_3yr IS NOT NULL AND ngs_yac_over_expected_score_3yr NOT BETWEEN 0 AND 100)
   OR (ngs_separation_score_3yr IS NOT NULL AND ngs_separation_score_3yr NOT BETWEEN 0 AND 100)
   OR (ngs_catch_over_expected_score_3yr IS NOT NULL AND ngs_catch_over_expected_score_3yr NOT BETWEEN 0 AND 100)
   OR (ngs_rushing_efficiency_score_3yr IS NOT NULL AND ngs_rushing_efficiency_score_3yr NOT BETWEEN 0 AND 100)
   OR (ngs_rush_yards_over_expected_score_3yr IS NOT NULL AND ngs_rush_yards_over_expected_score_3yr NOT BETWEEN 0 AND 100)
   OR (ngs_box_resilience_score_3yr IS NOT NULL AND ngs_box_resilience_score_3yr NOT BETWEEN 0 AND 100)
   OR (ngs_qb_passing_efficiency_score_3yr IS NOT NULL AND ngs_qb_passing_efficiency_score_3yr NOT BETWEEN 0 AND 100);
