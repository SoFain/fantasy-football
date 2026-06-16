"""Materialize the current trade-asset compatibility mart."""

from __future__ import annotations

import argparse
import logging
import os
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any

from google.api_core.exceptions import NotFound
from google.cloud import bigquery

from src.load import get_bigquery_project
from src.model_runs import get_latest_model_run


logger = logging.getLogger(__name__)

DEFAULT_DATASET = "fantasy_football_brain"
OUTPUT_TABLE = "mart_trade_assets_current"
DEFAULT_PROFILE_IDS = ("standard", "half_ppr", "ppr")
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
SOURCE_TABLES = (
    "market_values",
    "dim_players_current",
    "player_identity_bridge",
    "analytics_pigskin_rankings",
    "compat_trade_player_history",
    "analytics_fraud_watch",
    "scoring_profiles",
)
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@dataclass(frozen=True)
class SourceTableStatus:
    exists: bool
    row_count: int | None = None
    modified: datetime | None = None


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def table_status(client: bigquery.Client, dataset_id: str, table_name: str) -> SourceTableStatus:
    try:
        table = client.get_table(f"{client.project}.{dataset_id}.{table_name}")
        return SourceTableStatus(True, table.num_rows, table.modified)
    except NotFound:
        return SourceTableStatus(False)


def inspect_source_status(client: bigquery.Client, dataset_id: str) -> dict[str, SourceTableStatus]:
    return {table_name: table_status(client, dataset_id, table_name) for table_name in SOURCE_TABLES}


def load_active_scoring_profile_ids(
    client: bigquery.Client,
    dataset_id: str,
    requested_profile_ids: list[str] | tuple[str, ...] | None = None,
) -> list[str]:
    if requested_profile_ids:
        return list(dict.fromkeys(requested_profile_ids))
    if not table_status(client, dataset_id, "scoring_profiles").exists:
        return list(DEFAULT_PROFILE_IDS)
    sql = f"""
    SELECT scoring_profile_id
    FROM `{client.project}.{dataset_id}.scoring_profiles`
    WHERE COALESCE(active, TRUE)
    ORDER BY scoring_profile_id
    """
    rows = list(client.query(sql).result())
    profile_ids = [row.scoring_profile_id for row in rows]
    return profile_ids or list(DEFAULT_PROFILE_IDS)


def resolve_model_run_id(
    client: bigquery.Client,
    dataset_id: str,
    *,
    model_run_id: str | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
) -> str | None:
    if model_run_id:
        return model_run_id
    try:
        latest = get_latest_model_run(
            client=client,
            dataset_id=dataset_id,
            run_type="pigskin_rankings",
            scoring_profile_id=scoring_profile_id,
            league_type_id=league_type_id,
            roster_format_id=roster_format_id,
            status="complete",
        )
    except Exception as exc:
        logger.warning("Could not resolve latest Pigskin model run: %s", exc)
        return None
    return latest.get("model_run_id") if latest else None


