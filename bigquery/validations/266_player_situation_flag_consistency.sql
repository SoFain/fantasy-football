-- Validation helper. Render placeholders before running manually.
-- NEW_TEAM flag must agree with team_changed.
-- Expected result: zero rows

SELECT situation_for_season, player_name
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_situation`
WHERE team_changed != (STRPOS(flags_json, 'NEW_TEAM') > 0)
LIMIT 50;
