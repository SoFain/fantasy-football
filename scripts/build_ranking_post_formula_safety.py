"""Deploy the shared current-context safety view without changing rankings."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from google.cloud import bigquery


VIEW_FILE = Path(__file__).resolve().parents[1] / "bigquery" / "views" / "v_ranking_post_formula_safety.sql"
VIEW_NAME = "v_ranking_post_formula_safety"


def render_sql(project: str, dataset: str, brain_dataset: str = "fantasy_football_brain") -> str:
    return (
        VIEW_FILE.read_text(encoding="utf-8")
        .replace("{{PROJECT_ID}}", project)
        .replace("{{DATASET_ID}}", dataset)
        .replace("{{BRAIN_DATASET_ID}}", brain_dataset)
    )


def validation_sql(project: str, dataset: str) -> str:
    view = f"`{project}.{dataset}.{VIEW_NAME}`"
    return f"""
SELECT
  COUNT(*) AS row_count,
  COUNT(DISTINCT COALESCE(gsis_id, CONCAT('sleeper:', sleeper_player_id))) AS identity_count,
  COUNTIF(sleeper_hard_review) AS hard_review_count,
  COUNTIF(post_formula_adjustment = 0.02) AS depth_1_boost_count,
  COUNTIF(post_formula_adjustment = -0.04) AS depth_3_penalty_count,
  COUNTIF('INJURY_UNCERTAIN' IN UNNEST(review_flags)) AS injury_review_count,
  COUNTIF('DEPTH_CHART_UNKNOWN' IN UNNEST(review_flags)) AS unknown_depth_count,
  COUNTIF('ROOKIE_CONTEXT_REQUIRED' IN UNNEST(review_flags)) AS rookie_review_count,
  COUNTIF(NOT current_board_rank_eligible) AS teamless_unranked_count,
  COUNTIF(sleeper_hard_review AND post_formula_adjustment != 0.0) AS invalid_hard_review_adjustments,
  COUNTIF(team IS NULL AND current_board_rank_eligible) AS invalid_teamless_eligibility,
  COUNTIF(post_formula_adjustment NOT IN (-0.04, 0.0, 0.02)) AS invalid_adjustments,
  MAX(fetched_at) AS latest_fetched_at
FROM {view}
WHERE position IN ('QB', 'RB', 'WR', 'TE')
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--brain-dataset", default="fantasy_football_brain")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    client = bigquery.Client(project=args.project)
    sql = render_sql(args.project, args.dataset, args.brain_dataset)
    if not args.apply:
        job = client.query(
            sql,
            job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False),
        )
        print(json.dumps({"writes": False, "bytes": job.total_bytes_processed}, indent=2))
        return 0

    client.query(sql).result()
    result = dict(next(iter(client.query(validation_sql(args.project, args.dataset)).result())))
    if result["row_count"] != result["identity_count"]:
        raise RuntimeError("Shared safety view contains duplicate player identities")
    if (
        result["invalid_hard_review_adjustments"]
        or result["invalid_teamless_eligibility"]
        or result["invalid_adjustments"]
    ):
        raise RuntimeError(f"Shared safety view failed adjustment validation: {result}")
    print(json.dumps({"writes": True, "view": VIEW_NAME, "validation": result}, default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
