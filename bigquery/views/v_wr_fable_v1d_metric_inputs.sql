-- Phase 35.1D conditional injury variants. Rate metrics only; raw totals are never blended.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_metric_inputs` AS
WITH first_nfl_seasons AS (
  SELECT
    player_id_internal,
    MIN(season) AS first_nfl_season
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.stg_player_week_stats`
  WHERE position = 'WR'
    AND player_id_internal IS NOT NULL
    AND season BETWEEN 2014 AND 2025
  GROUP BY player_id_internal
), derived AS (
  SELECT
    splits.*,
    players.rookie_year,
    first_nfl_seasons.first_nfl_season,
    splits.non_garbage_time_routes_run * splits.non_garbage_time_targets_per_route_run
      AS non_garbage_time_targets,
    SAFE_DIVIDE(
      splits.non_garbage_time_routes_run * splits.non_garbage_time_targets_per_route_run,
      splits.games_played
    ) AS non_garbage_time_targets_per_game,
    splits.red_zone_routes_run * splits.red_zone_targets_per_route_run AS red_zone_targets,
    SAFE_DIVIDE(
      splits.red_zone_routes_run * splits.red_zone_targets_per_route_run,
      splits.games_played
    ) AS red_zone_targets_per_game,
    CASE WHEN splits.targets > 0 THEN SAFE_DIVIDE(splits.total_epa, splits.targets) END AS epa_per_target,
    CASE WHEN splits.receptions > 0 THEN SAFE_DIVIDE(splits.yac, splits.receptions) END AS yac_per_reception,
    1.5 * (splits.target_share / 100.0) + 0.7 * splits.air_yards_share AS wopr,
    SAFE_DIVIDE(splits.receiving_touchdowns, splits.games_played) AS actual_td_per_game,
    IF(splits.age BETWEEN 22 AND 25, 1, 0) AS breakout_window_bonus,
    CASE WHEN splits.age IS NULL THEN NULL ELSE -GREATEST(0, splits.age - 29) END AS decline_penalty,
    SAFE_DIVIDE(splits.games_played, 17) AS games_played_rate,
    (splits.games_played >= 6 OR splits.targets >= 40) AS season_qualified
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_situational_splits` AS splits
  LEFT JOIN `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.dim_players_current` AS players
    ON players.player_id_internal = splits.candidate_internal_player_id
  LEFT JOIN first_nfl_seasons
    ON first_nfl_seasons.player_id_internal = splits.candidate_internal_player_id
  WHERE splits.identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
    AND NOT splits.duplicate_identity_collision
    AND (splits.games_played >= 3 OR splits.routes_run >= 75 OR splits.targets >= 40)
), qualified_reference AS (
  SELECT * FROM derived WHERE season_qualified
), catch_rate_regression AS (
  SELECT
    season,
    AVG(catch_pct) AS mean_catch_pct,
    AVG(adot) AS mean_adot,
    SAFE_DIVIDE(COVAR_POP(catch_pct, adot), VAR_POP(adot)) AS adot_slope
  FROM qualified_reference
  WHERE catch_pct IS NOT NULL AND adot IS NOT NULL
  GROUP BY season
), league_rz_conversion AS (
  SELECT
    season,
    SAFE_DIVIDE(SUM(red_zone_touchdowns), SUM(red_zone_targets)) AS league_wr_rz_td_conversion
  FROM qualified_reference
  WHERE red_zone_targets IS NOT NULL AND red_zone_touchdowns IS NOT NULL
  GROUP BY season
), enriched AS (
  SELECT
    derived.*,
    derived.catch_pct
      - (regression.mean_catch_pct + regression.adot_slope * (derived.adot - regression.mean_adot))
      AS adot_adjusted_catch_rate,
    derived.red_zone_targets_per_game * conversion.league_wr_rz_td_conversion AS expected_td_per_game,
    0.70 * (derived.red_zone_targets_per_game * conversion.league_wr_rz_td_conversion)
      + 0.30 * derived.actual_td_per_game AS latest_blended_td_per_game
  FROM derived
  JOIN catch_rate_regression AS regression USING (season)
  JOIN league_rz_conversion AS conversion USING (season)
), paired AS (
  SELECT
    latest.*,
    previous.candidate_internal_player_id IS NOT NULL AS prior_season_available,
    previous.season_qualified AS prior_season_qualified,
    previous.wopr AS prior_wopr,
    previous.non_garbage_time_targets_per_game AS prior_ngt_targets_per_game,
    previous.red_zone_targets_per_game AS prior_rz_targets_per_game,
    previous.yprr AS prior_yprr,
    previous.epa_per_target AS prior_epa_per_target,
    previous.yac_per_reception AS prior_yac_per_reception,
    previous.adot_adjusted_catch_rate AS prior_adot_adjusted_catch_rate,
    previous.latest_blended_td_per_game AS prior_blended_td_per_game,
    previous.games_played_rate AS prior_games_played_rate,
    previous.routes_run AS prior_routes_run,
    previous.targets AS prior_targets,
    previous.team AS prior_team,
    COALESCE(latest.rookie_year, latest.first_nfl_season) = latest.season
      AS rookie_no_prior_season
  FROM enriched AS latest
  LEFT JOIN enriched AS previous
    ON previous.candidate_internal_player_id = latest.candidate_internal_player_id
   AND previous.season = latest.season - 1
), variants AS (
  SELECT * FROM UNNEST([
    STRUCT('I4' AS variant_id, 13 AS trigger_max_games),
    STRUCT('I7' AS variant_id, 10 AS trigger_max_games),
    STRUCT('I10' AS variant_id, 7 AS trigger_max_games)
  ])
), weighted AS (
  SELECT
    paired.*,
    variants.variant_id,
    variants.trigger_max_games,
    CASE
      WHEN paired.games_played > variants.trigger_max_games THEN 0.0
      WHEN NOT IFNULL(paired.prior_season_qualified, FALSE) THEN 0.0
      WHEN paired.wopr IS NULL OR paired.prior_wopr IS NULL THEN 0.0
      WHEN paired.non_garbage_time_targets_per_game IS NULL
        OR paired.prior_ngt_targets_per_game IS NULL THEN 0.0
      WHEN paired.red_zone_targets_per_game IS NULL
        OR paired.prior_rz_targets_per_game IS NULL THEN 0.0
      WHEN paired.yprr IS NULL OR paired.prior_yprr IS NULL THEN 0.0
      WHEN paired.epa_per_target IS NULL OR paired.prior_epa_per_target IS NULL THEN 0.0
      WHEN paired.yac_per_reception IS NULL OR paired.prior_yac_per_reception IS NULL THEN 0.0
      WHEN paired.adot_adjusted_catch_rate IS NULL
        OR paired.prior_adot_adjusted_catch_rate IS NULL THEN 0.0
      WHEN paired.latest_blended_td_per_game IS NULL
        OR paired.prior_blended_td_per_game IS NULL THEN 0.0
      WHEN paired.games_played BETWEEN 13 AND 17 THEN 0.0
      WHEN paired.games_played BETWEEN 9 AND 12 THEN 0.15
      WHEN paired.games_played BETWEEN 5 AND 8 THEN 0.30
      WHEN paired.games_played BETWEEN 3 AND 4 THEN 0.40
      ELSE 0.0
    END AS prior_season_weight,
    CASE
      WHEN paired.prior_games_played_rate IS NULL THEN paired.games_played_rate
      ELSE 0.70 * paired.games_played_rate + 0.30 * paired.prior_games_played_rate
    END AS two_year_availability_rate
  FROM paired
  CROSS JOIN variants
  WHERE paired.season_qualified
    OR (
      IFNULL(paired.prior_season_qualified, FALSE)
      AND (paired.games_played >= 3 OR paired.routes_run >= 75)
    )
    OR (
      paired.rookie_no_prior_season
      AND (paired.games_played >= 3 OR paired.routes_run >= 75)
    )
)
SELECT
  weighted.*,
  prior_season_weight > 0 AS injury_blend_applied,
  rookie_no_prior_season AS rookie_limited_sample_flag,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * wopr + prior_season_weight * prior_wopr
    ELSE wopr END AS modified_wopr,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * non_garbage_time_targets_per_game
      + prior_season_weight * prior_ngt_targets_per_game
    ELSE non_garbage_time_targets_per_game END AS modified_ngt_targets_per_game,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * red_zone_targets_per_game
      + prior_season_weight * prior_rz_targets_per_game
    ELSE red_zone_targets_per_game END AS modified_rz_targets_per_game,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * yprr + prior_season_weight * prior_yprr
    ELSE yprr END AS modified_yprr,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * epa_per_target + prior_season_weight * prior_epa_per_target
    ELSE epa_per_target END AS modified_epa_per_target,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * yac_per_reception + prior_season_weight * prior_yac_per_reception
    ELSE yac_per_reception END AS modified_yac_per_reception,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * adot_adjusted_catch_rate
      + prior_season_weight * prior_adot_adjusted_catch_rate
    ELSE adot_adjusted_catch_rate END AS modified_adot_adjusted_catch_rate,
  CASE WHEN prior_season_weight > 0
    THEN (1 - prior_season_weight) * latest_blended_td_per_game
      + prior_season_weight * prior_blended_td_per_game
    ELSE latest_blended_td_per_game END AS modified_blended_td_per_game,
  CASE
    WHEN rookie_no_prior_season THEN SAFE_DIVIDE(routes_run, routes_run + 90)
    ELSE SAFE_DIVIDE(
      routes_run + prior_season_weight * IFNULL(prior_routes_run, 0),
      routes_run + prior_season_weight * IFNULL(prior_routes_run, 0) + 60
    )
  END AS modified_route_efficiency_shrink,
  CASE
    WHEN rookie_no_prior_season THEN SAFE_DIVIDE(targets, targets + 90)
    ELSE SAFE_DIVIDE(
      targets + prior_season_weight * IFNULL(prior_targets, 0),
      targets + prior_season_weight * IFNULL(prior_targets, 0) + 60
    )
  END AS modified_target_efficiency_shrink
FROM weighted;
