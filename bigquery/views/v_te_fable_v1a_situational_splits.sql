-- Source-backed TE Fable v1.0a season/split inputs before qualification and scoring.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_situational_splits` AS
WITH standard AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.te_situational_metrics`
  WHERE refinement = 'standard'
),
red_zone AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.te_situational_metrics`
  WHERE refinement = 'red_zone'
),
vs_man AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.te_situational_metrics`
  WHERE refinement = 'vs_man'
),
regular_season AS (
  SELECT season, player_id_internal, games
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_season_advanced_metrics`
  WHERE metric_version = 'advanced_player_metrics_v1'
    AND season_type = 'REG'
    AND position = 'TE'
    AND season BETWEEN 2022 AND 2025
),
demographics AS (
  SELECT
    gsis_id AS player_id_internal,
    ARRAY_AGG(birth_date IGNORE NULLS ORDER BY updated_at DESC LIMIT 1)[SAFE_OFFSET(0)] AS birth_date
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_identity_bridge`
  WHERE gsis_id IS NOT NULL
  GROUP BY gsis_id
),
raw_receiving AS (
  SELECT
    season,
    player_id,
    SUM(targets) AS targets,
    SUM(receiving_tds) AS receiving_touchdowns
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_weekly`
  WHERE position = 'TE'
    AND season BETWEEN 2022 AND 2025
    AND week BETWEEN 1 AND 18
  GROUP BY season, player_id
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
  standard.target_share,
  standard.total_epa,
  standard.targets_per_route_run,
  standard.yprr,
  red_zone.routes_run AS red_zone_routes_run,
  red_zone.targets_per_route_run AS red_zone_targets_per_route_run,
  vs_man.routes_run AS vs_man_routes_run,
  vs_man.yprr AS vs_man_yprr,
  raw_receiving.targets,
  raw_receiving.receiving_touchdowns
FROM standard
LEFT JOIN red_zone USING (season, situational_player_id)
LEFT JOIN vs_man USING (season, situational_player_id)
LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_identity_bridge` AS identity
  ON identity.situational_player_id = standard.situational_player_id
 AND identity.player_slug = standard.player_slug
LEFT JOIN regular_season AS season_data
  ON season_data.season = standard.season
 AND season_data.player_id_internal = identity.candidate_internal_player_id
LEFT JOIN demographics
  ON demographics.player_id_internal = identity.candidate_internal_player_id
LEFT JOIN raw_receiving
  ON raw_receiving.season = standard.season
 AND raw_receiving.player_id = identity.candidate_internal_player_id;
