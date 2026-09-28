-- Phase 35.1D scores use the unchanged WR Fable v1 weights and v1 reference distributions.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_scored_seasons` AS
WITH baseline_stats AS (
  SELECT
    season,
    ANY_VALUE(avg_wopr) AS avg_wopr,
    ANY_VALUE(sd_wopr) AS sd_wopr,
    ANY_VALUE(avg_ngt_tgt) AS avg_ngt_tgt,
    ANY_VALUE(sd_ngt_tgt) AS sd_ngt_tgt,
    ANY_VALUE(avg_rz_tgt) AS avg_rz_tgt,
    ANY_VALUE(sd_rz_tgt) AS sd_rz_tgt,
    ANY_VALUE(avg_yprr) AS avg_yprr,
    ANY_VALUE(sd_yprr) AS sd_yprr,
    ANY_VALUE(avg_epa_tgt) AS avg_epa_tgt,
    ANY_VALUE(sd_epa_tgt) AS sd_epa_tgt,
    ANY_VALUE(avg_yac_rec) AS avg_yac_rec,
    ANY_VALUE(sd_yac_rec) AS sd_yac_rec,
    ANY_VALUE(avg_acr) AS avg_acr,
    ANY_VALUE(sd_acr) AS sd_acr,
    ANY_VALUE(avg_blend_td) AS avg_blend_td,
    ANY_VALUE(sd_blend_td) AS sd_blend_td,
    ANY_VALUE(avg_breakout) AS avg_breakout,
    ANY_VALUE(sd_breakout) AS sd_breakout,
    ANY_VALUE(avg_decline) AS avg_decline,
    ANY_VALUE(sd_decline) AS sd_decline,
    ANY_VALUE(avg_games_rate) AS avg_games_rate,
    ANY_VALUE(sd_games_rate) AS sd_games_rate
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_scored_seasons`
  WHERE season BETWEEN 2022 AND 2025
  GROUP BY season
), z_scores AS (
  SELECT
    inputs.*,
    SAFE_DIVIDE(inputs.modified_wopr - stats.avg_wopr, stats.sd_wopr) AS z_wopr,
    SAFE_DIVIDE(
      inputs.modified_ngt_targets_per_game - stats.avg_ngt_tgt,
      stats.sd_ngt_tgt
    ) AS z_ngt_targets_per_game,
    SAFE_DIVIDE(
      inputs.modified_rz_targets_per_game - stats.avg_rz_tgt,
      stats.sd_rz_tgt
    ) AS z_rz_targets_per_game,
    SAFE_DIVIDE(inputs.modified_yprr - stats.avg_yprr, stats.sd_yprr) AS z_yprr,
    SAFE_DIVIDE(
      inputs.modified_epa_per_target - stats.avg_epa_tgt,
      stats.sd_epa_tgt
    ) AS z_epa_per_target,
    SAFE_DIVIDE(
      inputs.modified_yac_per_reception - stats.avg_yac_rec,
      stats.sd_yac_rec
    ) AS z_yac_per_reception,
    SAFE_DIVIDE(
      inputs.modified_adot_adjusted_catch_rate - stats.avg_acr,
      stats.sd_acr
    ) AS z_adot_adjusted_catch_rate,
    SAFE_DIVIDE(
      inputs.modified_blended_td_per_game - stats.avg_blend_td,
      stats.sd_blend_td
    ) AS z_blended_td_per_game,
    SAFE_DIVIDE(inputs.breakout_window_bonus - stats.avg_breakout, stats.sd_breakout)
      AS z_breakout_window,
    SAFE_DIVIDE(inputs.decline_penalty - stats.avg_decline, stats.sd_decline)
      AS z_decline_penalty,
    SAFE_DIVIDE(
      inputs.two_year_availability_rate - stats.avg_games_rate,
      stats.sd_games_rate
    ) AS z_two_year_availability
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_metric_inputs` AS inputs
  JOIN baseline_stats AS stats USING (season)
), components AS (
  SELECT
    z_scores.*,
    0.30 * z_wopr
      + 0.12 * z_ngt_targets_per_game
      + 0.10 * z_rz_targets_per_game AS opportunity_component,
    0.12 * z_yprr * modified_route_efficiency_shrink
      + 0.06 * z_epa_per_target * modified_target_efficiency_shrink
      + 0.05 * z_yac_per_reception * modified_target_efficiency_shrink
      + 0.05 * z_adot_adjusted_catch_rate * modified_target_efficiency_shrink
      AS efficiency_component,
    0.10 * z_blended_td_per_game AS scoring_component,
    0.04 * z_breakout_window
      + 0.03 * z_decline_penalty
      + 0.03 * z_two_year_availability AS age_availability_component
  FROM z_scores
), candidate_scores AS (
  SELECT
    components.*,
    opportunity_component + efficiency_component + scoring_component + age_availability_component
      AS injury_candidate_score
  FROM components
), baseline AS (
  SELECT season, candidate_internal_player_id, wr_fable_v1_score, age_availability_component
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_scored_seasons`
  WHERE season BETWEEN 2022 AND 2025
), score_context AS (
  SELECT
    candidate_scores.*,
    baseline.wr_fable_v1_score AS baseline_v1_score,
    baseline.wr_fable_v1_score IS NOT NULL AS baseline_v1_score_available,
    prior_baseline.wr_fable_v1_score AS prior_v1_score,
    prior_baseline.age_availability_component AS prior_v1_age_availability_component,
    baseline.wr_fable_v1_score IS NULL
      AND prior_baseline.wr_fable_v1_score IS NOT NULL
      AND prior_baseline.age_availability_component IS NOT NULL
      AND candidate_scores.age_availability_component IS NOT NULL
      AND NOT candidate_scores.rookie_limited_sample_flag
      AND (candidate_scores.games_played >= 3 OR candidate_scores.routes_run >= 75)
      AS prior_score_carry_forward_eligible
  FROM candidate_scores
  LEFT JOIN baseline
    USING (season, candidate_internal_player_id)
  LEFT JOIN baseline AS prior_baseline
    ON prior_baseline.season = candidate_scores.season - 1
   AND prior_baseline.candidate_internal_player_id = candidate_scores.candidate_internal_player_id
)
SELECT
  score_context.*,
  COALESCE(baseline_v1_score, injury_candidate_score) AS exclusion_only_score,
  CASE WHEN prior_score_carry_forward_eligible
    THEN prior_v1_score - prior_v1_age_availability_component + age_availability_component
  END AS prior_score_carry_forward_score,
  CASE
    WHEN baseline_v1_score IS NOT NULL THEN baseline_v1_score
    WHEN prior_score_carry_forward_eligible
      THEN prior_v1_score - prior_v1_age_availability_component + age_availability_component
  END AS carry_forward_replacement_score,
  CASE
    WHEN baseline_v1_score IS NULL AND rookie_limited_sample_flag THEN injury_candidate_score
  END AS rookie_review_score
FROM score_context;
