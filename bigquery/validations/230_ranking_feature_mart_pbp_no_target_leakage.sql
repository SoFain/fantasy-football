-- Validation helper. Render placeholders before running manually.
-- Expected result: leaked_feature_count = 0

SELECT COUNT(*) AS leaked_feature_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE source_window_end_season >= target_season
  AND (
    receiving_xfp_pbp_3yr IS NOT NULL
    OR rushing_xfp_pbp_3yr IS NOT NULL
    OR passing_xfp_pbp_3yr IS NOT NULL
    OR opportunity_quality_score_3yr IS NOT NULL
  );
