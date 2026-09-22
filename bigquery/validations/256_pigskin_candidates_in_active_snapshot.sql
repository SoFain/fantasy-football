-- Validation helper. Render placeholders before running manually.
-- Every candidate must trace to an active player in the latest Sleeper
-- snapshot. Catches candidates built from a stale or non-Sleeper source.
-- Expected result: zero rows

WITH latest AS (
    SELECT MAX(snapshot_at) AS max_snapshot_at
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_current`
),
active_ids AS (
    SELECT sp.sleeper_player_id
    FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_players_current` sp, latest
    WHERE sp.snapshot_at = latest.max_snapshot_at
      AND sp.active IS TRUE
)
SELECT c.position, c.player_name, c.sleeper_player_id
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings_candidates` c
WHERE c.sleeper_player_id IS NULL
   OR c.sleeper_player_id NOT IN (SELECT sleeper_player_id FROM active_ids)
LIMIT 100;
