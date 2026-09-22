"""Direct nflverse Next Gen Stats derived metrics for ranking research."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping
from typing import Any


DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SOURCE_VERSION = "nflverse_ngs_direct_latest"
DEFAULT_SEASON_START = 2016
DEFAULT_SEASON_END = 2025
WRITE_GATE = "ALLOW_NFLVERSE_NGS_METRICS_MATERIALIZATION"
DERIVED_TABLE = "player_week_ngs_metrics"


def table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    return f"{project_id}.{dataset_id}.{table_name}"


def is_write_authorized(env: Mapping[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return source.get(WRITE_GATE, "").strip().lower() == "true"


def require_write_authorization(env: Mapping[str, str] | None = None) -> None:
    if not is_write_authorized(env):
        raise PermissionError(f"{WRITE_GATE} must be true to materialize NGS metrics")


def build_ngs_metrics_delete_sql(*, project_id: str, dataset_id: str) -> str:
    return f"""
DELETE FROM `{table_id(project_id, dataset_id, DERIVED_TABLE)}`
WHERE source_version = @source_version
  AND season BETWEEN @season_start AND @season_end
""".strip()


def _score_average(*scores: str) -> str:
    numerator = " + ".join(f"COALESCE({score}, 0.0)" for score in scores)
    denominator = " + ".join(f"IF({score} IS NULL, 0, 1)" for score in scores)
    return f"SAFE_DIVIDE({numerator}, NULLIF({denominator}, 0))"


def build_ngs_metrics_insert_sql(*, project_id: str, dataset_id: str) -> str:
    target_table = table_id(project_id, dataset_id, DERIVED_TABLE)
    receiving_table = table_id(project_id, dataset_id, "raw_nflverse_ngs_receiving")
    rushing_table = table_id(project_id, dataset_id, "raw_nflverse_ngs_rushing")
    passing_table = table_id(project_id, dataset_id, "raw_nflverse_ngs_passing")
    return f"""
