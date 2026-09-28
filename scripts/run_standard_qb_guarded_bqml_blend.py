"""Run a read-only Standard QB guarded BQML blend comparison."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.bqml_v2_feature_contract import build_advanced_profile_training_dataset_query


PROJECT = "fantasy-football-498121"
DATASET = "fantasy_football_brain"
LINEAR_MODEL = "ranking_bqml_v2_adv_standard_qb_linear_points_advanced_v0"
LOGISTIC_MODEL = "ranking_bqml_v2_adv_standard_qb_logistic_bust_advanced_v0"
CONTROL_CANDIDATE = "current_pigskin_candidate"
PROJECTION_CANDIDATE = "simple_projection"
RAW_LINEAR_CANDIDATE = "raw_advanced_linear_points"
RAW_LOGISTIC_CANDIDATE = "raw_advanced_logistic_bust"
DEFAULT_SIGNAL_WEIGHT = 0.10


def _season_list(seasons: tuple[int, ...]) -> str:
    if not seasons:
        raise ValueError("At least one target season is required")
    if any(season < 2017 or season > 2025 for season in seasons):
        raise ValueError("Target seasons must stay within the leakage-safe 2017-2025 range")
    return ", ".join(str(season) for season in sorted(set(seasons)))


def _blend_contract(signal_weight: float) -> tuple[float, str, str, str]:
    if signal_weight <= 0 or signal_weight > 0.40:
        raise ValueError("BQML signal weight must be greater than 0 and no more than 0.40")
    control_weight = 1.0 - signal_weight
    control_pct = round(control_weight * 100)
    signal_pct = round(signal_weight * 100)
    suffix = f"{control_pct}_{signal_pct}"
    return (
        control_weight,
        f"guarded_linear_{suffix}",
        f"guarded_logistic_{suffix}",
        f"guarded_consensus_{suffix}",
    )


def build_common_ctes(
    project: str,
    dataset: str,
    seasons: tuple[int, ...],
    signal_weight: float = DEFAULT_SIGNAL_WEIGHT,
) -> str:
    dataset_query = build_advanced_profile_training_dataset_query(
        project,
        dataset,
        scoring_profile_id="standard",
        include_order_by=False,
    )
    season_sql = _season_list(seasons)
    control_weight, guarded_linear, guarded_logistic, guarded_consensus = _blend_contract(signal_weight)
    consensus_weight = signal_weight / 2.0
    return f"""