def build_trade_assets_sql(
    *,
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus] | None = None,
) -> str:
    _validate_identifier(dataset_id, "dataset_id")
    source_status = source_status or {
        table_name: SourceTableStatus(False) for table_name in SOURCE_TABLES
    }
    source_flags = {
        table_name: "TRUE" if source_status.get(table_name, SourceTableStatus(False)).exists else "FALSE"
        for table_name in SOURCE_TABLES
    }
    market_cte = _market_values_cte(project_id, dataset_id, source_status["market_values"])
    identity_cte = _identity_cte(project_id, dataset_id, source_status)
    rankings_cte = _rankings_cte(project_id, dataset_id, source_status["analytics_pigskin_rankings"])
    history_cte = _history_cte(project_id, dataset_id, source_status["compat_trade_player_history"])
    fraud_cte = _fraud_cte(project_id, dataset_id, source_status["analytics_fraud_watch"])

    return f"""
CREATE OR REPLACE TABLE `{project_id}.{dataset_id}.{OUTPUT_TABLE}`
PARTITION BY market_snapshot_date
CLUSTER BY player_id_internal, position, team, scoring_profile_id AS
WITH selected_profiles AS (
    SELECT scoring_profile_id
    FROM UNNEST(@scoring_profile_ids) AS scoring_profile_id
),
run_context AS (
    SELECT
        @as_of_date AS market_snapshot_date,
        @market_snapshot_timestamp AS market_snapshot_timestamp,
        @league_type_id AS league_type_id,
        @roster_format_id AS roster_format_id,
        @model_run_id AS requested_model_run_id,
        CURRENT_TIMESTAMP() AS refreshed_at
),
{market_cte},
{identity_cte},
name_position_counts AS (
    SELECT normalized_name, position, COUNT(*) AS candidate_count
    FROM identity
    GROUP BY normalized_name, position
),
market_with_identity AS (
    SELECT * EXCEPT(rn)
    FROM (
        SELECT
            mv.* EXCEPT(team, age),
            id.player_id_internal,
            COALESCE(id.source_player_key, mv.market_player_id) AS source_player_key,
            id.sleeper_player_id,
            id.gsis_id,
            id.pfr_id,
            COALESCE(id.display_name, mv.market_player_name) AS display_name,
            COALESCE(id.fantasy_positions, mv.position) AS fantasy_positions,
            COALESCE(id.current_team, mv.team) AS team,
            COALESCE(id.age, mv.age) AS age,
            id.rookie_year,
            id.active_status,
            CASE
                WHEN id.player_id_internal IS NULL THEN 'no_identity_match'
                WHEN id.current_team = mv.team THEN 'temporary_name_position_team'
                ELSE 'temporary_unique_name_position'
            END AS identity_match_method,
            ROW_NUMBER() OVER(
                PARTITION BY mv.market_row_id
                ORDER BY
                    CASE
                        WHEN id.current_team = mv.team THEN 1
                        WHEN npc.candidate_count = 1 THEN 2
                        ELSE 3
                    END,
                    id.player_id_internal
            ) AS rn
        FROM market_source mv
        LEFT JOIN name_position_counts npc
            ON mv.normalized_name = npc.normalized_name
            AND mv.position = npc.position
        LEFT JOIN identity id
            ON mv.normalized_name = id.normalized_name
            AND mv.position = id.position
            AND (
                mv.team = id.current_team
                OR npc.candidate_count = 1
            )
    )
    WHERE rn = 1
),
{rankings_cte},
{history_cte},
{fraud_cte},
position_replacement AS (
    SELECT
        position,
        APPROX_QUANTILES(CAST(market_value AS FLOAT64), 100)[OFFSET(40)] AS replacement_value_estimate
    FROM market_source
    WHERE market_value IS NOT NULL
    GROUP BY position
),
base_assets AS (
    SELECT
        mwi.*,
        sp.scoring_profile_id,
        rc.league_type_id,
        rc.roster_format_id,
        rc.market_snapshot_date,
        rc.market_snapshot_timestamp,
        rc.refreshed_at
    FROM market_with_identity mwi
    CROSS JOIN selected_profiles sp
    CROSS JOIN run_context rc
),
enriched AS (
    SELECT
        ba.*,
        r.model_run_id AS ranking_model_run_id,
        r.ranking_version,
        r.pigskin_rank_position,
        r.pigskin_tier,
        r.pigskin_projection,
        r.pigskin_confidence,
        r.pigskin_risk_score,
        r.pigskin_breakout_score,
        CASE
            WHEN r.player_id IS NOT NULL AND ba.gsis_id IS NOT NULL AND r.player_id = ba.gsis_id THEN 'gsis'
            WHEN r.sleeper_player_id IS NOT NULL AND ba.sleeper_player_id IS NOT NULL AND r.sleeper_player_id = ba.sleeper_player_id THEN 'sleeper'
            WHEN r.normalized_name = ba.normalized_name AND r.position = ba.position THEN 'temporary_name_position'
            ELSE NULL
        END AS ranking_match_method,
        h.recent_fantasy_points_per_game,
        h.recent_usage_summary_json,
        h.recent_trend_label,
        f.pigskin_fraud_risk_score,
        pr.replacement_value_estimate,
        ROW_NUMBER() OVER(
            PARTITION BY COALESCE(ba.player_id_internal, ba.market_player_id), ba.scoring_profile_id, ba.league_type_id, ba.roster_format_id, ba.market_snapshot_date
            ORDER BY
                CASE
                    WHEN r.player_id IS NOT NULL AND ba.gsis_id IS NOT NULL AND r.player_id = ba.gsis_id THEN 1
                    WHEN r.sleeper_player_id IS NOT NULL AND ba.sleeper_player_id IS NOT NULL AND r.sleeper_player_id = ba.sleeper_player_id THEN 2
                    WHEN r.normalized_name = ba.normalized_name AND r.position = ba.position THEN 3
                    ELSE 4
                END,
                r.pigskin_rank_position
        ) AS rn
    FROM base_assets ba
    LEFT JOIN rankings r
        ON (
            ba.gsis_id IS NOT NULL
            AND r.player_id = ba.gsis_id
            AND r.position = ba.position
        )
        OR (
            ba.sleeper_player_id IS NOT NULL
            AND r.sleeper_player_id = ba.sleeper_player_id
            AND r.position = ba.position
        )
        OR (
            ba.normalized_name = r.normalized_name
            AND ba.position = r.position
        )
    LEFT JOIN history h
        ON h.scoring_profile_id = ba.scoring_profile_id
        AND (
            (ba.player_id_internal IS NOT NULL AND h.player_id_internal = ba.player_id_internal)
            OR (ba.source_player_key IS NOT NULL AND h.source_player_key = ba.source_player_key)
            OR (ba.normalized_name = h.normalized_name AND ba.position = h.position)
        )
    LEFT JOIN fraud f
        ON ba.normalized_name = f.normalized_name
        AND ba.position = f.position
    LEFT JOIN position_replacement pr
        ON ba.position = pr.position
)
SELECT
    player_id_internal,
    source_player_key,
    sleeper_player_id,
    gsis_id,
    pfr_id,
    display_name,
    normalized_name,
    position,
    fantasy_positions,
    team,
    age,
    rookie_year,
    active_status,
    market_source,
    market_player_id,
    market_player_name,
    market_value,
    market_value_raw,
    market_value_rank_overall,
    market_value_rank_position,
    market_tier,
    market_snapshot_date,
    market_snapshot_timestamp,
    roster_format_id AS market_format_label,
    scoring_profile_id AS market_scoring_label,
    league_type_id AS market_league_type_label,
    scoring_profile_id,
    league_type_id,
    roster_format_id,
    COALESCE(ranking_model_run_id, (SELECT requested_model_run_id FROM run_context)) AS model_run_id,
    ranking_version,
    CAST(NULL AS INT64) AS pigskin_rank_overall,
    pigskin_rank_position,
    pigskin_tier,
    pigskin_projection,
    pigskin_confidence,
    pigskin_risk_score,
    pigskin_breakout_score,
    pigskin_fraud_risk_score,
    recent_fantasy_points_per_game,
    recent_usage_summary_json,
    recent_trend_label,
    SAFE_DIVIDE(CAST(market_value AS FLOAT64) - replacement_value_estimate, NULLIF(replacement_value_estimate, 0)) AS position_scarcity_score,
    replacement_value_estimate,
    IF(league_type_id = 'dynasty', CAST(market_value AS FLOAT64), NULL) AS dynasty_value_placeholder,
    IF(league_type_id = 'redraft', COALESCE(redraft_value, CAST(market_value AS FLOAT64)), redraft_value) AS redraft_value_placeholder,
    CAST(market_value AS FLOAT64)
        * IF(pigskin_rank_position IS NULL, 0.95, 1.0)
        * IF(active_status IS NOT NULL AND LOWER(active_status) NOT IN ('active', 'act'), 0.90, 1.0)
        * IF(age IS NOT NULL AND position = 'RB' AND age >= 29, 0.88, 1.0)
        AS risk_adjusted_trade_value,
    TO_JSON_STRING(STRUCT(
        market_source AS market_source,
        market_value AS market_value,
        market_value_rank_overall AS market_value_rank_overall,
        market_value_rank_position AS market_value_rank_position,
        market_tier AS market_tier,
        pigskin_rank_position AS pigskin_rank_position,
        pigskin_tier AS pigskin_tier,
        recent_fantasy_points_per_game AS recent_fantasy_points_per_game,
        SAFE_DIVIDE(CAST(market_value AS FLOAT64) - replacement_value_estimate, NULLIF(replacement_value_estimate, 0)) AS position_scarcity_score
    )) AS trade_asset_summary_json,
    TO_JSON_STRING(STRUCT(
        'mart_trade_assets_current' AS mart,
        'market_values' AS market_source_table,
        'dim_players_current' AS identity_dimension,
        'player_identity_bridge' AS identity_bridge,
        'analytics_pigskin_rankings' AS ranking_source,
        'compat_trade_player_history' AS recent_history_source,
        'analytics_fraud_watch' AS fraud_source,
        {source_flags["market_values"]} AS market_values_available,
        {source_flags["dim_players_current"]} AS dim_players_current_available,
        {source_flags["player_identity_bridge"]} AS player_identity_bridge_available,
        {source_flags["analytics_pigskin_rankings"]} AS analytics_pigskin_rankings_available,
        {source_flags["compat_trade_player_history"]} AS compat_trade_player_history_available,
        {source_flags["analytics_fraud_watch"]} AS analytics_fraud_watch_available,
        market_snapshot_timestamp AS market_snapshot_timestamp,
        market_snapshot_date AS market_snapshot_date,
        refreshed_at AS refreshed_at
    )) AS source_freshness_json,
    TO_JSON_STRING(ARRAY(
        SELECT DISTINCT flag
        FROM UNNEST(ARRAY_CONCAT(
            IF(player_id_internal IS NULL, ['missing_player_id_internal'], []),
            IF(source_player_key IS NULL, ['missing_source_player_key'], []),
            IF(sleeper_player_id IS NULL, ['missing_sleeper_player_id'], []),
            IF(gsis_id IS NULL, ['missing_gsis_id'], []),
            IF(age IS NULL, ['missing_age'], []),
            IF(market_value IS NULL, ['missing_market_value'], []),
            IF(COALESCE(identity_match_method LIKE 'temporary_%', FALSE), ['temporary_name_join_identity'], []),
            IF(ranking_version IS NULL, ['missing_pigskin_ranking_context'], []),
            IF(COALESCE(ranking_match_method = 'temporary_name_position', FALSE), ['temporary_name_join_ranking'], []),
            IF(recent_fantasy_points_per_game IS NULL, ['missing_recent_trade_history'], []),
            IF(pigskin_fraud_risk_score IS NULL, ['missing_fraud_context'], []),
            IF({source_flags["market_values"]}, [], ['missing_market_values_source']),
            IF({source_flags["analytics_pigskin_rankings"]}, [], ['missing_rankings_source']),
            IF({source_flags["compat_trade_player_history"]}, [], ['missing_trade_history_source'])
        )) AS flag
        WHERE flag IS NOT NULL
        ORDER BY flag
    )) AS missing_data_flags,
    refreshed_at AS created_at,
    refreshed_at AS updated_at
FROM enriched
WHERE rn = 1
"""


