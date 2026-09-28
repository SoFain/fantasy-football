"""Diff the two most recent Sleeper snapshots and pull news for what moved.

Runs after ingest-sleeper-news. Reads the last two snapshots from
sleeper_players_history, writes one row per changed field to
player_status_changes, then fetches the beat feed for each team that had a
triggering change.

Feeds are fetched per affected team, not per affected player, so a day where
one team places six players on the injury report costs one request, and the
worst possible day costs 32.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from src.player_status_changes import (
    WATCHED_FIELDS,
    diff_snapshots,
    players_needing_news,
    summarize,
    teams_needing_news,
)
from src.team_news_feeds import (
    DEFAULT_MAX_ITEM_AGE_DAYS,
    DEFAULT_MAX_ITEMS_PER_TEAM,
    fetch_team_feed,
    filter_recent,
    match_players,
)

logger = logging.getLogger("detect_player_changes")

HISTORY_TABLE = "sleeper_players_history"
CHANGES_TABLE = "player_status_changes"
NEWS_TABLE = "team_news_items"
MATCHES_TABLE = "player_news_matches"

SNAPSHOT_COLUMNS = (
    "snapshot_at",
    "sleeper_player_id",
    "gsis_id",
    "player_name",
    "position",
    *WATCHED_FIELDS,
)


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    return f"{project_id}.{dataset_id}.{table_name}"


def recent_snapshot_times(client: Any, dataset_id: str, limit: int = 2) -> list[datetime]:
    """The most recent distinct snapshot timestamps, newest first."""
    sql = f"""
    SELECT DISTINCT snapshot_at
    FROM `{_table_id(client.project, dataset_id, HISTORY_TABLE)}`
    ORDER BY snapshot_at DESC
    LIMIT {int(limit)}
    """
    return [row["snapshot_at"] for row in client.query(sql).result()]


def load_snapshot(client: Any, dataset_id: str, snapshot_at: datetime) -> list[dict[str, Any]]:
    from google.cloud import bigquery

    columns = ", ".join(dict.fromkeys(SNAPSHOT_COLUMNS))
    sql = f"""
    SELECT {columns}
    FROM `{_table_id(client.project, dataset_id, HISTORY_TABLE)}`
    WHERE snapshot_at = @snapshot_at
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[bigquery.ScalarQueryParameter("snapshot_at", "TIMESTAMP", snapshot_at)]
    )
    return [dict(row) for row in client.query(sql, job_config=job_config).result()]


def _load_rows(client: Any, dataset_id: str, table_name: str, rows: list[dict[str, Any]]) -> None:
    """Write with a load job, never a streaming insert.

    Streamed rows sit in the buffer where DML cannot touch them, which is the
    same trap that broke job run completion recording.
    """
    if not rows:
        return
    from google.cloud import bigquery

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    client.load_table_from_json(
        rows, _table_id(client.project, dataset_id, table_name), job_config=job_config
    ).result()


def _iso(value: Any) -> Any:
    return value.isoformat() if isinstance(value, datetime) else value


def collect_team_news(
    changes: list[dict[str, Any]],
    *,
    fetched_at: datetime,
    session: Any | None = None,
    max_items: int = DEFAULT_MAX_ITEMS_PER_TEAM,
    max_age_days: int = DEFAULT_MAX_ITEM_AGE_DAYS,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Fetch feeds for affected teams; return (news rows, player match rows)."""
    teams = teams_needing_news(changes)
    players = players_needing_news(changes)
    players_by_team: dict[str, list[dict[str, Any]]] = {}
    for player in players:
        players_by_team.setdefault(str(player.get("team") or ""), []).append(player)

    triggers_by_player: dict[str, dict[str, Any]] = {}
    for change in changes:
        if change.get("triggers_news_check"):
            triggers_by_player.setdefault(str(change.get("sleeper_player_id")), change)

    news_rows: list[dict[str, Any]] = []
    match_rows: list[dict[str, Any]] = []

    for team in teams:
        items = filter_recent(
            fetch_team_feed(team, session=session),
            now=fetched_at,
            max_age_days=max_age_days,
            max_items=max_items,
        )
        if not items:
            continue

        # Match against players who changed on this team, plus anyone who moved
        # off it: the old team's beat writer often has the transaction story.
        candidates = players_by_team.get(team, []) + [
            p for p in players if str(p.get("team") or "") != team
        ]
        for item in match_players(items, candidates):
            matched = item.get("matched_players") or []
            news_rows.append({
                "fetched_at": _iso(fetched_at),
                "team": team,
                "feed_url": item.get("feed_url"),
                "item_url": item.get("url"),
                "title": item.get("title"),
                "summary": item.get("summary"),
                "author": item.get("author"),
                "published_at": _iso(item.get("published_at")),
                "matched_player_count": len(matched),
            })
            for player in matched:
                trigger = triggers_by_player.get(str(player.get("sleeper_player_id")), {})
                match_rows.append({
                    "fetched_at": _iso(fetched_at),
                    "team": team,
                    "item_url": item.get("url"),
                    "title": item.get("title"),
                    "published_at": _iso(item.get("published_at")),
                    "sleeper_player_id": player.get("sleeper_player_id"),
                    "gsis_id": player.get("gsis_id"),
                    "player_name": player.get("player_name"),
                    "position": player.get("position"),
                    "trigger_field": trigger.get("field_name"),
                    "trigger_old_value": trigger.get("old_value"),
                    "trigger_new_value": trigger.get("new_value"),
                })

    return news_rows, match_rows


def detect_player_changes(
    *,
    dataset_id: str = "fantasy_football_brain",
    client: Any | None = None,
    fetch_news: bool = True,
    dry_run: bool = False,
    session: Any | None = None,
) -> dict[str, Any]:
    if client is None:
        from google.cloud import bigquery

        from src.load import get_bigquery_project

        client = bigquery.Client(project=get_bigquery_project())

    snapshots = recent_snapshot_times(client, dataset_id)
    if len(snapshots) < 2:
        # First run after the migration has nothing to compare against. This is
        # expected once, not an error.
        logger.info("Need two snapshots to diff; found %s. Nothing to do.", len(snapshots))
        return {"change_count": 0, "reason": "insufficient_history", "snapshot_count": len(snapshots)}

    current_at, previous_at = snapshots[0], snapshots[1]
    detected_at = datetime.now(timezone.utc)

    changes = diff_snapshots(
        load_snapshot(client, dataset_id, previous_at),
        load_snapshot(client, dataset_id, current_at),
        detected_at=detected_at,
    )
    result = summarize(changes)
    result.update({
        "previous_snapshot_at": previous_at.isoformat(),
        "current_snapshot_at": current_at.isoformat(),
        "teams_to_check": teams_needing_news(changes),
    })

    if dry_run:
        result["dry_run"] = True
        return result

    _load_rows(client, dataset_id, CHANGES_TABLE, [
        {
            **change,
            "detected_at": _iso(change["detected_at"]),
            "previous_snapshot_at": _iso(previous_at),
            "current_snapshot_at": _iso(current_at),
        }
        for change in changes
    ])

    if fetch_news and changes:
        news_rows, match_rows = collect_team_news(
            changes, fetched_at=detected_at, session=session
        )
        _load_rows(client, dataset_id, NEWS_TABLE, news_rows)
        _load_rows(client, dataset_id, MATCHES_TABLE, match_rows)
        result["news_item_count"] = len(news_rows)
        result["news_match_count"] = len(match_rows)

    logger.info("Player change detection complete: %s", result)
    return result
