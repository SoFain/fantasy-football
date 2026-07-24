"""Build the Standard overall board by interleaving frozen positional queues with VORP.

The legacy module name is retained because existing production commands import it.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


POSITIONS = ("QB", "RB", "WR", "TE")
OVERALL_BOARD_SIZE = 150
REPLACEMENT_RANK = {"QB": 13, "RB": 34, "WR": 40, "TE": 9}
ONESIE_MULTIPLIER = {"QB": 0.85, "RB": 1.0, "WR": 1.0, "TE": 0.90}


def fit_log_curve(points: list[tuple[int, float]]) -> tuple[float, float]:
    """Fit PPG = a - b*ln(rank) with ordinary least squares."""
    if len(points) < 2:
        raise ValueError("at least two rank/PPG points are required")
    x = [math.log(rank) for rank, _ in points]
    y = [ppg for _, ppg in points]
    x_mean = sum(x) / len(x)
    y_mean = sum(y) / len(y)
    denominator = sum((value - x_mean) ** 2 for value in x)
    if denominator == 0:
        raise ValueError("rank values must vary")
    slope = sum((left - x_mean) * (right - y_mean) for left, right in zip(x, y)) / denominator
    return y_mean - slope * x_mean, -slope


def projected_ppg(position_rank: int, curve: tuple[float, float]) -> float:
    a, b = curve
    return a - b * math.log(position_rank)


def interleave(
    queues: dict[str, list[dict[str, Any]]],
    curves: dict[str, tuple[float, float]],
    availability: dict[str, float],
    *,
    limit: int = OVERALL_BOARD_SIZE,
    replacement_rank: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    replacement_rank = replacement_rank or REPLACEMENT_RANK
    candidates = []
    for position in POSITIONS:
        replacement_ppg = projected_ppg(replacement_rank[position], curves[position])
        for position_rank, source in enumerate(queues[position], 1):
            ppg = projected_ppg(position_rank, curves[position])
            vorp = ppg - replacement_ppg
            candidates.append({
                **source,
                "position": position,
                "position_rank": position_rank,
                "projected_ppg": ppg,
                "replacement_rank": replacement_rank[position],
                "replacement_ppg": replacement_ppg,
                "vorp": vorp,
                "availability_multiplier": availability[position],
                "onesie_multiplier": ONESIE_MULTIPLIER[position],
                "adjusted_vorp": vorp * availability[position] * ONESIE_MULTIPLIER[position],
            })
    ordered = sorted(candidates, key=lambda row: (-row["adjusted_vorp"], POSITIONS.index(row["position"]), row["position_rank"]))[:limit]
    return [{**row, "overall_rank": rank} for rank, row in enumerate(ordered, 1)]


def assert_position_order(board: list[dict[str, Any]]) -> None:
    for position in POSITIONS:
        ranks = [row["position_rank"] for row in board if row["position"] == position]
        if ranks != sorted(ranks) or ranks != list(range(1, len(ranks) + 1)):
            raise ValueError(f"{position} positional order was not preserved: {ranks}")


def render_markdown(board: list[dict[str, Any]], metadata: dict[str, Any]) -> str:
    mix = Counter(row["position"] for row in board)
    lines = [
        f"# Unified Fable v1 Standard Top-{OVERALL_BOARD_SIZE} Review Board",
        "",
        "> All positions use their active Standard queues. The interleaver cannot reorder players within a position.",
        "",
        "## Model",
        "",
        f"| Position | Curve | Replacement | Availability | Onesie | Top-{OVERALL_BOARD_SIZE} count |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for position in POSITIONS:
        curve = metadata["curves"][position]
        lines.append(
            f"| {position} | {curve['a']:.3f} - {curve['b']:.3f} ln(rank) | "
            f"{REPLACEMENT_RANK[position]} | {metadata['availability'][position]:.3f} | "
            f"{ONESIE_MULTIPLIER[position]:.2f} | {mix[position]} |"
        )
    lines.extend([
        "",
        "## Board",
        "",
        "| Ovr | Player | Team | Pos | Pos rank | Proj PPG | VORP | Adj VORP | Source version | Risk flags |",
        "|---:|---|---|---|---:|---:|---:|---:|---|---|",
    ])
    for row in board:
        flags = str(row.get("risk_flags") or "").replace("|", "/")
        lines.append(
            f"| {row['overall_rank']} | {row['player_name']} | {row.get('current_team') or ''} | "
            f"{row['position']} | {row['position_rank']} | {row['projected_ppg']:.2f} | "
            f"{row['vorp']:.2f} | {row['adjusted_vorp']:.2f} | {row.get('ranking_version') or ''} | {flags} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--json-output", type=Path, default=Path("output/unified-fable-v1-standard-top150.json"))
    parser.add_argument("--markdown-output", type=Path, default=Path("docs/rebuild/unified-fable-v1-standard-top150.md"))
    args = parser.parse_args()

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    historical = [dict(row) for row in client.query(f"""
WITH player_seasons AS (
  SELECT season, position, source_player_key AS player_id,
    COUNT(*) AS games_played,
    SAFE_DIVIDE(SUM(total_fantasy_points), COUNT(*)) AS standard_ppg
  FROM `{args.project}.{args.dataset}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'standard' AND position IN ('QB','RB','WR','TE')
    AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season, position, player_id
  HAVING games_played >= 6
), ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY season, position ORDER BY standard_ppg DESC, player_id) AS position_rank
  FROM player_seasons
)
SELECT * FROM ranked WHERE position_rank <= 60
ORDER BY season, position, position_rank
""").result()]
    active = [dict(row) for row in client.query(f"""
SELECT player_id, player_name, current_team, position, rank AS position_rank,
  ranking_version, rank_source, risk_flags
FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
WHERE is_active AND scoring_profile_id = 'standard' AND position IN ('QB','RB','WR','TE')
QUALIFY ROW_NUMBER() OVER (PARTITION BY position, player_id ORDER BY generated_at DESC) = 1
ORDER BY position, position_rank, player_name
""").result()]

    curves = {}
    availability = {}
    for position in POSITIONS:
        replacement = REPLACEMENT_RANK[position]
        rows = [row for row in historical if row["position"] == position and row["position_rank"] <= max(replacement + 12, 24)]
        curves[position] = fit_log_curve([(row["position_rank"], row["standard_ppg"]) for row in rows])
        top_cohort = [row for row in historical if row["position"] == position and row["position_rank"] <= replacement]
        availability[position] = sum(min(row["games_played"] / 17, 1.0) for row in top_cohort) / len(top_cohort)

    queues = {position: sorted((row for row in active if row["position"] == position), key=lambda row: (row["position_rank"], row["player_name"])) for position in POSITIONS}
    for position in POSITIONS:
        if len(queues[position]) < REPLACEMENT_RANK[position]:
            raise ValueError(f"{position} queue has only {len(queues[position])} active players")
        source_ranks = [row["position_rank"] for row in queues[position]]
        if source_ranks != list(range(1, len(source_ranks) + 1)):
            raise ValueError(f"{position} active ranks are not contiguous")

    board = interleave(queues, curves, availability)
    assert_position_order(board)
    if len({row["player_id"] for row in board}) != len(board):
        raise ValueError("duplicate player identity in unified board")
    metadata = {
        "curves": {position: {"a": curves[position][0], "b": curves[position][1]} for position in POSITIONS},
        "availability": availability,
        "replacement_rank": REPLACEMENT_RANK,
        "onesie_multiplier": ONESIE_MULTIPLIER,
        "source_versions": {position: sorted({row["ranking_version"] for row in queues[position]}) for position in POSITIONS},
        "composition": dict(Counter(row["position"] for row in board)),
        "historical_seasons": [2022, 2023, 2024, 2025],
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps({"metadata": metadata, "board": board}, indent=2, default=str) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(board, metadata), encoding="utf-8")
    print(json.dumps(metadata, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
