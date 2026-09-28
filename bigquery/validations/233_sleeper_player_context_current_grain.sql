-- Validation: current Sleeper context has one latest row per Sleeper player.
-- Expected result: duplicate_player_count = 0.

SELECT COUNT(1) AS duplicate_player_count
FROM (
  SELECT
    sleeper_player_id,
    COUNT(1) AS player_row_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_player_context_current`
  GROUP BY sleeper_player_id
  HAVING COUNT(1) > 1
);