WITH advanced_dataset AS (
{dataset_query}
),
qb_input AS (
  SELECT
    advanced_dataset.*,
    SAFE_DIVIDE(
      COALESCE(mart.analytical_grade_proxy, 0.0) * 0.55
      + COALESCE(mart.opportunity_score_proxy, 0.0) * 0.15
      + COALESCE(mart.efficiency_score_proxy, 0.0) * 0.10
      + COALESCE(mart.role_stability_score, 0.0) * 0.10
      + COALESCE(mart.profile_points_score, 0.0) * 0.10,
      IF(mart.analytical_grade_proxy IS NULL, 0.0, 0.55)
      + IF(mart.opportunity_score_proxy IS NULL, 0.0, 0.15)
      + IF(mart.efficiency_score_proxy IS NULL, 0.0, 0.10)
      + IF(mart.role_stability_score IS NULL, 0.0, 0.10)
      + IF(mart.profile_points_score IS NULL, 0.0, 0.10)
    ) AS current_pigskin_proxy_score
  FROM advanced_dataset
  JOIN `{project}.{dataset}.ranking_backtest_feature_mart` AS mart
    ON advanced_dataset.target_season = mart.target_season
    AND advanced_dataset.target_week = mart.target_week
    AND advanced_dataset.scoring_profile_id = mart.scoring_profile_id
    AND advanced_dataset.league_type_id = mart.league_type_id
    AND advanced_dataset.roster_format_id = mart.roster_format_id
    AND advanced_dataset.position = mart.position
    AND advanced_dataset.player_id_internal = mart.player_id_internal
  WHERE advanced_dataset.position = 'QB'
    AND advanced_dataset.target_season IN ({season_sql})
    AND mart.source_window_end_season < mart.target_season
),
linear_predictions AS (
  SELECT *
  FROM ML.PREDICT(
    MODEL `{project}.{dataset}.{LINEAR_MODEL}`,
    (SELECT * FROM qb_input)
  )
),
logistic_predictions AS (
  SELECT *
  FROM ML.PREDICT(
    MODEL `{project}.{dataset}.{LOGISTIC_MODEL}`,
    (SELECT * FROM qb_input)
  )
),
combined AS (
  SELECT
    linear.target_season,
    linear.target_week,
    linear.player_id_internal,
    linear.player_name,
    linear.team,
    linear.current_pigskin_proxy_score,
    linear.profile_points_score_3yr,
    linear.predicted_target_fantasy_points AS linear_points_score,
    (
      SELECT prob
      FROM UNNEST(logistic.predicted_bust_label_probs)
      WHERE label = 1
    ) AS bust_probability,
    linear.target_fantasy_points AS actual_points,
    linear.value_over_replacement,
    linear.actual_position_rank,
    linear.adv_passing_epa_per_dropback_3yr,
    linear.adv_passing_cpoe_3yr,
    linear.adv_qb_rushing_baseline_3yr
  FROM linear_predictions AS linear
  JOIN logistic_predictions AS logistic
    USING (
      target_season,
      target_week,
      scoring_profile_id,
      league_type_id,
      roster_format_id,
      position,
      player_id_internal
    )
),
ranked_signals AS (
  SELECT
    combined.*,
    ROW_NUMBER() OVER week_window_current AS control_rank,
    ROW_NUMBER() OVER week_window_projection AS projection_rank,
    ROW_NUMBER() OVER week_window_linear AS linear_rank,
    ROW_NUMBER() OVER week_window_logistic AS logistic_rank
  FROM combined
  WINDOW
    week_window_current AS (
      PARTITION BY target_season, target_week
      ORDER BY current_pigskin_proxy_score DESC, player_id_internal
    ),
    week_window_projection AS (
      PARTITION BY target_season, target_week
      ORDER BY profile_points_score_3yr DESC, player_id_internal
    ),
    week_window_linear AS (
      PARTITION BY target_season, target_week
      ORDER BY linear_points_score DESC, player_id_internal
    ),
    week_window_logistic AS (
      PARTITION BY target_season, target_week
      ORDER BY bust_probability ASC, player_id_internal
    )
),
priorities AS (
  SELECT
    ranked_signals.*,
    {control_weight:.2f} * control_rank + {signal_weight:.2f} * linear_rank AS guarded_linear_priority,
    {control_weight:.2f} * control_rank + {signal_weight:.2f} * logistic_rank AS guarded_logistic_priority,
    {control_weight:.2f} * control_rank + {consensus_weight:.3f} * linear_rank + {consensus_weight:.3f} * logistic_rank AS guarded_consensus_priority
  FROM ranked_signals
),
guarded_ranks AS (
  SELECT
    priorities.*,
    ROW_NUMBER() OVER (
      PARTITION BY target_season, target_week
      ORDER BY guarded_linear_priority, control_rank, player_id_internal
    ) AS guarded_linear_rank,
    ROW_NUMBER() OVER (
      PARTITION BY target_season, target_week
      ORDER BY guarded_logistic_priority, control_rank, player_id_internal
    ) AS guarded_logistic_rank,
    ROW_NUMBER() OVER (
      PARTITION BY target_season, target_week
      ORDER BY guarded_consensus_priority, control_rank, player_id_internal
    ) AS guarded_consensus_rank
  FROM priorities
),
candidate_rows AS (
  SELECT '{CONTROL_CANDIDATE}' AS candidate_id, *, control_rank AS predicted_rank FROM guarded_ranks
  UNION ALL
  SELECT '{PROJECTION_CANDIDATE}', *, projection_rank FROM guarded_ranks
  UNION ALL
  SELECT '{RAW_LINEAR_CANDIDATE}', *, linear_rank FROM guarded_ranks
  UNION ALL
  SELECT '{RAW_LOGISTIC_CANDIDATE}', *, logistic_rank FROM guarded_ranks
  UNION ALL
  SELECT '{guarded_linear}', *, guarded_linear_rank FROM guarded_ranks
  UNION ALL
  SELECT '{guarded_logistic}', *, guarded_logistic_rank FROM guarded_ranks
  UNION ALL
  SELECT '{guarded_consensus}', *, guarded_consensus_rank FROM guarded_ranks
)
""".strip()


def build_summary_sql(
    project: str,
    dataset: str,
    seasons: tuple[int, ...],
    signal_weight: float = DEFAULT_SIGNAL_WEIGHT,
) -> str:
    common = build_common_ctes(project, dataset, seasons, signal_weight)
    return f"""{common},
