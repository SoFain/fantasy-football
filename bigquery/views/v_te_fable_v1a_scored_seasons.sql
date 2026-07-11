-- TE Fable v1.0a scores for loaded seasons. Descriptive use for 2025; no future outcomes.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_scored_seasons` AS
WITH metric_stats AS (
  SELECT
    inputs.*,
    AVG(routes_per_game) OVER (PARTITION BY season) AS avg_routes,
    STDDEV_POP(routes_per_game) OVER (PARTITION BY season) AS sd_routes,
    AVG(target_share) OVER (PARTITION BY season) AS avg_target_share,
    STDDEV_POP(target_share) OVER (PARTITION BY season) AS sd_target_share,
    AVG(red_zone_targets_per_game) OVER (PARTITION BY season) AS avg_rz_targets,
    STDDEV_POP(red_zone_targets_per_game) OVER (PARTITION BY season) AS sd_rz_targets,
    AVG(targets_per_route_run) OVER (PARTITION BY season) AS avg_tprr,
    STDDEV_POP(targets_per_route_run) OVER (PARTITION BY season) AS sd_tprr,
    AVG(yprr) OVER (PARTITION BY season) AS avg_yprr,
    STDDEV_POP(yprr) OVER (PARTITION BY season) AS sd_yprr,
    AVG(vs_man_yprr) OVER (PARTITION BY season) AS avg_man_yprr,
    STDDEV_POP(vs_man_yprr) OVER (PARTITION BY season) AS sd_man_yprr,
    AVG(epa_per_target) OVER (PARTITION BY season) AS avg_epa_target,
    STDDEV_POP(epa_per_target) OVER (PARTITION BY season) AS sd_epa_target,
    AVG(blended_td_per_game) OVER (PARTITION BY season) AS avg_blended_td,
    STDDEV_POP(blended_td_per_game) OVER (PARTITION BY season) AS sd_blended_td,
    AVG(breakout_window_bonus) OVER (PARTITION BY season) AS avg_breakout,
    STDDEV_POP(breakout_window_bonus) OVER (PARTITION BY season) AS sd_breakout,
    AVG(decline_penalty) OVER (PARTITION BY season) AS avg_decline,
    STDDEV_POP(decline_penalty) OVER (PARTITION BY season) AS sd_decline,
    AVG(games_played_rate) OVER (PARTITION BY season) AS avg_games,
    STDDEV_POP(games_played_rate) OVER (PARTITION BY season) AS sd_games
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_metric_inputs` AS inputs
  WHERE season BETWEEN 2022 AND 2025
),
z_scores AS (
  SELECT
    metric_stats.*,
    SAFE_DIVIDE(routes_per_game - avg_routes, sd_routes) AS z_routes,
    SAFE_DIVIDE(target_share - avg_target_share, sd_target_share) AS z_target_share,
    SAFE_DIVIDE(red_zone_targets_per_game - avg_rz_targets, sd_rz_targets) AS z_rz_targets,
    SAFE_DIVIDE(targets_per_route_run - avg_tprr, sd_tprr) AS z_tprr,
    SAFE_DIVIDE(yprr - avg_yprr, sd_yprr) AS z_yprr,
    SAFE_DIVIDE(vs_man_yprr - avg_man_yprr, sd_man_yprr) AS z_man_yprr,
    SAFE_DIVIDE(epa_per_target - avg_epa_target, sd_epa_target) AS z_epa_target,
    SAFE_DIVIDE(blended_td_per_game - avg_blended_td, sd_blended_td) AS z_blended_td,
    SAFE_DIVIDE(breakout_window_bonus - avg_breakout, sd_breakout) AS z_breakout,
    SAFE_DIVIDE(decline_penalty - avg_decline, sd_decline) AS z_decline,
    SAFE_DIVIDE(games_played_rate - avg_games, sd_games) AS z_games
  FROM metric_stats
),
components AS (
  SELECT
    z_scores.*,
    0.22 * z_routes + 0.16 * z_target_share + 0.12 * z_rz_targets AS opportunity_component,
    0.12 * z_tprr * target_efficiency_shrink
      + 0.08 * z_yprr * route_efficiency_shrink
      + 0.05 * z_man_yprr * vs_man_efficiency_shrink
      + 0.05 * z_epa_target * target_efficiency_shrink AS efficiency_component,
    0.12 * z_tprr * target_efficiency_shrink
      + 0.13 * z_yprr * route_efficiency_shrink
      + 0.05 * z_epa_target * target_efficiency_shrink AS no_man_efficiency_component,
    0.10 * z_blended_td AS scoring_component,
    0.04 * z_breakout + 0.03 * z_decline + 0.03 * z_games AS age_availability_component
  FROM z_scores
)
SELECT
  components.*,
  opportunity_component + efficiency_component + scoring_component + age_availability_component AS te_fable_v1a_score,
  opportunity_component + no_man_efficiency_component + scoring_component + age_availability_component AS te_fable_v1a_no_man_score
FROM components;
