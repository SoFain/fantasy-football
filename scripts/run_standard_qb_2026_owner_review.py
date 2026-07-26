"""Build a read-only 2026 Standard QB guarded-formula owner-review board."""

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


def build_owner_review_sql(project: str, dataset: str) -> str:
    advanced_query = build_advanced_profile_training_dataset_query(
        project,
        dataset,
        scoring_profile_id="standard",
        include_order_by=False,
    )
    return f"""WITH advanced_dataset AS (
{advanced_query}
),
latest_features AS (
  SELECT *
  FROM advanced_dataset
  WHERE position = 'QB'
    AND target_season <= 2025
    AND source_window_end_season < 2026
  QUALIFY ROW_NUMBER() OVER (
    PARTITION BY player_id_internal
    ORDER BY target_season DESC, target_week DESC
  ) = 1
),
linear_predictions AS (
  SELECT *
  FROM ML.PREDICT(
    MODEL `{project}.{dataset}.{LINEAR_MODEL}`,
    (SELECT * FROM latest_features)
  )
),
logistic_predictions AS (
  SELECT *
  FROM ML.PREDICT(
    MODEL `{project}.{dataset}.{LOGISTIC_MODEL}`,
    (SELECT * FROM latest_features)
  )
),
feature_signals AS (
  SELECT
    linear.player_id_internal,
    linear.target_season AS feature_target_season,
    linear.target_week AS feature_target_week,
    linear.source_window_start_season,
    linear.source_window_end_season,
    linear.profile_points_score_3yr,
    linear.predicted_target_fantasy_points AS linear_points_score,
    (
      SELECT prob
      FROM UNNEST(logistic.predicted_bust_label_probs)
      WHERE label = 1
    ) AS bust_probability,
    linear.adv_passing_epa_per_dropback_3yr AS passing_epa_per_dropback,
    linear.adv_passing_cpoe_3yr AS passing_cpoe,
    linear.adv_qb_rushing_baseline_3yr AS qb_rushing_baseline
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
live_board AS (
  SELECT
    rankings.rank AS live_rank,
    COALESCE(rankings.candidate_rank, rankings.rank) AS anchor_rank,
    rankings.candidate_rank,
    rankings.player_id,
    rankings.player_name,
    rankings.current_team,
    rankings.ranking_version,
    rankings.model_run_id,
    rankings.ranking_score AS live_ranking_score,
    rankings.candidate_ranking_score,
    rankings.sleeper_player_id,
    rankings.sleeper_injury_status,
    rankings.sleeper_depth_chart_order,
    rankings.risk_flags,
    players.years_exp,
    players.status AS sleeper_status
  FROM `{project}.{dataset}.analytics_pigskin_rankings` AS rankings
  LEFT JOIN `{project}.{dataset}.sleeper_players_current` AS players
    USING (sleeper_player_id)
  WHERE rankings.is_active = TRUE
    AND rankings.scoring_profile_id = 'standard'
    AND rankings.league_type_id = 'redraft'
    AND rankings.roster_format_id = 'one_qb'
    AND rankings.position = 'QB'
),
matched_signals AS (
  SELECT live_board.*, feature_signals.* EXCEPT (player_id_internal)
  FROM live_board
  JOIN feature_signals
    ON live_board.player_id = feature_signals.player_id_internal
),
matched_ranks AS (
  SELECT
    matched_signals.*,
    ROW_NUMBER() OVER (ORDER BY linear_points_score DESC, player_id) AS linear_model_rank,
    ROW_NUMBER() OVER (ORDER BY bust_probability ASC, player_id) AS logistic_model_rank,
    COUNT(*) OVER () AS matched_player_count
  FROM matched_signals
),
scaled_signals AS (
  SELECT
    matched_ranks.*,
    1 + SAFE_DIVIDE(
      (linear_model_rank - 1) * (SELECT COUNT(*) - 1 FROM live_board),
      NULLIF(matched_player_count - 1, 0)
    ) AS linear_scaled_rank,
    1 + SAFE_DIVIDE(
      (logistic_model_rank - 1) * (SELECT COUNT(*) - 1 FROM live_board),
      NULLIF(matched_player_count - 1, 0)
    ) AS logistic_scaled_rank
  FROM matched_ranks
),
review_inputs AS (
  SELECT
    live_board.*,
    scaled_signals.feature_target_week,
    scaled_signals.feature_target_season,
    scaled_signals.source_window_start_season,
    scaled_signals.source_window_end_season,
    scaled_signals.profile_points_score_3yr,
    scaled_signals.linear_points_score,
    scaled_signals.bust_probability,
    scaled_signals.passing_epa_per_dropback,
    scaled_signals.passing_cpoe,
    scaled_signals.qb_rushing_baseline,
    scaled_signals.linear_model_rank,
    scaled_signals.logistic_model_rank,
    scaled_signals.linear_scaled_rank,
    scaled_signals.logistic_scaled_rank,
    scaled_signals.player_id IS NOT NULL AS has_bqml_features,
    CASE
      WHEN COALESCE(live_board.years_exp, 0) = 0 THEN 'rookie_deterministic_lane'
      WHEN scaled_signals.player_id IS NULL THEN 'missing_history_deterministic_lane'
      ELSE 'returning_player_bqml_lane'
    END AS review_lane,
    CASE
      WHEN scaled_signals.player_id IS NULL THEN live_board.anchor_rank
      ELSE 0.75 * live_board.anchor_rank
        + 0.125 * scaled_signals.linear_scaled_rank
        + 0.125 * scaled_signals.logistic_scaled_rank
    END AS consensus_75_25_priority,
    CASE
      WHEN scaled_signals.player_id IS NULL THEN live_board.anchor_rank
      ELSE 0.70 * live_board.anchor_rank
        + 0.30 * scaled_signals.linear_scaled_rank
    END AS linear_70_30_priority
  FROM live_board
  LEFT JOIN scaled_signals USING (player_id)
),
ranked AS (
  SELECT
    review_inputs.*,
    ROW_NUMBER() OVER (
      ORDER BY consensus_75_25_priority, anchor_rank, player_id
    ) AS consensus_75_25_rank,
    ROW_NUMBER() OVER (
      ORDER BY linear_70_30_priority, anchor_rank, player_id
    ) AS linear_70_30_rank
  FROM review_inputs
)
SELECT
  consensus_75_25_rank AS review_order,
  player_id,
  player_name,
  current_team,
  live_rank,
  anchor_rank,
  consensus_75_25_rank,
  linear_70_30_rank,
  anchor_rank - consensus_75_25_rank AS consensus_movement_from_anchor,
  anchor_rank - linear_70_30_rank AS linear_movement_from_anchor,
  live_rank - consensus_75_25_rank AS consensus_movement_from_live,
  live_rank - linear_70_30_rank AS linear_movement_from_live,
  ROUND(consensus_75_25_priority, 3) AS consensus_priority,
  ROUND(linear_70_30_priority, 3) AS linear_priority,
  linear_model_rank,
  logistic_model_rank,
  ROUND(linear_scaled_rank, 2) AS linear_scaled_rank,
  ROUND(logistic_scaled_rank, 2) AS logistic_scaled_rank,
  ROUND(linear_points_score, 3) AS linear_points_score,
  ROUND(bust_probability, 4) AS bust_probability,
  ROUND(profile_points_score_3yr, 3) AS profile_points_score_3yr,
  ROUND(passing_epa_per_dropback, 4) AS passing_epa_per_dropback,
  ROUND(passing_cpoe, 3) AS passing_cpoe,
  ROUND(qb_rushing_baseline, 2) AS qb_rushing_baseline,
  has_bqml_features,
  review_lane,
  years_exp,
  sleeper_status,
  sleeper_injury_status,
  sleeper_depth_chart_order,
  feature_target_week,
  feature_target_season,
  source_window_start_season,
  source_window_end_season,
  ranking_version,
  model_run_id,
  risk_flags,
  ABS(anchor_rank - consensus_75_25_rank) >= 3 AS consensus_movement_review,
  ABS(anchor_rank - linear_70_30_rank) >= 3 AS linear_movement_review,
  (
    consensus_75_25_rank < anchor_rank - 2
    AND qb_rushing_baseline > 50
    AND passing_epa_per_dropback <= 0
    AND passing_cpoe <= 0
  ) AS consensus_rushing_only_riser,
  (
    linear_70_30_rank < anchor_rank - 2
    AND qb_rushing_baseline > 50
    AND passing_epa_per_dropback <= 0
    AND passing_cpoe <= 0
  ) AS linear_rushing_only_riser,
  (anchor_rank <= 6) != (consensus_75_25_rank <= 6) AS consensus_qb6_crossing,
  (anchor_rank <= 12) != (consensus_75_25_rank <= 12) AS consensus_qb12_crossing,
  (anchor_rank <= 24) != (consensus_75_25_rank <= 24) AS consensus_qb24_crossing,
  (anchor_rank <= 6) != (linear_70_30_rank <= 6) AS linear_qb6_crossing,
  (anchor_rank <= 12) != (linear_70_30_rank <= 12) AS linear_qb12_crossing,
  (anchor_rank <= 24) != (linear_70_30_rank <= 24) AS linear_qb24_crossing
FROM ranked
ORDER BY review_order, player_name
"""


