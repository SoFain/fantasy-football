-- Validation helper. Render placeholders before running manually.
-- End-to-end check on the current published rankings, the artifact the rule
-- protects. A non-active player appears if a row carries sleeper_active not
-- TRUE, or its sleeper_player_id is absent from the latest active snapshot.
--
-- Scoped to the most recent run date. analytics_pigskin_rankings accumulates
-- ranking_versions (an untracked generator appends alongside the tracked
-- WRITE_TRUNCATE pigskin-llm writer), so older archived versions are out of
-- scope; the rule governs the rankings currently in force. History lives in
-- analytics_pigskin_rankings_history.
-- Expected result: zero rows

WITH latest_snapshot AS (
    SELECT MAX(snapshot_at) AS max_snapshot_at
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_current`
),
active_ids AS (
    SELECT sp.sleeper_player_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_current` sp, latest_snapshot
    WHERE sp.snapshot_at = latest_snapshot.max_snapshot_at
      AND sp.active IS TRUE
),
latest_run AS (
    SELECT MAX(DATE(generated_at)) AS max_run_date
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings`
)
SELECT r.ranking_version, r.position, r.player_name, r.sleeper_player_id, r.sleeper_active
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings` r, latest_run
WHERE DATE(r.generated_at) = latest_run.max_run_date
  AND (
      r.sleeper_active IS DISTINCT FROM TRUE
      OR r.sleeper_player_id IS NULL
      OR r.sleeper_player_id NOT IN (SELECT sleeper_player_id FROM active_ids)
  )
LIMIT 100;
