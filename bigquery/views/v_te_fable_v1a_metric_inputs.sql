-- Qualified, leakage-safe TE Fable v1.0a metrics before within-season z-scoring.
CREATE OR REPLACE VIEW `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_metric_inputs` AS
WITH derived AS (
  SELECT
    splits.*,
    SAFE_DIVIDE(splits.routes_run, splits.games_played) AS routes_per_game,
    splits.red_zone_routes_run * splits.red_zone_targets_per_route_run AS red_zone_targets,
    SAFE_DIVIDE(splits.red_zone_routes_run * splits.red_zone_targets_per_route_run, splits.games_played) AS red_zone_targets_per_game,
    CASE WHEN splits.targets > 0 THEN SAFE_DIVIDE(splits.total_epa, splits.targets) END AS epa_per_target,
    SAFE_DIVIDE(splits.receiving_touchdowns, splits.games_played) AS actual_td_per_game,
    IF(splits.age BETWEEN 24 AND 27, 1, 0) AS breakout_window_bonus,
    CASE WHEN splits.age IS NULL THEN NULL ELSE -GREATEST(0, splits.age - 30) END AS decline_penalty,
    SAFE_DIVIDE(splits.games_played, 17) AS games_played_rate,
    SAFE_DIVIDE(splits.targets, splits.targets + 70) AS target_efficiency_shrink,
    SAFE_DIVIDE(splits.routes_run, splits.routes_run + 70) AS route_efficiency_shrink,
    SAFE_DIVIDE(splits.vs_man_routes_run, splits.vs_man_routes_run + 70) AS vs_man_efficiency_shrink
  FROM `{{PROJECT_ID}}.{{DATASET_ID}}.v_te_fable_v1a_situational_splits` AS splits
  WHERE identity_status IN ('VERIFIED', 'EXACT_SLUG_MATCH', 'NAME_TEAM_SEASON_MATCH')
    AND NOT duplicate_identity_collision
),
qualified AS (
  SELECT * FROM derived
  WHERE games_played >= 4 AND routes_run >= 100
)
SELECT
  qualified.*,
  0.14 AS fixed_rz_td_conversion,
  qualified.red_zone_targets_per_game * 0.14 AS expected_td_per_game,
  0.70 * (qualified.red_zone_targets_per_game * 0.14)
    + 0.30 * qualified.actual_td_per_game AS blended_td_per_game
FROM qualified;