def materialize_trade_assets(
    client: bigquery.Client,
    *,
    dataset_id: str = DEFAULT_DATASET,
    as_of_date: date | None = None,
    scoring_profile_ids: list[str] | tuple[str, ...] | None = None,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    dry_run: bool = False,
) -> int:
    _validate_identifier(dataset_id, "dataset_id")
    profile_ids = load_active_scoring_profile_ids(client, dataset_id, scoring_profile_ids)
    resolved_model_run_id = resolve_model_run_id(
        client,
        dataset_id,
        model_run_id=model_run_id,
        scoring_profile_id=profile_ids[0] if len(profile_ids) == 1 else None,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
    )
    source_status = inspect_source_status(client, dataset_id)
    market_status = source_status["market_values"]
    if not market_status.exists:
        logger.warning("market_values source table is missing. Materializing an empty trade-asset mart.")
    elif not market_status.row_count:
        logger.warning("market_values source table is empty. Materializing an empty trade-asset mart.")

    sql = build_trade_assets_sql(
        project_id=client.project,
        dataset_id=dataset_id,
        source_status=source_status,
    )
    market_snapshot_timestamp = market_status.modified or datetime.now(timezone.utc)
    market_snapshot_date = as_of_date or market_snapshot_timestamp.date()
    job_config = bigquery.QueryJobConfig(
        dry_run=dry_run,
        use_query_cache=False,
        query_parameters=[
            bigquery.ArrayQueryParameter("scoring_profile_ids", "STRING", profile_ids),
            bigquery.ScalarQueryParameter("as_of_date", "DATE", market_snapshot_date),
            bigquery.ScalarQueryParameter("market_snapshot_timestamp", "TIMESTAMP", market_snapshot_timestamp),
            bigquery.ScalarQueryParameter("league_type_id", "STRING", league_type_id),
            bigquery.ScalarQueryParameter("roster_format_id", "STRING", roster_format_id),
            bigquery.ScalarQueryParameter("model_run_id", "STRING", resolved_model_run_id),
        ],
    )
    logger.info(
        "Materializing %s from source tables %s with market_snapshot_timestamp=%s",
        OUTPUT_TABLE,
        ", ".join(sorted(name for name, status in source_status.items() if status.exists)),
        market_snapshot_timestamp.isoformat(),
    )
    job = client.query(sql, job_config=job_config)
    if dry_run:
        logger.info("Dry run bytes processed: %s", job.total_bytes_processed)
        return 0
    job.result()
    row_count = _count_output_rows(client, dataset_id)
    missing_identity_count = _count_missing_identity_rows(client, dataset_id)
    logger.info(
        "Materialized %s rows in %s.%s.%s; missing identity rows=%s",
        row_count,
        client.project,
        dataset_id,
        OUTPUT_TABLE,
        missing_identity_count,
    )
    return row_count


