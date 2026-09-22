-- WR Fable v1.1 backtest prep: blended score plus leakage-safe team-environment modifier.
-- Destination team = target-season Week 1 roster (known before Week 1). Environment inputs come
-- only from the input season. No target-season outcomes feed any score.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v11_backtest_prep` AS
WITH scored AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_fable_v11_scored_seasons`
  WHERE season BETWEEN 2022 AND 2024
),
destination AS (
  SELECT season AS target_season, gsis_id,
    ARRAY_AGG(team ORDER BY week LIMIT 1)[SAFE_OFFSET(0)] AS destination_team_raw
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.raw_nflverse_rosters_weekly`
  WHERE position = 'WR' AND week = 1 AND season BETWEEN 2023 AND 2025 AND gsis_id IS NOT NULL
  GROUP BY season, gsis_id
),
environment AS (
  SELECT season, team, team_environment_score, team_environment_z
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_wr_team_environment`
),
target_totals AS (
  SELECT season, source_player_key AS target_player_id, COUNT(*) AS target_games,
    SUM(total_fantasy_points) AS target_standard_points,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS target_standard_ppg
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard' AND position = 'WR'
    AND season BETWEEN 2023 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, target_player_id
),
target_ranked AS (
  SELECT *, DENSE_RANK() OVER (PARTITION BY season ORDER BY target_standard_ppg DESC, target_standard_points DESC) AS target_standard_wr_rank
  FROM target_totals
  WHERE target_games >= 6
),
enriched AS (
  SELECT
    scored.*,
    scored.season + 1 AS target_season,
    CASE scored.team WHEN 'HST' THEN 'HOU' WHEN 'BLT' THEN 'BAL' WHEN 'CLV' THEN 'CLE'
                     WHEN 'ARZ' THEN 'ARI' WHEN 'LA' THEN 'LAR' ELSE scored.team END AS source_team_canonical,
    CASE destination.destination_team_raw WHEN 'LA' THEN 'LAR' ELSE destination.destination_team_raw END AS destination_team
  FROM scored
  LEFT JOIN destination
    ON destination.target_season = scored.season + 1
   AND destination.gsis_id = scored.candidate_internal_player_id
)
SELECT
  enriched.*,
  env_source.team_environment_z AS source_team_environment_z,
  env_destination.team_environment_z AS destination_team_environment_z,
  enriched.destination_team IS NOT NULL
    AND enriched.destination_team != enriched.source_team_canonical AS team_changed,
  CASE
    WHEN enriched.destination_team IS NULL OR enriched.destination_team = enriched.source_team_canonical THEN 0
    WHEN env_destination.team_environment_z - env_source.team_environment_z >= 0.50 THEN 1
    WHEN env_destination.team_environment_z - env_source.team_environment_z <= -0.50 THEN -1
    ELSE 0
  END AS situation_bucket,
  0.05 * CASE
    WHEN enriched.destination_team IS NULL OR enriched.destination_team = enriched.source_team_canonical THEN 0
    WHEN env_destination.team_environment_z - env_source.team_environment_z >= 0.50 THEN 1
    WHEN env_destination.team_environment_z - env_source.team_environment_z <= -0.50 THEN -1
    ELSE 0
  END AS team_situation_adjustment,
  enriched.wr_fable_v11_score + 0.05 * CASE
    WHEN enriched.destination_team IS NULL OR enriched.destination_team = enriched.source_team_canonical THEN 0
    WHEN env_destination.team_environment_z - env_source.team_environment_z >= 0.50 THEN 1
    WHEN env_destination.team_environment_z - env_source.team_environment_z <= -0.50 THEN -1
    ELSE 0
  END AS wr_fable_v11_env_score,
  target.target_games,
  target.target_standard_points,
  target.target_standard_ppg,
  target.target_standard_wr_rank,
  target.target_player_id IS NOT NULL AS target_available
FROM enriched
LEFT JOIN environment AS env_source
  ON env_source.season = enriched.season AND env_source.team = enriched.source_team_canonical
LEFT JOIN environment AS env_destination
  ON env_destination.season = enriched.season AND env_destination.team = enriched.destination_team
LEFT JOIN target_ranked AS target
  ON target.season = enriched.season + 1
 AND target.target_player_id = enriched.candidate_internal_player_id;
