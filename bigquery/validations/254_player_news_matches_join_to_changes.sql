-- Validation helper. Render placeholders before running manually.
-- Every news match should trace back to a change that triggered the fetch.
-- Expected result: orphaned_match_rows = 0

SELECT COUNT(*) AS orphaned_match_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_news_matches` m
WHERE NOT EXISTS (
    SELECT 1
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.player_status_changes` c
    WHERE c.sleeper_player_id = m.sleeper_player_id
      AND c.triggers_news_check
      AND DATE(c.detected_at) = DATE(m.fetched_at)
);
