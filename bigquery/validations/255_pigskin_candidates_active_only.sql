-- Validation helper. Render placeholders before running manually.
-- Hard rule: only Sleeper-active players may be ranking candidates. A row with
-- sleeper_active not TRUE means the active filter regressed.
-- Expected result: zero rows

SELECT position, player_name, sleeper_player_id, sleeper_active
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_pigskin_rankings_candidates`
WHERE sleeper_active IS DISTINCT FROM TRUE
LIMIT 100;
