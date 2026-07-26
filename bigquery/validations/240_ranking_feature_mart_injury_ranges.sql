-- Validation: feature mart injury context features are bounded when populated.
-- Expected result: invalid_feature_count = 0

SELECT COUNT(1) AS invalid_feature_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_feature_mart`
WHERE injury_status_score_3yr < 0
   OR injury_status_score_3yr > 100
   OR injury_burden_score_3yr < 0
   OR injury_burden_score_3yr > 100
   OR missed_time_risk_score_3yr < 0
   OR missed_time_risk_score_3yr > 100
   OR availability_score_3yr < 0
   OR availability_score_3yr > 100
   OR (
        injury_context_missing_flags_json IS NULL
        AND (
          injury_status_score_3yr IS NOT NULL
          OR injury_burden_score_3yr IS NOT NULL
          OR missed_time_risk_score_3yr IS NOT NULL
          OR availability_score_3yr IS NOT NULL
        )
      );
