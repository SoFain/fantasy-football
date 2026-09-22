-- Validation helper. Render placeholders before running manually.
-- Every transition season 2016-2025 must be present; a missing season means a
-- cross-season identity join silently broke (the 'gsis:' prefix defect).
-- Expected result: season_count = 11

SELECT COUNT(DISTINCT situation_for_season) AS season_count
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.analytics_player_situation`;
