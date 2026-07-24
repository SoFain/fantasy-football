"""Promote the guarded 75/25 board as the active Standard QB ranking lane."""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_standard_qb_2026_owner_review import (
    assign_guarded_consensus_ranks,
    build_owner_review_sql,
    summarize,
)


WRITE_GATE = "ALLOW_STANDARD_QB_GUARDED_PROMOTION"
CANDIDATE_ID = "standard_qb_guarded_bqml_75_25_v1"
FORMULA_VERSION = "1.0-phase-35-11"


def _sql_string(value: object) -> str:
    if value is None:
        return "NULL"
    return "'" + str(value).replace("\\", "\\\\").replace("'", "\\'") + "'"


def _sql_number(value: object) -> str:
    return "NULL" if value is None else str(value)


def validate_board(board: list[dict]) -> dict:
    summary = summarize(board)
    failures = []
    if summary["player_count"] != 45:
        failures.append("board must contain exactly 45 QBs")
    if summary["duplicate_guarded_rank_count"]:
        failures.append("guarded ranks must be unique")
    if summary["guarded_weak_passing_riser_count"]:
        failures.append("weak-passing upward guard failed")
    if summary["guarded_qb6_crossing_count"]:
        failures.append("QB6 cutline must remain stable")
    if summary["guarded_qb24_crossing_count"]:
        failures.append("QB24 cutline must remain stable")
    for record in board:
        depth_order = record.get("sleeper_depth_chart_order")
        rank = record["guarded_consensus_rank"]
        if depth_order == 2 and not 33 <= rank <= 43:
            failures.append(f"{record['player_name']} depth-2 rank {rank} is outside QB33-43")
        if depth_order is not None and depth_order >= 3 and rank < 44:
            failures.append(f"{record['player_name']} depth-{depth_order} rank {rank} is above QB44")
    if failures:
        raise RuntimeError("; ".join(failures))
    return summary