INSERT INTO `{target_table}` (
  source_version,
  season,
  week,
  player_id_internal,
  player_gsis_id,
  player_name,
  position,
  team,
  ngs_avg_cushion,
  ngs_avg_separation,
  ngs_avg_intended_air_yards,
  ngs_catch_percentage,
  ngs_expected_catch_percentage,
  ngs_catch_over_expected,
  ngs_yards_after_catch,
  ngs_expected_yac,
  ngs_yac_over_expected,
  ngs_receiving_efficiency_score,
  ngs_receiving_role_quality_score,
  ngs_efficiency,
  ngs_percent_attempts_gte_8_defenders,
  ngs_avg_time_behind_line,
  ngs_expected_rush_yards,
  ngs_rush_yards_over_expected,
  ngs_rush_yards_over_expected_per_attempt,
  ngs_rush_yards_over_expected_success_rate,
  ngs_rushing_efficiency_score,
  ngs_box_resilience_score,
  ngs_cpoe,
  ngs_avg_time_to_throw,
  ngs_intended_air_yards,
  ngs_aggressiveness,
  ngs_expected_completion_percentage,
  ngs_passing_efficiency_score,
  ngs_missing_flags_json,
  source_provenance_json,
  source_updated_at,
  created_at
)
WITH receiving_raw AS (
  SELECT
    season,
    week,
    player_gsis_id,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(position) AS position,
    ANY_VALUE(team) AS team,
    AVG(avg_cushion) AS ngs_avg_cushion,
    AVG(avg_separation) AS ngs_avg_separation,
    AVG(avg_intended_air_yards) AS ngs_avg_intended_air_yards,
    AVG(catch_percentage) AS ngs_catch_percentage,
    AVG(avg_yac) AS ngs_yards_after_catch,
    AVG(avg_expected_yac) AS ngs_expected_yac,
    AVG(avg_yac_above_expectation) AS ngs_yac_over_expected,
    MAX(loaded_at) AS source_updated_at,
    ARRAY_AGG(DISTINCT source_version IGNORE NULLS) AS source_versions,
    ARRAY_AGG(DISTINCT source_refresh_id IGNORE NULLS) AS source_refresh_ids
  FROM `{receiving_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND week BETWEEN 1 AND 23
  GROUP BY season, week, player_gsis_id
),
rushing_raw AS (
  SELECT
    season,
    week,
    player_gsis_id,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(position) AS position,
    ANY_VALUE(team) AS team,
    AVG(efficiency) AS ngs_efficiency,
    AVG(percent_attempts_gte_eight_defenders) AS ngs_percent_attempts_gte_8_defenders,
    AVG(avg_time_to_los) AS ngs_avg_time_behind_line,
    AVG(expected_yards) AS ngs_expected_rush_yards,
    AVG(rush_yards_over_expected) AS ngs_rush_yards_over_expected,
    AVG(rush_yards_over_expected_per_att) AS ngs_rush_yards_over_expected_per_attempt,
    AVG(rush_pct_over_expected) AS ngs_rush_yards_over_expected_success_rate,
    MAX(loaded_at) AS source_updated_at,
    ARRAY_AGG(DISTINCT source_version IGNORE NULLS) AS source_versions,
    ARRAY_AGG(DISTINCT source_refresh_id IGNORE NULLS) AS source_refresh_ids
  FROM `{rushing_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND week BETWEEN 1 AND 23
  GROUP BY season, week, player_gsis_id
),
passing_raw AS (
  SELECT
    season,
    week,
    player_gsis_id,
    ANY_VALUE(player_name) AS player_name,
    ANY_VALUE(position) AS position,
    ANY_VALUE(team) AS team,
    AVG(cpoe) AS ngs_cpoe,
    AVG(avg_time_to_throw) AS ngs_avg_time_to_throw,
    AVG(avg_air_yards) AS ngs_intended_air_yards,
    AVG(aggressiveness) AS ngs_aggressiveness,
    AVG(expected_completion_percentage) AS ngs_expected_completion_percentage,
    MAX(loaded_at) AS source_updated_at,
    ARRAY_AGG(DISTINCT source_version IGNORE NULLS) AS source_versions,
    ARRAY_AGG(DISTINCT source_refresh_id IGNORE NULLS) AS source_refresh_ids
  FROM `{passing_table}`
  WHERE season BETWEEN @season_start AND @season_end
    AND week BETWEEN 1 AND 23
  GROUP BY season, week, player_gsis_id
),
player_keys AS (
  SELECT season, week, player_gsis_id FROM receiving_raw
  UNION DISTINCT
  SELECT season, week, player_gsis_id FROM rushing_raw
  UNION DISTINCT
  SELECT season, week, player_gsis_id FROM passing_raw
),
joined AS (
  SELECT
    @source_version AS source_version,
    keys.season,
    keys.week,
    keys.player_gsis_id AS player_id_internal,
    keys.player_gsis_id,
    COALESCE(receiving.player_name, rushing.player_name, passing.player_name) AS player_name,
    COALESCE(receiving.position, rushing.position, passing.position) AS position,
    COALESCE(receiving.team, rushing.team, passing.team) AS team,
    receiving.ngs_avg_cushion,
    receiving.ngs_avg_separation,
    receiving.ngs_avg_intended_air_yards,
    receiving.ngs_catch_percentage,
    CAST(NULL AS FLOAT64) AS ngs_expected_catch_percentage,
    CAST(NULL AS FLOAT64) AS ngs_catch_over_expected,
    receiving.ngs_yards_after_catch,
    receiving.ngs_expected_yac,
    receiving.ngs_yac_over_expected,
    rushing.ngs_efficiency,
    rushing.ngs_percent_attempts_gte_8_defenders,
    rushing.ngs_avg_time_behind_line,
    rushing.ngs_expected_rush_yards,
    rushing.ngs_rush_yards_over_expected,
    rushing.ngs_rush_yards_over_expected_per_attempt,
    rushing.ngs_rush_yards_over_expected_success_rate,
    passing.ngs_cpoe,
    passing.ngs_avg_time_to_throw,
    passing.ngs_intended_air_yards,
    passing.ngs_aggressiveness,
    passing.ngs_expected_completion_percentage,
    GREATEST(
      COALESCE(receiving.source_updated_at, TIMESTAMP '1970-01-01'),
      COALESCE(rushing.source_updated_at, TIMESTAMP '1970-01-01'),
      COALESCE(passing.source_updated_at, TIMESTAMP '1970-01-01')
    ) AS source_updated_at,
    TO_JSON_STRING(STRUCT(
      receiving.source_versions AS receiving_source_versions,
      rushing.source_versions AS rushing_source_versions,
      passing.source_versions AS passing_source_versions,
      receiving.source_refresh_ids AS receiving_source_refresh_ids,
      rushing.source_refresh_ids AS rushing_source_refresh_ids,
      passing.source_refresh_ids AS passing_source_refresh_ids,
      'nflreadpy.load_nextgen_stats' AS loader,
      'source seasons only; feature mart excludes target season' AS leakage_policy
    )) AS source_provenance_json
  FROM player_keys keys
  LEFT JOIN receiving_raw receiving USING (season, week, player_gsis_id)
  LEFT JOIN rushing_raw rushing USING (season, week, player_gsis_id)
  LEFT JOIN passing_raw passing USING (season, week, player_gsis_id)
),
scored AS (
  SELECT
    *,
    LEAST(100.0, GREATEST(0.0, ngs_avg_separation / 4.0 * 100.0)) AS receiving_separation_score,
    LEAST(100.0, GREATEST(0.0, 50.0 + ngs_yac_over_expected * 12.0)) AS receiving_yac_score,
    LEAST(100.0, GREATEST(0.0, IF(ngs_catch_percentage <= 1.0, ngs_catch_percentage * 100.0, ngs_catch_percentage))) AS receiving_catch_score,
    LEAST(100.0, GREATEST(0.0, 100.0 - ABS(COALESCE(ngs_avg_intended_air_yards, 0.0) - 10.0) * 5.0)) AS receiving_depth_score,
    LEAST(100.0, GREATEST(0.0, 100.0 - (ngs_efficiency - 2.5) * 20.0)) AS rushing_efficiency_component,
    LEAST(100.0, GREATEST(0.0, 50.0 + ngs_rush_yards_over_expected_per_attempt * 12.0)) AS rushing_ryoe_component,
    LEAST(100.0, GREATEST(0.0, IF(ngs_rush_yards_over_expected_success_rate <= 1.0, ngs_rush_yards_over_expected_success_rate * 100.0, ngs_rush_yards_over_expected_success_rate))) AS rushing_success_component,
    LEAST(100.0, GREATEST(0.0, 50.0 + COALESCE(ngs_rush_yards_over_expected_per_attempt, 0.0) * 10.0 + IF(ngs_percent_attempts_gte_8_defenders <= 1.0, ngs_percent_attempts_gte_8_defenders * 20.0, ngs_percent_attempts_gte_8_defenders * 0.2))) AS rushing_box_component,
    LEAST(100.0, GREATEST(0.0, 50.0 + ngs_cpoe * 2.0)) AS passing_cpoe_component,
    LEAST(100.0, GREATEST(0.0, 100.0 - ngs_avg_time_to_throw * 18.0)) AS passing_time_component,
    LEAST(100.0, GREATEST(0.0, ngs_expected_completion_percentage)) AS passing_expected_completion_component
  FROM joined
)
SELECT
  source_version,
  season,
  week,
  player_id_internal,
  player_gsis_id,
  player_name,
  position,
  team,
  ngs_avg_cushion,
  ngs_avg_separation,
  ngs_avg_intended_air_yards,
  ngs_catch_percentage,
  ngs_expected_catch_percentage,
  ngs_catch_over_expected,
  ngs_yards_after_catch,
  ngs_expected_yac,
  ngs_yac_over_expected,
  {_score_average("receiving_separation_score", "receiving_yac_score", "receiving_catch_score")} AS ngs_receiving_efficiency_score,
  {_score_average("receiving_separation_score", "receiving_depth_score")} AS ngs_receiving_role_quality_score,
  ngs_efficiency,
  ngs_percent_attempts_gte_8_defenders,
  ngs_avg_time_behind_line,
  ngs_expected_rush_yards,
  ngs_rush_yards_over_expected,
  ngs_rush_yards_over_expected_per_attempt,
  ngs_rush_yards_over_expected_success_rate,
  {_score_average("rushing_efficiency_component", "rushing_ryoe_component", "rushing_success_component")} AS ngs_rushing_efficiency_score,
  {_score_average("rushing_ryoe_component", "rushing_box_component")} AS ngs_box_resilience_score,
  ngs_cpoe,
  ngs_avg_time_to_throw,
  ngs_intended_air_yards,
  ngs_aggressiveness,
  ngs_expected_completion_percentage,
  {_score_average("passing_cpoe_component", "passing_time_component", "passing_expected_completion_component")} AS ngs_passing_efficiency_score,
  TO_JSON_STRING(STRUCT(
    ngs_avg_separation IS NULL AS ngs_avg_separation_missing,
    ngs_avg_cushion IS NULL AS ngs_avg_cushion_missing,
    ngs_catch_percentage IS NULL AS ngs_catch_percentage_missing,
    TRUE AS ngs_expected_catch_percentage_unavailable,
    TRUE AS ngs_catch_over_expected_unavailable,
    ngs_yac_over_expected IS NULL AS ngs_yac_over_expected_missing,
    ngs_efficiency IS NULL AS ngs_rushing_efficiency_missing,
    ngs_rush_yards_over_expected_per_attempt IS NULL AS ngs_rush_yards_over_expected_per_attempt_missing,
    ngs_percent_attempts_gte_8_defenders IS NULL AS ngs_box_rate_missing,
    ngs_cpoe IS NULL AS ngs_cpoe_missing,
    ngs_expected_completion_percentage IS NULL AS ngs_expected_completion_percentage_missing
  )) AS ngs_missing_flags_json,
  source_provenance_json,
  NULLIF(source_updated_at, TIMESTAMP '1970-01-01') AS source_updated_at,
  CURRENT_TIMESTAMP() AS created_at
FROM scored
WHERE player_gsis_id IS NOT NULL
  AND season BETWEEN @season_start AND @season_end
""".strip()


def _query_job_config(params: list[Any]) -> Any:
    from google.cloud import bigquery

    return bigquery.QueryJobConfig(query_parameters=params)


def _params(*, source_version: str, season_start: int, season_end: int) -> list[Any]:
    from google.cloud import bigquery

    return [
        bigquery.ScalarQueryParameter("source_version", "STRING", source_version),
        bigquery.ScalarQueryParameter("season_start", "INT64", int(season_start)),
        bigquery.ScalarQueryParameter("season_end", "INT64", int(season_end)),
    ]


def materialize_ngs_metrics(
    *,
    client: Any,
    project_id: str = DEFAULT_PROJECT,
    dataset_id: str = DEFAULT_DATASET,
    source_version: str = DEFAULT_SOURCE_VERSION,
    season_start: int = DEFAULT_SEASON_START,
    season_end: int = DEFAULT_SEASON_END,
    write: bool = False,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    params = _params(source_version=source_version, season_start=season_start, season_end=season_end)
    delete_sql = build_ngs_metrics_delete_sql(project_id=project_id, dataset_id=dataset_id)
    insert_sql = build_ngs_metrics_insert_sql(project_id=project_id, dataset_id=dataset_id)
    if not write:
        return {
            "dry_run": True,
            "write": False,
            "target_table": table_id(project_id, dataset_id, DERIVED_TABLE),
            "source_version": source_version,
            "season_start": int(season_start),
            "season_end": int(season_end),
            "delete_sql": delete_sql,
            "insert_sql": insert_sql,
        }
    require_write_authorization(env)
    job_config = _query_job_config(params)
    client.query(delete_sql, job_config=job_config).result()
    insert_job = client.query(insert_sql, job_config=job_config)
    insert_job.result()
    return {
        "dry_run": False,
        "write": True,
        "target_table": table_id(project_id, dataset_id, DERIVED_TABLE),
        "source_version": source_version,
        "season_start": int(season_start),
        "season_end": int(season_end),
        "insert_job_id": getattr(insert_job, "job_id", None),
        "affected_row_count": int(getattr(insert_job, "num_dml_affected_rows", 0) or 0),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Materialize direct nflverse NGS metrics.")
    parser.add_argument("--project", default=os.environ.get("BQ_PROJECT") or DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=os.environ.get("BQ_DATASET") or DEFAULT_DATASET)
    parser.add_argument("--source-version", default=DEFAULT_SOURCE_VERSION)
    parser.add_argument("--season-start", type=int, default=DEFAULT_SEASON_START)
    parser.add_argument("--season-end", type=int, default=DEFAULT_SEASON_END)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    from google.cloud import bigquery

    client = bigquery.Client(project=args.project)
    result = materialize_ngs_metrics(
        client=client,
        project_id=args.project,
        dataset_id=args.dataset,
        source_version=args.source_version,
        season_start=args.season_start,
        season_end=args.season_end,
        write=args.write and not args.dry_run,
    )
    printable = {key: value for key, value in result.items() if not key.endswith("_sql")}
    print(json.dumps(printable, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
