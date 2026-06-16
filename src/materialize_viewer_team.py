"""Materialize the Viewer Team context mart."""

from __future__ import annotations

import argparse
import logging
import os
import re
from datetime import datetime, timezone

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_project


logger = logging.getLogger(__name__)

DEFAULT_DATASET = "fantasy_football_brain"
OUTPUT_TABLE = "mart_viewer_team_context"
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


def build_viewer_team_sql(
    project_id: str,
    dataset_id: str,
    has_snapshots: bool,
    has_roster_players: bool,
    has_lineups: bool,
    has_available: bool,
) -> str:
    _validate_identifier(dataset_id, "dataset_id")

    # 1. Base snapshots CTE
    if has_snapshots:
        base_snapshots_cte = f"""
        base_snapshots AS (
            SELECT DISTINCT
                league_id,
                season,
                week,
                viewer_roster_id,
                viewer_team_name,
                snapshot_at
            FROM `{project_id}.{dataset_id}.sleeper_viewer_team_snapshots`
        )
        """
    elif has_roster_players:
        # Fallback if snapshots table doesn't exist yet
        base_snapshots_cte = f"""
        base_snapshots AS (
            SELECT DISTINCT
                league_id,
                CAST(EXTRACT(YEAR FROM CURRENT_DATE()) AS INT64) AS season,
                week,
                roster_id AS viewer_roster_id,
                CAST(NULL AS STRING) AS viewer_team_name,
                snapshot_at
            FROM `{project_id}.{dataset_id}.sleeper_roster_players`
        )
        """
    else:
        # Fallback empty snapshots if no sleeper data is available
        base_snapshots_cte = """
        base_snapshots AS (
            SELECT
                CAST(NULL AS STRING) AS league_id,
                CAST(NULL AS INT64) AS season,
                CAST(NULL AS INT64) AS week,
                CAST(NULL AS INT64) AS viewer_roster_id,
                CAST(NULL AS STRING) AS viewer_team_name,
                CAST(NULL AS TIMESTAMP) AS snapshot_at
            WHERE FALSE
        )
        """

    # 2. Roster rows JSON subquery
    if has_roster_players:
        lineup_join = f"LEFT JOIN `{project_id}.{dataset_id}.sleeper_lineups` lp ON lp.league_id = rp.league_id AND lp.week = rp.week AND lp.roster_id = rp.roster_id AND lp.sleeper_player_id = rp.sleeper_player_id AND lp.snapshot_at = rp.snapshot_at" if has_lineups else ""
        lineup_points = "lp.points" if has_lineups else "CAST(NULL AS FLOAT64)"
        roster_rows_cte = f"""
        roster_players_enriched AS (
            SELECT
                rp.league_id,
                rp.week,
                rp.roster_id AS viewer_roster_id,
                rp.player_name,
                rp.position,
                rp.team AS sleeper_team,
                rp.status,
                rp.injury_status,
                rp.is_starter,
                rp.is_taxi,
                rp.is_reserve,
                {lineup_points} AS week_points,
                truth.current_team,
                truth.roster_status,
                truth.avg_role_quality_score,
                truth.avg_points_over_role_score,
                truth.avg_role_fragility_score,
                truth.avg_ppr,
                truth.avg_target_share,
                truth.avg_wopr,
                truth.avg_offense_pct,
                truth.sample_verdict
            FROM `{project_id}.{dataset_id}.sleeper_roster_players` rp
            {lineup_join}
            LEFT JOIN (
                SELECT
                    player_name,
                    position,
                    ANY_VALUE(current_team) AS current_team,
                    ANY_VALUE(roster_status) AS roster_status,
                    AVG(role_quality_score) AS avg_role_quality_score,
                    AVG(points_over_role_score) AS avg_points_over_role_score,
                    AVG(role_fragility_score) AS avg_role_fragility_score,
                    AVG(fantasy_points_ppr) AS avg_ppr,
                    AVG(target_share) AS avg_target_share,
                    AVG(wopr) AS avg_wopr,
                    AVG(offense_pct) AS avg_offense_pct,
                    MAX(analytical_verdict) AS sample_verdict
                FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth`
                WHERE season >= 2024
                GROUP BY player_name, position
            ) truth ON LOWER(truth.player_name) = LOWER(rp.player_name) AND truth.position = rp.position
        ),
        roster_json_cte AS (
            SELECT
                league_id,
                week,
                viewer_roster_id,
                TO_JSON_STRING(ARRAY_AGG(STRUCT(
                    player_name, position, sleeper_team, status, injury_status,
                    is_starter, is_taxi, is_reserve, week_points, current_team,
                    roster_status, avg_role_quality_score, avg_points_over_role_score,
                    avg_role_fragility_score, avg_ppr, avg_target_share, avg_wopr,
                    avg_offense_pct, sample_verdict
                ) ORDER BY is_starter DESC, position, player_name)) AS roster_rows_json,
                TO_JSON_STRING(ARRAY_AGG(IF(is_starter = TRUE, STRUCT(
                    player_name, position, sleeper_team, status, injury_status,
                    week_points, avg_ppr, avg_wopr, avg_offense_pct
                ), NULL) IGNORE NULLS ORDER BY position, player_name)) AS lineup_rows_json
            FROM roster_players_enriched
            GROUP BY league_id, week, viewer_roster_id
        )
        """
    else:
        roster_rows_cte = """
        roster_json_cte AS (
            SELECT
                league_id,
                week,
                viewer_roster_id,
                CAST(NULL AS STRING) AS roster_rows_json,
                CAST(NULL AS STRING) AS lineup_rows_json
            FROM base_snapshots
        )
        """

    # 3. Waiver rows JSON subquery
    if has_available:
        waiver_rows_cte = f"""
        waiver_players_enriched AS (
            SELECT
                ap.league_id,
                ap.week,
                ap.player_name,
                ap.position,
                ap.team AS sleeper_team,
                ap.status,
                ap.injury_status,
                ap.depth_chart_position,
                ap.depth_chart_order,
                truth.current_team,
                truth.roster_status,
                truth.avg_role_quality_score,
                truth.avg_points_over_role_score,
                truth.avg_role_fragility_score,
                truth.avg_ppr,
                truth.avg_target_share,
                truth.avg_wopr,
                truth.avg_offense_pct,
                truth.sample_verdict,
                ROW_NUMBER() OVER(
                    PARTITION BY ap.league_id, ap.week, ap.position
                    ORDER BY COALESCE(truth.avg_role_quality_score, 0) DESC, COALESCE(truth.avg_wopr, 0) DESC, COALESCE(truth.avg_ppr, 0) DESC, ap.player_name
                ) AS pos_rn
            FROM `{project_id}.{dataset_id}.sleeper_available_players` ap
            LEFT JOIN (
                SELECT
                    player_name,
                    position,
                    ANY_VALUE(current_team) AS current_team,
                    ANY_VALUE(roster_status) AS roster_status,
                    AVG(role_quality_score) AS avg_role_quality_score,
                    AVG(points_over_role_score) AS avg_points_over_role_score,
                    AVG(role_fragility_score) AS avg_role_fragility_score,
                    AVG(fantasy_points_ppr) AS avg_ppr,
                    AVG(target_share) AS avg_target_share,
                    AVG(wopr) AS avg_wopr,
                    AVG(offense_pct) AS avg_offense_pct,
                    MAX(analytical_verdict) AS sample_verdict
                FROM `{project_id}.{dataset_id}.analytics_player_weekly_truth`
                WHERE season >= 2024
                GROUP BY player_name, position
            ) truth ON LOWER(truth.player_name) = LOWER(ap.player_name) AND truth.position = ap.position
            WHERE ap.position IN ('QB', 'RB', 'WR', 'TE')
        ),
        waiver_json_cte AS (
            SELECT
                league_id,
                week,
                TO_JSON_STRING(ARRAY_AGG(STRUCT(
                    player_name, position, sleeper_team, status, injury_status,
                    depth_chart_position, depth_chart_order, current_team, roster_status,
                    avg_role_quality_score, avg_points_over_role_score, avg_role_fragility_score,
                    avg_ppr, avg_target_share, avg_wopr, avg_offense_pct, sample_verdict
                ) ORDER BY avg_role_quality_score DESC, avg_wopr DESC, avg_ppr DESC LIMIT 45)) AS waiver_rows_json
            FROM waiver_players_enriched
            WHERE pos_rn <= 15
            GROUP BY league_id, week
        )
        """
    else:
        waiver_rows_cte = """
        waiver_json_cte AS (
            SELECT
                league_id,
                week,
                CAST(NULL AS STRING) AS waiver_rows_json
            FROM base_snapshots
        )
        """

    # Build full DDL CREATE OR REPLACE TABLE query
    sql = f"""
    CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{OUTPUT_TABLE}`
    PARTITION BY RANGE_BUCKET(season, GENERATE_ARRAY(2020, 2030, 1))
    CLUSTER BY league_id, viewer_roster_id AS
    WITH
    {base_snapshots_cte},
    {roster_rows_cte},
    {waiver_rows_cte}
    SELECT
        TO_HEX(MD5(CONCAT(s.league_id, '|', CAST(s.season AS STRING), '|', CAST(s.week AS STRING), '|', CAST(s.viewer_roster_id AS STRING)))) AS context_id,
        s.league_id,
        s.season,
        s.week,
        s.viewer_roster_id,
        s.viewer_team_name,
        r.roster_rows_json,
        r.lineup_rows_json,
        w.waiver_rows_json,
        -- pigskin_evidence_json
        TO_JSON_STRING(STRUCT(
            'viewer_team_context' AS type,
            s.viewer_team_name AS team_name,
            ARRAY_LENGTH(JSON_EXTRACT_ARRAY(r.roster_rows_json)) AS roster_size
        )) AS pigskin_evidence_json,
        -- rank_tier_json
        CAST(NULL AS STRING) AS rank_tier_json,
        -- source_freshness_json
        TO_JSON_STRING(STRUCT(
            'mart_viewer_team_context' AS mart,
            s.snapshot_at AS snapshot_at,
            CURRENT_TIMESTAMP() AS refreshed_at
        )) AS source_freshness_json,
        -- missing_data_flags
        TO_JSON_STRING(ARRAY(
            SELECT DISTINCT flag
            FROM UNNEST(ARRAY_CONCAT(
                IF(s.league_id IS NULL, ['missing_league_id'], []),
                IF(r.roster_rows_json IS NULL, ['missing_roster_rows'], []),
                IF(w.waiver_rows_json IS NULL, ['missing_waiver_rows'], [])
            )) AS flag
            WHERE flag IS NOT NULL
        )) AS missing_data_flags,
        CURRENT_TIMESTAMP() AS created_at,
        CURRENT_TIMESTAMP() AS updated_at
    FROM base_snapshots s
    LEFT JOIN roster_json_cte r ON s.league_id = r.league_id AND s.week = r.week AND s.viewer_roster_id = r.viewer_roster_id
    LEFT JOIN waiver_json_cte w ON s.league_id = w.league_id AND s.week = w.week
    """
    return sql


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.match(value):
        raise ValueError(f"Unsafe BigQuery {label}: {value}")


