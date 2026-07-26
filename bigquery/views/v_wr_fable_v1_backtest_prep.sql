-- WR Fable v1 prior-season scores and next-season Standard outcomes. No rankings are written.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_backtest_prep` AS
WITH scored AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v1_scored_seasons`
  WHERE season BETWEEN 2022 AND 2024
),
target_totals AS (
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
),
target_ranked AS (
  SELECT
    *,
    DENSE_RANK() OVER (PARTITION BY season ORDER BY target_standard_ppg DESC, target_standard_points DESC) AS target_standard_wr_rank
  FROM target_totals
  WHERE target_games >= 6
)
SELECT
  scored.*,
  scored.season + 1 AS target_season,
  target.target_games,
  target.target_standard_points,
  target.target_standard_ppg,
  target.target_standard_wr_rank,
  target.target_player_id IS NOT NULL AS target_available
FROM scored
LEFT JOIN target_ranked AS target
  ON target.season = scored.season + 1
 AND target.target_player_id = scored.candidate_internal_player_id;
