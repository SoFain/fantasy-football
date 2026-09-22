"""Materialize player-week injury/depth role context metrics.

This module writes a derived research table only. It does not update active
rankings, champion formulas, or detail-row tournament outputs.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Any


DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
WRITE_GATE = "ALLOW_ROLE_CONTEXT_MATERIALIZATION"


def build_role_context_sql(project: str, dataset: str) -> str:
    return f"""
DELETE FROM `{project}.{dataset}.player_week_role_context_metrics`
WHERE season BETWEEN @season_start AND @season_end;

INSERT INTO `{project}.{dataset}.player_week_role_context_metrics` (
  season,
  week,
  player_id_internal,
  gsis_id,
  player_name,
  team,
  position,
  injury_report_count,
  out_status_count,
  doubtful_status_count,
  questionable_status_count,
  limited_practice_count,
  did_not_practice_count,
  injury_risk_score,
  injury_status_score,
  injury_burden_score,
  missed_time_risk_score,
  availability_score,
  depth_chart_role_score,
  missing_flags_json,
  injury_context_missing_flags_json,
  source_freshness_json,
  source_provenance_json,
  identity_mapping_method,
  identity_mapping_confidence,
  role_context_run_id,
  created_at
)
WITH injury_source AS (
  SELECT
    season,
    week,
    team,
    gsis_id,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(position) AS position,
    COUNT(1) AS injury_report_count,
    COUNTIF(LOWER(COALESCE(report_status, game_status, '')) = 'out') AS out_status_count,
    COUNTIF(LOWER(COALESCE(report_status, game_status, '')) = 'doubtful') AS doubtful_status_count,
    COUNTIF(LOWER(COALESCE(report_status, game_status, '')) = 'questionable') AS questionable_status_count,
    COUNTIF(LOWER(COALESCE(practice_status, '')) LIKE '%limited%') AS limited_practice_count,
    COUNTIF(LOWER(COALESCE(practice_status, '')) LIKE '%did not participate%') AS did_not_practice_count,
    MAX(loaded_at) AS source_updated_at
  FROM `{project}.{dataset}.raw_nflverse_injuries`
  WHERE season BETWEEN @season_start AND @season_end
  GROUP BY season, week, team, gsis_id
),
identity_bridge AS (
  SELECT
    gsis_id,
    ANY_VALUE(player_id_internal) AS player_id_internal
  FROM `{project}.{dataset}.player_identity_bridge`
  WHERE gsis_id IS NOT NULL
  GROUP BY gsis_id
)
SELECT
  injury_source.season,
  injury_source.week,
  COALESCE(identity_bridge.player_id_internal, CONCAT('gsis:', injury_source.gsis_id)) AS player_id_internal,
  injury_source.gsis_id,
  injury_source.player_name,
  injury_source.team,
  injury_source.position,
  injury_source.injury_report_count,
  injury_source.out_status_count,
  injury_source.doubtful_status_count,
  injury_source.questionable_status_count,
  injury_source.limited_practice_count,
  injury_source.did_not_practice_count,
  LEAST(100.0, GREATEST(0.0,
    injury_source.out_status_count * 100.0
    + injury_source.doubtful_status_count * 75.0
    + injury_source.questionable_status_count * 45.0
    + injury_source.did_not_practice_count * 25.0
    + injury_source.limited_practice_count * 10.0
  )) AS injury_risk_score,
  -- Higher is healthier. This is the direct inverse of the current-week source-supported risk score.
  100.0 - LEAST(100.0, GREATEST(0.0,
    injury_source.out_status_count * 100.0
    + injury_source.doubtful_status_count * 75.0
    + injury_source.questionable_status_count * 45.0
    + injury_source.did_not_practice_count * 25.0
    + injury_source.limited_practice_count * 10.0
  )) AS injury_status_score,
  -- Higher means more historical burden. It uses only report/practice designations present in the source.
  LEAST(100.0, GREATEST(0.0,
    injury_source.injury_report_count * 8.0
    + injury_source.questionable_status_count * 10.0
    + injury_source.doubtful_status_count * 20.0
    + injury_source.out_status_count * 30.0
    + injury_source.did_not_practice_count * 10.0
    + injury_source.limited_practice_count * 4.0
  )) AS injury_burden_score,
  -- Higher means missed-time concern. Only explicit Out and Doubtful report statuses are counted.
  LEAST(100.0, GREATEST(0.0,
    injury_source.out_status_count * 100.0
    + injury_source.doubtful_status_count * 75.0
  )) AS missed_time_risk_score,
  -- Higher means more available. This avoids zero-fill by keeping source rows distinct from missing rows.
  100.0 - LEAST(100.0, GREATEST(0.0,
    injury_source.out_status_count * 100.0
    + injury_source.doubtful_status_count * 75.0
    + injury_source.questionable_status_count * 45.0
    + injury_source.did_not_practice_count * 25.0
    + injury_source.limited_practice_count * 10.0
  )) AS availability_score,
  CAST(NULL AS FLOAT64) AS depth_chart_role_score,
  TO_JSON_STRING(ARRAY_CONCAT(
    IF(identity_bridge.player_id_internal IS NULL, ['using_exact_gsis_fallback_identity'], []),
    ['historical_depth_chart_context_unavailable']
  )) AS missing_flags_json,
  TO_JSON_STRING(STRUCT(
    FALSE AS injury_source_row_missing,
    injury_source.injury_report_count = 0 AS injury_report_count_missing,
    injury_source.out_status_count = 0 AND injury_source.doubtful_status_count = 0 AND injury_source.questionable_status_count = 0 AS report_status_signal_missing,
    injury_source.did_not_practice_count = 0 AND injury_source.limited_practice_count = 0 AS practice_status_signal_missing,
    identity_bridge.player_id_internal IS NULL AS primary_identity_bridge_missing,
    TRUE AS historical_depth_chart_context_unavailable
  )) AS injury_context_missing_flags_json,
  TO_JSON_STRING(STRUCT(
    injury_source.source_updated_at AS raw_nflverse_injuries_loaded_at,
    CAST(NULL AS TIMESTAMP) AS raw_nflverse_depth_charts_loaded_at
  )) AS source_freshness_json,
  TO_JSON_STRING(STRUCT(
    'raw_nflverse_injuries' AS injury_source_table,
    'raw_nflverse_depth_charts' AS depth_source_table,
    'depth loader lacks historical season/week keys in current nflreadpy output' AS depth_source_status
  )) AS source_provenance_json,
  IF(identity_bridge.player_id_internal IS NOT NULL, 'identity_bridge_gsis_exact', 'gsis_exact_fallback') AS identity_mapping_method,
  IF(identity_bridge.player_id_internal IS NOT NULL, 1.0, 0.75) AS identity_mapping_confidence,
  @role_context_run_id AS role_context_run_id,
  CURRENT_TIMESTAMP() AS created_at
