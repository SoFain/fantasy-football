-- WR Fable v1.1 scores: v1 weights over two-season blended inputs, availability separated.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v11_scored_seasons` AS
WITH metric_stats AS (
  SELECT
    inputs.*,
    AVG(b_wopr) OVER (PARTITION BY season) AS avg_wopr,
    STDDEV_POP(b_wopr) OVER (PARTITION BY season) AS sd_wopr,
    AVG(b_ngt_tgt_pg) OVER (PARTITION BY season) AS avg_ngt_tgt,
    STDDEV_POP(b_ngt_tgt_pg) OVER (PARTITION BY season) AS sd_ngt_tgt,
    AVG(b_rz_tgt_pg) OVER (PARTITION BY season) AS avg_rz_tgt,
    STDDEV_POP(b_rz_tgt_pg) OVER (PARTITION BY season) AS sd_rz_tgt,
    AVG(b_yprr) OVER (PARTITION BY season) AS avg_yprr,
    STDDEV_POP(b_yprr) OVER (PARTITION BY season) AS sd_yprr,
    AVG(b_epa_per_target) OVER (PARTITION BY season) AS avg_epa_tgt,
    STDDEV_POP(b_epa_per_target) OVER (PARTITION BY season) AS sd_epa_tgt,
    AVG(b_yac_per_reception) OVER (PARTITION BY season) AS avg_yac_rec,
    STDDEV_POP(b_yac_per_reception) OVER (PARTITION BY season) AS sd_yac_rec,
    AVG(b_adot_adjusted_catch_rate) OVER (PARTITION BY season) AS avg_acr,
    STDDEV_POP(b_adot_adjusted_catch_rate) OVER (PARTITION BY season) AS sd_acr,
    AVG(b_blended_td_per_game) OVER (PARTITION BY season) AS avg_blend_td,
    STDDEV_POP(b_blended_td_per_game) OVER (PARTITION BY season) AS sd_blend_td,
    AVG(breakout_window_bonus) OVER (PARTITION BY season) AS avg_breakout,
    STDDEV_POP(breakout_window_bonus) OVER (PARTITION BY season) AS sd_breakout,
    AVG(decline_penalty) OVER (PARTITION BY season) AS avg_decline,
    STDDEV_POP(decline_penalty) OVER (PARTITION BY season) AS sd_decline,
    AVG(two_year_availability_rate) OVER (PARTITION BY season) AS avg_avail,
    STDDEV_POP(two_year_availability_rate) OVER (PARTITION BY season) AS sd_avail
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v11_metric_inputs` AS inputs
  WHERE season BETWEEN 2022 AND 2025
),
z_scores AS (
  SELECT
    metric_stats.*,
    SAFE_DIVIDE(b_wopr - avg_wopr, sd_wopr) AS z_wopr,
    SAFE_DIVIDE(b_ngt_tgt_pg - avg_ngt_tgt, sd_ngt_tgt) AS z_ngt_tgt,
    SAFE_DIVIDE(b_rz_tgt_pg - avg_rz_tgt, sd_rz_tgt) AS z_rz_tgt,
    SAFE_DIVIDE(b_yprr - avg_yprr, sd_yprr) AS z_yprr,
    SAFE_DIVIDE(b_epa_per_target - avg_epa_tgt, sd_epa_tgt) AS z_epa_per_target,
    SAFE_DIVIDE(b_yac_per_reception - avg_yac_rec, sd_yac_rec) AS z_yac_per_reception,
    SAFE_DIVIDE(b_adot_adjusted_catch_rate - avg_acr, sd_acr) AS z_adot_adjusted_catch_rate,
    SAFE_DIVIDE(b_blended_td_per_game - avg_blend_td, sd_blend_td) AS z_blended_td,
    SAFE_DIVIDE(breakout_window_bonus - avg_breakout, sd_breakout) AS z_breakout_window,
    SAFE_DIVIDE(decline_penalty - avg_decline, sd_decline) AS z_decline_penalty,
    SAFE_DIVIDE(two_year_availability_rate - avg_avail, sd_avail) AS z_two_year_availability
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
    0.04 * z_breakout_window + 0.03 * z_decline_penalty + 0.03 * z_two_year_availability AS age_availability_component
  FROM z_scores
)
SELECT
  components.*,
  opportunity_component + efficiency_component + scoring_component + age_availability_component AS wr_fable_v11_score
FROM components;
