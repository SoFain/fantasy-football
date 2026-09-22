-- Team-season offensive environment score for WR Fable v1.1. Source-backed, season-local z-scores.
-- For folds, only the input season's environment is ever consumed (prior-season info for the target season).
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_team_environment` AS
WITH game_sides AS (
  SELECT season, week,
    JSON_VALUE(raw_payload_json, '$.home_team') AS team,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.home_score') AS FLOAT64) AS points_for,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.away_score') AS FLOAT64) AS points_against
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_schedules`
  WHERE season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  UNION ALL
  SELECT season, week,
    JSON_VALUE(raw_payload_json, '$.away_team'),
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.away_score') AS FLOAT64),
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.home_score') AS FLOAT64)
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_schedules`
  WHERE season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
),
team_results AS (
  SELECT season, team,
    AVG(points_for) AS offensive_points_per_game,
    AVG(CASE WHEN points_for > points_against THEN 1.0 WHEN points_for = points_against THEN 0.5 ELSE 0.0 END) AS win_percentage
  FROM game_sides
  WHERE points_for IS NOT NULL AND points_against IS NOT NULL
  GROUP BY season, team
),
qb_epa AS (
  SELECT season, team, SAFE_DIVIDE(SUM(passing_epa), SUM(dropbacks)) AS qb_passing_epa_per_dropback
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.qb_week_environment_metrics`
  WHERE season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, team
),
pass_plays AS (
  SELECT
    season,
    week,
    game_id,
    play_id,
    ANY_VALUE(posteam) AS team,
    ANY_VALUE(epa) AS epa
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.stg_play_player_events`
  WHERE season BETWEEN 2022 AND 2025
    AND week BETWEEN 1 AND 18
    AND pass_attempt
  GROUP BY season, week, game_id, play_id
),
pass_epa AS (
  SELECT season, team, AVG(epa) AS team_pass_epa_per_play
  FROM pass_plays
  WHERE team IS NOT NULL AND epa IS NOT NULL
  GROUP BY season, team
),
attempts AS (
  SELECT season, team, SAFE_DIVIDE(SUM(pass_attempts), COUNT(DISTINCT week)) AS pass_attempts_per_game
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.stg_team_week_stats`
  WHERE season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, team
),
joined AS (
  SELECT
    results.season,
    -- Canonical team code (LAR-style) so situational, Sleeper, and NFLverse codes can join.
    CASE results.team WHEN 'LA' THEN 'LAR' ELSE results.team END AS team,
    qb_epa.qb_passing_epa_per_dropback,
    pass_epa.team_pass_epa_per_play,
    attempts.pass_attempts_per_game,
    results.offensive_points_per_game,
    results.win_percentage
  FROM team_results AS results
  LEFT JOIN qb_epa USING (season, team)
  LEFT JOIN pass_epa USING (season, team)
  LEFT JOIN attempts USING (season, team)
),
scored AS (
  SELECT
    joined.*,
    0.35 * SAFE_DIVIDE(qb_passing_epa_per_dropback - AVG(qb_passing_epa_per_dropback) OVER (PARTITION BY season), STDDEV_POP(qb_passing_epa_per_dropback) OVER (PARTITION BY season))
    + 0.20 * SAFE_DIVIDE(team_pass_epa_per_play - AVG(team_pass_epa_per_play) OVER (PARTITION BY season), STDDEV_POP(team_pass_epa_per_play) OVER (PARTITION BY season))
    + 0.20 * SAFE_DIVIDE(pass_attempts_per_game - AVG(pass_attempts_per_game) OVER (PARTITION BY season), STDDEV_POP(pass_attempts_per_game) OVER (PARTITION BY season))
    + 0.15 * SAFE_DIVIDE(offensive_points_per_game - AVG(offensive_points_per_game) OVER (PARTITION BY season), STDDEV_POP(offensive_points_per_game) OVER (PARTITION BY season))
    + 0.10 * SAFE_DIVIDE(win_percentage - AVG(win_percentage) OVER (PARTITION BY season), STDDEV_POP(win_percentage) OVER (PARTITION BY season))
    AS team_environment_score
  FROM joined
)
SELECT
  scored.*,
  SAFE_DIVIDE(team_environment_score - AVG(team_environment_score) OVER (PARTITION BY season),
              STDDEV_POP(team_environment_score) OVER (PARTITION BY season)) AS team_environment_z
FROM scored;
