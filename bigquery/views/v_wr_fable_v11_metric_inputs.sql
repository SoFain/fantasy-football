-- WR Fable v1.1 inputs: two-season dynamic blend + carry-forward eligibility.
-- Blends only per-game / per-target / per-reception / per-route / share metrics, never raw totals.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v11_metric_inputs` AS
WITH derived AS (
  -- Same derivations as WR Fable v1, over a relaxed pool so injury-shortened seasons stay visible.
  SELECT
    splits.*,
    splits.non_garbage_time_routes_run * splits.non_garbage_time_targets_per_route_run AS non_garbage_time_targets,
    SAFE_DIVIDE(splits.non_garbage_time_routes_run * splits.non_garbage_time_targets_per_route_run, splits.games_played) AS non_garbage_time_targets_per_game,
    splits.red_zone_routes_run * splits.red_zone_targets_per_route_run AS red_zone_targets,
    SAFE_DIVIDE(splits.red_zone_routes_run * splits.red_zone_targets_per_route_run, splits.games_played) AS red_zone_targets_per_game,
    CASE WHEN splits.targets > 0 THEN SAFE_DIVIDE(splits.total_epa, splits.targets) END AS epa_per_target,
    CASE WHEN splits.receptions > 0 THEN SAFE_DIVIDE(splits.yac, splits.receptions) END AS yac_per_reception,
    1.5 * (splits.target_share / 100.0) + 0.7 * splits.air_yards_share AS wopr,
    SAFE_DIVIDE(splits.receiving_touchdowns, splits.games_played) AS actual_td_per_game,
    IF(splits.age BETWEEN 22 AND 25, 1, 0) AS breakout_window_bonus,
    CASE WHEN splits.age IS NULL THEN NULL ELSE -GREATEST(0, splits.age - 29) END AS decline_penalty,
    SAFE_DIVIDE(splits.games_played, 17) AS games_played_rate,
    (splits.games_played >= 6 OR splits.targets >= 40) AS season_qualified
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_situational_splits` AS splits
  WHERE identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
    AND NOT duplicate_identity_collision
    AND (splits.games_played >= 3 OR splits.routes_run >= 75 OR splits.targets >= 40)
),
catch_rate_regression AS (
  SELECT season, AVG(catch_pct) AS mean_catch_pct, AVG(adot) AS mean_adot,
    SAFE_DIVIDE(COVAR_POP(catch_pct, adot), VAR_POP(adot)) AS adot_slope
  FROM derived
  WHERE season_qualified AND catch_pct IS NOT NULL AND adot IS NOT NULL
  GROUP BY season
),
league_rz_conversion AS (
  -- Red-zone-based xTD fallback (owner approved); NOT end-zone xTD.
  SELECT season, SAFE_DIVIDE(SUM(red_zone_touchdowns), SUM(red_zone_targets)) AS league_wr_rz_td_conversion
  FROM derived
  WHERE season_qualified AND red_zone_targets IS NOT NULL AND red_zone_touchdowns IS NOT NULL
  GROUP BY season
),
enriched AS (
  SELECT
    derived.*,
    derived.catch_pct - (regression.mean_catch_pct + regression.adot_slope * (derived.adot - regression.mean_adot)) AS adot_adjusted_catch_rate,
    derived.red_zone_targets_per_game * conversion.league_wr_rz_td_conversion AS expected_td_per_game
  FROM derived
  JOIN catch_rate_regression AS regression USING (season)
  JOIN league_rz_conversion AS conversion USING (season)
),
paired AS (
  SELECT
    latest.*,
    prev.season_qualified AS prev_qualified,
    prev.wopr AS prev_wopr,
    prev.non_garbage_time_targets_per_game AS prev_ngt_tgt_pg,
    prev.red_zone_targets_per_game AS prev_rz_tgt_pg,
    prev.yprr AS prev_yprr,
    prev.epa_per_target AS prev_epa_per_target,
    prev.yac_per_reception AS prev_yac_per_reception,
    prev.adot_adjusted_catch_rate AS prev_adot_adjusted_catch_rate,
    prev.expected_td_per_game AS prev_expected_td_per_game,
    prev.actual_td_per_game AS prev_actual_td_per_game,
    prev.games_played_rate AS prev_games_played_rate,
    prev.routes_run AS prev_routes_run,
    prev.targets AS prev_targets,
    prev.team AS prev_team
  FROM enriched AS latest
  LEFT JOIN enriched AS prev
    ON prev.candidate_internal_player_id = latest.candidate_internal_player_id
   AND prev.season = latest.season - 1
   AND prev.season_qualified
),
weighted AS (
  SELECT
    paired.*,
    paired.season_qualified AS latest_qualified,
    (NOT paired.season_qualified AND paired.prev_qualified IS NOT NULL
      AND (paired.games_played >= 3 OR paired.routes_run >= 75)) AS carry_forward_eligible,
    -- Dynamic latest-season weight: routes/(routes+200), clamped [0.35, 0.70].
    -- Full seasons hit the caps, reproducing the static 70/30 (opportunity/TD) and 60/40 (efficiency) blends.
    CASE WHEN paired.prev_qualified IS NULL THEN 1.0
         ELSE LEAST(GREATEST(SAFE_DIVIDE(paired.routes_run, paired.routes_run + 200), 0.35), 0.70)
    END AS latest_weight_raw
  FROM paired
)
SELECT
  weighted.*,
  LEAST(latest_weight_raw, 0.70) AS opportunity_latest_weight,
  LEAST(latest_weight_raw, 0.60) AS efficiency_latest_weight,
  -- Blended rate metrics (latest-only when no qualified prior season; prior-only never occurs alone
  -- because carry-forward still requires a live latest season).
  CASE WHEN prev_qualified IS NULL OR prev_wopr IS NULL THEN wopr
       WHEN wopr IS NULL THEN prev_wopr
       ELSE LEAST(latest_weight_raw, 0.70) * wopr + (1 - LEAST(latest_weight_raw, 0.70)) * prev_wopr END AS b_wopr,
  CASE WHEN prev_qualified IS NULL OR prev_ngt_tgt_pg IS NULL THEN non_garbage_time_targets_per_game
       WHEN non_garbage_time_targets_per_game IS NULL THEN prev_ngt_tgt_pg
       ELSE LEAST(latest_weight_raw, 0.70) * non_garbage_time_targets_per_game + (1 - LEAST(latest_weight_raw, 0.70)) * prev_ngt_tgt_pg END AS b_ngt_tgt_pg,
  CASE WHEN prev_qualified IS NULL OR prev_rz_tgt_pg IS NULL THEN red_zone_targets_per_game
       WHEN red_zone_targets_per_game IS NULL THEN prev_rz_tgt_pg
       ELSE LEAST(latest_weight_raw, 0.70) * red_zone_targets_per_game + (1 - LEAST(latest_weight_raw, 0.70)) * prev_rz_tgt_pg END AS b_rz_tgt_pg,
  CASE WHEN prev_qualified IS NULL OR prev_yprr IS NULL THEN yprr
       WHEN yprr IS NULL THEN prev_yprr
       ELSE LEAST(latest_weight_raw, 0.60) * yprr + (1 - LEAST(latest_weight_raw, 0.60)) * prev_yprr END AS b_yprr,
  CASE WHEN prev_qualified IS NULL OR prev_epa_per_target IS NULL THEN epa_per_target
       WHEN epa_per_target IS NULL THEN prev_epa_per_target
       ELSE LEAST(latest_weight_raw, 0.60) * epa_per_target + (1 - LEAST(latest_weight_raw, 0.60)) * prev_epa_per_target END AS b_epa_per_target,
  CASE WHEN prev_qualified IS NULL OR prev_yac_per_reception IS NULL THEN yac_per_reception
       WHEN yac_per_reception IS NULL THEN prev_yac_per_reception
       ELSE LEAST(latest_weight_raw, 0.60) * yac_per_reception + (1 - LEAST(latest_weight_raw, 0.60)) * prev_yac_per_reception END AS b_yac_per_reception,
  CASE WHEN prev_qualified IS NULL OR prev_adot_adjusted_catch_rate IS NULL THEN adot_adjusted_catch_rate
       WHEN adot_adjusted_catch_rate IS NULL THEN prev_adot_adjusted_catch_rate
       ELSE LEAST(latest_weight_raw, 0.60) * adot_adjusted_catch_rate + (1 - LEAST(latest_weight_raw, 0.60)) * prev_adot_adjusted_catch_rate END AS b_adot_adjusted_catch_rate,
  0.70 * (CASE WHEN prev_qualified IS NULL OR prev_expected_td_per_game IS NULL THEN expected_td_per_game
               WHEN expected_td_per_game IS NULL THEN prev_expected_td_per_game
               ELSE LEAST(latest_weight_raw, 0.70) * expected_td_per_game + (1 - LEAST(latest_weight_raw, 0.70)) * prev_expected_td_per_game END)
  + 0.30 * (CASE WHEN prev_qualified IS NULL OR prev_actual_td_per_game IS NULL THEN actual_td_per_game
                 WHEN actual_td_per_game IS NULL THEN prev_actual_td_per_game
                 ELSE LEAST(latest_weight_raw, 0.70) * actual_td_per_game + (1 - LEAST(latest_weight_raw, 0.70)) * prev_actual_td_per_game END)
    AS b_blended_td_per_game,
  -- Availability stays separate from on-field performance.
  CASE WHEN prev_games_played_rate IS NULL THEN games_played_rate
       ELSE 0.70 * games_played_rate + 0.30 * prev_games_played_rate END AS two_year_availability_rate,
  -- Shrinkage samples include the weighted prior-season contribution.
  SAFE_DIVIDE(routes_run + (1 - LEAST(latest_weight_raw, 0.60)) * IFNULL(prev_routes_run, 0),
              routes_run + (1 - LEAST(latest_weight_raw, 0.60)) * IFNULL(prev_routes_run, 0) + 60) AS route_efficiency_shrink,
  SAFE_DIVIDE(targets + (1 - LEAST(latest_weight_raw, 0.60)) * IFNULL(prev_targets, 0),
              targets + (1 - LEAST(latest_weight_raw, 0.60)) * IFNULL(prev_targets, 0) + 60) AS target_efficiency_shrink
FROM weighted
WHERE latest_qualified OR (NOT season_qualified AND prev_qualified IS NOT NULL AND (games_played >= 3 OR routes_run >= 75));