def _add_flow_edge(graph: list[list[dict]], start: int, end: int, capacity: int, cost: int) -> None:
    graph[start].append({"to": end, "rev": len(graph[end]), "cap": capacity, "cost": cost})
    graph[end].append({"to": start, "rev": len(graph[start]) - 1, "cap": 0, "cost": -cost})


def assign_guarded_consensus_ranks(board: list[dict]) -> list[dict]:
    """Assign unique ranks under exact movement, missingness, and weak-passing constraints."""

    player_count = len(board)
    source = 0
    first_player = 1
    first_slot = first_player + player_count
    sink = first_slot + player_count
    graph: list[list[dict]] = [[] for _ in range(sink + 1)]
    second_string_count = sum(record.get("sleeper_depth_chart_order") == 2 for record in board)
    third_string_count = sum((record.get("sleeper_depth_chart_order") or 0) >= 3 for record in board)
    starter_slot_count = player_count - second_string_count - third_string_count
    second_string_last_rank = player_count - third_string_count

    for index, record in enumerate(board):
        player_node = first_player + index
        _add_flow_edge(graph, source, player_node, 1, 0)
        anchor_rank = int(record["anchor_rank"])
        desired_rank = int(record["consensus_75_25_rank"])
        depth_order = record.get("sleeper_depth_chart_order")
        if depth_order is not None and depth_order >= 3:
            role_minimum, role_maximum = second_string_last_rank + 1, player_count
        elif depth_order == 2:
            role_minimum, role_maximum = starter_slot_count + 1, second_string_last_rank
        else:
            role_minimum, role_maximum = 1, starter_slot_count
        anchor_in_role_bucket = role_minimum <= anchor_rank <= role_maximum
        if not record.get("has_bqml_features") and anchor_in_role_bucket:
            allowed_ranks = (anchor_rank,)
        else:
            if anchor_in_role_bucket:
                minimum_rank = max(role_minimum, anchor_rank - 4)
                maximum_rank = min(role_maximum, anchor_rank + 4)
            else:
                minimum_rank = role_minimum
                maximum_rank = role_maximum
            weak_passing = (
                record.get("passing_epa_per_dropback") is not None
                and record.get("passing_cpoe") is not None
                and record["passing_epa_per_dropback"] <= 0
                and record["passing_cpoe"] <= 0
            )
            if weak_passing:
                minimum_rank = max(minimum_rank, anchor_rank - 1)
                for cutline in (6, 12, 24):
                    if anchor_rank > cutline:
                        minimum_rank = max(minimum_rank, cutline + 1)
            allowed_ranks = range(minimum_rank, maximum_rank + 1)
        for slot_rank in allowed_ranks:
            slot_node = first_slot + slot_rank - 1
            cost = (
                abs(slot_rank - desired_rank) * 10_000
                + abs(slot_rank - anchor_rank) * 100
                + anchor_rank
            )
            _add_flow_edge(graph, player_node, slot_node, 1, cost)

    for slot_index in range(player_count):
        _add_flow_edge(graph, first_slot + slot_index, sink, 1, 0)

    total_flow = 0
    while total_flow < player_count:
        distance = [10**18] * len(graph)
        previous_node = [-1] * len(graph)
        previous_edge = [-1] * len(graph)
        in_queue = [False] * len(graph)
        queue = [source]
        distance[source] = 0
        in_queue[source] = True
        cursor = 0
        while cursor < len(queue):
            node = queue[cursor]
            cursor += 1
            in_queue[node] = False
            for edge_index, edge in enumerate(graph[node]):
                if edge["cap"] <= 0:
                    continue
                candidate_distance = distance[node] + edge["cost"]
                if candidate_distance >= distance[edge["to"]]:
                    continue
                distance[edge["to"]] = candidate_distance
                previous_node[edge["to"]] = node
                previous_edge[edge["to"]] = edge_index
                if not in_queue[edge["to"]]:
                    queue.append(edge["to"])
                    in_queue[edge["to"]] = True
        if previous_node[sink] < 0:
            raise RuntimeError("Guarded QB rank constraints do not admit a complete unique board")
        node = sink
        while node != source:
            prior = previous_node[node]
            edge_index = previous_edge[node]
            edge = graph[prior][edge_index]
            edge["cap"] -= 1
            graph[node][edge["rev"]]["cap"] += 1
            node = prior
        total_flow += 1

    guarded_board = []
    for index, record in enumerate(board):
        player_node = first_player + index
        assigned_rank = next(
            edge["to"] - first_slot + 1
            for edge in graph[player_node]
            if first_slot <= edge["to"] < sink and edge["cap"] == 0
        )
        guarded_record = dict(record)
        guarded_record["guarded_consensus_rank"] = assigned_rank
        guarded_record["guarded_movement_from_anchor"] = record["anchor_rank"] - assigned_rank
        guarded_record["guarded_movement_from_live"] = record["live_rank"] - assigned_rank
        guarded_record["guarded_movement_review"] = abs(record["anchor_rank"] - assigned_rank) >= 3
        guarded_record["guarded_weak_passing_riser"] = bool(
            assigned_rank < record["anchor_rank"] - 1
            and record.get("passing_epa_per_dropback") is not None
            and record.get("passing_cpoe") is not None
            and record["passing_epa_per_dropback"] <= 0
            and record["passing_cpoe"] <= 0
        )
        guarded_record["guarded_qb6_crossing"] = (record["anchor_rank"] <= 6) != (assigned_rank <= 6)
        guarded_record["guarded_qb12_crossing"] = (record["anchor_rank"] <= 12) != (assigned_rank <= 12)
        guarded_record["guarded_qb24_crossing"] = (record["anchor_rank"] <= 24) != (assigned_rank <= 24)
        guarded_record["review_order"] = assigned_rank
        guarded_board.append(guarded_record)
    return sorted(guarded_board, key=lambda record: (record["guarded_consensus_rank"], record["player_name"]))


