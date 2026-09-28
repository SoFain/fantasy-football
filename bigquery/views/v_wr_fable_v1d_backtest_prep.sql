-- Phase 35.1D bounded folds. No undated current context enters historical evaluation.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_backtest_prep` AS
WITH scored AS (
  SELECT
    season,
    variant_id,
    candidate_internal_player_id,
    player_name,
    team,
    games_played,
    routes_run,
    prior_season_available,
    prior_season_qualified,
    prior_season_weight,
    rookie_limited_sample_flag,
    age_availability_component,
    injury_candidate_score,
    baseline_v1_score,
    baseline_v1_score_available,
    exclusion_only_score,
    prior_v1_score,
    prior_v1_age_availability_component,
    prior_score_carry_forward_eligible,
    prior_score_carry_forward_score,
    carry_forward_replacement_score,
    rookie_review_score
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_scored_seasons`
  WHERE season BETWEEN 2022 AND 2024
    AND (injury_candidate_score IS NOT NULL OR carry_forward_replacement_score IS NOT NULL)
), destination AS (
  SELECT
    season AS target_season,
    gsis_id,
    ARRAY_AGG(CASE team WHEN 'LA' THEN 'LAR' ELSE team END ORDER BY team LIMIT 1)[SAFE_OFFSET(0)]
      AS destination_team
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_rosters_weekly`
  WHERE position = 'WR'
    AND week = 1
    AND season BETWEEN 2023 AND 2025
    AND gsis_id IS NOT NULL
  GROUP BY target_season, gsis_id
), target_totals AS (
  SELECT
    season,
    source_player_key AS target_player_id,
    COUNT(*) AS target_games,
    SUM(total_fantasy_points) AS target_standard_points,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS target_standard_ppg
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard'
    AND position = 'WR'
    AND season BETWEEN 2023 AND 2025
    AND week BETWEEN 1 AND 18
  GROUP BY season, target_player_id
), target_ranked AS (
  SELECT
    target_totals.*,
    DENSE_RANK() OVER (
      PARTITION BY season
      ORDER BY target_standard_ppg DESC, target_standard_points DESC
    ) AS target_standard_wr_rank
  FROM target_totals
  WHERE target_games >= 6
), context AS (
  SELECT
    scored.*,
    scored.season + 1 AS target_season,
    CASE scored.team
      WHEN 'HST' THEN 'HOU'
      WHEN 'BLT' THEN 'BAL'
      WHEN 'CLV' THEN 'CLE'
      WHEN 'ARZ' THEN 'ARI'
      WHEN 'LA' THEN 'LAR'
      ELSE scored.team
    END AS source_team,
    destination.destination_team
  FROM scored
  LEFT JOIN destination
    ON destination.target_season = scored.season + 1
   AND destination.gsis_id = scored.candidate_internal_player_id
), enriched AS (
  SELECT
    context.*,
    source_environment.team_environment_score AS source_environment_score,
    destination_environment.team_environment_score AS destination_environment_score,
    destination_environment.team_environment_score - source_environment.team_environment_score
      AS environment_delta,
    context.destination_team IS NOT NULL
      AND context.destination_team != context.source_team AS team_changed,
    target.target_games,
    target.target_standard_points,
    target.target_standard_ppg,
    target.target_standard_wr_rank,
    target.target_player_id IS NOT NULL AS target_available
  FROM context
  LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_team_environment` AS source_environment
    ON source_environment.season = context.season
   AND source_environment.team = context.source_team
  LEFT JOIN `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_team_environment` AS destination_environment
    ON destination_environment.season = context.season
   AND destination_environment.team = context.destination_team
  LEFT JOIN target_ranked AS target
    ON target.season = context.target_season
   AND target.target_player_id = context.candidate_internal_player_id
)
SELECT
  enriched.*,
  CASE WHEN team_changed AND environment_delta IS NOT NULL
    THEN 0.015 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
    ELSE 0.0 END AS e15_adjustment,
  CASE WHEN team_changed AND environment_delta IS NOT NULL
    THEN 0.025 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
    ELSE 0.0 END AS e25_adjustment,
  CASE WHEN team_changed AND environment_delta IS NOT NULL
    THEN 0.040 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
    ELSE 0.0 END AS e40_adjustment,
  injury_candidate_score + CASE WHEN team_changed AND environment_delta IS NOT NULL
    THEN 0.015 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
    ELSE 0.0 END AS injury_e15_score,
  injury_candidate_score + CASE WHEN team_changed AND environment_delta IS NOT NULL
    THEN 0.025 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
    ELSE 0.0 END AS injury_e25_score,
  injury_candidate_score + CASE WHEN team_changed AND environment_delta IS NOT NULL
    THEN 0.040 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
    ELSE 0.0 END AS injury_e40_score
FROM enriched;
