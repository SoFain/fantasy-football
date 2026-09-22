-- Validation helper. Render placeholders before running manually.
-- Expected result: duplicate_summary_rows = 0 and invalid_metric_rows = 0

WITH duplicate_summary_keys AS (
    SELECT
        backtest_run_id,
        candidate_id,
        position,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        target_name,
        COUNT(*) AS row_count
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_candidate_summaries`
    GROUP BY 1, 2, 3, 4, 5, 6, 7
    HAVING row_count > 1
),
invalid_metric_values AS (
    SELECT COUNT(*) AS invalid_metric_rows
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.ranking_backtest_candidate_summaries`
    WHERE sample_size < 0
       OR pairwise_win_rate < 0
       OR pairwise_win_rate > 1
       OR top_n_hit_rate < 0
       OR top_n_hit_rate > 1
       OR actual_points_captured_rate < 0
       OR actual_points_captured_rate > 1
       OR missing_input_rate < 0
       OR missing_input_rate > 1
       OR mean_absolute_error < 0
       OR regret_score < 0
       OR metric_json IS NULL
       OR missing_flags_json IS NULL
       OR source_freshness_json IS NULL
)
SELECT
    (SELECT COUNT(*) FROM duplicate_summary_keys) AS duplicate_summary_rows,
    invalid_metric_rows
FROM invalid_metric_values;
