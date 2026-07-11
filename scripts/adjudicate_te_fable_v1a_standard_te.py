"""Run one guarded Pigskin exception review over the active TE Fable board."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.generate_pigskin_rankings import (
    DEFAULT_MODEL,
    generate_position_rows,
    get_code_version,
    write_rankings,
)
from src.model_runs import (
    create_model_run,
    create_source_freshness_snapshot,
    mark_model_run_complete,
    mark_model_run_failed,
)


WRITE_GATE = "ALLOW_TE_FABLE_V1A_STANDARD_TE_PROMOTION"
EXPECTED_RANK_SOURCE = "te_fable_v1a_no_man_formula"


def summarize(rows: list[dict]) -> dict:
    moved = [row for row in rows if row["llm_rank_delta"] != 0]
    substantive = [row for row in rows if row["llm_adjustment_code"] not in {"NO_ADJUSTMENT", "ORDER_REBALANCE", "INJURY_UNCERTAIN"}]
    return {
        "row_count": len(rows),
        "moved_count": len(moved),
        "substantive_adjustment_count": len(substantive),
        "total_absolute_movement": sum(abs(row["llm_rank_delta"]) for row in moved),
        "code_counts": {
            code: sum(row["llm_adjustment_code"] == code for row in rows)
            for code in sorted({row["llm_adjustment_code"] for row in rows})
        },
        "movements": [{
            "player_name": row["player_name"],
            "candidate_rank": row["candidate_rank"],
            "final_rank": row["rank"],
            "delta": row["llm_rank_delta"],
            "code": row["llm_adjustment_code"],
            "detail": row["llm_adjustment_detail"],
            "evidence": row["llm_adjustment_evidence"],
        } for row in moved],
    }


def archive_board(client: bigquery.Client, dataset: str, ranking_version: str) -> None:
    sql = f"""
INSERT INTO `{client.project}.{dataset}.analytics_pigskin_rankings_history`
SELECT live.*
FROM `{client.project}.{dataset}.analytics_pigskin_rankings` AS live
WHERE live.is_active
  AND live.position='TE'
  AND live.scoring_profile_id='standard'
  AND live.league_type_id='redraft'
  AND live.roster_format_id='one_qb'
  AND live.ranking_version=@ranking_version
  AND NOT EXISTS (
    SELECT 1 FROM `{client.project}.{dataset}.analytics_pigskin_rankings_history` AS prior
    WHERE prior.ranking_version=live.ranking_version AND prior.player_id=live.player_id
      AND prior.position=live.position AND prior.scoring_profile_id=live.scoring_profile_id)
"""
    config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("ranking_version", "STRING", ranking_version),
    ])
    client.query(sql, job_config=config).result()


def run(args: argparse.Namespace) -> dict:
    if args.apply and os.environ.get(WRITE_GATE) != "true":
        raise RuntimeError(f"{WRITE_GATE} must be true to write guarded TE rankings")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required")

    client = bigquery.Client(project=args.project)
    query = f"""
SELECT * FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
WHERE is_active AND position='TE' AND scoring_profile_id='standard'
  AND league_type_id='redraft' AND roster_format_id='one_qb'
  AND rank_source=@rank_source
ORDER BY rank
"""
    config = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("rank_source", "STRING", EXPECTED_RANK_SOURCE),
    ])
    candidates = client.query(query, job_config=config).result().to_dataframe()
    if len(candidates) != 35 or candidates["rank"].tolist() != list(range(1, 36)):
        raise RuntimeError(f"Expected a complete active TE Fable TE35 board; found {len(candidates)} rows")

    candidate_version = str(candidates.iloc[0]["ranking_version"])
    ranking_version = f"te-fable-guarded-pigskin-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
    snapshot_id = create_source_freshness_snapshot(
        client=client,
        dataset_id=args.dataset,
        source_table_names=("analytics_pigskin_rankings", "sleeper_players_current"),
        max_value_table_names=("analytics_pigskin_rankings",),
    )
    model_run_id = create_model_run(
        client=client,
        dataset_id=args.dataset,
        run_type="pigskin_rankings_guarded_exception_review",
        model_name=args.model,
        model_version="te-fable-v1a-no-man",
        prompt_version="pigskin-rankings-exception-repair-v1",
        code_version=get_code_version(),
        season=2026,
        week=None,
        scoring_profile_id="standard",
        league_type_id="redraft",
        roster_format_id="one_qb",
        feature_config_version_id=None,
        source_freshness_snapshot_id=snapshot_id,
        created_by="adjudicate_te_fable_v1a_standard_te",
        notes=f"candidate_ranking_version={candidate_version}",
    )
    metadata = {
        "model_run_id": model_run_id,
        "scoring_profile_id": "standard",
        "league_type_id": "redraft",
        "roster_format_id": "one_qb",
        "feature_config_version_id": None,
        "source_freshness_snapshot_id": snapshot_id,
        "prompt_version": "pigskin-rankings-exception-repair-v1",
    }
    try:
        rows = generate_position_rows(api_key, args.model, "TE", candidates, ranking_version, metadata)
        summary = summarize(rows)
        if summary["substantive_adjustment_count"] > 5:
            raise RuntimeError("Guarded review exceeded five substantive adjustments")
        if any(not row["llm_adjustment_code"] for row in rows):
            raise RuntimeError("Guarded review returned an uncoded row")
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps({"summary": summary, "rows": rows}, default=str, indent=2) + "\n", encoding="utf-8")
        if args.apply:
            archive_board(client, args.dataset, candidate_version)
            write_rankings(client, args.dataset, rows)
        mark_model_run_complete(
            model_run_id,
            client=client,
            dataset_id=args.dataset,
            notes=f"apply={str(args.apply).lower()}; ranking_version={ranking_version}; row_count={len(rows)}",
        )
        return {
            "mode": "apply" if args.apply else "dry-run",
            "candidate_ranking_version": candidate_version,
            "ranking_version": ranking_version,
            "model_run_id": model_run_id,
            "summary": summary,
        }
    except Exception as exc:
        mark_model_run_failed(model_run_id, str(exc), client=client, dataset_id=args.dataset)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--output", type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(run(args), default=str, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