def materialize_viewer_team(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    dry_run: bool = False,
) -> int:
    _validate_identifier(dataset_id, "dataset_id")
    has_snapshots = table_exists(client, dataset_id, "sleeper_viewer_team_snapshots")
    has_roster_players = table_exists(client, dataset_id, "sleeper_roster_players")
    has_lineups = table_exists(client, dataset_id, "sleeper_lineups")
    has_available = table_exists(client, dataset_id, "sleeper_available_players")

    sql = build_viewer_team_sql(
        client.project,
        dataset_id,
        has_snapshots=has_snapshots,
        has_roster_players=has_roster_players,
        has_lineups=has_lineups,
        has_available=has_available,
    )

    job_config = bigquery.QueryJobConfig(dry_run=dry_run)
    job = client.query(sql, job_config=job_config)
    if dry_run:
        logger.info("Dry run bytes processed: %s", job.total_bytes_processed)
        return 0
    job.result()

    # Count output rows
    rows = list(client.query(
        f"SELECT COUNT(*) AS row_count FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`"
    ).result())
    row_count = int(rows[0].row_count) if rows else 0
    logger.info("Materialized %s rows in %s.%s.%s", row_count, client.project, dataset_id, OUTPUT_TABLE)
    return row_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize Viewer Team context.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    client = bigquery.Client(project=args.project)
    materialize_viewer_team(client, dataset_id=args.dataset, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