def _market_values_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_market_values_cte()
    return f"""
market_source AS (
    SELECT
        ROW_NUMBER() OVER(
            ORDER BY COALESCE(overall_rank, 999999), player_display_name, position, team
        ) AS market_row_id,
        'fantasycalc' AS market_source,
        CONCAT(
            'fantasycalc:',
            {_normalized_name_sql("player_display_name")},
            ':',
            COALESCE(CAST(position AS STRING), 'UNK'),
            ':',
            COALESCE(CAST(team AS STRING), 'UNK')
        ) AS market_player_id,
        CAST(player_display_name AS STRING) AS market_player_name,
        {_normalized_name_sql("player_display_name")} AS normalized_name,
        CAST(position AS STRING) AS position,
        CAST(team AS STRING) AS team,
        SAFE_CAST(market_value AS INT64) AS market_value,
        SAFE_CAST(market_value AS FLOAT64) AS market_value_raw,
        SAFE_CAST(overall_rank AS INT64) AS market_value_rank_overall,
        SAFE_CAST(position_rank AS INT64) AS market_value_rank_position,
        CAST(tier AS STRING) AS market_tier,
        SAFE_CAST(redraft_value AS FLOAT64) AS redraft_value,
        SAFE_CAST(age AS FLOAT64) AS age
    FROM `{project_id}.{dataset_id}.market_values`
    WHERE player_display_name IS NOT NULL
)"""


