-- Source-backed RB Fable 01 season/split inputs before qualification and scoring.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_situational_splits` AS
WITH standard AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.rb_situational_metrics`
  WHERE refinement = 'standard'
),
non_garbage AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.rb_situational_metrics`
  WHERE refinement = 'non_garbage_time'
),
red_zone AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.rb_situational_metrics`
  WHERE refinement = 'red_zone'
),
stacked_box AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.rb_situational_metrics`
  WHERE refinement = '8-plus-box-defenders'
),
regular_season AS (
  SELECT season, player_id_internal, games
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_season_advanced_metrics`
  WHERE metric_version = 'advanced_player_metrics_v1'
    AND season_type = 'REG'
    AND position = 'RB'
    AND season BETWEEN 2022 AND 2025
),
demographics AS (
  SELECT
    gsis_id AS player_id_internal,
    ARRAY_AGG(birth_date IGNORE NULLS ORDER BY updated_at DESC LIMIT 1)[SAFE_OFFSET(0)] AS birth_date
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_identity_bridge`
  WHERE gsis_id IS NOT NULL
  GROUP BY gsis_id
)
SELECT
  standard.season,
  standard.situational_player_id,
  standard.player_name,
  standard.player_slug,
  standard.team,
  identity.candidate_internal_player_id,
  identity.identity_status,
  identity.identity_confidence,
  identity.duplicate_identity_collision,
  season_data.games AS games_played,
  demographics.birth_date,
  CASE
    WHEN demographics.birth_date IS NULL THEN NULL
    ELSE DATE_DIFF(DATE(standard.season, 9, 1), demographics.birth_date, YEAR)
      - IF(FORMAT_DATE('%m%d', DATE(standard.season, 9, 1)) < FORMAT_DATE('%m%d', demographics.birth_date), 1, 0)
  END AS age,
  standard.rushes AS standard_rushes,
  standard.receptions AS standard_receptions,
  standard.rush_yards AS standard_rush_yards,
  standard.receiving_yards AS standard_receiving_yards,
  standard.rush_td AS standard_rush_td,
  standard.receiving_td AS standard_receiving_td,
  standard.yards_per_carry,
  standard.total_epa,
  standard.epa_per_rush,
  standard.success_pct,
  standard.explosive_pct,
  standard.first_down_pct,
  standard.tfl_pct,
  standard.target_share,
  standard.avg_box_defenders,
  standard.yards_after_contact,
  standard.yac,
  non_garbage.rushes AS non_garbage_time_rushes,
  non_garbage.receptions AS non_garbage_time_receptions,
  red_zone.rushes AS red_zone_rushes,
  red_zone.receptions AS red_zone_receptions,
  red_zone.rush_td AS red_zone_rush_td,
  red_zone.receiving_td AS red_zone_receiving_td,
  stacked_box.rushes AS stacked_box_rushes,
  stacked_box.yards_per_carry AS stacked_box_yards_per_carry
FROM standard
LEFT JOIN non_garbage USING (season, situational_player_id)
LEFT JOIN red_zone USING (season, situational_player_id)
LEFT JOIN stacked_box USING (season, situational_player_id)
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.situational_identity_bridge_review` AS identity
  ON identity.source_position = 'RB'
 AND identity.situational_player_id = standard.situational_player_id
 AND identity.player_slug = standard.player_slug
LEFT JOIN regular_season AS season_data
  ON season_data.season = standard.season
 AND season_data.player_id_internal = identity.candidate_internal_player_id
LEFT JOIN demographics
  ON demographics.player_id_internal = identity.candidate_internal_player_id;
