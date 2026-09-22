-- WR Fable v1.1 current board (2025 source metrics) with Sleeper current-team environment and
-- alpha-role adjustments. Current-board only: the alpha modifier uses today's Sleeper snapshot,
-- which has no dated historical archive yet, so it never appears in backtest folds.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v11_current_board` AS
WITH scored AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v11_scored_seasons`
  WHERE season = 2025 AND wr_fable_v11_score IS NOT NULL
),
sleeper AS (
  SELECT
    sleeper_player_id,
    gsis_id,
    team,
    status,
    injury_status,
    depth_chart_order,
    active,
    REGEXP_REPLACE(LOWER(full_name), r'[^a-z0-9]', '') AS normalized_name,
    COUNT(*) OVER (PARTITION BY REGEXP_REPLACE(LOWER(full_name), r'[^a-z0-9]', '')) AS normalized_name_count
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.sleeper_current_player_context`
  WHERE position = 'WR'
),
environment AS (
  SELECT team, team_environment_z FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_team_environment`
  WHERE season = 2025
),
enriched AS (
  SELECT
    scored.*,
    CASE scored.team WHEN 'HST' THEN 'HOU' WHEN 'BLT' THEN 'BAL' WHEN 'CLV' THEN 'CLE'
                     WHEN 'ARZ' THEN 'ARI' WHEN 'LA' THEN 'LAR' ELSE scored.team END AS source_team_canonical,
    sleeper.sleeper_player_id,
    sleeper.team AS sleeper_current_team,
    sleeper.status AS sleeper_status,
    sleeper.injury_status AS sleeper_injury_status,
    sleeper.depth_chart_order AS sleeper_depth_chart_order,
    sleeper.sleeper_player_id IS NULL AS sleeper_id_missing
  FROM scored
  LEFT JOIN sleeper
    ON sleeper.gsis_id = scored.candidate_internal_player_id
    OR (
      sleeper.gsis_id IS NULL
      AND sleeper.normalized_name_count = 1
      AND sleeper.normalized_name = REGEXP_REPLACE(LOWER(scored.player_name), r'[^a-z0-9]', '')
    )
),
adjusted AS (
  SELECT
    enriched.*,
    enriched.sleeper_current_team IS NOT NULL
      AND enriched.sleeper_current_team != enriched.source_team_canonical AS team_changed,
    env_destination.team_environment_z AS destination_environment_z,
    env_source.team_environment_z AS source_environment_z,
    CASE
      WHEN enriched.sleeper_current_team IS NULL OR enriched.sleeper_current_team = enriched.source_team_canonical THEN 0
      WHEN env_destination.team_environment_z - env_source.team_environment_z >= 0.50 THEN 1
      WHEN env_destination.team_environment_z - env_source.team_environment_z <= -0.50 THEN -1
      ELSE 0
    END AS situation_bucket,
    CASE
      WHEN enriched.sleeper_current_team IS NULL OR enriched.sleeper_current_team = enriched.source_team_canonical THEN 0.0
      WHEN enriched.sleeper_depth_chart_order = 1 THEN 0.03
      WHEN enriched.sleeper_depth_chart_order >= 3 THEN -0.03
      ELSE 0.0
    END AS alpha_role_adjustment,
    (enriched.sleeper_current_team IS NOT NULL
      AND enriched.sleeper_current_team != enriched.source_team_canonical
      AND enriched.sleeper_depth_chart_order IS NULL) AS alpha_role_review_flag
  FROM enriched
  LEFT JOIN environment AS env_source ON env_source.team = enriched.source_team_canonical
  LEFT JOIN environment AS env_destination ON env_destination.team = enriched.sleeper_current_team
)
SELECT
  adjusted.*,
  0.05 * situation_bucket AS team_situation_adjustment,
  LEAST(GREATEST(0.05 * situation_bucket + alpha_role_adjustment, -0.08), 0.08) AS total_context_adjustment,
  wr_fable_v11_score
    + LEAST(GREATEST(0.05 * situation_bucket + alpha_role_adjustment, -0.08), 0.08) AS wr_fable_v11_current_score
FROM adjusted;