def _empty_market_values_cte() -> str:
    return """
market_source AS (
    SELECT
        CAST(NULL AS INT64) AS market_row_id,
        CAST(NULL AS STRING) AS market_source,
        CAST(NULL AS STRING) AS market_player_id,
        CAST(NULL AS STRING) AS market_player_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS team,
        CAST(NULL AS INT64) AS market_value,
        CAST(NULL AS FLOAT64) AS market_value_raw,
        CAST(NULL AS INT64) AS market_value_rank_overall,
        CAST(NULL AS INT64) AS market_value_rank_position,
        CAST(NULL AS STRING) AS market_tier,
        CAST(NULL AS FLOAT64) AS redraft_value,
        CAST(NULL AS FLOAT64) AS age
    WHERE FALSE
)"""


def _identity_cte(
    project_id: str,
    dataset_id: str,
    source_status: dict[str, SourceTableStatus],
) -> str:
    dim_exists = source_status["dim_players_current"].exists
    bridge_exists = source_status["player_identity_bridge"].exists
    if dim_exists and bridge_exists:
        return f"""
identity AS (
    SELECT
        COALESCE(d.player_id_internal, b.player_id_internal) AS player_id_internal,
        COALESCE(d.gsis_id, b.gsis_id) AS gsis_id,
        COALESCE(d.sleeper_player_id, b.sleeper_player_id) AS sleeper_player_id,
        COALESCE(d.pfr_id, b.pfr_id) AS pfr_id,
        COALESCE(d.display_name, b.display_name) AS display_name,
        COALESCE(d.normalized_name, b.normalized_name) AS normalized_name,
        COALESCE(d.position, b.position) AS position,
        COALESCE(d.fantasy_positions, b.fantasy_positions) AS fantasy_positions,
        COALESCE(d.current_team, b.current_team) AS current_team,
        COALESCE(d.active_status, b.active_status) AS active_status,
        COALESCE(d.rookie_year, b.rookie_year) AS rookie_year,
        COALESCE(d.age, SAFE_DIVIDE(DATE_DIFF(CURRENT_DATE(), d.birth_date, DAY), 365.25)) AS age,
        COALESCE(d.gsis_id, b.gsis_id, d.sleeper_player_id, b.sleeper_player_id, d.pfr_id, b.pfr_id, d.player_id_internal, b.player_id_internal) AS source_player_key
    FROM `{project_id}.{dataset_id}.dim_players_current` d
    FULL OUTER JOIN `{project_id}.{dataset_id}.player_identity_bridge` b
        ON d.player_id_internal = b.player_id_internal
    WHERE COALESCE(d.position, b.position) IN ('QB', 'RB', 'WR', 'TE')
)"""
    if dim_exists:
        return f"""
identity AS (
    SELECT
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        pfr_id,
        display_name,
        normalized_name,
        position,
        fantasy_positions,
        current_team,
        active_status,
        rookie_year,
        COALESCE(age, SAFE_DIVIDE(DATE_DIFF(CURRENT_DATE(), birth_date, DAY), 365.25)) AS age,
        COALESCE(gsis_id, sleeper_player_id, pfr_id, player_id_internal) AS source_player_key
    FROM `{project_id}.{dataset_id}.dim_players_current`
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
)"""
    if bridge_exists:
        return f"""
identity AS (
    SELECT
        player_id_internal,
        gsis_id,
        sleeper_player_id,
        pfr_id,
        display_name,
        normalized_name,
        position,
        fantasy_positions,
        current_team,
        active_status,
        rookie_year,
        CAST(NULL AS FLOAT64) AS age,
        COALESCE(gsis_id, sleeper_player_id, pfr_id, player_id_internal) AS source_player_key
    FROM `{project_id}.{dataset_id}.player_identity_bridge`
    WHERE position IN ('QB', 'RB', 'WR', 'TE')
)"""
    return _empty_identity_cte()


