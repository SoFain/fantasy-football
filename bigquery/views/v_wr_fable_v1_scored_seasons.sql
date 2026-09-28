-- WR Fable v1 scores for all loaded seasons. Descriptive use for 2025; no future outcomes.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_scored_seasons` AS
WITH metric_stats AS (
  SELECT
    inputs.*,
    AVG(wopr) OVER (PARTITION BY season) AS avg_wopr,
    STDDEV_POP(wopr) OVER (PARTITION BY season) AS sd_wopr,
    AVG(non_garbage_time_targets_per_game) OVER (PARTITION BY season) AS avg_ngt_tgt,
    STDDEV_POP(non_garbage_time_targets_per_game) OVER (PARTITION BY season) AS sd_ngt_tgt,
    AVG(red_zone_targets_per_game) OVER (PARTITION BY season) AS avg_rz_tgt,
    STDDEV_POP(red_zone_targets_per_game) OVER (PARTITION BY season) AS sd_rz_tgt,
    AVG(yprr) OVER (PARTITION BY season) AS avg_yprr,
    STDDEV_POP(yprr) OVER (PARTITION BY season) AS sd_yprr,
    AVG(epa_per_target) OVER (PARTITION BY season) AS avg_epa_tgt,
    STDDEV_POP(epa_per_target) OVER (PARTITION BY season) AS sd_epa_tgt,
    AVG(yac_per_reception) OVER (PARTITION BY season) AS avg_yac_rec,
    STDDEV_POP(yac_per_reception) OVER (PARTITION BY season) AS sd_yac_rec,
    AVG(adot_adjusted_catch_rate) OVER (PARTITION BY season) AS avg_acr,
    STDDEV_POP(adot_adjusted_catch_rate) OVER (PARTITION BY season) AS sd_acr,
    AVG(blended_td_per_game) OVER (PARTITION BY season) AS avg_blend_td,
    STDDEV_POP(blended_td_per_game) OVER (PARTITION BY season) AS sd_blend_td,
    AVG(breakout_window_bonus) OVER (PARTITION BY season) AS avg_breakout,
    STDDEV_POP(breakout_window_bonus) OVER (PARTITION BY season) AS sd_breakout,
    AVG(decline_penalty) OVER (PARTITION BY season) AS avg_decline,
    STDDEV_POP(decline_penalty) OVER (PARTITION BY season) AS sd_decline,
    AVG(games_played_rate) OVER (PARTITION BY season) AS avg_games_rate,
    STDDEV_POP(games_played_rate) OVER (PARTITION BY season) AS sd_games_rate
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_metric_inputs` AS inputs
  WHERE season BETWEEN 2022 AND 2025
),
z_scores AS (
  SELECT
    metric_stats.*,
    SAFE_DIVIDE(wopr - avg_wopr, sd_wopr) AS z_wopr,
    SAFE_DIVIDE(non_garbage_time_targets_per_game - avg_ngt_tgt, sd_ngt_tgt) AS z_ngt_tgt,
    SAFE_DIVIDE(red_zone_targets_per_game - avg_rz_tgt, sd_rz_tgt) AS z_rz_tgt,
    SAFE_DIVIDE(yprr - avg_yprr, sd_yprr) AS z_yprr,
    SAFE_DIVIDE(epa_per_target - avg_epa_tgt, sd_epa_tgt) AS z_epa_per_target,
    SAFE_DIVIDE(yac_per_reception - avg_yac_rec, sd_yac_rec) AS z_yac_per_reception,
    SAFE_DIVIDE(adot_adjusted_catch_rate - avg_acr, sd_acr) AS z_adot_adjusted_catch_rate,
    SAFE_DIVIDE(blended_td_per_game - avg_blend_td, sd_blend_td) AS z_blended_td,
    SAFE_DIVIDE(breakout_window_bonus - avg_breakout, sd_breakout) AS z_breakout_window,
    SAFE_DIVIDE(decline_penalty - avg_decline, sd_decline) AS z_decline_penalty,
    SAFE_DIVIDE(games_played_rate - avg_games_rate, sd_games_rate) AS z_games_rate
  FROM metric_stats
),
components AS (
  SELECT
    z_scores.*,
    0.30 * z_wopr + 0.12 * z_ngt_tgt + 0.10 * z_rz_tgt AS opportunity_component,
    0.12 * z_yprr * route_efficiency_shrink
      + 0.06 * z_epa_per_target * target_efficiency_shrink
      + 0.05 * z_yac_per_reception * target_efficiency_shrink
      + 0.05 * z_adot_adjusted_catch_rate * target_efficiency_shrink
      AS efficiency_component,
    0.10 * z_blended_td AS scoring_component,
    0.04 * z_breakout_window + 0.03 * z_decline_penalty + 0.03 * z_games_rate AS age_availability_component
  FROM z_scores
)
SELECT
  components.*,
  opportunity_component + efficiency_component + scoring_component + age_availability_component AS wr_fable_v1_score
FROM components;
