-- Phase 35.1D WR team environment. Uses input-season team and passing context only.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_team_environment` AS
WITH source_metrics AS (
  SELECT
    season,
    team,
    qb_passing_epa_per_dropback,
    team_pass_epa_per_play,
    pass_attempts_per_game,
    offensive_points_per_game,
    win_percentage
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_team_environment`
  WHERE season BETWEEN 2022 AND 2025
), standardized AS (
  SELECT
    source_metrics.*,
    SAFE_DIVIDE(
      qb_passing_epa_per_dropback - AVG(qb_passing_epa_per_dropback) OVER (PARTITION BY season),
      STDDEV_POP(qb_passing_epa_per_dropback) OVER (PARTITION BY season)
    ) AS z_qb_passing_epa_per_dropback,
    SAFE_DIVIDE(
      team_pass_epa_per_play - AVG(team_pass_epa_per_play) OVER (PARTITION BY season),
      STDDEV_POP(team_pass_epa_per_play) OVER (PARTITION BY season)
    ) AS z_team_pass_epa_per_play,
    SAFE_DIVIDE(
      pass_attempts_per_game - AVG(pass_attempts_per_game) OVER (PARTITION BY season),
      STDDEV_POP(pass_attempts_per_game) OVER (PARTITION BY season)
    ) AS z_pass_attempts_per_game,
    SAFE_DIVIDE(
      offensive_points_per_game - AVG(offensive_points_per_game) OVER (PARTITION BY season),
      STDDEV_POP(offensive_points_per_game) OVER (PARTITION BY season)
    ) AS z_offensive_points_per_game,
    SAFE_DIVIDE(
      win_percentage - AVG(win_percentage) OVER (PARTITION BY season),
      STDDEV_POP(win_percentage) OVER (PARTITION BY season)
    ) AS z_win_percentage
  FROM source_metrics
)
SELECT
  standardized.*,
  0.45 * z_qb_passing_epa_per_dropback
    + 0.25 * z_team_pass_epa_per_play
    + 0.15 * z_pass_attempts_per_game
    + 0.10 * z_offensive_points_per_game
    + 0.05 * z_win_percentage AS team_environment_score
FROM standardized;
