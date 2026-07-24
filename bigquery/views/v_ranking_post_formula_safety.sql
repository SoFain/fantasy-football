-- Current-player context applied only after a deterministic formula is scored.
-- Historical formula and backtest views must never join this view.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_ranking_post_formula_safety` AS
WITH identity_bridge AS (
  SELECT
    sleeper_player_id,
    ARRAY_AGG(gsis_id IGNORE NULLS ORDER BY source_confidence DESC, updated_at DESC LIMIT 1)[SAFE_OFFSET(0)]
      AS bridge_gsis_id
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_identity_bridge`
  WHERE sleeper_player_id IS NOT NULL
  GROUP BY sleeper_player_id
), identity_by_name AS (
  SELECT
    REGEXP_REPLACE(LOWER(CONCAT(first_name, last_name)), r'[^a-z0-9]', '') AS normalized_name,
    position,
    ARRAY_AGG(gsis_id IGNORE NULLS ORDER BY source_confidence DESC, updated_at DESC LIMIT 1)[SAFE_OFFSET(0)]
      AS bridge_gsis_id,
    COUNT(DISTINCT gsis_id) AS gsis_id_count
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.player_identity_bridge`
  WHERE gsis_id IS NOT NULL AND first_name IS NOT NULL AND last_name IS NOT NULL
  GROUP BY normalized_name, position
), latest AS (
  SELECT
    context.sleeper_player_id,
    COALESCE(context.gsis_id, identity_bridge.bridge_gsis_id, identity_by_name.bridge_gsis_id) AS gsis_id,
    context.full_name AS player_name,
    context.team,
    context.position,
    context.active,
    context.status,
    context.injury_status,
    context.injury_body_part,
    context.injury_notes,
    context.depth_chart_position,
    context.depth_chart_order,
    context.years_exp,
    context.fetched_at
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_current_player_context` AS context
  LEFT JOIN identity_bridge USING (sleeper_player_id)
  LEFT JOIN identity_by_name
    ON identity_by_name.normalized_name = REGEXP_REPLACE(LOWER(context.full_name), r'[^a-z0-9]', '')
    AND identity_by_name.position = context.position
    AND identity_by_name.gsis_id_count = 1
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY context.sleeper_player_id
    ORDER BY context.fetched_at DESC
  ) = 1
), deduped AS (
  SELECT *
  FROM latest
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY COALESCE(gsis_id, CONCAT('sleeper:', sleeper_player_id)), position
    ORDER BY fetched_at DESC, sleeper_player_id
  ) = 1
), evaluated AS (
  SELECT
    *,
    active IS TRUE
      AND team IS NOT NULL
      AND status IN ('Active', 'ACT')
      AND fetched_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 72 HOUR)
      AS roster_context_eligible,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), fetched_at, HOUR) AS context_age_hours
  FROM deduped
), flagged AS (
  SELECT
    *,
    ARRAY(
      SELECT flag
      FROM UNNEST([
        IF(NOT roster_context_eligible, 'SLEEPER_ROSTER_REVIEW', NULL),
        IF(active IS NOT TRUE, 'SLEEPER_INACTIVE', NULL),
        IF(team IS NULL, 'SLEEPER_TEAMLESS', NULL),
        IF(status IS NULL OR status NOT IN ('Active', 'ACT'), 'SLEEPER_STATUS_REVIEW', NULL),
        IF(context_age_hours > 72, 'SLEEPER_CONTEXT_STALE', NULL),
        IF(roster_context_eligible AND depth_chart_order IS NULL, 'DEPTH_CHART_UNKNOWN', NULL),
        IF(position = 'QB' AND roster_context_eligible AND depth_chart_order > 1, 'QB_BACKUP_ROLE_REVIEW', NULL),
        IF(injury_status IS NOT NULL, 'INJURY_UNCERTAIN', NULL),
        IF(years_exp = 0, 'ROOKIE_CONTEXT_REQUIRED', NULL)
      ]) AS flag
      WHERE flag IS NOT NULL
    ) AS review_flags
  FROM evaluated
)
SELECT
  sleeper_player_id,
  gsis_id,
  player_name,
  team,
  position,
  active,
  status,
  injury_status,
  injury_body_part,
  injury_notes,
  depth_chart_position,
  depth_chart_order,
  years_exp,
  fetched_at,
  context_age_hours,
  roster_context_eligible,
  team IS NOT NULL AS current_board_rank_eligible,
  NOT roster_context_eligible
    OR (position = 'QB' AND depth_chart_order > 1) AS sleeper_hard_review,
  CASE
    WHEN NOT roster_context_eligible OR years_exp = 0 THEN 0.0
    WHEN depth_chart_order = 1 THEN 0.02
    WHEN position IN ('RB', 'WR', 'TE') AND depth_chart_order >= 3 THEN -0.04
    ELSE 0.0
  END AS post_formula_adjustment,
  CASE
    WHEN NOT roster_context_eligible THEN 'NO_ADJUSTMENT_REVIEW_REQUIRED'
    WHEN years_exp = 0 THEN 'NO_ADJUSTMENT_ROOKIE_REVIEW'
    WHEN depth_chart_order = 1 THEN 'CURRENT_ROLE_DEPTH_1'
    WHEN position IN ('RB', 'WR', 'TE') AND depth_chart_order >= 3 THEN 'CURRENT_ROLE_DEPTH_3_PLUS'
    ELSE 'NO_ADJUSTMENT'
  END AS post_formula_adjustment_code,
  CASE
    WHEN NOT roster_context_eligible THEN 'No role movement. Current roster context requires review.'
    WHEN years_exp = 0 THEN 'No role movement. Rookie context requires review.'
    WHEN depth_chart_order = 1 THEN 'Sleeper current depth order 1: +0.020.'
    WHEN position IN ('RB', 'WR', 'TE') AND depth_chart_order >= 3
      THEN 'Sleeper current depth order 3 or worse: -0.040.'
    ELSE 'No bounded current-role adjustment.'
  END AS post_formula_adjustment_detail,
  review_flags,
  ARRAY_TO_STRING(review_flags, '; ') AS review_flags_text,
  TO_JSON_STRING(review_flags) AS review_flags_json,
  ARRAY_LENGTH(review_flags) > 0 AS requires_owner_review,
  CASE
    WHEN team IS NULL THEN 'teamless_unranked'
    WHEN roster_context_eligible THEN 'eligible_current_sleeper_player'
    ELSE 'current_roster_review_required'
  END AS ranking_eligibility
FROM flagged;