def summarize(board: list[dict]) -> dict:
    def count(field: str) -> int:
        return sum(bool(record.get(field)) for record in board)

    guarded_ranks = [record["guarded_consensus_rank"] for record in board]
    return {
        "player_count": len(board),
        "ranking_version": board[0].get("ranking_version") if board else None,
        "model_run_id": board[0].get("model_run_id") if board else None,
        "bqml_feature_count": count("has_bqml_features"),
        "deterministic_lane_count": sum(
            record.get("review_lane") != "returning_player_bqml_lane" for record in board
        ),
        "rookie_lane_count": sum(
            record.get("review_lane") == "rookie_deterministic_lane" for record in board
        ),
        "duplicate_guarded_rank_count": len(guarded_ranks) - len(set(guarded_ranks)),
        "deterministic_lane_rank_change_count": sum(
            record.get("review_lane") != "returning_player_bqml_lane"
            and record["guarded_consensus_rank"] != record["anchor_rank"]
            for record in board
        ),
        "consensus_max_movement": max(
            (abs(record["consensus_movement_from_anchor"]) for record in board), default=0
        ),
        "linear_max_movement": max(
            (abs(record["linear_movement_from_anchor"]) for record in board), default=0
        ),
        "guarded_max_movement": max(
            (abs(record["guarded_movement_from_anchor"]) for record in board), default=0
        ),
        "consensus_movement_review_count": count("consensus_movement_review"),
        "linear_movement_review_count": count("linear_movement_review"),
        "guarded_movement_review_count": count("guarded_movement_review"),
        "consensus_rushing_only_riser_count": count("consensus_rushing_only_riser"),
        "linear_rushing_only_riser_count": count("linear_rushing_only_riser"),
        "guarded_weak_passing_riser_count": count("guarded_weak_passing_riser"),
        "consensus_qb6_crossing_count": count("consensus_qb6_crossing"),
        "consensus_qb12_crossing_count": count("consensus_qb12_crossing"),
        "consensus_qb24_crossing_count": count("consensus_qb24_crossing"),
        "linear_qb6_crossing_count": count("linear_qb6_crossing"),
        "linear_qb12_crossing_count": count("linear_qb12_crossing"),
        "linear_qb24_crossing_count": count("linear_qb24_crossing"),
        "guarded_qb6_crossing_count": count("guarded_qb6_crossing"),
        "guarded_qb12_crossing_count": count("guarded_qb12_crossing"),
        "guarded_qb24_crossing_count": count("guarded_qb24_crossing"),
    }


def run(args: argparse.Namespace) -> dict:
    client = bigquery.Client(project=args.project)
    sql = build_owner_review_sql(args.project, args.dataset)
    dry_job = client.query(
        sql,
        job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False),
    )
    if args.dry_run:
        return {
            "dry_run": True,
            "estimated_bytes_processed": int(dry_job.total_bytes_processed or 0),
            "writes": False,
        }
    query_job = client.query(sql)
    board = assign_guarded_consensus_ranks([dict(record) for record in query_job.result()])
    return {
        "dry_run": False,
        "query_job_id": query_job.job_id,
        "summary": summarize(board),
        "board": board,
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
