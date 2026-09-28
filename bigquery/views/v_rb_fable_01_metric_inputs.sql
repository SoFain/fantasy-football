-- Qualified, leakage-safe RB Fable 01 metrics before within-season z-scoring.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_metric_inputs` AS
WITH derived AS (
  SELECT
    splits.*,
    COALESCE(standard_rushes, 0) + COALESCE(standard_receptions, 0) AS standard_touches,
    SAFE_DIVIDE(COALESCE(standard_rushes, 0) + COALESCE(standard_receptions, 0), games_played) AS standard_touches_per_game,
    COALESCE(non_garbage_time_rushes, 0) + COALESCE(non_garbage_time_receptions, 0) AS non_garbage_time_touches,
    SAFE_DIVIDE(COALESCE(non_garbage_time_rushes, 0) + COALESCE(non_garbage_time_receptions, 0), games_played) AS non_garbage_time_touches_per_game,
    COALESCE(red_zone_rushes, 0) + COALESCE(red_zone_receptions, 0) AS red_zone_touches,
    SAFE_DIVIDE(COALESCE(red_zone_rushes, 0) + COALESCE(red_zone_receptions, 0), games_played) AS red_zone_touches_per_game,
    SAFE_DIVIDE(yards_after_contact, standard_rushes) AS yac_per_rush,
    SAFE_DIVIDE(total_epa, COALESCE(standard_rushes, 0) + COALESCE(standard_receptions, 0)) AS epa_per_touch,
    COALESCE(standard_rush_td, 0) + COALESCE(standard_receiving_td, 0) AS actual_td,
    SAFE_DIVIDE(COALESCE(standard_rush_td, 0) + COALESCE(standard_receiving_td, 0), games_played) AS actual_td_per_game,
    0.16 * SAFE_DIVIDE(red_zone_rushes, games_played)
      + 0.10 * SAFE_DIVIDE(red_zone_receptions, games_played) AS expected_td_per_game,
    -GREATEST(0, age - 25) AS age_penalty,
    SAFE_DIVIDE(games_played, 17) AS games_played_rate
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_situational_splits` AS splits
  WHERE identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
    AND NOT duplicate_identity_collision
),
qualified AS (
  SELECT *
  FROM derived
  WHERE games_played >= 6 OR standard_touches >= 50
),
regression_inputs AS (
  SELECT
    season,
    AVG(yards_per_carry) AS mean_ypc,
    AVG(avg_box_defenders) AS mean_box,
    SAFE_DIVIDE(COVAR_POP(yards_per_carry, avg_box_defenders), VAR_POP(avg_box_defenders)) AS box_slope
  FROM qualified
  WHERE yards_per_carry IS NOT NULL AND avg_box_defenders IS NOT NULL
  GROUP BY season
)
SELECT
  qualified.*,
  CASE
    WHEN stacked_box_rushes >= 20 AND stacked_box_yards_per_carry IS NOT NULL
      THEN stacked_box_yards_per_carry
    ELSE yards_per_carry
      - (regression.mean_ypc + regression.box_slope * (avg_box_defenders - regression.mean_box))
  END AS box_adjusted_ypc,
  CASE WHEN stacked_box_rushes >= 20 AND stacked_box_yards_per_carry IS NOT NULL
    THEN 'STACKED_BOX_YPC' ELSE 'STANDARD_BOX_RESIDUAL' END AS box_adjusted_ypc_method,
  CASE WHEN stacked_box_rushes >= 20 AND stacked_box_yards_per_carry IS NOT NULL
    THEN stacked_box_rushes ELSE standard_rushes END AS box_adjusted_ypc_sample_size,
  0.7 * expected_td_per_game + 0.3 * actual_td_per_game AS blended_td_per_game,
  SAFE_DIVIDE(standard_rushes, standard_rushes + 125) AS rushing_efficiency_shrink,
  SAFE_DIVIDE(standard_touches, standard_touches + 125) AS touch_efficiency_shrink
FROM qualified
JOIN regression_inputs AS regression USING (season);