def _empty_identity_cte() -> str:
    return """
identity AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS gsis_id,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS pfr_id,
        CAST(NULL AS STRING) AS display_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS fantasy_positions,
        CAST(NULL AS STRING) AS current_team,
        CAST(NULL AS STRING) AS active_status,
        CAST(NULL AS INT64) AS rookie_year,
        CAST(NULL AS FLOAT64) AS age,
        CAST(NULL AS STRING) AS source_player_key
    WHERE FALSE
)"""


def _rankings_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_rankings_cte()
    return f"""
rankings AS (
    SELECT * EXCEPT(rn)
    FROM (
        SELECT
            player_id,
            sleeper_player_id,
            player_name,
            {_normalized_name_sql("player_name")} AS normalized_name,
            position,
            current_team,
            model_run_id,
            ranking_version,
            rank AS pigskin_rank_position,
            tier AS pigskin_tier,
            ranking_score AS pigskin_projection,
            confidence_score AS pigskin_confidence,
            avg_role_fragility AS pigskin_risk_score,
            ranking_score AS pigskin_breakout_score,
            generated_at,
            ROW_NUMBER() OVER(
                PARTITION BY COALESCE(player_id, sleeper_player_id, {_normalized_name_sql("player_name")}), position
                ORDER BY generated_at DESC, rank ASC
            ) AS rn
        FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings`
        WHERE COALESCE(is_active, TRUE)
            AND (@model_run_id IS NULL OR model_run_id = @model_run_id)
    )
    WHERE rn = 1
)"""


def _empty_rankings_cte() -> str:
    return """
rankings AS (
    SELECT
        CAST(NULL AS STRING) AS player_id,
        CAST(NULL AS STRING) AS sleeper_player_id,
        CAST(NULL AS STRING) AS player_name,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS current_team,
        CAST(NULL AS STRING) AS model_run_id,
        CAST(NULL AS STRING) AS ranking_version,
        CAST(NULL AS INT64) AS pigskin_rank_position,
        CAST(NULL AS STRING) AS pigskin_tier,
        CAST(NULL AS FLOAT64) AS pigskin_projection,
        CAST(NULL AS FLOAT64) AS pigskin_confidence,
        CAST(NULL AS FLOAT64) AS pigskin_risk_score,
        CAST(NULL AS FLOAT64) AS pigskin_breakout_score,
        CAST(NULL AS TIMESTAMP) AS generated_at
    WHERE FALSE
)"""


