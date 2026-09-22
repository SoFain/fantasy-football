"""Build the repaired Standard WR Fable board after current-context safety."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ranking_owner_decisions import (
    STANDARD_WR_ELITE_ORDER,
)


def _sql_strings(values: tuple[str, ...]) -> str:
    return ",".join(f"'{value.replace(chr(39), chr(39) * 2)}'" for value in values)


def _base_ctes(project: str, metrics_dataset: str, brain_dataset: str) -> str:
    root = f"{project}.{metrics_dataset}"
    return f"""
WITH formula AS (
  SELECT
    candidate_internal_player_id AS player_id,
    player_name,
    team AS source_team,
    wr_fable_v1_score AS formula_score,
    coverage_method,
    score_source_season,
    baseline_v1_score_available,
    ROW_NUMBER() OVER (ORDER BY wr_fable_v1_score DESC, player_name) AS formula_rank
  FROM `{root}.v_wr_fable_v1_current_candidates`
  WHERE wr_fable_v1_score IS NOT NULL
), live_standard AS (
  SELECT player_id, rank AS current_standard_rank
  FROM `{project}.{brain_dataset}.analytics_pigskin_rankings`
  WHERE is_active AND scoring_profile_id = 'standard' AND position = 'WR'
    AND league_type_id = 'redraft' AND roster_format_id = 'one_qb'
  QUALIFY ROW_NUMBER() OVER (PARTITION BY player_id ORDER BY generated_at DESC) = 1
), joined AS (
  SELECT
    formula.*,
    safety.gsis_id IS NOT NULL
      AND safety.current_board_rank_eligible IS FALSE AS teamless_unranked,
    live_standard.current_standard_rank,
    safety.sleeper_player_id,
    safety.team AS current_team,
    safety.active AS sleeper_active,
    safety.status AS sleeper_status,
    safety.injury_status AS sleeper_injury_status,
    safety.depth_chart_position AS sleeper_depth_chart_position,
    safety.depth_chart_order AS sleeper_depth_chart_order,
    safety.fetched_at AS sleeper_fetched_at,
    COALESCE(safety.sleeper_hard_review, TRUE) AS sleeper_hard_review,
    COALESCE(safety.post_formula_adjustment, 0.0) AS post_formula_adjustment,
    COALESCE(safety.post_formula_adjustment_code, 'NO_ADJUSTMENT_CONTEXT_MISSING')
      AS post_formula_adjustment_code,
    COALESCE(safety.post_formula_adjustment_detail, 'No role movement. Sleeper context is missing.')
      AS post_formula_adjustment_detail,
    COALESCE(safety.review_flags_json, '["SLEEPER_CONTEXT_MISSING"]') AS review_flags_json,
    COALESCE(safety.requires_owner_review, TRUE) AS requires_owner_review,
    COALESCE(safety.ranking_eligibility, 'current_roster_review_required') AS ranking_eligibility,
    safety.gsis_id IS NULL AS sleeper_context_missing
  FROM formula
  LEFT JOIN live_standard USING (player_id)
  LEFT JOIN `{root}.v_ranking_post_formula_safety` AS safety
    ON safety.gsis_id = formula.player_id AND safety.position = 'WR'
)
"""


def build_query(
    project: str,
    metrics_dataset: str,
    brain_dataset: str = "fantasy_football_brain",
) -> str:
    elite_order = _sql_strings(STANDARD_WR_ELITE_ORDER)
    elite_rank_cases = "\n".join(
        f"      WHEN '{player}' THEN elite_slots.occupied_ranks[SAFE_OFFSET({index})]"
        for index, player in enumerate(STANDARD_WR_ELITE_ORDER)
    )
    return f"""
{_base_ctes(project, metrics_dataset, brain_dataset)}, eligible AS (
  SELECT * FROM joined WHERE NOT teamless_unranked
), ranked AS (
  SELECT
    *,
    formula_score + post_formula_adjustment AS post_formula_score,
    ROW_NUMBER() OVER (
      ORDER BY formula_score + post_formula_adjustment DESC, player_name
    ) AS post_formula_rank
  FROM eligible
), elite_slots AS (
  SELECT ARRAY_AGG(post_formula_rank ORDER BY post_formula_rank) AS occupied_ranks
  FROM ranked
  WHERE player_name IN ({elite_order})
), guarded AS (
  SELECT
    ranked.*,
    CASE player_name
{elite_rank_cases}
      ELSE post_formula_rank
    END AS final_rank
  FROM ranked
  CROSS JOIN elite_slots
)
SELECT
  *,
  formula_rank - post_formula_rank AS safety_rank_delta,
  post_formula_rank - final_rank AS elite_order_rank_delta,
  formula_rank - final_rank AS rank_delta,
  IF(
    player_name IN ({elite_order}) AND post_formula_rank != final_rank,
    'OWNER_APPROVED_ELITE_ORDER',
    post_formula_adjustment_code
  ) AS final_adjustment_code,
  IF(
    player_name IN ({elite_order}) AND post_formula_rank != final_rank,
    CONCAT(post_formula_adjustment_detail, ' Owner-approved elite order: A.J. Brown, Justin Jefferson, Garrett Wilson.'),
    post_formula_adjustment_detail
  ) AS final_adjustment_detail
