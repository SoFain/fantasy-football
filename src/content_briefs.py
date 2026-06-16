"""Deterministic show content brief builders for AI vs. Meatbags.

This module assembles compact, source-aware briefs from curated packet and
output tables. It does not call LLMs, query source tables, or create UI
runtime behavior.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_SCORING_PROFILE = "ppr"
DEFAULT_LEAGUE_TYPE = "redraft"
DEFAULT_ROSTER_FORMAT = "one_qb"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("CONTENT_BRIEFS_MAX_BYTES_BILLED", "1000000000"))
MAX_BRIEF_TEXT_CHARS = 12000
MAX_TOKEN_ESTIMATE = 3500
MAX_ITEM_CAP = 20
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

RUNS_TABLE = "content_brief_runs"
BRIEFS_TABLE = "content_briefs"
ITEMS_TABLE = "content_brief_items"

SUPPORTED_BRIEF_TYPES = {
    "fraud_watch_show",
    "sleeper_breakout_show",
    "trade_review_show",
    "rankings_debate_show",
    "meatbag_accountability_show",
    "weekly_streamers_show",
    "dynasty_value_show",
    "full_weekly_show_prep",
}
ITEM_CAPS = {
    "fraud_watch_show": 5,
    "sleeper_breakout_show": 5,
    "trade_review_show": 3,
    "rankings_debate_show": 8,
    "meatbag_accountability_show": 6,
    "weekly_streamers_show": 8,
    "dynasty_value_show": 8,
    "full_weekly_show_prep": 14,
}
BRIEF_OBJECTIVES = {
    "fraud_watch_show": "Expose fantasy point totals that outran role quality and repeatability.",
    "sleeper_breakout_show": "Identify underpriced players with usage, role, or market signals moving up.",
    "trade_review_show": "Turn trade packet evidence into concise deal verdicts and rebuttals.",
    "rankings_debate_show": "Surface ranking calls that deserve debate, defense, or correction.",
    "meatbag_accountability_show": "Hold analyst claims against actual outcomes and model baselines.",
    "weekly_streamers_show": "Find short-term usable players without pretending they are season-long saviors.",
    "dynasty_value_show": "Find longer-horizon value gaps using dynasty projection context.",
    "full_weekly_show_prep": "Assemble a compact weekly show order from the strongest available segments.",
}
BRIEF_TITLES = {
    "fraud_watch_show": "Fraud Watch Show Brief",
    "sleeper_breakout_show": "Sleeper Breakout Show Brief",
    "trade_review_show": "Trade Review Show Brief",
    "rankings_debate_show": "Rankings Debate Show Brief",
    "meatbag_accountability_show": "Meatbag Accountability Show Brief",
    "weekly_streamers_show": "Weekly Streamers Show Brief",
    "dynasty_value_show": "Dynasty Value Show Brief",
    "full_weekly_show_prep": "Full Weekly Show Prep Brief",
}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def create_content_brief_run(
    *,
    brief_type: str,
    season: int,
    week: int | None = None,
    model_run_id: str | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    status: str = "created",
    created_by: str = "content_briefs",
    notes: str | None = None,
    content_brief_run_id: str | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Create one content-brief run row."""

    brief_type = _validate_brief_type(brief_type)
    content_brief_run_id = content_brief_run_id or _new_run_id(brief_type, season, week)
    row = {
        "content_brief_run_id": content_brief_run_id,
        "brief_type": brief_type,
        "model_run_id": model_run_id,
        "season": int(season),
        "week": _int_or_none(week),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "status": status,
        "created_by": created_by,
        "created_at": _utc_timestamp(),
        "completed_at": None,
        "error_message": None,
        "notes": notes,
    }
    if dry_run:
        return row
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    _insert_rows(client, dataset_id, RUNS_TABLE, [row])
    return row


