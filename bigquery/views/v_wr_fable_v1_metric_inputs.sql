-- Qualified, leakage-safe WR Fable v1 metrics before within-season z-scoring.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_metric_inputs` AS
WITH derived AS (
  SELECT
    splits.*,
    -- Situational-refinement targets derive from routes * TPRR; raw season targets stay canonical.
    CASE WHEN splits.non_garbage_structural_fallback
      THEN splits.sourced_non_garbage_targets
      ELSE splits.non_garbage_time_routes_run * splits.non_garbage_time_targets_per_route_run
    END AS non_garbage_time_targets,
    SAFE_DIVIDE(
      CASE WHEN splits.non_garbage_structural_fallback
        THEN splits.sourced_non_garbage_targets
        ELSE splits.non_garbage_time_routes_run * splits.non_garbage_time_targets_per_route_run
      END,
      splits.games_played
    ) AS non_garbage_time_targets_per_game,
    CASE WHEN splits.red_zone_structural_fallback
      THEN splits.sourced_red_zone_targets
      ELSE splits.red_zone_routes_run * splits.red_zone_targets_per_route_run
    END AS red_zone_targets,
    SAFE_DIVIDE(
      CASE WHEN splits.red_zone_structural_fallback
        THEN splits.sourced_red_zone_targets
        ELSE splits.red_zone_routes_run * splits.red_zone_targets_per_route_run
      END,
      splits.games_played
    ) AS red_zone_targets_per_game,
    CASE WHEN splits.targets > 0 THEN SAFE_DIVIDE(splits.total_epa, splits.targets) END AS epa_per_target,
    CASE WHEN splits.receptions > 0 THEN SAFE_DIVIDE(splits.yac, splits.receptions) END AS yac_per_reception,
    -- Situational target_share is in percent; brain air_yards_share is a 0-1 fraction.
    1.5 * (splits.target_share / 100.0) + 0.7 * splits.air_yards_share AS wopr,
    SAFE_DIVIDE(splits.receiving_touchdowns, splits.games_played) AS actual_td_per_game,
    IF(splits.age BETWEEN 22 AND 25, 1, 0) AS breakout_window_bonus,
    CASE WHEN splits.age IS NULL THEN NULL ELSE -GREATEST(0, splits.age - 29) END AS decline_penalty,
    SAFE_DIVIDE(splits.games_played, 17) AS games_played_rate,
    SAFE_DIVIDE(splits.routes_run, splits.routes_run + 60) AS route_efficiency_shrink,
    SAFE_DIVIDE(splits.targets, splits.targets + 60) AS target_efficiency_shrink
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_situational_splits` AS splits
  WHERE identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
    AND NOT duplicate_identity_collision
),
qualified AS (
  SELECT * FROM derived
  WHERE games_played >= 6 OR targets >= 40
),
catch_rate_regression AS (
  -- aDOT-adjusted catch rate: residual of catch_pct regressed on aDOT within the season pool.
  SELECT
    season,
    AVG(catch_pct) AS mean_catch_pct,
    AVG(adot) AS mean_adot,
    SAFE_DIVIDE(COVAR_POP(catch_pct, adot), VAR_POP(adot)) AS adot_slope
  FROM qualified
  WHERE catch_pct IS NOT NULL AND adot IS NOT NULL
  GROUP BY season
),
league_rz_conversion AS (
  -- Red-zone-based expected-TD fallback (owner approved). NOT end-zone xTD.
  SELECT
    season,
    SAFE_DIVIDE(SUM(red_zone_touchdowns), SUM(red_zone_targets)) AS league_wr_rz_td_conversion
  FROM qualified
  WHERE red_zone_targets IS NOT NULL AND red_zone_touchdowns IS NOT NULL
  GROUP BY season
)
SELECT
  qualified.*,
  qualified.catch_pct
    - (regression.mean_catch_pct + regression.adot_slope * (qualified.adot - regression.mean_adot))
    AS adot_adjusted_catch_rate,
  conversion.league_wr_rz_td_conversion,
  qualified.red_zone_targets_per_game * conversion.league_wr_rz_td_conversion AS expected_td_per_game,
  0.70 * (qualified.red_zone_targets_per_game * conversion.league_wr_rz_td_conversion)
    + 0.30 * qualified.actual_td_per_game AS blended_td_per_game
FROM qualified
JOIN catch_rate_regression AS regression USING (season)
JOIN league_rz_conversion AS conversion USING (season);
