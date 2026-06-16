-- Production compatibility view for Player Profiles.
-- Backing table is refreshed by src/materialize_player_profiles.py.
-- Replaces future reads in fetch_player_profiles_data, app.py:1090-1275.

CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.compat_player_profiles_current` AS
SELECT *
FROM `{{PROJECT_ID}}.{{DATASET_ID}}.mart_player_profiles_current`;
