-- Validation helper. Render placeholders before running manually.
-- Change detection needs two snapshots to diff. One snapshot means the daily
-- job has run only once since the history table was created.
-- Expected result: snapshot_count > 1

SELECT COUNT(DISTINCT snapshot_at) AS snapshot_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_history`;
