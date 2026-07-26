"""Run the read-only QB Fable v1 Standard scoring backtest."""

from __future__ import annotations

import argparse
import json

from google.cloud import bigquery


PROJECT = "fantasy-football-498121"
DATASET = "fantasy_football_brain"
INPUT_SEASONS = (2022, 2023, 2024)


def build_qb_fable_v1_sql(project: str, dataset: str) -> str:
    return f"""
WITH pbp AS (
  SELECT
    season,
    week,
    game_id,
    posteam,
    passer_player_id,
    rusher_player_id,
    JSON_VALUE(raw_payload_json, '$.passer_player_name') AS passer_player_name,
    JSON_VALUE(raw_payload_json, '$.rusher_player_name') AS rusher_player_name,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.qb_dropback') AS FLOAT64) AS qb_dropback,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.qb_epa') AS FLOAT64) AS qb_epa,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.cpoe') AS FLOAT64) AS cpoe,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.sack') AS FLOAT64) AS sack,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.qb_kneel') AS FLOAT64) AS qb_kneel,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.pass_attempt') AS FLOAT64) AS pass_attempt,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.pass_touchdown') AS FLOAT64) AS pass_touchdown,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.rush_attempt') AS FLOAT64) AS rush_attempt,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.rush_touchdown') AS FLOAT64) AS rush_touchdown,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.rushing_yards') AS FLOAT64) AS rushing_yards,
    yardline_100,
    SAFE_CAST(JSON_VALUE(raw_payload_json, '$.wp') AS FLOAT64) AS wp
  FROM `{project}.{dataset}.raw_nflverse_pbp`
  WHERE season IN (2022, 2023, 2024)
),
passing AS (
  SELECT
    season,
    passer_player_id AS player_id_internal,
    ARRAY_AGG(passer_player_name IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS player_name,
    ARRAY_AGG(posteam IGNORE NULLS ORDER BY week DESC LIMIT 1)[SAFE_OFFSET(0)] AS team,
    COUNT(DISTINCT IF(COALESCE(qb_dropback, 0) = 1, game_id, NULL)) AS games,
    COUNTIF(COALESCE(qb_dropback, 0) = 1) AS dropbacks,
    COUNTIF(COALESCE(qb_dropback, 0) = 1 AND wp BETWEEN 0.05 AND 0.95) AS non_garbage_dropbacks,
    COUNTIF(COALESCE(pass_attempt, 0) = 1) AS pass_attempts,
    COUNTIF(COALESCE(pass_attempt, 0) = 1 AND yardline_100 <= 20) AS red_zone_pass_attempts,
    SUM(IF(COALESCE(pass_attempt, 0) = 1, COALESCE(pass_touchdown, 0), 0)) AS pass_touchdowns,
    SUM(IF(COALESCE(qb_dropback, 0) = 1, COALESCE(sack, 0), 0)) AS sacks,
    SAFE_DIVIDE(
      SUM(IF(COALESCE(qb_dropback, 0) = 1, COALESCE(qb_epa, 0), 0)),
      COUNTIF(COALESCE(qb_dropback, 0) = 1)
    ) AS epa_per_dropback,
    AVG(IF(COALESCE(pass_attempt, 0) = 1, cpoe, NULL)) AS passing_cpoe
  FROM pbp
  WHERE passer_player_id IS NOT NULL
  GROUP BY season, passer_player_id
),
rushing AS (
  SELECT
    season,
    rusher_player_id AS player_id_internal,
    COUNTIF(COALESCE(rush_attempt, 0) = 1 AND COALESCE(qb_kneel, 0) = 0) AS rush_attempts,
    SUM(IF(COALESCE(rush_attempt, 0) = 1 AND COALESCE(qb_kneel, 0) = 0, COALESCE(rushing_yards, 0), 0)) AS rush_yards,
    COUNTIF(COALESCE(rush_attempt, 0) = 1 AND COALESCE(qb_kneel, 0) = 0 AND yardline_100 <= 20) AS red_zone_rush_attempts,
    COUNTIF(COALESCE(rush_attempt, 0) = 1 AND COALESCE(qb_kneel, 0) = 0 AND yardline_100 <= 10) AS goal_to_go_rush_attempts,
    SUM(IF(COALESCE(rush_attempt, 0) = 1 AND COALESCE(qb_kneel, 0) = 0, COALESCE(rush_touchdown, 0), 0)) AS rush_touchdowns
  FROM pbp
  WHERE rusher_player_id IS NOT NULL
  GROUP BY season, rusher_player_id
),
roster AS (
  SELECT
    season,
    gsis_id AS player_id_internal,
    ARRAY_AGG(display_name IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS roster_player_name,
    ARRAY_AGG(SAFE.PARSE_DATE('%Y-%m-%d', birth_date) IGNORE NULLS LIMIT 1)[SAFE_OFFSET(0)] AS birth_date
  FROM `{project}.{dataset}.player_rosters`
  WHERE season IN (2022, 2023, 2024)
    AND position = 'QB'
    AND gsis_id IS NOT NULL
  GROUP BY season, gsis_id
),
input_points AS (
  SELECT
    season,
    source_player_key AS player_id_internal,
    SUM(rushing_points) AS rushing_points,
    SUM(total_fantasy_points) AS total_fantasy_points,
    AVG(total_fantasy_points) AS input_standard_ppg
  FROM `{project}.{dataset}.analytics_player_fantasy_points_by_profile`
  WHERE season IN (2022, 2023, 2024)
    AND scoring_profile_id = 'standard'
    AND COALESCE(league_type_id, 'redraft') = 'redraft'
    AND COALESCE(roster_format_id, 'one_qb') = 'one_qb'
    AND position = 'QB'
  GROUP BY season, source_player_key
),
target_points AS (
  SELECT
    season,
    source_player_key AS player_id_internal,
    COUNT(DISTINCT week) AS target_games,
    AVG(total_fantasy_points) AS target_standard_ppg
  FROM `{project}.{dataset}.analytics_player_fantasy_points_by_profile`
  WHERE season IN (2023, 2024, 2025)
    AND scoring_profile_id = 'standard'
    AND COALESCE(league_type_id, 'redraft') = 'redraft'
    AND COALESCE(roster_format_id, 'one_qb') = 'one_qb'
    AND position = 'QB'
  GROUP BY season, source_player_key
),
inputs AS (
  SELECT
    passing.season AS input_season,
    passing.season + 1 AS target_season,
    passing.player_id_internal,
    COALESCE(roster.roster_player_name, passing.player_name) AS player_name,
    passing.team,
    passing.games,
    passing.dropbacks,
    SAFE_DIVIDE(COALESCE(rushing.rush_attempts, 0), passing.games) AS rush_attempts_per_game,
    SAFE_DIVIDE(passing.non_garbage_dropbacks, passing.games) AS non_garbage_dropbacks_per_game,
    SAFE_DIVIDE(COALESCE(rushing.red_zone_rush_attempts, 0), passing.games) AS red_zone_rush_attempts_per_game,
    passing.epa_per_dropback,
    passing.passing_cpoe,
    -SAFE_DIVIDE(passing.sacks, passing.dropbacks) AS inverse_sack_rate,
    SAFE_DIVIDE(COALESCE(rushing.rush_yards, 0), NULLIF(rushing.rush_attempts, 0)) AS rush_yards_per_attempt,
    0.7 * (
      0.045 * SAFE_DIVIDE(passing.pass_attempts, passing.games)
      + 0.09 * SAFE_DIVIDE(passing.red_zone_pass_attempts, passing.games)
    ) + 0.3 * SAFE_DIVIDE(passing.pass_touchdowns, passing.games) AS blended_pass_touchdowns_per_game,
    0.7 * (0.20 * SAFE_DIVIDE(COALESCE(rushing.goal_to_go_rush_attempts, 0), passing.games))
      + 0.3 * SAFE_DIVIDE(COALESCE(rushing.rush_touchdowns, 0), passing.games) AS blended_rush_touchdowns_per_game,
    SAFE_DIVIDE(passing.games, 17.0) AS games_active_rate_proxy,
    DATE_DIFF(DATE(passing.season, 9, 1), roster.birth_date, YEAR) AS age,
    SAFE_DIVIDE(input_points.rushing_points, NULLIF(input_points.total_fantasy_points, 0)) AS rush_fantasy_share,
    input_points.input_standard_ppg,
    target_points.target_games,
    target_points.target_standard_ppg
  FROM passing
  LEFT JOIN rushing USING (season, player_id_internal)
  LEFT JOIN roster USING (season, player_id_internal)
  LEFT JOIN input_points USING (season, player_id_internal)
  JOIN target_points
    ON target_points.season = passing.season + 1
    AND target_points.player_id_internal = passing.player_id_internal
  WHERE passing.dropbacks >= 200
    AND target_points.target_games >= 6
),
prepared AS (
  SELECT
    inputs.*,
    -GREATEST(0, age - 28) * COALESCE(rush_fantasy_share, 0) AS dual_threat_age_penalty,
    -GREATEST(0, age - 33) AS general_age_penalty
  FROM inputs
),
standardized AS (
  SELECT
    prepared.*,
    SAFE_DIVIDE(rush_attempts_per_game - AVG(rush_attempts_per_game) OVER season_window, STDDEV_POP(rush_attempts_per_game) OVER season_window) AS z_rush_attempts_per_game,
    SAFE_DIVIDE(non_garbage_dropbacks_per_game - AVG(non_garbage_dropbacks_per_game) OVER season_window, STDDEV_POP(non_garbage_dropbacks_per_game) OVER season_window) AS z_non_garbage_dropbacks_per_game,
    SAFE_DIVIDE(red_zone_rush_attempts_per_game - AVG(red_zone_rush_attempts_per_game) OVER season_window, STDDEV_POP(red_zone_rush_attempts_per_game) OVER season_window) AS z_red_zone_rush_attempts_per_game,
    SAFE_DIVIDE(epa_per_dropback - AVG(epa_per_dropback) OVER season_window, STDDEV_POP(epa_per_dropback) OVER season_window) AS z_epa_per_dropback,
    SAFE_DIVIDE(passing_cpoe - AVG(passing_cpoe) OVER season_window, STDDEV_POP(passing_cpoe) OVER season_window) AS z_passing_cpoe,
    SAFE_DIVIDE(inverse_sack_rate - AVG(inverse_sack_rate) OVER season_window, STDDEV_POP(inverse_sack_rate) OVER season_window) AS z_inverse_sack_rate,
    SAFE_DIVIDE(rush_yards_per_attempt - AVG(rush_yards_per_attempt) OVER season_window, STDDEV_POP(rush_yards_per_attempt) OVER season_window) AS z_rush_yards_per_attempt,
    SAFE_DIVIDE(blended_pass_touchdowns_per_game - AVG(blended_pass_touchdowns_per_game) OVER season_window, STDDEV_POP(blended_pass_touchdowns_per_game) OVER season_window) AS z_blended_pass_touchdowns_per_game,
    SAFE_DIVIDE(blended_rush_touchdowns_per_game - AVG(blended_rush_touchdowns_per_game) OVER season_window, STDDEV_POP(blended_rush_touchdowns_per_game) OVER season_window) AS z_blended_rush_touchdowns_per_game,
    SAFE_DIVIDE(games_active_rate_proxy - AVG(games_active_rate_proxy) OVER season_window, STDDEV_POP(games_active_rate_proxy) OVER season_window) AS z_games_active_rate_proxy,
    SAFE_DIVIDE(dual_threat_age_penalty - AVG(dual_threat_age_penalty) OVER season_window, STDDEV_POP(dual_threat_age_penalty) OVER season_window) AS z_dual_threat_age_penalty,
    SAFE_DIVIDE(general_age_penalty - AVG(general_age_penalty) OVER season_window, STDDEV_POP(general_age_penalty) OVER season_window) AS z_general_age_penalty
  FROM prepared
  WINDOW season_window AS (PARTITION BY input_season)
),
scored AS (
  SELECT
    standardized.*,
    0.20 * COALESCE(z_rush_attempts_per_game, 0)
    + 0.12 * COALESCE(z_non_garbage_dropbacks_per_game, 0)
    + 0.08 * COALESCE(z_red_zone_rush_attempts_per_game, 0)
    + 0.13 * COALESCE(z_epa_per_dropback, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.09 * COALESCE(z_passing_cpoe, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.07 * COALESCE(z_inverse_sack_rate, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.06 * COALESCE(z_rush_yards_per_attempt, 0) * SAFE_DIVIDE(COALESCE(rush_attempts_per_game, 0) * games, COALESCE(rush_attempts_per_game, 0) * games + 40)
    + 0.10 * COALESCE(z_blended_pass_touchdowns_per_game, 0)
    + 0.05 * COALESCE(z_blended_rush_touchdowns_per_game, 0)
    + 0.04 * COALESCE(z_games_active_rate_proxy, 0)
    + 0.03 * COALESCE(z_dual_threat_age_penalty, 0)
    + 0.03 * COALESCE(z_general_age_penalty, 0) AS qb_fable_v1_score,
    0.15 * COALESCE(z_rush_attempts_per_game, 0)
    + 0.16 * COALESCE(z_non_garbage_dropbacks_per_game, 0)
    + 0.05 * COALESCE(z_red_zone_rush_attempts_per_game, 0)
    + 0.16 * COALESCE(z_epa_per_dropback, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.11 * COALESCE(z_passing_cpoe, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.08 * COALESCE(z_inverse_sack_rate, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.04 * COALESCE(z_rush_yards_per_attempt, 0) * SAFE_DIVIDE(COALESCE(rush_attempts_per_game, 0) * games, COALESCE(rush_attempts_per_game, 0) * games + 40)
    + 0.11 * COALESCE(z_blended_pass_touchdowns_per_game, 0)
    + 0.04 * COALESCE(z_blended_rush_touchdowns_per_game, 0)
    + 0.04 * COALESCE(z_games_active_rate_proxy, 0)
    + 0.03 * COALESCE(z_dual_threat_age_penalty, 0)
    + 0.03 * COALESCE(z_general_age_penalty, 0) AS qb_fable_balanced_score,
    0.12 * COALESCE(z_rush_attempts_per_game, 0)
    + 0.18 * COALESCE(z_non_garbage_dropbacks_per_game, 0)
    + 0.04 * COALESCE(z_red_zone_rush_attempts_per_game, 0)
    + 0.18 * COALESCE(z_epa_per_dropback, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.12 * COALESCE(z_passing_cpoe, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.09 * COALESCE(z_inverse_sack_rate, 0) * SAFE_DIVIDE(dropbacks, dropbacks + 200)
    + 0.03 * COALESCE(z_rush_yards_per_attempt, 0) * SAFE_DIVIDE(COALESCE(rush_attempts_per_game, 0) * games, COALESCE(rush_attempts_per_game, 0) * games + 40)
    + 0.12 * COALESCE(z_blended_pass_touchdowns_per_game, 0)
    + 0.02 * COALESCE(z_blended_rush_touchdowns_per_game, 0)
    + 0.04 * COALESCE(z_games_active_rate_proxy, 0)
    + 0.03 * COALESCE(z_dual_threat_age_penalty, 0)
    + 0.03 * COALESCE(z_general_age_penalty, 0) AS qb_fable_passing_score
  FROM standardized
),
candidate_scores AS (
  SELECT input_season, target_season, player_id_internal, target_standard_ppg,
    'qb_fable_v1' AS candidate_id, qb_fable_v1_score AS candidate_score
  FROM scored
  UNION ALL
  SELECT input_season, target_season, player_id_internal, target_standard_ppg,
    'qb_fable_balanced' AS candidate_id, qb_fable_balanced_score AS candidate_score
  FROM scored
  UNION ALL
  SELECT input_season, target_season, player_id_internal, target_standard_ppg,
    'qb_fable_passing' AS candidate_id, qb_fable_passing_score AS candidate_score
  FROM scored
  UNION ALL
  SELECT input_season, target_season, player_id_internal, target_standard_ppg,
    'prior_year_standard_ppg' AS candidate_id, input_standard_ppg AS candidate_score
  FROM scored
),
ranked AS (
  SELECT
    candidate_scores.*,
    ROW_NUMBER() OVER (PARTITION BY input_season, candidate_id ORDER BY candidate_score DESC, player_id_internal) AS predicted_rank,
    ROW_NUMBER() OVER (PARTITION BY input_season, candidate_id ORDER BY target_standard_ppg DESC, player_id_internal) AS actual_rank
  FROM candidate_scores
),
summary AS (
  SELECT
    input_season,
    target_season,
    candidate_id,
    COUNT(*) AS qualified_qbs,
    CORR(CAST(predicted_rank AS FLOAT64), CAST(actual_rank AS FLOAT64)) AS spearman_rank_correlation,
    SAFE_DIVIDE(COUNTIF(predicted_rank <= 5 AND actual_rank <= 5), 5) AS top_5_precision,
    SAFE_DIVIDE(COUNTIF(predicted_rank <= 12 AND actual_rank <= 12), 12) AS top_12_precision,
    SAFE_DIVIDE(
      SUM(IF(predicted_rank <= 12, target_standard_ppg, 0)),
      SUM(IF(actual_rank <= 12, target_standard_ppg, 0))
    ) AS top_12_points_captured_rate,
    AVG(ABS(predicted_rank - actual_rank)) AS mean_absolute_rank_error
  FROM ranked
  GROUP BY input_season, target_season, candidate_id
)
SELECT summary.*
FROM summary
ORDER BY input_season, candidate_id
"""


def run(args: argparse.Namespace) -> dict:
    client = bigquery.Client(project=args.project)
    sql = build_qb_fable_v1_sql(args.project, args.dataset)
    dry_job = client.query(sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
    if args.dry_run:
        return {
            "dry_run": True,
            "estimated_bytes_processed": int(dry_job.total_bytes_processed or 0),
            "writes": False,
            "qualification": "200+ input-season dropbacks; target season has 6+ scored games",
            "starts_limitation": "verified starts unavailable; games-active rate is an availability proxy",
        }
    job = client.query(sql)
    return {
        "dry_run": False,
        "query_job_id": job.job_id,
        "results": [dict(row) for row in job.result()],
        "writes": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=PROJECT)
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run(args), default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
