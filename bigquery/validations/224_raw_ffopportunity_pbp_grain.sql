-- Validation helper. Render placeholders before running manually.
-- Expected result: invalid_duplicate_count = 0

WITH pass_grain AS (
  SELECT
    source_version,
    season,
    week,
    game_id,
    play_id,
    COALESCE(receiver_player_id_internal, '') AS receiver_key,
    COALESCE(passer_player_id_internal, '') AS passer_key,
    COUNT(*) AS row_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.raw_ffopportunity_pbp_pass`
  GROUP BY source_version, season, week, game_id, play_id, receiver_key, passer_key
),
rush_grain AS (
  SELECT
    source_version,
    season,
    week,
    game_id,
    play_id,
    rusher_player_id_internal,
    COUNT(*) AS row_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.raw_ffopportunity_pbp_rush`
  GROUP BY source_version, season, week, game_id, play_id, rusher_player_id_internal
),
duplicates AS (
  SELECT row_count FROM pass_grain WHERE row_count > 1
  UNION ALL
  SELECT row_count FROM rush_grain WHERE row_count > 1
)
SELECT COUNT(*) AS invalid_duplicate_count
FROM duplicates;
