-- TE Fable v1.0a prior-season scores and next-season Standard outcomes. No rankings are written.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_backtest_prep` AS
WITH scored AS (
  SELECT * FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_scored_seasons`
  WHERE season BETWEEN 2022 AND 2024
),
standard_totals AS (
  SELECT
    season,
    source_player_key AS player_id,
    COUNT(*) AS games,
    SUM(total_fantasy_points) AS standard_points,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS standard_ppg
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard'
    AND position = 'TE'
    AND season BETWEEN 2022 AND 2025
    AND week BETWEEN 1 AND 18
  GROUP BY season, player_id
),
current_pigskin AS (
  SELECT
    target_season,
    player_id_internal,
    ANY_VALUE(
      0.55 * analytical_grade_proxy
      + 0.15 * opportunity_score_proxy
      + 0.10 * efficiency_score_proxy
      + 0.10 * role_stability_score
      + 0.10 * profile_points_score
    ) AS current_pigskin_candidate_score_v1
  FROM `{{PROJECT_ID}}.{{BRAIN_DATASET_ID}}.ranking_backtest_feature_mart`
  WHERE scoring_profile_id = 'standard'
    AND league_type_id = 'redraft'
    AND roster_format_id = 'one_qb'
    AND position = 'TE'
    AND target_season BETWEEN 2023 AND 2025
  GROUP BY target_season, player_id_internal
),
target_ranked AS (
  SELECT
    *,
    DENSE_RANK() OVER (PARTITION BY season ORDER BY standard_ppg DESC, standard_points DESC) AS target_standard_te_rank
  FROM standard_totals
  WHERE games >= 4
)
SELECT
  scored.*,
  source.standard_ppg AS source_standard_ppg,
  current_pigskin.current_pigskin_candidate_score_v1,
  scored.season + 1 AS target_season,
  target.games AS target_games,
  target.standard_points AS target_standard_points,
  target.standard_ppg AS target_standard_ppg,
  target.target_standard_te_rank,
  target.player_id IS NOT NULL AS target_available
FROM scored
LEFT JOIN standard_totals AS source
  ON source.season = scored.season
 AND source.player_id = scored.candidate_internal_player_id
LEFT JOIN current_pigskin
  ON current_pigskin.target_season = scored.season + 1
 AND current_pigskin.player_id_internal = scored.candidate_internal_player_id
LEFT JOIN target_ranked AS target
  ON target.season = scored.season + 1
 AND target.player_id = scored.candidate_internal_player_id;