summary AS (
  SELECT
    candidate_id,
    COUNT(*) AS sample_size,
    SAFE_DIVIDE(
      COUNTIF(predicted_rank <= 12 AND actual_position_rank <= 12),
      NULLIF(COUNTIF(actual_position_rank <= 12), 0)
    ) AS top_12_hit_rate,
    CORR(CAST(predicted_rank AS FLOAT64), CAST(actual_position_rank AS FLOAT64)) AS rank_correlation,
    SAFE_DIVIDE(
      SUM(IF(predicted_rank <= 12, actual_points, 0)),
      NULLIF(SUM(IF(actual_position_rank <= 12, actual_points, 0)), 0)
    ) AS captured_points_rate,
    SAFE_DIVIDE(
      SUM(IF(predicted_rank <= 12, value_over_replacement, 0)),
      NULLIF(SUM(IF(actual_position_rank <= 12, value_over_replacement, 0)), 0)
    ) AS vor_captured_rate,
    SUM(IF(actual_position_rank <= 12, value_over_replacement, 0))
      - SUM(IF(predicted_rank <= 12, value_over_replacement, 0)) AS regret,
    SAFE_DIVIDE(
      COUNTIF(predicted_rank <= 12 AND actual_position_rank > 24),
      NULLIF(COUNTIF(predicted_rank <= 12), 0)
    ) AS bust_rate,
    ROUND(AVG(ABS(predicted_rank - control_rank)), 4) AS mean_absolute_movement,
    MAX(ABS(predicted_rank - control_rank)) AS max_absolute_movement,
    COUNTIF(ABS(predicted_rank - control_rank) > 3) AS movement_over_three_count,
    COUNTIF(
      predicted_rank < control_rank - 3
      AND adv_qb_rushing_baseline_3yr > 50
      AND adv_passing_epa_per_dropback_3yr <= 0
      AND adv_passing_cpoe_3yr <= 0
    ) AS rushing_only_riser_count,
    COUNTIF((control_rank <= 6) != (predicted_rank <= 6)) AS qb6_crossing_count,
    COUNTIF((control_rank <= 12) != (predicted_rank <= 12)) AS qb12_crossing_count,
    COUNTIF((control_rank <= 24) != (predicted_rank <= 24)) AS qb24_crossing_count
  FROM candidate_rows
  GROUP BY candidate_id
),
pairwise AS (
  SELECT
    left_side.candidate_id,
    COUNT(*) AS comparison_count,
    SAFE_DIVIDE(
      COUNTIF(left_side.actual_position_rank < right_side.actual_position_rank),
      COUNT(*)
    ) AS rank_pairwise_win_rate
  FROM candidate_rows AS left_side
  JOIN candidate_rows AS right_side
    ON left_side.candidate_id = right_side.candidate_id
    AND left_side.target_season = right_side.target_season
    AND left_side.target_week = right_side.target_week
    AND left_side.predicted_rank < right_side.predicted_rank
  GROUP BY left_side.candidate_id
)
SELECT summary.*, pairwise.rank_pairwise_win_rate, pairwise.comparison_count
FROM summary
JOIN pairwise USING (candidate_id)
ORDER BY candidate_id
"""


def build_movement_sql(
    project: str,
    dataset: str,
    seasons: tuple[int, ...],
    signal_weight: float = DEFAULT_SIGNAL_WEIGHT,
) -> str:
    common = build_common_ctes(project, dataset, seasons, signal_weight)
    _, guarded_linear, guarded_logistic, guarded_consensus = _blend_contract(signal_weight)
    return f"""{common}
SELECT
  candidate_id,
  target_season,
  target_week,
  player_name,
  team,
  control_rank,
  predicted_rank,
  control_rank - predicted_rank AS upward_movement,
  actual_position_rank,
  ROUND(adv_passing_epa_per_dropback_3yr, 4) AS passing_epa_per_dropback,
  ROUND(adv_passing_cpoe_3yr, 4) AS passing_cpoe,
  ROUND(adv_qb_rushing_baseline_3yr, 2) AS qb_rushing_baseline,
  (
    predicted_rank < control_rank - 3
    AND adv_qb_rushing_baseline_3yr > 50
    AND adv_passing_epa_per_dropback_3yr <= 0
    AND adv_passing_cpoe_3yr <= 0
  ) AS rushing_only_riser
FROM candidate_rows
WHERE candidate_id IN (
    '{guarded_linear}',
    '{guarded_logistic}',
    '{guarded_consensus}'
  )
  AND (
    ABS(predicted_rank - control_rank) > 3
    OR (control_rank <= 6) != (predicted_rank <= 6)
    OR (control_rank <= 12) != (predicted_rank <= 12)
    OR (control_rank <= 24) != (predicted_rank <= 24)
  )
ORDER BY candidate_id, target_season, target_week, ABS(predicted_rank - control_rank) DESC, player_name
"""


def run(args: argparse.Namespace) -> dict:
    client = bigquery.Client(project=args.project)
    seasons = tuple(args.seasons)
    summary_sql = build_summary_sql(args.project, args.dataset, seasons, args.signal_weight)
    movement_sql = build_movement_sql(args.project, args.dataset, seasons, args.signal_weight)
    dry_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    summary_dry = client.query(summary_sql, job_config=dry_config)
    movement_dry = client.query(movement_sql, job_config=dry_config)
    if args.dry_run:
        return {
            "dry_run": True,
            "seasons": seasons,
            "signal_weight": args.signal_weight,
            "estimated_bytes_processed": int(summary_dry.total_bytes_processed or 0)
            + int(movement_dry.total_bytes_processed or 0),
            "writes": False,
        }
    summary_job = client.query(summary_sql)
    movement_job = client.query(movement_sql)
    return {
        "dry_run": False,
        "seasons": seasons,
        "signal_weight": args.signal_weight,
        "summary_job_id": summary_job.job_id,
        "movement_job_id": movement_job.job_id,
        "summaries": [dict(row) for row in summary_job.result()],
        "movements": [dict(row) for row in movement_job.result()],
        "writes": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=PROJECT)
    parser.add_argument("--dataset", default=DATASET)
    parser.add_argument("--seasons", type=int, nargs="+", default=[2024, 2025])
    parser.add_argument("--signal-weight", type=float, default=DEFAULT_SIGNAL_WEIGHT)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps(run(args), default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