FROM injury_source
LEFT JOIN identity_bridge
  ON injury_source.gsis_id = identity_bridge.gsis_id
""".strip()


def build_summary_sql(project: str, dataset: str) -> str:
    return f"""
SELECT
  COUNT(1) AS row_count,
  COUNT(DISTINCT season) AS season_count,
  MIN(season) AS min_season,
  MAX(season) AS max_season,
  MIN(injury_risk_score) AS min_injury_risk_score,
  MAX(injury_risk_score) AS max_injury_risk_score,
  AVG(injury_risk_score) AS avg_injury_risk_score,
  AVG(injury_status_score) AS avg_injury_status_score,
  AVG(injury_burden_score) AS avg_injury_burden_score,
  AVG(missed_time_risk_score) AS avg_missed_time_risk_score,
  AVG(availability_score) AS avg_availability_score,
  COUNTIF(player_id_internal IS NULL) AS missing_identity_count,
  COUNTIF(identity_mapping_method = 'gsis_exact_fallback') AS gsis_fallback_identity_count,
  COUNTIF(depth_chart_role_score IS NULL) AS missing_depth_score_count
FROM `{project}.{dataset}.player_week_role_context_metrics`
WHERE season BETWEEN @season_start AND @season_end
""".strip()


def _params(season_start: int, season_end: int, role_context_run_id: str) -> list[Any]:
    from google.cloud import bigquery

    return [
        bigquery.ScalarQueryParameter("season_start", "INT64", int(season_start)),
        bigquery.ScalarQueryParameter("season_end", "INT64", int(season_end)),
        bigquery.ScalarQueryParameter("role_context_run_id", "STRING", role_context_run_id),
    ]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize derived player-week role context metrics.")
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT", DEFAULT_PROJECT))
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET", DEFAULT_DATASET))
    parser.add_argument("--season-start", type=int, required=True)
    parser.add_argument("--season-end", type=int, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.write and args.dry_run:
        print("--write and --dry-run cannot be combined", file=sys.stderr)
        return 2
    role_context_run_id = f"role_context_{args.season_start}_{args.season_end}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    if not args.write:
        print(json.dumps({
            "dry_run": True,
            "wrote": False,
            "target_table": f"{args.project}.{args.dataset}.player_week_role_context_metrics",
            "season_start": args.season_start,
            "season_end": args.season_end,
            "role_context_run_id": role_context_run_id,
        }, indent=2, sort_keys=True))
        return 0
    if os.environ.get(WRITE_GATE) != "true":
        print(f"{WRITE_GATE} must be true to materialize role context metrics", file=sys.stderr)
        return 2

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    job_config = bigquery.QueryJobConfig(
        query_parameters=_params(args.season_start, args.season_end, role_context_run_id)
    )
    client.query(build_role_context_sql(args.project, args.dataset), job_config=job_config).result()
    summary_rows = list(client.query(build_summary_sql(args.project, args.dataset), job_config=job_config).result())
    summary = dict(summary_rows[0].items()) if summary_rows else {}
    summary.update({
        "dry_run": False,
        "wrote": True,
        "target_table": f"{args.project}.{args.dataset}.player_week_role_context_metrics",
        "season_start": args.season_start,
        "season_end": args.season_end,
        "role_context_run_id": role_context_run_id,
        "write_gate": WRITE_GATE,
    })
    print(json.dumps(summary, indent=2, sort_keys=True, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
