"""Materialize Phase 2 packets and projection tables."""

from __future__ import annotations

import argparse
import logging
import os
import re
from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_project


logger = logging.getLogger(__name__)

DEFAULT_DATASET = "fantasy_football_brain"
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def table_exists(client: bigquery.Client, dataset_id: str, table_name: str) -> bool:
    try:
        client.get_table(f"{client.project}.{dataset_id}.{table_name}")
        return True
    except NotFound:
        return False


def build_projections_sql(project_id: str, dataset_id: str) -> str:
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.mart_projection_tables`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2030, 1))
    CLUSTER BY player_id_internal, scoring_profile_id, season, week AS
    WITH latest_week AS (
        SELECT MAX(season) AS max_season, MAX(week) AS max_week
        FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth`
    ),
    active_profiles AS (
        SELECT DISTINCT scoring_profile_id
        FROM `{project_id}.{dataset_id}.scoring_profiles`
        WHERE COALESCE(active, TRUE)
    )
    SELECT
        r.player_id AS player_id_internal,
        r.player_id AS source_player_key,
        r.model_run_id,
        ap.scoring_profile_id,
        COALESCE(lw.max_season, 2026) AS season,
        COALESCE(lw.max_week, 1) AS week,
        r.ranking_score AS projected_points,
        TO_JSON_STRING(STRUCT(
            r.tier AS tier,
            r.confidence_score AS confidence_score,
            r.rank AS rank,
            r.rank_rationale AS rationale
        )) AS projection_metadata_json,
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings` r
    LEFT JOIN latest_week lw ON TRUE
    CROSS JOIN active_profiles ap
    WHERE r.is_active = TRUE
    """


def build_fraud_packets_sql(project_id: str, dataset_id: str) -> str:
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.mart_fraud_sleeper_packets`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2030, 1))
    CLUSTER BY season, week, scoring_profile_id AS
    WITH active_profiles AS (
        SELECT DISTINCT scoring_profile_id
        FROM `{project_id}.{dataset_id}.scoring_profiles`
        WHERE COALESCE(active, TRUE)
    ),
    latest_model_run AS (
        SELECT model_run_id
        FROM `{project_id}.{dataset_id}.model_runs`
        WHERE run_type = 'pigskin_rankings'
            AND status = 'complete'
        ORDER BY COALESCE(completed_at, created_at) DESC
        LIMIT 1
    ),
    candidates AS (
        SELECT
            f.season,
            f.week,
            ap.scoring_profile_id,
            lmr.model_run_id,
            TO_JSON_STRING(ARRAY_AGG(STRUCT(
                f.player_name,
                f.position,
                f.team,
                f.current_team,
                f.opponent_team,
                f.fantasy_points_ppr,
                f.skill_player_opportunities,
                f.target_share,
                f.wopr,
                f.touchdowns,
                f.touchdown_dependency_rate,
                f.role_quality_score,
                f.role_fragility_score,
                f.fraud_score,
                f.fraud_label,
                f.fraud_case
            ) ORDER BY f.fraud_score DESC)) AS candidates_json
        FROM `{project_id}.{dataset_id}.analytics_fraud_watch` f
        CROSS JOIN active_profiles ap
        LEFT JOIN latest_model_run lmr ON TRUE
        GROUP BY f.season, f.week, ap.scoring_profile_id, lmr.model_run_id
    )
    SELECT
        TO_HEX(MD5(CONCAT(COALESCE(model_run_id, 'missing-run'), '|', CAST(season AS STRING), '|', CAST(week AS STRING), '|', scoring_profile_id))) AS packet_id,
        model_run_id,
        season,
        week,
        scoring_profile_id,
        candidates_json,
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM candidates
    """


def build_trade_packets_sql(project_id: str, dataset_id: str) -> str:
    return f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.mart_trade_review_packets`
    PARTITION BY DATE(updated_at)
    CLUSTER BY scoring_profile_id, league_type_id, roster_format_id AS
    SELECT
        CAST(NULL AS STRING) AS packet_id,
        CAST(NULL AS STRING) AS model_run_id,
        CAST(NULL AS STRING) AS proposal_id,
        CAST(NULL AS STRING) AS scoring_profile_id,
        CAST(NULL AS STRING) AS league_type_id,
        CAST(NULL AS STRING) AS roster_format_id,
        CAST(NULL AS STRING) AS side_a_assets_json,
        CAST(NULL AS STRING) AS side_b_assets_json,
        CAST(NULL AS STRING) AS analysis_json,
        CAST(NULL AS STRING) AS verdict,
        CAST(NULL AS TIMESTAMP) AS created_at,
        CAST(NULL AS TIMESTAMP) AS updated_at
    FROM UNNEST([1]) AS dummy
    WHERE FALSE
    """


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.match(value):
        raise ValueError(f"Unsafe BigQuery {label}: {value}")


def materialize_packets(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    dry_run: bool = False,
) -> None:
    _validate_identifier(dataset_id, "dataset_id")

    # 1. Projections table
    sql_proj = build_projections_sql(client.project, dataset_id)
    logger.info("Materializing mart_projection_tables...")
    job_proj = client.query(sql_proj, job_config=bigquery.QueryJobConfig(dry_run=dry_run))
    if not dry_run:
        job_proj.result()

    # 2. Fraud packets table
    sql_fraud = build_fraud_packets_sql(client.project, dataset_id)
    logger.info("Materializing mart_fraud_sleeper_packets...")
    job_fraud = client.query(sql_fraud, job_config=bigquery.QueryJobConfig(dry_run=dry_run))
    if not dry_run:
        job_fraud.result()

    # 3. Trade packets table
    sql_trade = build_trade_packets_sql(client.project, dataset_id)
    logger.info("Materializing mart_trade_review_packets...")
    job_trade = client.query(sql_trade, job_config=bigquery.QueryJobConfig(dry_run=dry_run))
    if not dry_run:
        job_trade.result()


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize Phase 2 packets and projections.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    client = bigquery.Client(project=args.project)
    materialize_packets(client, dataset_id=args.dataset, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
