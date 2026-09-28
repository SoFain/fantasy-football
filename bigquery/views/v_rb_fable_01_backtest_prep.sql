-- RB Fable 01 prior-season scores and next-season Standard outcomes. No rankings are written.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_backtest_prep` AS
WITH metric_stats AS (
  SELECT
    inputs.*,
    AVG(non_garbage_time_touches_per_game) OVER (PARTITION BY season) AS avg_ngt_tpg,
    STDDEV_POP(non_garbage_time_touches_per_game) OVER (PARTITION BY season) AS sd_ngt_tpg,
    AVG(red_zone_touches_per_game) OVER (PARTITION BY season) AS avg_rz_tpg,
    STDDEV_POP(red_zone_touches_per_game) OVER (PARTITION BY season) AS sd_rz_tpg,
    AVG(target_share) OVER (PARTITION BY season) AS avg_target_share,
    STDDEV_POP(target_share) OVER (PARTITION BY season) AS sd_target_share,
    AVG(yac_per_rush) OVER (PARTITION BY season) AS avg_yac_per_rush,
    STDDEV_POP(yac_per_rush) OVER (PARTITION BY season) AS sd_yac_per_rush,
    AVG(success_pct) OVER (PARTITION BY season) AS avg_success_pct,
    STDDEV_POP(success_pct) OVER (PARTITION BY season) AS sd_success_pct,
    AVG(epa_per_touch) OVER (PARTITION BY season) AS avg_epa_per_touch,
    STDDEV_POP(epa_per_touch) OVER (PARTITION BY season) AS sd_epa_per_touch,
    AVG(explosive_pct) OVER (PARTITION BY season) AS avg_explosive_pct,
    STDDEV_POP(explosive_pct) OVER (PARTITION BY season) AS sd_explosive_pct,
    AVG(box_adjusted_ypc) OVER (PARTITION BY season) AS avg_box_adjusted_ypc,
    STDDEV_POP(box_adjusted_ypc) OVER (PARTITION BY season) AS sd_box_adjusted_ypc,
    AVG(blended_td_per_game) OVER (PARTITION BY season) AS avg_blended_td,
    STDDEV_POP(blended_td_per_game) OVER (PARTITION BY season) AS sd_blended_td,
    AVG(age_penalty) OVER (PARTITION BY season) AS avg_age_penalty,
    STDDEV_POP(age_penalty) OVER (PARTITION BY season) AS sd_age_penalty,
    AVG(games_played_rate) OVER (PARTITION BY season) AS avg_games_rate,
    STDDEV_POP(games_played_rate) OVER (PARTITION BY season) AS sd_games_rate
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_metric_inputs` AS inputs
  WHERE season BETWEEN 2022 AND 2024
),
z_scores AS (
  SELECT
    metric_stats.*,
    SAFE_DIVIDE(non_garbage_time_touches_per_game - avg_ngt_tpg, sd_ngt_tpg) AS z_ngt_tpg,
    SAFE_DIVIDE(red_zone_touches_per_game - avg_rz_tpg, sd_rz_tpg) AS z_rz_tpg,
    SAFE_DIVIDE(target_share - avg_target_share, sd_target_share) AS z_target_share,
    SAFE_DIVIDE(yac_per_rush - avg_yac_per_rush, sd_yac_per_rush) AS z_yac_per_rush,
    SAFE_DIVIDE(success_pct - avg_success_pct, sd_success_pct) AS z_success_pct,
    SAFE_DIVIDE(epa_per_touch - avg_epa_per_touch, sd_epa_per_touch) AS z_epa_per_touch,
    SAFE_DIVIDE(explosive_pct - avg_explosive_pct, sd_explosive_pct) AS z_explosive_pct,
    SAFE_DIVIDE(box_adjusted_ypc - avg_box_adjusted_ypc, sd_box_adjusted_ypc) AS z_box_adjusted_ypc,
    SAFE_DIVIDE(blended_td_per_game - avg_blended_td, sd_blended_td) AS z_blended_td,
    SAFE_DIVIDE(age_penalty - avg_age_penalty, sd_age_penalty) AS z_age_penalty,
    SAFE_DIVIDE(games_played_rate - avg_games_rate, sd_games_rate) AS z_games_rate
  FROM metric_stats
),
components AS (
  SELECT
    z_scores.*,
    0.30 * z_ngt_tpg
      + 0.13 * z_rz_tpg
      + 0.12 * z_target_share AS opportunity_component,
    0.08 * z_yac_per_rush * rushing_efficiency_shrink
      + 0.06 * z_success_pct * rushing_efficiency_shrink
      + 0.05 * z_epa_per_touch * touch_efficiency_shrink
      + 0.04 * z_explosive_pct * rushing_efficiency_shrink
      + 0.04 * z_box_adjusted_ypc * SAFE_DIVIDE(box_adjusted_ypc_sample_size, box_adjusted_ypc_sample_size + 125)
      AS efficiency_component,
    0.10 * z_blended_td AS scoring_component,
    -- Phase 34.4 elite-volume protection: forgive up to 60% of the age penalty as prior-season
    -- non-garbage-time volume rises from z=0.75 to z=1.5. Workhorse veterans (Henry) keep most of
    -- their score while moderate-volume veterans (Mostert) stay fully penalized.
    0.05 * z_age_penalty * (1 - 0.6 * LEAST(GREATEST((z_ngt_tpg - 0.75) / 0.75, 0), 1))
      + 0.03 * z_games_rate AS age_availability_component
  FROM z_scores
),
scored AS (
  SELECT
    components.*,
    opportunity_component + efficiency_component + scoring_component + age_availability_component AS rb_fable_01_score
  FROM components
),
target_totals AS (
  SELECT
    season,
    source_player_key AS target_player_id,
    COUNT(*) AS target_games,
    SUM(total_fantasy_points) AS target_standard_points,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS target_standard_ppg
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard'
    AND position = 'RB'
    AND season BETWEEN 2023 AND 2025
    AND week BETWEEN 1 AND 18
  GROUP BY season, target_player_id
),
target_ranked AS (
  SELECT
    *,
    DENSE_RANK() OVER (PARTITION BY season ORDER BY target_standard_ppg DESC, target_standard_points DESC) AS target_standard_rb_rank
  FROM target_totals
  WHERE target_games >= 6
)
SELECT
  scored.*,
  scored.season + 1 AS target_season,
  target.target_games,
  target.target_standard_points,
  target.target_standard_ppg,
  target.target_standard_rb_rank,
  target.target_standard_rb_rank <= 6 AS target_top_6,
  target.target_standard_rb_rank <= 12 AS target_top_12,
  target.target_standard_rb_rank <= 24 AS target_top_24,
  CAST(NULL AS FLOAT64) AS current_pigskin_historical_score,
  CAST(NULL AS INT64) AS current_pigskin_historical_rank,
  'UNAVAILABLE_HISTORICAL_BASELINE' AS current_pigskin_comparison_status,
  CAST(NULL AS FLOAT64) AS prior_episode_formula_score,
  'UNAVAILABLE' AS prior_episode_formula_status,
  target.target_player_id IS NOT NULL AS target_available
FROM scored
LEFT JOIN target_ranked AS target
  ON target.season = scored.season + 1
 AND target.target_player_id = scored.candidate_internal_player_id;
