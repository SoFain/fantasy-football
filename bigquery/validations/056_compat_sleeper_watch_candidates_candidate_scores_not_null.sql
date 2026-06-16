-- Validation helper. Render placeholders before running manually.
-- Expected result: missing_streamer_score_rows = 0.

SELECT
    'compat_sleeper_watch_candidates_candidate_scores_not_null' AS validation_name,
    COUNT(*) AS row_count,
    COUNTIF(streamer_score IS NULL) AS missing_streamer_score_rows,
    COUNTIF(breakout_score IS NULL) AS missing_breakout_score_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.compat_sleeper_watch_candidates`;