def build_fraud_watch_brief(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    packets: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    rows = packets if packets is not None else _load_fraud_packets(client, dataset_id, season, week, scoring_profile_id, league_type_id, roster_format_id, model_run_id, _cap("fraud_watch_show", limit))
    return _build_brief(
        brief_type="fraud_watch_show",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_fraud_item,
        limit=limit,
    )


def build_sleeper_breakout_brief(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    packets: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    rows = packets if packets is not None else _load_breakout_packets(client, dataset_id, season, week, scoring_profile_id, league_type_id, roster_format_id, model_run_id, _cap("sleeper_breakout_show", limit))
    return _build_brief(
        brief_type="sleeper_breakout_show",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_breakout_item,
        limit=limit,
    )


def build_trade_review_brief(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    packets: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    rows = packets if packets is not None else _load_trade_packets(client, dataset_id, scoring_profile_id, league_type_id, roster_format_id, model_run_id, _cap("trade_review_show", limit))
    return _build_brief(
        brief_type="trade_review_show",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_trade_item,
        limit=limit,
    )


def build_rankings_debate_brief(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    ranking_rows: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    rows = ranking_rows if ranking_rows is not None else _load_ranking_rows(client, dataset_id, "ros", season, week, scoring_profile_id, league_type_id, roster_format_id, model_run_id, _cap("rankings_debate_show", limit))
    return _build_brief(
        brief_type="rankings_debate_show",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_ranking_item,
        limit=limit,
    )


def build_meatbag_accountability_brief(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    scorecard_rows: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    rows = scorecard_rows if scorecard_rows is not None else _load_scorecards(client, dataset_id, season, week, _cap("meatbag_accountability_show", limit))
    return _build_brief(
        brief_type="meatbag_accountability_show",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_accountability_item,
        limit=limit,
    )


def build_weekly_streamers_brief(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    ranking_rows: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    rows = ranking_rows if ranking_rows is not None else _load_ranking_rows(client, dataset_id, "weekly", season, week, scoring_profile_id, league_type_id, roster_format_id, model_run_id, _cap("weekly_streamers_show", limit))
    return _build_brief(
        brief_type="weekly_streamers_show",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_streamer_item,
        limit=limit,
    )


def build_dynasty_value_brief(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = "dynasty",
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    ranking_rows: list[dict[str, Any]] | None = None,
    limit: int | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    rows = ranking_rows if ranking_rows is not None else _load_ranking_rows(client, dataset_id, "dynasty", season, week, scoring_profile_id, league_type_id, roster_format_id, model_run_id, _cap("dynasty_value_show", limit))
    return _build_brief(
        brief_type="dynasty_value_show",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_dynasty_item,
        limit=limit,
    )


def build_full_weekly_show_prep(
    *,
    season: int,
    week: int | None = None,
    scoring_profile_id: str = DEFAULT_SCORING_PROFILE,
    league_type_id: str = DEFAULT_LEAGUE_TYPE,
    roster_format_id: str = DEFAULT_ROSTER_FORMAT,
    model_run_id: str | None = None,
    source_briefs: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    if source_briefs is None:
        source_briefs = [
            build_fraud_watch_brief(season=season, week=week, scoring_profile_id=scoring_profile_id, league_type_id=league_type_id, roster_format_id=roster_format_id, model_run_id=model_run_id, limit=3, client=client, dataset_id=dataset_id),
            build_sleeper_breakout_brief(season=season, week=week, scoring_profile_id=scoring_profile_id, league_type_id=league_type_id, roster_format_id=roster_format_id, model_run_id=model_run_id, limit=3, client=client, dataset_id=dataset_id),
            build_meatbag_accountability_brief(season=season, week=week, scoring_profile_id=scoring_profile_id, league_type_id=league_type_id, roster_format_id=roster_format_id, model_run_id=model_run_id, limit=3, client=client, dataset_id=dataset_id),
            build_rankings_debate_brief(season=season, week=week, scoring_profile_id=scoring_profile_id, league_type_id=league_type_id, roster_format_id=roster_format_id, model_run_id=model_run_id, limit=5, client=client, dataset_id=dataset_id),
        ]
    rows = []
    for brief in source_briefs:
        for item in brief.get("items", []):
            rows.append(dict(item, segment_title=brief["brief"]["title"], source_brief_type=brief["brief"]["brief_type"]))
    return _build_brief(
        brief_type="full_weekly_show_prep",
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        model_run_id=model_run_id,
        source_rows=rows,
        item_builder=_full_prep_item,
        limit=ITEM_CAPS["full_weekly_show_prep"],
    )


def save_content_brief(
    brief_bundle: dict[str, Any],
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Persist a content brief run, brief row, and item rows."""

    if dry_run:
        return {"dry_run": True, "brief_id": brief_bundle["brief"]["content_brief_id"], "item_count": len(brief_bundle["items"])}
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    run = dict(brief_bundle["run"], status="completed", completed_at=_utc_timestamp())
    _insert_rows(client, dataset_id, RUNS_TABLE, [run])
    _insert_rows(client, dataset_id, BRIEFS_TABLE, [brief_bundle["brief"]])
    _insert_rows(client, dataset_id, ITEMS_TABLE, brief_bundle["items"])
    return {"dry_run": False, "brief_id": brief_bundle["brief"]["content_brief_id"], "item_count": len(brief_bundle["items"])}


def get_content_brief(content_brief_id: str, *, client: Any | None = None, dataset_id: str | None = None) -> dict[str, Any] | None:
    """Fetch one content brief and its item rows."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    brief_sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, BRIEFS_TABLE)}`
    WHERE content_brief_id = @content_brief_id
    ORDER BY updated_at DESC
    LIMIT 1
    """
    item_sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, ITEMS_TABLE)}`
    WHERE content_brief_id = @content_brief_id
    ORDER BY item_order
    """
    job_config = _job_config([("content_brief_id", "STRING", content_brief_id)])
    rows = _query_rows(client, brief_sql, job_config)
    if not rows:
        return None
    brief = rows[0]
    brief["brief"] = _json_object(brief.get("brief_json"))
    brief["items"] = _query_rows(client, item_sql, job_config)
    return brief


def list_content_briefs(
    *,
    brief_type: str | None = None,
    season: int | None = None,
    week: int | None = None,
    review_status: str | None = None,
    limit: int = 50,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """List recent content briefs with bounded filters."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["1 = 1"]
    params: list[tuple[str, str, Any]] = [("limit", "INT64", max(1, min(int(limit), 200)))]
    if brief_type:
        where.append("brief_type = @brief_type")
        params.append(("brief_type", "STRING", _validate_brief_type(brief_type)))
    if season is not None:
        where.append("season = @season")
        params.append(("season", "INT64", int(season)))
    if week is not None:
        where.append("week = @week")
        params.append(("week", "INT64", int(week)))
    if review_status:
        where.append("review_status = @review_status")
        params.append(("review_status", "STRING", str(review_status).lower()))
    sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, BRIEFS_TABLE)}`
    WHERE {" AND ".join(where)}
    ORDER BY updated_at DESC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def _build_brief(
    *,
    brief_type: str,
    season: int,
    week: int | None,
    scoring_profile_id: str,
    league_type_id: str,
    roster_format_id: str,
    model_run_id: str | None,
    source_rows: list[dict[str, Any]],
    item_builder: Callable[[dict[str, Any], int, str], dict[str, Any]],
    limit: int | None,
) -> dict[str, Any]:
    brief_type = _validate_brief_type(brief_type)
    cap = _cap(brief_type, limit)
    content_brief_run_id = _new_run_id(brief_type, season, week)
    content_brief_id = _new_brief_id(brief_type, season, week)
    now = _utc_timestamp()
    run = create_content_brief_run(
        brief_type=brief_type,
        season=season,
        week=week,
        model_run_id=model_run_id,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        status="completed",
        content_brief_run_id=content_brief_run_id,
        dry_run=True,
    )
    items = [
        item_builder(row, index + 1, content_brief_id)
        for index, row in enumerate((source_rows or [])[:cap])
    ]
    if not items:
        items = [_empty_item(content_brief_id, brief_type, now)]
    source_freshness = _merged_source_freshness(items)
    missing_flags = sorted(set(_merged_missing_flags(items) + ([] if source_rows else ["missing_source_rows"])))
    brief_json = _brief_json(
        brief_type=brief_type,
        title=BRIEF_TITLES[brief_type],
        objective=BRIEF_OBJECTIVES[brief_type],
        items=items,
        source_freshness=source_freshness,
        missing_flags=missing_flags,
    )
    brief_text = _bounded_text(_brief_text(brief_json))
    token_estimate = min(MAX_TOKEN_ESTIMATE, _estimate_tokens(brief_text))
    brief_row = {
        "content_brief_id": content_brief_id,
        "content_brief_run_id": content_brief_run_id,
        "brief_type": brief_type,
        "title": BRIEF_TITLES[brief_type],
        "season": int(season),
        "week": _int_or_none(week),
        "scoring_profile_id": scoring_profile_id,
        "league_type_id": league_type_id,
        "roster_format_id": roster_format_id,
        "model_run_id": model_run_id,
        "brief_json": _json_dumps(brief_json),
        "brief_text": brief_text,
        "token_estimate": token_estimate,
        "source_freshness_json": _json_dumps(source_freshness),
        "missing_data_flags": _json_dumps(missing_flags),
        "review_status": "draft",
        "created_at": now,
        "updated_at": now,
    }
    return {"run": run, "brief": brief_row, "items": items, "brief_json": brief_json}


def _fraud_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    name = _name(row)
    return _item_row(
        content_brief_id=content_brief_id,
        item_type="player",
        item_order=order,
        player_id_internal=row.get("player_id_internal"),
        packet_id=row.get("packet_id"),
        title=f"Fraud Watch: {name}",
        claim=row.get("recommended_take") or f"{name} is outrunning the role.",
        evidence_summary=_summary(row.get("packet_text") or row.get("packet_json"), 650),
        counterargument=row.get("counterargument") or "If the role stabilizes, the fraud label gets weaker.",
        snark_hook=_snark(row, f"{name} may be a points mirage with a nice haircut."),
        confidence_score=_num(row.get("confidence_score"), None),
        source_freshness_json=row.get("source_freshness_json"),
        missing_data_flags=row.get("missing_data_flags"),
    )


def _breakout_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    name = _name(row)
    return _item_row(
        content_brief_id=content_brief_id,
        item_type="player",
        item_order=order,
        player_id_internal=row.get("player_id_internal"),
        packet_id=row.get("packet_id"),
        title=f"Sleeper Breakout: {name}",
        claim=row.get("recommended_take") or f"{name} has rising usage at a cheaper price.",
        evidence_summary=_summary(row.get("packet_text") or row.get("packet_json"), 650),
        counterargument=row.get("counterargument") or "The market may be right if usage never turns into bankable volume.",
        snark_hook=_snark(row, f"{name} is not free money, but the room is sleeping through the alarm."),
        confidence_score=_num(row.get("confidence_score"), None),
        source_freshness_json=row.get("source_freshness_json"),
        missing_data_flags=row.get("missing_data_flags"),
    )


def _trade_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    winner = row.get("recommended_winner") or "unknown"
    return _item_row(
        content_brief_id=content_brief_id,
        item_type="trade",
        item_order=order,
        trade_review_id=row.get("trade_review_id"),
        title=f"Trade Review: {winner}",
        claim=f"Recommended winner: {winner}",
        evidence_summary=_summary(row.get("packet_text") or row.get("packet_json"), 650),
        counterargument="If team context or roster construction flips the need, the value edge can overstate the verdict.",
        snark_hook="Accepting a bad trade because it feels balanced is how leagues collect donations.",
        confidence_score=_num(row.get("confidence_score"), None),
        source_freshness_json=row.get("source_freshness_json"),
        missing_data_flags=row.get("missing_data_flags"),
    )


def _ranking_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    name = _name(row)
    pos_rank = _int_or_none(row.get("rank_position"))
    tier = row.get("tier") or "untiered"
    return _item_row(
        content_brief_id=content_brief_id,
        item_type="ranking",
        item_order=order,
        player_id_internal=row.get("player_id_internal"),
        title=f"Ranking Debate: {name}",
        claim=f"{name} sits at {row.get('position') or 'UNK'}{pos_rank or '?'} in {tier}.",
        evidence_summary=f"Projected value {row.get('projected_points_or_value')}; risk {row.get('risk_score')}; confidence {row.get('confidence_score')}.",
        counterargument="A rank without role context is just a spreadsheet wearing sunglasses.",
        snark_hook=f"{name} at this rank is either brave or a cry for help. The evidence decides.",
        confidence_score=_num(row.get("confidence_score"), None),
        source_freshness_json=row.get("source_freshness_json"),
        missing_data_flags=row.get("missing_data_flags"),
    )


def _accountability_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    source = row.get("source_name") or row.get("source_id") or "Unknown source"
    return _item_row(
        content_brief_id=content_brief_id,
        item_type="claim",
        item_order=order,
        title=f"Accountability: {source}",
        claim=f"{source}: {row.get('graded_count', 0)} graded claims, average accuracy {_fmt(row.get('average_claim_accuracy'))}.",
        evidence_summary=f"Good takes {row.get('good_take_count', 0)}, wrong {row.get('wrong_count', 0)}, fraud {row.get('fraud_count', 0)}, galaxy brain {row.get('galaxy_brain_count', 0)}.",
        counterargument="Small samples do not make someone smart or cooked. Yet.",
        snark_hook=f"{source} is now on the receipt printer. Hopefully they brought ink.",
        confidence_score=_num(row.get("average_claim_accuracy"), None),
        missing_data_flags=row.get("missing_data_flags") or "[]",
        source_freshness_json=row.get("source_freshness_json") or "{}",
    )


def _streamer_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    name = _name(row)
    return _item_row(
        content_brief_id=content_brief_id,
        item_type="player",
        item_order=order,
        player_id_internal=row.get("player_id_internal"),
        title=f"Streamer: {name}",
        claim=f"{name} is a weekly streamer candidate at projected value {row.get('projected_points_or_value')}.",
        evidence_summary=f"Rank overall {row.get('rank_overall')}, position rank {row.get('rank_position')}, tier {row.get('tier')}, confidence {row.get('confidence_score')}.",
        counterargument="Streamer is not a personality type. Keep the leash short.",
        snark_hook=f"{name} is a rental car, not a family heirloom.",
        confidence_score=_num(row.get("confidence_score"), None),
        source_freshness_json=row.get("source_freshness_json"),
        missing_data_flags=row.get("missing_data_flags"),
    )


def _dynasty_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    name = _name(row)
    return _item_row(
        content_brief_id=content_brief_id,
        item_type="player",
        item_order=order,
        player_id_internal=row.get("player_id_internal"),
        title=f"Dynasty Value: {name}",
        claim=f"{name} has dynasty rank {row.get('rank_overall')} with value {row.get('projected_points_or_value')}.",
        evidence_summary=f"Position rank {row.get('rank_position')}, tier {row.get('tier')}, confidence {row.get('confidence_score')}, risk {row.get('risk_score')}.",
        counterargument="Long-horizon rankings punish fake certainty. Treat this as a thesis, not a tattoo.",
        snark_hook=f"{name} is where patience meets the waiver-wire panic crowd.",
        confidence_score=_num(row.get("confidence_score"), None),
        source_freshness_json=row.get("source_freshness_json"),
        missing_data_flags=row.get("missing_data_flags"),
    )


def _full_prep_item(row: dict[str, Any], order: int, content_brief_id: str) -> dict[str, Any]:
    return _item_row(
        content_brief_id=content_brief_id,
        item_type=row.get("source_brief_type") or row.get("item_type") or "segment",
        item_order=order,
        player_id_internal=row.get("player_id_internal"),
        claim_id=row.get("claim_id"),
        trade_review_id=row.get("trade_review_id"),
        packet_id=row.get("packet_id"),
        title=f"{row.get('segment_title', 'Segment')}: {row.get('title', 'Untitled')}",
        claim=row.get("claim"),
        evidence_summary=row.get("evidence_summary"),
        counterargument=row.get("counterargument"),
        snark_hook=row.get("snark_hook"),
        confidence_score=_num(row.get("confidence_score"), None),
        source_freshness_json=row.get("source_freshness_json"),
        missing_data_flags=row.get("missing_data_flags"),
    )


def _item_row(
    *,
    content_brief_id: str,
    item_type: str,
    item_order: int,
    title: str,
    claim: str | None,
    evidence_summary: str | None,
    counterargument: str | None,
    snark_hook: str | None,
    confidence_score: float | None,
    player_id_internal: str | None = None,
    claim_id: str | None = None,
    trade_review_id: str | None = None,
    packet_id: str | None = None,
    source_freshness_json: Any = None,
    missing_data_flags: Any = None,
) -> dict[str, Any]:
    return {
        "content_brief_id": content_brief_id,
        "item_id": f"{content_brief_id}:{item_order:02d}",
        "item_type": item_type,
        "item_order": int(item_order),
        "player_id_internal": player_id_internal,
        "claim_id": claim_id,
        "trade_review_id": trade_review_id,
        "packet_id": packet_id,
        "title": _summary(title, 180),
        "claim": _summary(claim, 360),
        "evidence_summary": _summary(evidence_summary, 900),
        "counterargument": _summary(counterargument, 420),
        "snark_hook": _summary(snark_hook, 240),
        "confidence_score": _round(confidence_score),
        "source_freshness_json": _json_dumps(_json_object(source_freshness_json)),
        "missing_data_flags": _json_dumps(_json_array(missing_data_flags)),
        "created_at": _utc_timestamp(),
    }


def _empty_item(content_brief_id: str, brief_type: str, now: str) -> dict[str, Any]:
    return {
        "content_brief_id": content_brief_id,
        "item_id": f"{content_brief_id}:00",
        "item_type": "segment",
        "item_order": 0,
        "player_id_internal": None,
        "claim_id": None,
        "trade_review_id": None,
        "packet_id": None,
        "title": "No qualified items available",
        "claim": "The source tables returned no qualified rows for this brief.",
        "evidence_summary": "Do not force a segment. Refresh source packets or widen the scope.",
        "counterargument": "An empty board can be honest if the data is not ready.",
        "snark_hook": "Nothing to cook here unless you enjoy serving air.",
        "confidence_score": 0.0,
        "source_freshness_json": "{}",
        "missing_data_flags": "[\"missing_source_rows\"]",
        "created_at": now,
    }


def _brief_json(
    *,
    brief_type: str,
    title: str,
    objective: str,
    items: list[dict[str, Any]],
    source_freshness: dict[str, Any],
    missing_flags: list[str],
) -> dict[str, Any]:
    compact_items = [_compact_item(item) for item in items]
    prompt_items = [_prompt_item(item) for item in items]
    caveats = [
        "Use only the evidence in this brief.",
        "Do not invent stats, injuries, quotes, rankings, or source claims.",
        "State missing data honestly.",
        "Do not turn a confidence score into certainty.",
    ]
    return {
        "title": title,
        "brief_type": brief_type,
        "segment_objective": objective,
        "top_items": compact_items,
        "items": compact_items,
        "suggested_segment_order": [item["item_id"] for item in items],
        "do_not_overclaim_caveats": caveats,
        "source_freshness_json": source_freshness,
        "missing_data_flags": missing_flags,
        "llm_prompt_payload_json": {
            "task": "Write a show segment from the supplied evidence only.",
            "tone": "AI vs. Meatbags, snarky but evidence-bound.",
            "brief_type": brief_type,
            "title": title,
            "segment_objective": objective,
            "ordered_items": prompt_items,
            "caveats": caveats,
        },
    }


def _brief_text(brief_json: dict[str, Any]) -> str:
    lines = [
        brief_json["title"],
        f"Objective: {brief_json['segment_objective']}",
        "",
        "Segment Order:",
    ]
    for index, item in enumerate(brief_json["items"], start=1):
        lines.extend([
            f"{index}. {item['title']}",
            f"Claim: {item.get('claim') or 'No claim supplied.'}",
            f"Evidence: {item.get('evidence_summary') or 'No evidence summary supplied.'}",
            f"Counter: {item.get('counterargument') or 'No counterargument supplied.'}",
            f"Hook: {item.get('snark_hook') or 'No hook supplied.'}",
            f"Confidence: {item.get('confidence_score')}",
            "",
        ])
    lines.append("Do Not Overclaim:")
    lines.extend([f"- {caveat}" for caveat in brief_json["do_not_overclaim_caveats"]])
    return "\n".join(lines)


def _compact_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_id": item["item_id"],
        "item_type": item["item_type"],
        "item_order": item["item_order"],
        "player_id_internal": item.get("player_id_internal"),
        "claim_id": item.get("claim_id"),
        "trade_review_id": item.get("trade_review_id"),
        "packet_id": item.get("packet_id"),
        "title": item.get("title"),
        "claim": item.get("claim"),
        "evidence_summary": item.get("evidence_summary"),
        "counterargument": item.get("counterargument"),
        "snark_hook": item.get("snark_hook"),
        "confidence_score": item.get("confidence_score"),
        "missing_data_flags": _json_array(item.get("missing_data_flags")),
    }


def _prompt_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "item_type": item["item_type"],
        "item_order": item["item_order"],
        "player_id_internal": item.get("player_id_internal"),
        "claim_id": item.get("claim_id"),
        "trade_review_id": item.get("trade_review_id"),
        "packet_id": item.get("packet_id"),
        "title": item.get("title"),
        "claim": item.get("claim"),
        "evidence_summary": item.get("evidence_summary"),
        "counterargument": item.get("counterargument"),
        "snark_hook": item.get("snark_hook"),
        "confidence_score": item.get("confidence_score"),
        "missing_data_flags": _json_array(item.get("missing_data_flags")),
    }


def _load_fraud_packets(client: Any | None, dataset_id: str | None, season: int, week: int | None, scoring_profile_id: str, league_type_id: str, roster_format_id: str, model_run_id: str | None, limit: int) -> list[dict[str, Any]]:
    return _load_packet_rows(client, dataset_id, "fraud_watch_packets", "fraud_score", season, week, scoring_profile_id, league_type_id, roster_format_id, model_run_id, limit)


def _load_breakout_packets(client: Any | None, dataset_id: str | None, season: int, week: int | None, scoring_profile_id: str, league_type_id: str, roster_format_id: str, model_run_id: str | None, limit: int) -> list[dict[str, Any]]:
    return _load_packet_rows(client, dataset_id, "sleeper_breakout_packets", "breakout_score", season, week, scoring_profile_id, league_type_id, roster_format_id, model_run_id, limit)


def _load_packet_rows(client: Any | None, dataset_id: str | None, table_name: str, score_field: str, season: int, week: int | None, scoring_profile_id: str, league_type_id: str, roster_format_id: str, model_run_id: str | None, limit: int) -> list[dict[str, Any]]:
    if client is None:
        return []
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["season = @season", "scoring_profile_id = @scoring_profile_id", "league_type_id = @league_type_id", "roster_format_id = @roster_format_id"]
    params = [
        ("season", "INT64", int(season)),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("limit", "INT64", limit),
    ]
    if week is not None:
        where.append("week = @week")
        params.append(("week", "INT64", int(week)))
    if model_run_id:
        where.append("model_run_id = @model_run_id")
        params.append(("model_run_id", "STRING", model_run_id))
    sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, table_name)}`
    WHERE {" AND ".join(where)}
    ORDER BY {score_field} DESC, updated_at DESC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def _load_trade_packets(client: Any | None, dataset_id: str | None, scoring_profile_id: str, league_type_id: str, roster_format_id: str, model_run_id: str | None, limit: int) -> list[dict[str, Any]]:
    if client is None:
        return []
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["scoring_profile_id = @scoring_profile_id", "league_type_id = @league_type_id", "roster_format_id = @roster_format_id"]
    params = [
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("limit", "INT64", limit),
    ]
    if model_run_id:
        where.append("model_run_id = @model_run_id")
        params.append(("model_run_id", "STRING", model_run_id))
    sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, "trade_review_packets")}`
    WHERE {" AND ".join(where)}
    ORDER BY confidence_score DESC, updated_at DESC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def _load_ranking_rows(client: Any | None, dataset_id: str | None, horizon: str, season: int, week: int | None, scoring_profile_id: str, league_type_id: str, roster_format_id: str, model_run_id: str | None, limit: int) -> list[dict[str, Any]]:
    if client is None:
        return []
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["projection_horizon = @horizon", "(season = @season OR as_of_season = @season)", "scoring_profile_id = @scoring_profile_id", "league_type_id = @league_type_id", "roster_format_id = @roster_format_id"]
    params = [
        ("horizon", "STRING", horizon),
        ("season", "INT64", int(season)),
        ("scoring_profile_id", "STRING", scoring_profile_id),
        ("league_type_id", "STRING", league_type_id),
        ("roster_format_id", "STRING", roster_format_id),
        ("limit", "INT64", limit),
    ]
    if week is not None:
        where.append("(week = @week OR as_of_week = @week)")
        params.append(("week", "INT64", int(week)))
    if model_run_id:
        where.append("model_run_id = @model_run_id")
        params.append(("model_run_id", "STRING", model_run_id))
    sql = f"""
    SELECT *, TO_JSON_STRING(STRUCT(model_run_id, created_at, rank_source)) AS source_freshness_json
    FROM `{_table_id(client.project, dataset_id, "projection_rankings_current")}`
    WHERE {" AND ".join(where)}
    ORDER BY COALESCE(confidence_score, 0) DESC, COALESCE(risk_score, 0) DESC, rank_overall ASC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def _load_scorecards(client: Any | None, dataset_id: str | None, season: int, week: int | None, limit: int) -> list[dict[str, Any]]:
    if client is None:
        return []
    dataset_id = dataset_id or get_bigquery_dataset()
    where = ["(season = @season OR season IS NULL)"]
    params = [("season", "INT64", int(season)), ("limit", "INT64", limit)]
    if week is not None:
        where.append("(week = @week OR week IS NULL)")
        params.append(("week", "INT64", int(week)))
    sql = f"""
    SELECT *, TO_JSON_STRING(STRUCT(claim_grading_run_id, created_at)) AS source_freshness_json
    FROM `{_table_id(client.project, dataset_id, "claim_source_scorecards")}`
    WHERE {" AND ".join(where)}
    ORDER BY fraud_count DESC, wrong_count DESC, average_claim_accuracy ASC
    LIMIT @limit
    """
    return _query_rows(client, sql, _job_config(params))


def _merged_source_freshness(items: list[dict[str, Any]]) -> dict[str, Any]:
    entries = [_json_object(item.get("source_freshness_json")) for item in items]
    entries = [entry for entry in entries if entry]
    return {"item_count": len(items), "sources": entries[:10], "generated_at": _utc_timestamp()}


def _merged_missing_flags(items: list[dict[str, Any]]) -> list[str]:
    flags: list[str] = []
    for item in items:
        flags.extend(_json_array(item.get("missing_data_flags")))
    return sorted(set(flags))


def _bounded_text(text: str) -> str:
    return text if len(text) <= MAX_BRIEF_TEXT_CHARS else text[: MAX_BRIEF_TEXT_CHARS - 32] + "\n[brief truncated]"


def _estimate_tokens(text: str) -> int:
    return max(1, int(math.ceil(len(text) / 4)))


def _cap(brief_type: str, limit: int | None) -> int:
    default = ITEM_CAPS[_validate_brief_type(brief_type)]
    return max(1, min(int(limit or default), min(default, MAX_ITEM_CAP)))


def _name(row: dict[str, Any]) -> str:
    return str(row.get("display_name") or row.get("player_display_name") or row.get("title") or "Unknown").strip()


def _snark(row: dict[str, Any], fallback: str) -> str:
    hooks = _json_array(row.get("snark_hooks_json"))
    return hooks[0] if hooks else fallback


def _summary(value: Any, max_chars: int) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        value = _json_dumps(value)
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text if len(text) <= max_chars else text[: max_chars - 3].rstrip() + "..."


def _fmt(value: Any) -> str:
    parsed = _num(value, None)
    return "n/a" if parsed is None else f"{parsed:.3f}"


def _new_run_id(brief_type: str, season: int, week: int | None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    week_part = f"w{week}" if week is not None else "season"
    return f"{brief_type}-{season}-{week_part}-{stamp}-{uuid.uuid4().hex[:8]}"


def _new_brief_id(brief_type: str, season: int, week: int | None) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    week_part = f"w{week}" if week is not None else "season"
    return f"brief-{brief_type}-{season}-{week_part}-{stamp}-{uuid.uuid4().hex[:8]}"


def _validate_brief_type(value: str) -> str:
    normalized = str(value or "").strip().lower()
    if normalized not in SUPPORTED_BRIEF_TYPES:
        raise ValueError(f"Invalid brief_type: {value!r}")
    return normalized


def _insert_rows(client: Any, dataset_id: str, table_name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    errors = client.insert_rows_json(_table_id(client.project, dataset_id, table_name), rows)
    if errors:
        raise RuntimeError(f"Failed to insert {table_name}: {errors}")


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    rows = client.query(sql, job_config=job_config).result()
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(dict(row))
        elif hasattr(row, "items"):
            result.append(dict(row.items()))
        else:
            result.append(dict(row))
    return result


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[bigquery.ScalarQueryParameter(name, param_type, value) for name, param_type, value in params],
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    _validate_project_id(project_id)
    _validate_identifier(dataset_id, "dataset_id")
    _validate_identifier(table_name, "table_name")
    return f"{project_id}.{dataset_id}.{table_name}"


def _validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid BigQuery {label}: {value!r}")


def _validate_project_id(value: str) -> None:
    if not PROJECT_ID_RE.fullmatch(value):
        raise ValueError(f"Invalid BigQuery project_id: {value!r}")


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return dict(value)
    if value in (None, ""):
        return {}
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _json_array(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    if value in (None, ""):
        return []
    try:
        parsed = json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return []
    return [str(item) for item in parsed] if isinstance(parsed, list) else []


def _num(value: Any, default: float | None = 0.0) -> float | None:
    if value in (None, ""):
        return default
    try:
        parsed = float(str(value).replace(",", ""))
    except (TypeError, ValueError):
        return default
    if math.isnan(parsed) or math.isinf(parsed):
        return default
    return parsed


def _int_or_none(value: Any) -> int | None:
    parsed = _num(value, None)
    return None if parsed is None else int(parsed)


def _round(value: float | None) -> float | None:
    return None if value is None else round(value, 4)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build deterministic AI vs. Meatbags content briefs.")
    parser.add_argument("--brief-type", required=True, choices=sorted(SUPPORTED_BRIEF_TYPES))
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--week", type=int)
    parser.add_argument("--scoring-profile", default=DEFAULT_SCORING_PROFILE)
    parser.add_argument("--league-type", default=DEFAULT_LEAGUE_TYPE)
    parser.add_argument("--roster-format", default=DEFAULT_ROSTER_FORMAT)
    parser.add_argument("--model-run-id")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    client = None if args.dry_run else get_bigquery_client()
    kwargs = {
        "season": args.season,
        "week": args.week,
        "scoring_profile_id": args.scoring_profile,
        "league_type_id": args.league_type,
        "roster_format_id": args.roster_format,
        "model_run_id": args.model_run_id,
        "client": client,
    }
    builders = {
        "fraud_watch_show": build_fraud_watch_brief,
        "sleeper_breakout_show": build_sleeper_breakout_brief,
        "trade_review_show": build_trade_review_brief,
        "rankings_debate_show": build_rankings_debate_brief,
        "meatbag_accountability_show": build_meatbag_accountability_brief,
        "weekly_streamers_show": build_weekly_streamers_brief,
        "dynasty_value_show": build_dynasty_value_brief,
        "full_weekly_show_prep": build_full_weekly_show_prep,
    }
    brief = builders[args.brief_type](**kwargs)
    result = save_content_brief(brief, client=client, dry_run=args.dry_run)
    result["brief"] = brief["brief"]
    result["items"] = brief["items"]
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
