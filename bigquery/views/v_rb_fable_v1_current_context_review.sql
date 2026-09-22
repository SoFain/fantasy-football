-- Review-only Sleeper current-team context for the RB Fable v1 vs Standard comparison.
-- Evidence layer for owner review. It is NOT a Fable formula input and writes no ranking.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_v1_current_context_review` AS
WITH fable AS (
  SELECT
    player_name,
    team AS fable_source_team_raw,
    -- Situational source team codes normalized to standard NFL codes.
    CASE team
      WHEN 'HST' THEN 'HOU' WHEN 'BLT' THEN 'BAL' WHEN 'CLV' THEN 'CLE'
      WHEN 'ARZ' THEN 'ARI' WHEN 'LA' THEN 'LAR'
      ELSE team
    END AS fable_source_team,
    candidate_internal_player_id,
    identity_status AS fable_identity_status,
    identity_confidence,
    rb_fable_01_score,
    RANK() OVER (ORDER BY rb_fable_01_score DESC) AS fable_rank
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_rb_fable_01_scored_seasons`
  WHERE season = 2025 AND rb_fable_01_score IS NOT NULL
),
std AS (
  SELECT
    rank AS standard_rank,
    ranking_score AS standard_score,
    player_id,
    player_name AS standard_player_name,
    current_team AS current_standard_team,
    sleeper_player_id AS standard_sleeper_player_id
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.analytics_pigskin_rankings`
  WHERE is_active AND position = 'RB' AND scoring_profile_id = 'standard'
),
universe AS (
  SELECT
    COALESCE(fable.player_name, std.standard_player_name) AS player_name,
    fable.fable_source_team_raw,
    fable.fable_source_team,
    std.current_standard_team,
    COALESCE(fable.candidate_internal_player_id, std.player_id) AS internal_player_id,
    std.standard_sleeper_player_id,
    fable.fable_identity_status,
    fable.identity_confidence,
    fable.fable_rank,
    fable.rb_fable_01_score AS fable_score,
    std.standard_rank,
    std.standard_score,
    std.standard_rank - fable.fable_rank AS rank_delta
  FROM fable
  FULL OUTER JOIN std
    ON std.player_id = fable.candidate_internal_player_id
  WHERE fable.fable_rank <= 40 OR std.standard_rank <= 40
),
sleeper AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_current_player_context`
),
matched AS (
  SELECT
    universe.*,
    COALESCE(by_id.sleeper_player_id, by_gsis.sleeper_player_id, by_name.sleeper_player_id) AS sleeper_player_id,
    COALESCE(by_id.team, by_gsis.team, by_name.team) AS sleeper_current_team,
    COALESCE(by_id.status, by_gsis.status, by_name.status) AS sleeper_status,
    COALESCE(by_id.injury_status, by_gsis.injury_status, by_name.injury_status) AS sleeper_injury_status,
    COALESCE(by_id.injury_body_part, by_gsis.injury_body_part, by_name.injury_body_part) AS sleeper_injury_body_part,
    COALESCE(by_id.depth_chart_position, by_gsis.depth_chart_position, by_name.depth_chart_position) AS sleeper_depth_chart_position,
    COALESCE(by_id.depth_chart_order, by_gsis.depth_chart_order, by_name.depth_chart_order) AS sleeper_depth_chart_order,
    COALESCE(by_id.years_exp, by_gsis.years_exp, by_name.years_exp) AS sleeper_years_exp,
    COALESCE(by_id.age, by_gsis.age, by_name.age) AS sleeper_age,
    CASE
      WHEN by_id.sleeper_player_id IS NOT NULL THEN 'STANDARD_BOARD_SLEEPER_ID'
      WHEN by_gsis.sleeper_player_id IS NOT NULL THEN 'SLEEPER_GSIS_BRIDGE'
      WHEN by_name.sleeper_player_id IS NOT NULL THEN 'NORMALIZED_NAME_TEAM_FALLBACK'
      ELSE 'NO_SLEEPER_MATCH'
    END AS identity_match_method
  FROM universe
  LEFT JOIN sleeper AS by_id
    ON by_id.sleeper_player_id = universe.standard_sleeper_player_id
  LEFT JOIN sleeper AS by_gsis
    ON by_gsis.gsis_id = universe.internal_player_id
   AND by_id.sleeper_player_id IS NULL
  LEFT JOIN sleeper AS by_name
    ON by_name.position = 'RB'
   AND LOWER(REGEXP_REPLACE(by_name.full_name, r'[^a-zA-Z]', '')) =
       LOWER(REGEXP_REPLACE(universe.player_name, r'[^a-zA-Z]', ''))
   AND by_name.team IN (universe.fable_source_team, universe.current_standard_team)
   AND by_id.sleeper_player_id IS NULL
   AND by_gsis.sleeper_player_id IS NULL
)
SELECT
  matched.*,
  fable_source_team IS NOT NULL
    AND sleeper_current_team IS NOT NULL
    AND fable_source_team != sleeper_current_team AS team_changed_from_fable_source,
  current_standard_team IS NOT NULL
    AND sleeper_current_team IS NOT NULL
    AND current_standard_team != sleeper_current_team AS team_mismatch_between_standard_and_sleeper,
  CASE
    WHEN fable_rank IS NULL THEN 'NO_QUALIFIED_FABLE_ROW'
    WHEN sleeper_player_id IS NULL THEN 'SLEEPER_ID_MISSING'
    WHEN current_standard_team IS NOT NULL AND sleeper_current_team IS NOT NULL
      AND current_standard_team != sleeper_current_team THEN 'CURRENT_TEAM_MISMATCH'
    WHEN fable_source_team != sleeper_current_team
      AND COALESCE(fable_rank, 999) <= 30 THEN 'CURRENT_ROLE_REVIEW_REQUIRED'
    WHEN fable_source_team != sleeper_current_team THEN 'STALE_TEAM_CONTEXT'
    WHEN sleeper_injury_status IS NOT NULL THEN 'INJURY_STATUS_WARNING'
    WHEN COALESCE(sleeper_depth_chart_order, 1) > 1
      AND COALESCE(fable_rank, 999) <= 30 THEN 'SLEEPER_DEPTH_CHART_WARNING'
    WHEN identity_match_method = 'NORMALIZED_NAME_TEAM_FALLBACK' THEN 'MANUAL_REVIEW_REQUIRED'
    ELSE 'FABLE_SCORE_TRUSTED'
  END AS context_flag,
  CASE
    WHEN fable_rank IS NULL THEN 'No qualified 2025 Fable metric row; formula cannot rank this player.'
    WHEN sleeper_player_id IS NULL THEN 'No Sleeper identity match; verify manually.'
    WHEN current_standard_team IS NOT NULL AND sleeper_current_team IS NOT NULL
      AND current_standard_team != sleeper_current_team
      THEN 'Standard board team and Sleeper team disagree; one source is stale.'
    WHEN fable_source_team != sleeper_current_team AND COALESCE(fable_rank, 999) <= 30
      THEN 'Fable score is built on prior-team usage; current role must be reviewed by the owner.'
    WHEN fable_source_team != sleeper_current_team
      THEN 'Team changed since the 2025 source season; score context is stale.'
    WHEN sleeper_injury_status IS NOT NULL
      THEN 'Sleeper reports an active injury designation.'
    WHEN COALESCE(sleeper_depth_chart_order, 1) > 1 AND COALESCE(fable_rank, 999) <= 30
      THEN 'Sleeper depth chart lists this player below RB1 on his own team.'
    WHEN identity_match_method = 'NORMALIZED_NAME_TEAM_FALLBACK'
      THEN 'Matched by normalized name and team only; confirm identity.'
    ELSE 'Current team matches the 2025 source team; no context warning.'
  END AS context_note
FROM matched;
