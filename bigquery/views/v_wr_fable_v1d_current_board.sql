-- Phase 35.1D current review context. Sleeper is display/current-team context only, never historical input.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_current_board` AS
WITH modified AS (
  SELECT
    season,
    variant_id,
    candidate_internal_player_id,
    player_name,
    team,
    games_played,
    routes_run,
    prior_season_available,
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
  WHERE season = 2025
    AND (injury_candidate_score IS NOT NULL OR carry_forward_replacement_score IS NOT NULL)
), baseline AS (
  SELECT
    candidate_internal_player_id,
    wr_fable_v1_score,
    RANK() OVER (ORDER BY wr_fable_v1_score DESC, player_name) AS old_fable_rank
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_scored_seasons`
  WHERE season = 2025
    AND wr_fable_v1_score IS NOT NULL
), standard_rankings AS (
  SELECT
    player_id,
    rank AS current_standard_rank
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.analytics_pigskin_rankings`
  WHERE is_active
    AND season = 2026
    AND position = 'WR'
    AND scoring_profile_id = 'standard'
    AND league_type_id = 'redraft'
    AND roster_format_id = 'one_qb'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY generated_at DESC) = 1
), sleeper AS (
  SELECT
    sleeper_player_id,
    gsis_id,
    team,
    status,
    injury_status,
    depth_chart_order,
    REGEXP_REPLACE(LOWER(full_name), r'[^a-z0-9]', '') AS normalized_name,
    COUNT(*) OVER (
      PARTITION BY REGEXP_REPLACE(LOWER(full_name), r'[^a-z0-9]', '')
    ) AS normalized_name_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_current_player_context`
  WHERE position = 'WR'
), context AS (
  SELECT
    modified.*,
    baseline.wr_fable_v1_score,
    baseline.old_fable_rank,
    standard_rankings.current_standard_rank,
    CASE modified.team
      WHEN 'HST' THEN 'HOU'
      WHEN 'BLT' THEN 'BAL'
      WHEN 'CLV' THEN 'CLE'
      WHEN 'ARZ' THEN 'ARI'
      WHEN 'LA' THEN 'LAR'
      ELSE modified.team
    END AS source_team,
    sleeper.team AS sleeper_current_team,
    sleeper.status AS sleeper_status,
    sleeper.injury_status AS sleeper_injury_status,
    sleeper.depth_chart_order AS sleeper_depth_chart_order
  FROM modified
  LEFT JOIN baseline USING (candidate_internal_player_id)
  LEFT JOIN standard_rankings
    ON standard_rankings.player_id = modified.candidate_internal_player_id
  LEFT JOIN sleeper
    ON sleeper.gsis_id = modified.candidate_internal_player_id
    OR (
      sleeper.gsis_id IS NULL
      AND sleeper.normalized_name_count = 1
      AND sleeper.normalized_name = REGEXP_REPLACE(LOWER(modified.player_name), r'[^a-z0-9]', '')
    )
), environment AS (
  SELECT team, team_environment_score
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1d_team_environment`
  WHERE season = 2025
), adjusted AS (
  SELECT
    context.*,
    source_environment.team_environment_score AS source_environment_score,
    destination_environment.team_environment_score AS destination_environment_score,
    destination_environment.team_environment_score - source_environment.team_environment_score
      AS environment_delta,
    context.sleeper_current_team IS NOT NULL
      AND context.sleeper_current_team != context.source_team AS team_changed
  FROM context
  LEFT JOIN environment AS source_environment
    ON source_environment.team = context.source_team
  LEFT JOIN environment AS destination_environment
    ON destination_environment.team = context.sleeper_current_team
), scores AS (
  SELECT
    adjusted.*,
    CASE WHEN team_changed AND environment_delta IS NOT NULL
      THEN 0.015 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
      ELSE 0.0 END AS e15_adjustment,
    CASE WHEN team_changed AND environment_delta IS NOT NULL
      THEN 0.025 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
      ELSE 0.0 END AS e25_adjustment,
    CASE WHEN team_changed AND environment_delta IS NOT NULL
      THEN 0.040 * LEAST(GREATEST(environment_delta, -1.5), 1.5)
      ELSE 0.0 END AS e40_adjustment
  FROM adjusted
)
SELECT
  scores.*,
  RANK() OVER (
    PARTITION BY variant_id
    ORDER BY injury_candidate_score DESC, player_name
  ) AS injury_candidate_rank,
  RANK() OVER (
    PARTITION BY variant_id
    ORDER BY injury_candidate_score + e15_adjustment DESC, player_name
  ) AS injury_e15_rank,
  RANK() OVER (
    PARTITION BY variant_id
    ORDER BY injury_candidate_score + e25_adjustment DESC, player_name
  ) AS injury_e25_rank,
  RANK() OVER (
    PARTITION BY variant_id
    ORDER BY injury_candidate_score + e40_adjustment DESC, player_name
  ) AS injury_e40_rank,
  RANK() OVER (
    PARTITION BY variant_id
    ORDER BY exclusion_only_score DESC, player_name
  ) AS exclusion_only_rank,
  RANK() OVER (
    PARTITION BY variant_id
    ORDER BY carry_forward_replacement_score DESC, player_name
  ) AS carry_forward_replacement_rank
FROM scores;
