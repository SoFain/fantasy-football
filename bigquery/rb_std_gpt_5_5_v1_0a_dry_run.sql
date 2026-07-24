-- Phase 33.35 read-only Standard RB formula dry-run.
-- No DDL or DML. Target outcomes are used only after scoring for evaluation.

WITH target_universe_base AS (
  SELECT
    target_season,
    target_week,
    player_id_internal,
    player_name,
    source_team AS team,
    analytical_grade_proxy,
    opportunity_score_proxy,
    efficiency_score_proxy,
    role_stability_score,
    profile_points_score,
    xfp_score_3yr,
    receiving_usage,
    high_value_xfp_score_3yr,
    offensive_snap_share_3yr,
    snap_role_stability_3yr,
    availability_score_3yr,
    source_window_start_season,
    source_window_end_season
  FROM `fantasy-football-498121.fantasy_football_brain.ranking_backtest_feature_mart`
  WHERE scoring_profile_id = 'standard'
    AND league_type_id = 'redraft'
    AND roster_format_id = 'one_qb'
    AND position = 'RB'
    AND target_week = 18
    AND target_season BETWEEN 2023 AND 2025
    AND source_window_end_season < target_season
),
season_outcomes_agg AS (
  SELECT
    season AS target_season,
    REGEXP_REPLACE(player_id_internal, r'^gsis:', '') AS player_id_internal,
    SUM(total_fantasy_points) AS actual_points
  FROM `fantasy-football-498121.fantasy_football_brain.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard'
    AND position = 'RB'
    AND season BETWEEN 2023 AND 2025
    AND week BETWEEN 1 AND 18
  GROUP BY target_season, player_id_internal
),
season_outcomes_ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY target_season ORDER BY actual_points DESC, player_id_internal) AS actual_position_rank
  FROM season_outcomes_agg
),
season_outcomes AS (
  SELECT
    *,
    MAX(IF(actual_position_rank = 36, actual_points, NULL)) OVER (PARTITION BY target_season) AS replacement_points
  FROM season_outcomes_ranked
),
target_universe AS (
  SELECT
    base.*,
    outcomes.actual_points,
    outcomes.actual_position_rank,
    outcomes.actual_points - outcomes.replacement_points AS value_over_replacement
  FROM target_universe_base base
  JOIN season_outcomes outcomes USING (target_season, player_id_internal)
),
source_weights AS (
  SELECT 1 AS seasons_ago, 0.60 AS source_weight
  UNION ALL SELECT 2, 0.30
  UNION ALL SELECT 3, 0.10
),
xfp_player_team_year AS (
  SELECT
    season,
    REGEXP_REPLACE(player_id_internal, r'^gsis:', '') AS player_id_internal,
    team,
    SUM(COALESCE(rush_fantasy_points_exp, 0.0)) AS rushing_xfp,
    SUM(
      COALESCE(rec_fantasy_points_exp, 0.0)
      - COALESCE(SAFE_CAST(JSON_VALUE(raw_payload_json, '$.receptions_exp') AS FLOAT64), 0.0)
    ) AS receiving_xfp_standard
  FROM `fantasy-football-498121.fantasy_football_brain.raw_ffopportunity_weekly`
  WHERE source_version = 'ffopportunity_weekly_latest'
    AND position = 'RB'
    AND season BETWEEN 2020 AND 2024
  GROUP BY season, player_id_internal, team
),
xfp_team_year AS (
  SELECT
    season,
    team,
    SUM(rushing_xfp) AS team_rushing_xfp,
    SUM(receiving_xfp_standard) AS team_receiving_xfp_standard
  FROM xfp_player_team_year
  GROUP BY season, team
),
xfp_league_year AS (
  SELECT
    season,
    AVG(team_rushing_xfp) AS league_team_rushing_xfp,
    AVG(team_receiving_xfp_standard) AS league_team_receiving_xfp_standard
  FROM xfp_team_year
  GROUP BY season
),
xfp_player_year AS (
  SELECT
    p.season,
    p.player_id_internal,
    SUM(p.rushing_xfp) AS rushing_xfp,
    SUM(p.receiving_xfp_standard) AS receiving_xfp_standard,
    SUM(t.team_rushing_xfp) AS represented_team_rushing_xfp,
    SUM(t.team_receiving_xfp_standard) AS represented_team_receiving_xfp_standard,
    SAFE_DIVIDE(SUM(p.rushing_xfp), NULLIF(SUM(t.team_rushing_xfp), 0.0)) AS rushing_xfp_share,
    SAFE_DIVIDE(
      SUM(p.receiving_xfp_standard),
      NULLIF(SUM(t.team_receiving_xfp_standard), 0.0)
    ) AS receiving_xfp_share,
    AVG(l.league_team_rushing_xfp) AS league_team_rushing_xfp,
    AVG(l.league_team_receiving_xfp_standard) AS league_team_receiving_xfp_standard
  FROM xfp_player_team_year p
  JOIN xfp_team_year t USING (season, team)
  JOIN xfp_league_year l USING (season)
  GROUP BY p.season, p.player_id_internal
),
advanced_year_raw AS (
  SELECT
    season,
    player_id_internal,
    team,
    receptions,
    carries,
    targets,
    receiving_epa,
    offensive_snap_share,
    weighted_opportunity_standard,
    red_zone_opportunities,
    goal_line_opportunities,
    ngs_rush_yards_over_expected_per_att,
    ngs_rushing_efficiency,
    ngs_box_count_rate
  FROM `fantasy-football-498121.fantasy_football_brain.player_season_advanced_metrics`
  WHERE metric_version = 'advanced_player_metrics_v1'
    AND position = 'RB'
    AND season BETWEEN 2020 AND 2024
),
advanced_team_year AS (
  SELECT
    season,
    team,
    SUM(weighted_opportunity_standard) AS team_weighted_opportunity_standard,
    SUM(red_zone_opportunities) AS team_red_zone_opportunities,
    SUM(goal_line_opportunities) AS team_goal_line_opportunities
  FROM advanced_year_raw
  GROUP BY season, team
),
advanced_share_rows AS (
  SELECT
    a.*,
    t.team_weighted_opportunity_standard,
    t.team_red_zone_opportunities,
    t.team_goal_line_opportunities,
    SAFE_DIVIDE(a.weighted_opportunity_standard, NULLIF(t.team_weighted_opportunity_standard, 0.0)) AS high_value_opportunity_share,
    SAFE_DIVIDE(a.red_zone_opportunities, NULLIF(t.team_red_zone_opportunities, 0.0)) AS red_zone_opportunity_share,
    SAFE_DIVIDE(a.goal_line_opportunities, NULLIF(t.team_goal_line_opportunities, 0.0)) AS goal_line_opportunity_share,
    SAFE_DIVIDE(a.receiving_epa, NULLIF(a.targets, 0.0)) AS receiving_epa_per_target,
    a.carries + a.receptions AS touches
  FROM advanced_year_raw a
  LEFT JOIN advanced_team_year t USING (season, team)
),
advanced_share_year AS (
  SELECT
    season,
    player_id_internal,
    ANY_VALUE(team HAVING MAX touches) AS team,
    SUM(receptions) AS receptions,
    SUM(carries) AS carries,
    SUM(targets) AS targets,
    SUM(receiving_epa) AS receiving_epa,
    AVG(offensive_snap_share) AS offensive_snap_share,
    SAFE_DIVIDE(SUM(weighted_opportunity_standard), NULLIF(SUM(team_weighted_opportunity_standard), 0.0)) AS high_value_opportunity_share,
    SAFE_DIVIDE(SUM(red_zone_opportunities), NULLIF(SUM(team_red_zone_opportunities), 0.0)) AS red_zone_opportunity_share,
    SAFE_DIVIDE(SUM(goal_line_opportunities), NULLIF(SUM(team_goal_line_opportunities), 0.0)) AS goal_line_opportunity_share,
    AVG(ngs_rush_yards_over_expected_per_att) AS ngs_rush_yards_over_expected_per_att,
    AVG(ngs_rushing_efficiency) AS ngs_rushing_efficiency,
    AVG(ngs_box_count_rate) AS ngs_box_count_rate,
    SAFE_DIVIDE(SUM(receiving_epa), NULLIF(SUM(targets), 0.0)) AS receiving_epa_per_target,
    SUM(touches) AS touches
  FROM advanced_share_rows
  GROUP BY season, player_id_internal
),
snap_games_year AS (
  SELECT
    season,
    player_id_internal,
    COUNT(DISTINCT IF(offensive_snaps > 0, week, NULL)) AS games_with_offensive_snaps
  FROM `fantasy-football-498121.fantasy_football_brain.player_week_advanced_metrics`
  WHERE metric_version = 'advanced_player_metrics_v1'
    AND position = 'RB'
    AND season BETWEEN 2020 AND 2024
  GROUP BY season, player_id_internal
),
fumbles_year AS (
  SELECT
    season,
    player_id_internal,
    SUM(COALESCE(SAFE_CAST(JSON_VALUE(source_stat_json, '$.fumbles_lost') AS FLOAT64), 0.0)) AS fumbles_lost
  FROM `fantasy-football-498121.fantasy_football_brain.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard'
    AND position = 'RB'
    AND season BETWEEN 2020 AND 2024
  GROUP BY season, player_id_internal
),
birth_dates AS (
  SELECT
    gsis_id AS player_id_internal,
    MAX(birth_date) AS birth_date,
    MAX(display_name) AS display_name
  FROM `fantasy-football-498121.fantasy_football_brain.dim_players_current`
  WHERE gsis_id IS NOT NULL
  GROUP BY gsis_id
),
weighted_source AS (
  SELECT
    u.target_season,
    u.player_id_internal,
    w.seasons_ago,
    w.source_weight,
    x.represented_team_rushing_xfp,
    x.represented_team_receiving_xfp_standard,
    x.league_team_rushing_xfp,
    x.league_team_receiving_xfp_standard,
    x.rushing_xfp_share,
    x.receiving_xfp_share,
    a.offensive_snap_share,
    a.high_value_opportunity_share,
    a.red_zone_opportunity_share,
    a.goal_line_opportunity_share,
    a.ngs_rush_yards_over_expected_per_att,
    a.ngs_rushing_efficiency,
    a.ngs_box_count_rate,
    a.receiving_epa_per_target,
    a.touches,
    f.fumbles_lost,
    SAFE_DIVIDE(f.fumbles_lost, NULLIF(a.touches, 0.0)) AS fumbles_lost_rate
  FROM target_universe u
  CROSS JOIN source_weights w
  LEFT JOIN xfp_player_year x
    ON x.player_id_internal = u.player_id_internal
   AND x.season = u.target_season - w.seasons_ago
  LEFT JOIN advanced_share_year a
    ON a.player_id_internal = u.player_id_internal
   AND a.season = u.target_season - w.seasons_ago
  LEFT JOIN fumbles_year f
    ON f.player_id_internal = u.player_id_internal
   AND f.season = u.target_season - w.seasons_ago
),
projected AS (
  SELECT
    target_season,
    player_id_internal,
    COUNTIF(represented_team_rushing_xfp IS NOT NULL) AS xfp_source_seasons,
    COUNTIF(ngs_rush_yards_over_expected_per_att IS NOT NULL) AS ngs_source_seasons,
    SAFE_DIVIDE(
      SUM(IF(represented_team_rushing_xfp IS NOT NULL, source_weight * represented_team_rushing_xfp, 0.0)),
      SUM(IF(represented_team_rushing_xfp IS NOT NULL, source_weight, 0.0))
    ) AS weighted_team_rushing_xfp,
    SAFE_DIVIDE(
      SUM(IF(represented_team_receiving_xfp_standard IS NOT NULL, source_weight * represented_team_receiving_xfp_standard, 0.0)),
      SUM(IF(represented_team_receiving_xfp_standard IS NOT NULL, source_weight, 0.0))
    ) AS weighted_team_receiving_xfp_standard,
    SAFE_DIVIDE(
      SUM(IF(league_team_rushing_xfp IS NOT NULL, source_weight * league_team_rushing_xfp, 0.0)),
      SUM(IF(league_team_rushing_xfp IS NOT NULL, source_weight, 0.0))
    ) AS weighted_league_team_rushing_xfp,
    SAFE_DIVIDE(
      SUM(IF(league_team_receiving_xfp_standard IS NOT NULL, source_weight * league_team_receiving_xfp_standard, 0.0)),
      SUM(IF(league_team_receiving_xfp_standard IS NOT NULL, source_weight, 0.0))
    ) AS weighted_league_team_receiving_xfp_standard,
    SAFE_DIVIDE(SUM(IF(rushing_xfp_share IS NOT NULL, source_weight * rushing_xfp_share, 0.0)), SUM(IF(rushing_xfp_share IS NOT NULL, source_weight, 0.0))) AS projected_rushing_xfp_share,
    SAFE_DIVIDE(SUM(IF(receiving_xfp_share IS NOT NULL, source_weight * receiving_xfp_share, 0.0)), SUM(IF(receiving_xfp_share IS NOT NULL, source_weight, 0.0))) AS projected_receiving_xfp_share,
    SAFE_DIVIDE(SUM(IF(offensive_snap_share IS NOT NULL, source_weight * offensive_snap_share, 0.0)), SUM(IF(offensive_snap_share IS NOT NULL, source_weight, 0.0))) AS projected_snap_share,
    SAFE_DIVIDE(SUM(IF(high_value_opportunity_share IS NOT NULL, source_weight * high_value_opportunity_share, 0.0)), SUM(IF(high_value_opportunity_share IS NOT NULL, source_weight, 0.0))) AS projected_high_value_share,
    SAFE_DIVIDE(SUM(IF(red_zone_opportunity_share IS NOT NULL, source_weight * red_zone_opportunity_share, 0.0)), SUM(IF(red_zone_opportunity_share IS NOT NULL, source_weight, 0.0))) AS projected_red_zone_share,
    SAFE_DIVIDE(SUM(IF(goal_line_opportunity_share IS NOT NULL, source_weight * goal_line_opportunity_share, 0.0)), SUM(IF(goal_line_opportunity_share IS NOT NULL, source_weight, 0.0))) AS projected_goal_line_share,
    SAFE_DIVIDE(SUM(IF(ngs_rush_yards_over_expected_per_att IS NOT NULL, source_weight * ngs_rush_yards_over_expected_per_att, 0.0)), SUM(IF(ngs_rush_yards_over_expected_per_att IS NOT NULL, source_weight, 0.0))) AS projected_ryoe_per_attempt,
    SAFE_DIVIDE(SUM(IF(ngs_rushing_efficiency IS NOT NULL, source_weight * ngs_rushing_efficiency, 0.0)), SUM(IF(ngs_rushing_efficiency IS NOT NULL, source_weight, 0.0))) AS projected_ngs_rushing_efficiency,
    SAFE_DIVIDE(SUM(IF(ngs_box_count_rate IS NOT NULL, source_weight * ngs_box_count_rate, 0.0)), SUM(IF(ngs_box_count_rate IS NOT NULL, source_weight, 0.0))) AS projected_box_resilience,
    SAFE_DIVIDE(SUM(IF(receiving_epa_per_target IS NOT NULL, source_weight * receiving_epa_per_target, 0.0)), SUM(IF(receiving_epa_per_target IS NOT NULL, source_weight, 0.0))) AS projected_receiving_epa_per_target,
    SAFE_DIVIDE(SUM(IF(fumbles_lost_rate IS NOT NULL, source_weight * fumbles_lost_rate, 0.0)), SUM(IF(fumbles_lost_rate IS NOT NULL, source_weight, 0.0))) AS projected_fumbles_lost_rate,
    SAFE_DIVIDE(SUM(IF(touches IS NOT NULL, source_weight * touches, 0.0)), SUM(IF(touches IS NOT NULL, source_weight, 0.0))) AS projected_touches
  FROM weighted_source
  GROUP BY target_season, player_id_internal
),
availability AS (
  SELECT
    u.target_season,
    u.player_id_internal,
    b.birth_date,
    b.display_name,
    DATE_DIFF(DATE(u.target_season, 9, 1), b.birth_date, YEAR) AS target_season_age,
    COALESCE(last.games_with_offensive_snaps, 0) AS games_with_snaps_last_season,
    COALESCE(prior.games_with_offensive_snaps, 0) AS games_with_snaps_two_years_ago
  FROM target_universe u
  LEFT JOIN birth_dates b USING (player_id_internal)
  LEFT JOIN snap_games_year last
    ON last.player_id_internal = u.player_id_internal
   AND last.season = u.target_season - 1
  LEFT JOIN snap_games_year prior
    ON prior.player_id_internal = u.player_id_internal
   AND prior.season = u.target_season - 2
),
component_values AS (
  SELECT
    u.*,
    p.* EXCEPT (target_season, player_id_internal),
    COALESCE(a.display_name, u.player_name) AS player_display_name,
    a.birth_date,
    a.target_season_age,
    a.games_with_snaps_last_season,
    a.games_with_snaps_two_years_ago,
    0.75 * p.weighted_team_rushing_xfp + 0.25 * p.weighted_league_team_rushing_xfp AS regressed_team_rushing_xfp,
    0.75 * p.weighted_team_receiving_xfp_standard + 0.25 * p.weighted_league_team_receiving_xfp_standard AS regressed_team_receiving_xfp_standard,
    LEAST(1.0, GREATEST(0.65, (0.70 * a.games_with_snaps_last_season + 0.30 * a.games_with_snaps_two_years_ago) / 17.0)) AS historical_availability_factor,
    CASE
      WHEN a.target_season_age BETWEEN 21 AND 24 THEN 1.00
      WHEN a.target_season_age = 25 THEN 0.99
      WHEN a.target_season_age = 26 THEN 0.98
      WHEN a.target_season_age = 27 THEN 0.96
      WHEN a.target_season_age = 28 THEN 0.93
      WHEN a.target_season_age = 29 THEN 0.89
      WHEN a.target_season_age >= 30 THEN 0.84
      ELSE NULL
    END AS age_availability_factor
  FROM target_universe u
  LEFT JOIN projected p USING (target_season, player_id_internal)
  LEFT JOIN availability a USING (target_season, player_id_internal)
),
base_components AS (
  SELECT
    *,
    regressed_team_rushing_xfp * projected_rushing_xfp_share
      + regressed_team_receiving_xfp_standard * projected_receiving_xfp_share AS base_rb_standard_xfp,
    age_availability_factor * historical_availability_factor AS availability_multiplier,
    2.0 * projected_fumbles_lost_rate * projected_touches AS fumble_lost_penalty,
    0.55 * analytical_grade_proxy
      + 0.15 * opportunity_score_proxy
      + 0.10 * efficiency_score_proxy
      + 0.10 * role_stability_score
      + 0.10 * profile_points_score AS current_pigskin_proxy_score,
    0.50 * (
      0.55 * analytical_grade_proxy
      + 0.15 * opportunity_score_proxy
      + 0.10 * efficiency_score_proxy
      + 0.10 * role_stability_score
      + 0.10 * profile_points_score
    )
      + 0.20 * xfp_score_3yr
      + 0.15 * receiving_usage
      + 0.075 * high_value_xfp_score_3yr
      + 0.025 * offensive_snap_share_3yr
      + 0.025 * snap_role_stability_3yr
      + 0.025 * availability_score_3yr AS prior_episode_formula_score
  FROM component_values
),
normalized AS (
  SELECT
    *,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(projected_snap_share - AVG(projected_snap_share) OVER (PARTITION BY target_season), STDDEV_POP(projected_snap_share) OVER (PARTITION BY target_season)))) / 2.0 AS snap_modifier,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(projected_high_value_share - AVG(projected_high_value_share) OVER (PARTITION BY target_season), STDDEV_POP(projected_high_value_share) OVER (PARTITION BY target_season)))) / 2.0 AS high_value_modifier,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(projected_red_zone_share - AVG(projected_red_zone_share) OVER (PARTITION BY target_season), STDDEV_POP(projected_red_zone_share) OVER (PARTITION BY target_season)))) / 2.0 AS red_zone_modifier,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(projected_goal_line_share - AVG(projected_goal_line_share) OVER (PARTITION BY target_season), STDDEV_POP(projected_goal_line_share) OVER (PARTITION BY target_season)))) / 2.0 AS goal_line_modifier,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(projected_ryoe_per_attempt - AVG(projected_ryoe_per_attempt) OVER (PARTITION BY target_season), STDDEV_POP(projected_ryoe_per_attempt) OVER (PARTITION BY target_season)))) / 2.0 AS ryoe_modifier,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(AVG(projected_ngs_rushing_efficiency) OVER (PARTITION BY target_season) - projected_ngs_rushing_efficiency, STDDEV_POP(projected_ngs_rushing_efficiency) OVER (PARTITION BY target_season)))) / 2.0 AS rushing_efficiency_modifier,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(projected_box_resilience - AVG(projected_box_resilience) OVER (PARTITION BY target_season), STDDEV_POP(projected_box_resilience) OVER (PARTITION BY target_season)))) / 2.0 AS box_resilience_modifier,
    LEAST(2.0, GREATEST(-2.0, SAFE_DIVIDE(projected_receiving_epa_per_target - AVG(projected_receiving_epa_per_target) OVER (PARTITION BY target_season), STDDEV_POP(projected_receiving_epa_per_target) OVER (PARTITION BY target_season)))) / 2.0 AS receiving_epa_modifier
  FROM base_components
),
scored_components AS (
  SELECT
    *,
    0.40 * snap_modifier
      + 0.30 * high_value_modifier
      + 0.20 * red_zone_modifier
      + 0.10 * goal_line_modifier AS role_stability_formula_score,
    0.4375 * ryoe_modifier
      + 0.3125 * rushing_efficiency_modifier
      + 0.2500 * box_resilience_modifier AS efficiency_score_rushing_only,
    0.35 * ryoe_modifier
      + 0.25 * rushing_efficiency_modifier
      + 0.20 * box_resilience_modifier
      + 0.20 * receiving_epa_modifier AS efficiency_score_epa,
    birth_date IS NOT NULL
      AND xfp_source_seasons > 0
      AND projected_snap_share IS NOT NULL
      AND projected_high_value_share IS NOT NULL
      AND projected_red_zone_share IS NOT NULL
      AND projected_goal_line_share IS NOT NULL
      AND projected_ryoe_per_attempt IS NOT NULL
      AND projected_ngs_rushing_efficiency IS NOT NULL
      AND projected_box_resilience IS NOT NULL
      AND projected_fumbles_lost_rate IS NOT NULL
      AND projected_touches IS NOT NULL AS rushing_only_eligible
  FROM normalized
),
formula_scores AS (
  SELECT
    *,
    LEAST(1.035, GREATEST(0.965, 1.0 + 0.035 * role_stability_formula_score)) AS role_multiplier,
    LEAST(1.030, GREATEST(0.970, 1.0 + 0.030 * efficiency_score_rushing_only)) AS efficiency_multiplier_rushing_only,
    LEAST(1.030, GREATEST(0.970, 1.0 + 0.030 * efficiency_score_epa)) AS efficiency_multiplier_epa,
    rushing_only_eligible AND projected_receiving_epa_per_target IS NOT NULL AS epa_eligible,
    (
      IF(games_with_snaps_last_season <= 12, 1, 0)
      + IF(games_with_snaps_last_season + games_with_snaps_two_years_ago <= 26, 1, 0)
      + IF(target_season_age >= 28, 1, 0)
      + IF(historical_availability_factor < 0.80, 1, 0)
      + IF(projected_touches >= 300 AND target_season_age >= 27, 1, 0)
    ) >= 2 AS availability_risk_flag
  FROM scored_components
),
candidate_rows AS (
  SELECT
    target_season,
    player_id_internal,
    player_display_name AS player_name,
    team,
    actual_points,
    actual_position_rank,
    value_over_replacement,
    source_window_start_season,
    source_window_end_season,
    xfp_source_seasons,
    ngs_source_seasons,
    base_rb_standard_xfp,
    role_multiplier,
    efficiency_multiplier_rushing_only,
    efficiency_multiplier_epa,
    availability_multiplier,
    fumble_lost_penalty,
    availability_risk_flag,
    rushing_only_eligible,
    epa_eligible,
    current_pigskin_proxy_score,
    prior_episode_formula_score,
    IF(
      rushing_only_eligible,
      base_rb_standard_xfp * role_multiplier * efficiency_multiplier_rushing_only * availability_multiplier - fumble_lost_penalty,
      NULL
    ) AS rushing_only_projected_points,
    IF(
      epa_eligible,
      base_rb_standard_xfp * role_multiplier * efficiency_multiplier_epa * availability_multiplier - fumble_lost_penalty,
      NULL
    ) AS epa_projected_points,
    projected_receiving_epa_per_target,
    projected_receiving_xfp_share
  FROM formula_scores
),
ranked AS (
  SELECT
    *,
    ROW_NUMBER() OVER (PARTITION BY target_season ORDER BY current_pigskin_proxy_score DESC, player_id_internal) AS current_pigskin_rank,
    ROW_NUMBER() OVER (PARTITION BY target_season ORDER BY prior_episode_formula_score DESC, player_id_internal) AS prior_episode_rank,
    IF(rushing_only_eligible, ROW_NUMBER() OVER (PARTITION BY target_season, rushing_only_eligible ORDER BY rushing_only_projected_points DESC, player_id_internal), NULL) AS rushing_only_rank,
    IF(epa_eligible, ROW_NUMBER() OVER (PARTITION BY target_season, epa_eligible ORDER BY epa_projected_points DESC, player_id_internal), NULL) AS epa_rank
  FROM candidate_rows
)
SELECT
  target_season,
  player_id_internal,
  player_name,
  team,
  actual_points,
  actual_position_rank,
  value_over_replacement,
  current_pigskin_rank,
  prior_episode_rank,
  rushing_only_rank,
  epa_rank,
  current_pigskin_proxy_score,
  prior_episode_formula_score,
  rushing_only_projected_points,
  epa_projected_points,
  base_rb_standard_xfp,
  role_multiplier,
  efficiency_multiplier_rushing_only,
  efficiency_multiplier_epa,
  availability_multiplier,
  fumble_lost_penalty,
  availability_risk_flag,
  rushing_only_eligible,
  epa_eligible,
  xfp_source_seasons,
  ngs_source_seasons,
  projected_receiving_epa_per_target,
  projected_receiving_xfp_share,
  source_window_start_season,
  source_window_end_season
FROM ranked
ORDER BY target_season, current_pigskin_rank;
