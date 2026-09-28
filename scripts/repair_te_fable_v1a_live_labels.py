"""Repair deterministic labels on the active Standard TE Fable board.

The guarded Pigskin pass may annotate rows with adjustment codes, but it must
not author formula tiers or verdict copy. Writes require the existing bounded
TE promotion gate and never update rank or score fields.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from google.cloud import bigquery


WRITE_GATE = "ALLOW_TE_FABLE_V1A_STANDARD_TE_PROMOTION"
EXPECTED_ROW_COUNT = 35


def build_repair_sql(project: str, dataset: str) -> str:
    live = f"`{project}.{dataset}.analytics_pigskin_rankings`"
    history = f"`{project}.{dataset}.analytics_pigskin_rankings_history`"
    return f"""
BEGIN TRANSACTION;

INSERT INTO {history}
SELECT live.*
FROM {live} AS live
WHERE live.is_active
  AND live.position = 'TE'
  AND live.scoring_profile_id = 'standard'
  AND live.league_type_id = 'redraft'
  AND live.roster_format_id = 'one_qb'
  AND live.ranking_version = @ranking_version
  AND NOT EXISTS (
    SELECT 1
    FROM {history} AS prior
    WHERE prior.ranking_version = live.ranking_version
      AND prior.player_id = live.player_id
      AND prior.position = live.position
      AND prior.scoring_profile_id = live.scoring_profile_id
  );

UPDATE {live} AS target
SET
  tier = CASE
    WHEN target.rank <= 5 THEN 'elite'
    WHEN target.rank <= 12 THEN 'front-line starter'
    WHEN target.rank <= 24 THEN 'starter'
    ELSE 'flex or matchup'
  END,
  pigskin_verdict = CASE
    WHEN target.llm_adjustment_code = 'INJURY_UNCERTAIN' THEN
      FORMAT(
        'TE Fable v1.0a no-man ranks %s at TE%d from the deterministic 2025 input formula. Current injury information is unresolved and has no preseason rank effect.',
        target.player_name,
        target.rank
      )
    ELSE
      FORMAT(
        'TE Fable v1.0a no-man ranks %s at TE%d from the deterministic 2025 input formula.',
        target.player_name,
        target.rank
      )
  END,
  what_would_change_mind =
    'A source-backed current-role change, verified rookie evidence, or an estimated regular-season games-missed range.'
WHERE target.is_active
  AND target.position = 'TE'
  AND target.scoring_profile_id = 'standard'
  AND target.league_type_id = 'redraft'
  AND target.roster_format_id = 'one_qb'
  AND target.ranking_version = @ranking_version;

COMMIT TRANSACTION;
"""


def active_board_query(project: str, dataset: str) -> str:
    return f"""
SELECT
  ranking_version,
  COUNT(*) AS row_count,
  COUNT(DISTINCT rank) AS distinct_rank_count,
  MIN(rank) AS min_rank,
  MAX(rank) AS max_rank,
  TO_HEX(MD5(STRING_AGG(
    FORMAT('%s|%d|%.6f', player_id, rank, ranking_score),
    '|' ORDER BY rank
  ))) AS board_fingerprint
FROM `{project}.{dataset}.analytics_pigskin_rankings`
WHERE is_active
  AND position = 'TE'
  AND scoring_profile_id = 'standard'
  AND league_type_id = 'redraft'
  AND roster_format_id = 'one_qb'
GROUP BY ranking_version
"""


def label_summary_query(project: str, dataset: str) -> str:
    return f"""
SELECT
  tier,
  llm_adjustment_code,
  COUNT(*) AS row_count
FROM `{project}.{dataset}.analytics_pigskin_rankings`
WHERE is_active
  AND position = 'TE'
  AND scoring_profile_id = 'standard'
  AND league_type_id = 'redraft'
  AND roster_format_id = 'one_qb'
  AND ranking_version = @ranking_version
GROUP BY tier, llm_adjustment_code
ORDER BY tier, llm_adjustment_code
"""


def get_active_board(client: bigquery.Client, dataset: str) -> dict:
    summaries = [dict(item) for item in client.query(active_board_query(client.project, dataset)).result()]
    if len(summaries) != 1:
        raise RuntimeError(f"Expected one active Standard TE ranking version; found {len(summaries)}")
    summary = summaries[0]
    if (
        summary["row_count"] != EXPECTED_ROW_COUNT
        or summary["distinct_rank_count"] != EXPECTED_ROW_COUNT
        or summary["min_rank"] != 1
        or summary["max_rank"] != EXPECTED_ROW_COUNT
    ):
        raise RuntimeError(f"Expected a complete active TE35 board; found {summary}")
    return summary


def query_config(ranking_version: str) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("ranking_version", "STRING", ranking_version),
    ])


def run(args: argparse.Namespace) -> dict:
    client = bigquery.Client(project=args.project)
    before = get_active_board(client, args.dataset)
    ranking_version = str(before["ranking_version"])
    if args.apply:
        if os.environ.get(WRITE_GATE) != "true":
            raise RuntimeError(f"{WRITE_GATE} must be true to repair live TE labels")
        client.query(
            build_repair_sql(args.project, args.dataset),
            job_config=query_config(ranking_version),
        ).result()

    after = get_active_board(client, args.dataset)
    if before["board_fingerprint"] != after["board_fingerprint"]:
        raise RuntimeError("TE board player/rank/score fingerprint changed during label repair")
    labels = [
        dict(item)
        for item in client.query(
            label_summary_query(args.project, args.dataset),
            job_config=query_config(ranking_version),
        ).result()
    ]
    return {
        "mode": "apply" if args.apply else "dry-run",
        "ranking_version": ranking_version,
        "row_count": after["row_count"],
        "board_fingerprint_before": before["board_fingerprint"],
        "board_fingerprint_after": after["board_fingerprint"],
        "label_summary": labels,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run(args), default=str, indent=2))
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
