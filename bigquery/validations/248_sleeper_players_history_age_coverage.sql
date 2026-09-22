-- Validation helper. Render placeholders before running manually.
-- Age drives the dynasty and value curves. Missing age on a rostered fantasy
-- player is the gap this ingest was extended to close.
-- Expected result: missing_age_rows should be low

SELECT COUNT(*) AS missing_age_rows
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_history`
WHERE snapshot_at = (SELECT MAX(snapshot_at) FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_history`)
  AND team IS NOT NULL
  AND position IN ('QB', 'RB', 'WR', 'TE')
  AND age IS NULL;