FROM guarded
WHERE final_rank <= 100
ORDER BY final_rank
"""


def build_watchlist_query(
    project: str,
    metrics_dataset: str,
    brain_dataset: str = "fantasy_football_brain",
) -> str:
    return f"""
{_base_ctes(project, metrics_dataset, brain_dataset)}
SELECT
  *,
  formula_score + post_formula_adjustment AS post_formula_score,
  'TEAMLESS_UNRANKED' AS watchlist_code,
  'Unranked until Sleeper reports a current team and the role is verified.' AS watchlist_reason
FROM joined
WHERE teamless_unranked
ORDER BY formula_rank
"""


def _write_table(client: bigquery.Client, rows: list[dict], table_id: str) -> None:
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        autodetect=True,
    )
    payload = json.loads(json.dumps(rows, default=str))
    client.load_table_from_json(payload, table_id, job_config=job_config).result()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("output/standard-wr-fable-v1-post-formula-safety-review.json"),
    )
    parser.add_argument(
        "--watchlist-output",
        type=Path,
        default=Path("output/standard-wr-fable-v1-unranked-watchlist.json"),
    )
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    rows = [
        dict(row)
        for row in client.query(
            build_query(args.project, args.metrics_dataset, args.brain_dataset)
        ).result()
    ]
    watchlist_rows = [
        dict(row)
        for row in client.query(
            build_watchlist_query(args.project, args.metrics_dataset, args.brain_dataset)
        ).result()
    ]

    if len(rows) != 100 or len({row["player_id"] for row in rows}) != 100:
        raise RuntimeError("Standard WR safety review must contain 100 unique players")
    if {row["final_rank"] for row in rows} != set(range(1, 101)):
        raise RuntimeError("Standard WR final ranks must be unique and contiguous from 1 through 100")
    elite_rows = sorted(
        (row for row in rows if row["player_name"] in STANDARD_WR_ELITE_ORDER),
        key=lambda row: row["final_rank"],
    )
    if tuple(row["player_name"] for row in elite_rows) != STANDARD_WR_ELITE_ORDER:
        raise RuntimeError(f"Elite WR guardrail failed: {elite_rows}")
    if any(not row["sleeper_hard_review"] or row["current_team"] is not None for row in watchlist_rows):
        raise RuntimeError("Teamless watchlist contains a player without a current roster hard review")
    if any(row["teamless_unranked"] for row in rows):
        raise RuntimeError("Teamless player remained on the candidate board")

    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.watchlist_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(rows, default=str, indent=2) + "\n", encoding="utf-8")
    args.watchlist_output.write_text(
        json.dumps(watchlist_rows, default=str, indent=2) + "\n",
        encoding="utf-8",
    )

    board_table = f"{args.project}.{args.metrics_dataset}.standard_wr_fable_v1_post_formula_review"
    watchlist_table = f"{args.project}.{args.metrics_dataset}.standard_wr_fable_v1_unranked_watchlist"
    if args.apply:
        _write_table(client, rows, board_table)
        _write_table(client, watchlist_rows, watchlist_table)

    summary = {
        "rows": len(rows),
        "hard_reviews": sum(row["sleeper_hard_review"] for row in rows),
        "owner_reviews": sum(row["requires_owner_review"] for row in rows),
        "injury_reviews": sum("INJURY_UNCERTAIN" in row["review_flags_json"] for row in rows),
        "context_missing": sum(row["sleeper_context_missing"] for row in rows),
        "adjusted_rows": sum(row["post_formula_adjustment"] != 0.0 for row in rows),
        "elite_order": [
            {"final_rank": row["final_rank"], "player_name": row["player_name"]}
            for row in elite_rows
        ],
        "watchlist": [row["player_name"] for row in watchlist_rows],
        "watchlist_count": len(watchlist_rows),
        "largest_absolute_rank_delta": max(abs(row["rank_delta"]) for row in rows),
        "largest_live_rank_delta": max(
            (
                abs(row["current_standard_rank"] - row["final_rank"])
                for row in rows
                if row["current_standard_rank"] is not None
            ),
            default=None,
        ),
        "sleeper_fetched_at": max(
            (row["sleeper_fetched_at"] for row in rows if row["sleeper_fetched_at"] is not None),
            default=None,
        ),
        "applied": args.apply,
        "board_table": board_table if args.apply else None,
        "watchlist_table": watchlist_table if args.apply else None,
        "live_rankings_changed": False,
    }
    print(json.dumps(summary, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