def build_promotion_sql(
    board: list[dict],
    *,
    project: str,
    dataset: str,
    ranking_version: str,
    model_run_id: str,
    prior_ranking_version: str,
) -> str:
    live = f"`{project}.{dataset}.analytics_pigskin_rankings`"
    history = f"`{project}.{dataset}.analytics_pigskin_rankings_history`"
    candidates = f"`{project}.{dataset}.ranking_formula_candidates`"
    champions = f"`{project}.{dataset}.ranking_formula_champions`"
    promoted_records = []
    for record in board:
        promoted_records.append(
            "STRUCT("
            f"{_sql_string(record['player_id'])} AS player_id, "
            f"{record['guarded_consensus_rank']} AS guarded_rank, "
            f"{record['anchor_rank']} AS anchor_rank, "
            f"{record['consensus_75_25_rank']} AS raw_consensus_rank, "
            f"{record['linear_70_30_rank']} AS raw_linear_rank, "
            f"{_sql_number(record.get('consensus_priority'))} AS consensus_priority, "
            f"{_sql_number(record.get('passing_epa_per_dropback'))} AS passing_epa, "
            f"{_sql_number(record.get('passing_cpoe'))} AS passing_cpoe, "
            f"{_sql_number(record.get('qb_rushing_baseline'))} AS rushing_baseline, "
            f"{_sql_number(record.get('sleeper_depth_chart_order'))} AS depth_order, "
            f"{_sql_string(record.get('review_lane'))} AS review_lane)"
        )
    promoted_sql = ",\n    ".join(promoted_records)
    formula_json = json.dumps(
        {
            "anchor_weight": 0.75,
            "linear_points_weight": 0.125,
            "logistic_bust_weight": 0.125,
            "movement_cap": 4,
            "weak_passing_rule": "no rise over 1 and no upward QB6/QB12/QB24 crossing when EPA and CPOE are non-positive",
            "role_buckets": {"starter_or_unknown": "QB1-32", "depth_2": "QB33-43", "depth_3_plus": "QB44-45"},
            "missing_history_rule": "deterministic anchor unless role bucket conflicts",
        },
        sort_keys=True,
    ).replace("'", "\\'")
    scope = (
        "position='QB' AND scoring_profile_id='standard' "
        "AND league_type_id='redraft' AND roster_format_id='one_qb'"
    )
    return f"""
BEGIN TRANSACTION;

MERGE {candidates} AS target
USING (SELECT '{CANDIDATE_ID}' AS candidate_id) AS source
ON target.candidate_id=source.candidate_id
WHEN MATCHED THEN UPDATE SET
  status='champion', formula_version='{FORMULA_VERSION}', formula_json='{formula_json}',
  notes='Owner-approved guarded Standard QB formula. Phases 35.9-35.11.', updated_at=CURRENT_TIMESTAMP()
WHEN NOT MATCHED THEN INSERT
  (candidate_id, formula_set_id, formula_name, formula_version, position, formula_json,
   feature_allowlist_json, target_definition_json, source_requirements_json, status, notes,
   created_by, created_at, updated_at)
VALUES
  ('{CANDIDATE_ID}', 'standard_redraft_one_qb', 'Standard QB Guarded BQML 75/25', '{FORMULA_VERSION}', 'QB',
   '{formula_json}',
   '{{"features":"deterministic candidate rank, advanced QB linear-points and logistic-bust signals, Sleeper depth order as role guard only"}}',
   '{{"target":"next-season Standard QB fantasy points and bust control","no_2026_outcomes":true}}',
   '{{"models":["ranking_bqml_v2_adv_standard_qb_linear_points_advanced_v0","ranking_bqml_v2_adv_standard_qb_logistic_bust_advanced_v0"]}}',
   'champion', 'Owner-approved Phase 35.11 Standard QB promotion.', 'owner', CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP());

UPDATE {champions}
SET active=FALSE, notes=COALESCE(notes,'') || ' | deactivated by {model_run_id}'
WHERE active AND position='QB' AND formula_set_id='standard_redraft_one_qb';

INSERT INTO {champions}
  (champion_id, formula_set_id, position, candidate_id, formula_version, backtest_run_id,
   champion_reason, metric_name, metric_value, season_start, season_end, week_start, week_end,
   active, selected_by, selected_at, notes)
VALUES
  ('{ranking_version}', 'standard_redraft_one_qb', 'QB', '{CANDIDATE_ID}', '{FORMULA_VERSION}',
   'phase-35-9-guarded-backtest',
   'Owner-approved after historical stability, 2026 player review, weak-passing locks, and Sleeper depth-order buckets.',
   'combined_rank_correlation', 0.5383, 2024, 2025, 1, 18, TRUE, 'owner', CURRENT_TIMESTAMP(),
   'Standard QB only. Old Flash board archived. No LLM reordering applied.');

INSERT INTO {history}
SELECT active_board.*
FROM {live} AS active_board
WHERE active_board.is_active AND active_board.{scope}
  AND NOT EXISTS (
    SELECT 1 FROM {history} AS archived_board
    WHERE archived_board.ranking_version=active_board.ranking_version
      AND archived_board.player_id=active_board.player_id
      AND archived_board.position=active_board.position
      AND archived_board.scoring_profile_id=active_board.scoring_profile_id
  );

UPDATE {live}
SET is_active=FALSE
WHERE is_active AND {scope};

INSERT INTO {live}
WITH promoted AS (
  SELECT * FROM UNNEST([
    {promoted_sql}
  ])
)
SELECT prior_board.* REPLACE(
  '{ranking_version}' AS ranking_version,
  CURRENT_TIMESTAMP() AS generated_at,
  CURRENT_TIMESTAMP() AS adjudicated_at,
  promoted.guarded_rank AS rank,
  CASE
    WHEN promoted.guarded_rank<=6 THEN 'elite'
    WHEN promoted.guarded_rank<=12 THEN 'front-line starter'
    WHEN promoted.guarded_rank<=24 THEN 'matchup starter'
    WHEN promoted.guarded_rank<=32 THEN 'starter depth'
    ELSE 'backup or watchlist'
  END AS tier,
  ROUND(100 - (promoted.guarded_rank-1) * 50.0/44.0, 1) AS ranking_score,
  100 - promoted.consensus_priority AS raw_ranking_score,
  promoted.guarded_rank AS candidate_rank,
  ROUND(100 - (promoted.guarded_rank-1) * 50.0/44.0, 1) AS candidate_ranking_score,
  FORMAT(
    'Guarded 75/25: anchor QB%d, raw consensus QB%d, raw linear QB%d; EPA/DB %s; CPOE %s; depth order %s.',
    promoted.anchor_rank, promoted.raw_consensus_rank, promoted.raw_linear_rank,
    COALESCE(CAST(ROUND(promoted.passing_epa,3) AS STRING),'unavailable'),
    COALESCE(CAST(ROUND(promoted.passing_cpoe,2) AS STRING),'unavailable'),
    COALESCE(CAST(promoted.depth_order AS STRING),'unknown')
  ) AS rank_rationale,
  FORMAT(
    'Deterministic guarded Standard formula ranks %s at QB%d. No LLM reordering was applied.',
    prior_board.player_name, promoted.guarded_rank
  ) AS pigskin_verdict,
  'A verified starter-role change, source-backed 2026 rookie evidence, or a coded injury games-missed adjustment.' AS what_would_change_mind,
  ARRAY_TO_STRING(ARRAY(
    SELECT flag FROM UNNEST([
      IF(promoted.depth_order>1, 'SLEEPER_DEPTH_ORDER_' || CAST(promoted.depth_order AS STRING), NULL),
      IF(prior_board.sleeper_injury_status IS NOT NULL, 'SLEEPER_INJURY_' || UPPER(prior_board.sleeper_injury_status), NULL),
      IF(promoted.review_lane!='returning_player_bqml_lane', UPPER(promoted.review_lane), NULL)
    ]) AS flag WHERE flag IS NOT NULL
  ), '; ') AS risk_flags,
  'standard_qb_guarded_bqml_75_25' AS model_name,
  'deterministic-no-llm' AS prompt_version,
  'latest-pre-2026-bqml-plus-sleeper-depth' AS data_snapshot_label,
  TRUE AS is_active,
  'standard_qb_guarded_75_25' AS rank_source,
  '{model_run_id}' AS model_run_id,
  'NO_ADJUSTMENT' AS llm_adjustment_code,
  'Deterministic formula promotion; no LLM movement applied.' AS llm_adjustment_detail,
  'Phases 35.9-35.11 historical, owner-review, and depth-order evidence.' AS llm_adjustment_evidence,
  CAST(NULL AS INT64) AS llm_estimated_games_missed,
  0 AS llm_rank_delta
)
FROM {live} AS prior_board
JOIN promoted USING (player_id)
WHERE prior_board.ranking_version='{prior_ranking_version}'
  AND NOT prior_board.is_active
  AND prior_board.{scope};

ASSERT (
  SELECT COUNT(*)=45 AND COUNT(DISTINCT rank)=45
  FROM {live}
  WHERE is_active AND {scope}
) AS 'Active Standard QB board must contain 45 unique ranks';

ASSERT NOT EXISTS (
  SELECT 1 FROM {live}
  WHERE is_active AND {scope}
    AND sleeper_depth_chart_order=2 AND rank<33
) AS 'Second-string QB appeared above QB33';

ASSERT NOT EXISTS (
  SELECT 1 FROM {live}
  WHERE is_active AND {scope}
    AND sleeper_depth_chart_order>=3 AND rank<44
) AS 'Third-string QB appeared above QB44';

COMMIT TRANSACTION;
"""


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)

    if args.apply and os.environ.get(WRITE_GATE) != "true":
        print(f"{WRITE_GATE} must be true to apply the promotion", file=sys.stderr)
        return 2

    client = bigquery.Client(project=args.project)
    review_job = client.query(build_owner_review_sql(args.project, args.dataset))
    board = assign_guarded_consensus_ranks([dict(record) for record in review_job.result()])
    summary = validate_board(board)
    now = datetime.now(timezone.utc)
    ranking_version = now.strftime("standard-qb-guarded-75-25-%Y%m%d%H%M%S")
    model_run_id = now.strftime("standard_qb_guarded_75_25-%Y%m%dT%H%M%SZ")
    prior_ranking_version = str(board[0]["ranking_version"])
    sql = build_promotion_sql(
        board,
        project=args.project,
        dataset=args.dataset,
        ranking_version=ranking_version,
        model_run_id=model_run_id,
        prior_ranking_version=prior_ranking_version,
    )
    if args.dry_run:
        print(json.dumps({
            "mode": "dry-run",
            "review_job_id": review_job.job_id,
            "prior_ranking_version": prior_ranking_version,
            "ranking_version": ranking_version,
            "model_run_id": model_run_id,
            "summary": summary,
            "writes": False,
        }, indent=2, default=str))
        return 0

    promotion_job = client.query(sql)
    promotion_job.result()
    print(json.dumps({
        "mode": "apply",
        "review_job_id": review_job.job_id,
        "promotion_job_id": promotion_job.job_id,
        "prior_ranking_version": prior_ranking_version,
        "ranking_version": ranking_version,
        "model_run_id": model_run_id,
        "summary": summary,
    }, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
