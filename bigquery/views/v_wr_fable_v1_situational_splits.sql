-- Source-backed WR Fable v1 season/split inputs before qualification and scoring.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_situational_splits` AS
WITH standard AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.wr_situational_metrics`
  WHERE refinement = 'standard'
),
non_garbage AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.wr_situational_metrics`
  WHERE refinement = 'non_garbage_time'
),
red_zone AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.wr_situational_metrics`
  WHERE refinement = 'red_zone'
),
pbp_non_garbage AS (
  SELECT
    season,
    receiver_player_id AS player_id_internal,
    COUNTIF(
      SAFE_CAST(JSON_VALUE(raw_payload_json, '$.pass_attempt') AS FLOAT64) = 1
      AND SAFE_CAST(JSON_VALUE(raw_payload_json, '$.wp') AS FLOAT64) BETWEEN 0.05 AND 0.95
    ) AS sourced_non_garbage_targets
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_pbp`
  WHERE season BETWEEN 2022 AND 2025
    AND receiver_player_id IS NOT NULL
  GROUP BY season, player_id_internal
),
regular_season AS (
  SELECT
    season,
    player_id_internal,
    games,
    red_zone_targets AS sourced_red_zone_targets
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_season_advanced_metrics`
  WHERE metric_version = 'advanced_player_metrics_v1'
    AND season_type = 'REG'
    AND position = 'WR'
    AND season BETWEEN 2022 AND 2025
),
pbp_red_zone AS (
  SELECT
    season,
    player_id_internal,
    COUNTIF(event_type = 'target' AND yardline_100 <= 20 AND touchdown) AS sourced_red_zone_touchdowns
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.stg_play_player_events`
  WHERE season BETWEEN 2022 AND 2025
  GROUP BY season, player_id_internal
),
demographics AS (
  SELECT
    gsis_id AS player_id_internal,
    ARRAY_AGG(birth_date IGNORE NULLS ORDER BY updated_at DESC LIMIT 1)[SAFE_OFFSET(0)] AS birth_date
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_identity_bridge`
  WHERE gsis_id IS NOT NULL
  GROUP BY gsis_id
),
raw_targets AS (
  -- Raw NFLverse season targets, regular season weeks 1-18. Canonical standard-season targets.
  SELECT season, player_id, SUM(targets) AS raw_targets, SUM(receiving_tds) AS raw_receiving_tds
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_weekly`
  WHERE position = 'WR' AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, player_id
),
air_yards AS (
  -- Season air-yards share: player intended air yards over team intended air yards, REG weeks.
  -- Weekly nulls represent zero-target weeks and contribute nothing to either sum.
  SELECT
    player_weeks.season,
    player_weeks.player_id_internal,
    SAFE_DIVIDE(SUM(player_weeks.receiving_air_yards), SUM(team_weeks.team_air_yards)) AS air_yards_share,
    AVG(player_weeks.wopr) AS stored_wopr_weekly_avg
  FROM (
    SELECT season, week, team, player_id_internal, receiving_air_yards, wopr
    FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_week_advanced_metrics`
    WHERE season BETWEEN 2022 AND 2025 AND season_type = 'REG'
  ) AS player_weeks
  JOIN (
    SELECT season, week, team, SUM(receiving_air_yards) AS team_air_yards
    FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_week_advanced_metrics`
    WHERE season BETWEEN 2022 AND 2025 AND season_type = 'REG'
    GROUP BY season, week, team
  ) AS team_weeks
    ON team_weeks.season = player_weeks.season
   AND team_weeks.week = player_weeks.week
   AND team_weeks.team = player_weeks.team
  GROUP BY player_weeks.season, player_weeks.player_id_internal
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
  standard.routes_run,
  standard.receptions,
  standard.receiving_yards,
  standard.target_share,
  standard.touchdowns AS receiving_touchdowns,
  standard.yac,
  standard.adot,
  standard.catch_pct,
  standard.total_epa,
  standard.targets_per_route_run,
  standard.yprr,
  non_garbage.situational_player_id IS NULL AS non_garbage_structural_fallback,
  CASE WHEN non_garbage.situational_player_id IS NULL
    THEN 'PBP_WP_5_95' ELSE 'SITUATIONAL_SPLIT' END AS non_garbage_input_method,
  pbp_non_garbage.sourced_non_garbage_targets,
  non_garbage.routes_run AS non_garbage_time_routes_run,
  non_garbage.targets_per_route_run AS non_garbage_time_targets_per_route_run,
  red_zone.situational_player_id IS NULL AS red_zone_structural_fallback,
  CASE WHEN red_zone.situational_player_id IS NULL
    THEN 'ADVANCED_TARGETS_PBP_TDS' ELSE 'SITUATIONAL_SPLIT' END AS red_zone_input_method,
  season_data.sourced_red_zone_targets,
  red_zone.routes_run AS red_zone_routes_run,
  red_zone.targets_per_route_run AS red_zone_targets_per_route_run,
  red_zone.receptions AS red_zone_receptions,
  CASE WHEN red_zone.situational_player_id IS NULL
    THEN pbp_red_zone.sourced_red_zone_touchdowns ELSE red_zone.touchdowns END AS red_zone_touchdowns,
  raw_targets.raw_targets AS targets,
  raw_targets.raw_receiving_tds,
  air_yards.air_yards_share,
  air_yards.stored_wopr_weekly_avg
FROM standard
LEFT JOIN non_garbage USING (season, situational_player_id)
LEFT JOIN red_zone USING (season, situational_player_id)
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_identity_bridge` AS identity
  ON identity.situational_player_id = standard.situational_player_id
 AND identity.player_slug = standard.player_slug
LEFT JOIN regular_season AS season_data
  ON season_data.season = standard.season
 AND season_data.player_id_internal = identity.candidate_internal_player_id
LEFT JOIN pbp_non_garbage
  ON pbp_non_garbage.season = standard.season
 AND pbp_non_garbage.player_id_internal = identity.candidate_internal_player_id
LEFT JOIN pbp_red_zone
  ON pbp_red_zone.season = standard.season
 AND pbp_red_zone.player_id_internal = identity.candidate_internal_player_id
LEFT JOIN demographics
  ON demographics.player_id_internal = identity.candidate_internal_player_id
LEFT JOIN raw_targets
  ON raw_targets.season = standard.season
 AND raw_targets.player_id = identity.candidate_internal_player_id
LEFT JOIN air_yards
  ON air_yards.season = standard.season
 AND air_yards.player_id_internal = identity.candidate_internal_player_id;