def _history_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_history_cte()
    return f"""
history AS (
    SELECT
        player_id_internal,
        source_player_key,
        normalized_name,
        position,
        scoring_profile_id,
        AVG(total_fantasy_points) AS recent_fantasy_points_per_game,
        TO_JSON_STRING(STRUCT(
            AVG(targets) AS avg_targets,
            AVG(carries) AS avg_carries,
            AVG(receptions) AS avg_receptions,
            AVG(target_share) AS avg_target_share,
            AVG(rush_share) AS avg_rush_share,
            AVG(high_value_touches) AS avg_high_value_touches
        )) AS recent_usage_summary_json,
        CASE
            WHEN AVG(total_fantasy_points) >= 18 THEN 'recent_ceiling'
            WHEN AVG(total_fantasy_points) >= 12 THEN 'recent_stable'
            WHEN AVG(total_fantasy_points) IS NULL THEN 'recent_unknown'
            ELSE 'recent_fragile'
        END AS recent_trend_label
    FROM `{project_id}.{dataset_id}.compat_trade_player_history`
    WHERE recency_order <= 5
    GROUP BY player_id_internal, source_player_key, normalized_name, position, scoring_profile_id
)"""


def _empty_history_cte() -> str:
    return """
history AS (
    SELECT
        CAST(NULL AS STRING) AS player_id_internal,
        CAST(NULL AS STRING) AS source_player_key,
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS STRING) AS scoring_profile_id,
        CAST(NULL AS FLOAT64) AS recent_fantasy_points_per_game,
        CAST(NULL AS STRING) AS recent_usage_summary_json,
        CAST(NULL AS STRING) AS recent_trend_label
    WHERE FALSE
)"""


def _fraud_cte(project_id: str, dataset_id: str, status: SourceTableStatus) -> str:
    if not status.exists:
        return _empty_fraud_cte()
    return f"""
fraud AS (
    SELECT
        {_normalized_name_sql("player_name")} AS normalized_name,
        position,
        MAX(fraud_score) AS pigskin_fraud_risk_score
    FROM `{project_id}.{dataset_id}.analytics_fraud_watch`
    GROUP BY normalized_name, position
)"""


def _empty_fraud_cte() -> str:
    return """
fraud AS (
    SELECT
        CAST(NULL AS STRING) AS normalized_name,
        CAST(NULL AS STRING) AS position,
        CAST(NULL AS FLOAT64) AS pigskin_fraud_risk_score
    WHERE FALSE
)"""


def _count_output_rows(client: bigquery.Client, dataset_id: str) -> int:
    rows = list(client.query(
        f"SELECT COUNT(*) AS row_count FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`"
    ).result())
    return int(rows[0].row_count) if rows else 0


def _count_missing_identity_rows(client: bigquery.Client, dataset_id: str) -> int:
    rows = list(client.query(
        f"""
        SELECT COUNT(*) AS row_count
        FROM `{client.project}.{dataset_id}.{OUTPUT_TABLE}`
        WHERE player_id_internal IS NULL
        """
    ).result())
    return int(rows[0].row_count) if rows else 0


def _normalized_name_sql(expr: str) -> str:
    return (
        "REGEXP_REPLACE("
        f"REGEXP_REPLACE(LOWER(COALESCE({expr}, '')), r'\\s+(jr|sr|ii|iii|iv|v)\\.?$', ''), "
        "r'[^a-z0-9]+', '')"
    )


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.match(value):
        raise ValueError(f"Unsafe BigQuery {label}: {value}")


def _parse_profile_ids(values: list[str] | None) -> list[str] | None:
    if not values:
        return None
    profile_ids = []
    for value in values:
        profile_ids.extend(item.strip() for item in value.split(",") if item.strip())
    return profile_ids or None


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Materialize current trade asset mart.")
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--as-of-date")
    parser.add_argument("--scoring-profile-id", action="append")
    parser.add_argument("--league-type-id", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format-id", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--model-run-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    client = bigquery.Client(project=args.project)
    row_count = materialize_trade_assets(
        client,
        dataset_id=args.dataset,
        as_of_date=_parse_date(args.as_of_date),
        scoring_profile_ids=_parse_profile_ids(args.scoring_profile_id),
        league_type_id=args.league_type_id,
        roster_format_id=args.roster_format_id,
        model_run_id=args.model_run_id,
        dry_run=args.dry_run,
    )
    print(f"{OUTPUT_TABLE} rows materialized: {row_count}")


if __name__ == "__main__":
    main()
