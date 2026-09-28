-- Review-only 2026 rookie TE lane. This is not a fantasy ranking or live-board source.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_rookie_candidates` AS
WITH latest AS (
  SELECT *
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.sleeper_players_current`
  WHERE snapshot_at = (
    SELECT MAX(snapshot_at)
    FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.sleeper_players_current`
  )
),
eligible AS (
  SELECT
    sleeper_player_id,
    gsis_id,
    player_name,
    team,
    active,
    status,
    injury_status,
    depth_chart_position,
    depth_chart_order,
    search_rank,
    years_exp,
    snapshot_at,
    CASE
      WHEN depth_chart_position = 'TE' AND depth_chart_order = 1 THEN 'CURRENT_ROLE_TE1'
      WHEN depth_chart_position = 'TE' AND depth_chart_order = 2 THEN 'CURRENT_ROLE_TE2'
      WHEN depth_chart_position = 'TE' AND depth_chart_order IS NOT NULL THEN 'CURRENT_ROLE_DEPTH'
      ELSE 'CURRENT_ROLE_INCOMPLETE'
    END AS rookie_lane_status,
    CAST(NULL AS FLOAT64) AS formula_score,
    TO_JSON_STRING(STRUCT(
      gsis_id IS NULL AS gsis_id_missing,
      TRUE AS college_production_missing,
      TRUE AS draft_capital_missing,
      depth_chart_order IS NULL AS depth_chart_order_missing
    )) AS missing_flags_json
  FROM latest
  WHERE position = 'TE'
    AND years_exp = 0
    AND active
    AND status IN ('Active', 'ACT')
    AND team IS NOT NULL
    AND player_name != 'Player Invalid'
)
SELECT
  ROW_NUMBER() OVER (
    ORDER BY
      CASE rookie_lane_status
        WHEN 'CURRENT_ROLE_TE1' THEN 1
        WHEN 'CURRENT_ROLE_TE2' THEN 2
        WHEN 'CURRENT_ROLE_DEPTH' THEN 3
        ELSE 4
      END,
      IFNULL(search_rank, 9999999),
      player_name
  ) AS review_order,
  eligible.*
FROM eligible;
