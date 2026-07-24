"""Detect day-over-day player attribute changes from Sleeper snapshots.

The Sleeper snapshot was historically written WRITE_TRUNCATE, which made
change detection impossible: yesterday's state was gone. `sleeper_players_history`
is append-only and partitioned, so two consecutive snapshots can be diffed.

Field authority: Sleeper wins on conflict with nflreadpy for team, status, and
biographical fields including birth_date. nflreadpy fills gaps only. Conflicts
are recorded rather than silently absorbed, so a Sleeper data-entry error that
moves a player's age or team can be reviewed instead of quietly propagating
into the identity bridge and the age-curve formulas.
"""

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import Any, Iterable, Mapping

logger = logging.getLogger("player_status_changes")

# Fields diffed between consecutive snapshots.
#
# `active` is deliberately absent. The Sleeper players endpoint is called with
# ?active=true to honor the once-per-day guidance and keep the payload small,
# so every ingested row has active=true and the field can never differ. A
# player leaving the active set drops out of the snapshot entirely rather than
# flipping a boolean; that disappearance is not tracked here.
WATCHED_FIELDS: tuple[str, ...] = (
    "team",
    "status",
    "injury_status",
    "depth_chart_position",
    "depth_chart_order",
)

# Changes that warrant pulling the player's team feed for context. Deliberately
# narrower than WATCHED_FIELDS: status alone flips on routine roster paperwork,
# and depth_chart_position alone flips on positional relabeling. This is exactly
# the injury / team / depth-chart set.
NEWS_TRIGGER_FIELDS: frozenset[str] = frozenset({
    "injury_status",
    "team",
    "depth_chart_order",
})

IDENTITY_FIELDS: tuple[str, ...] = (
    "sleeper_player_id",
    "gsis_id",
    "player_name",
    "position",
    "team",
)


def _normalize(value: Any) -> Any:
    """Collapse the several ways Sleeper spells 'no value'.

    Without this, a player flipping between null and "" produces a spurious
    change every single day.
    """
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    return value


def _changed(previous: Any, current: Any) -> bool:
    return _normalize(previous) != _normalize(current)


def _as_text(value: Any) -> str | None:
    normalized = _normalize(value)
    if normalized is None:
        return None
    if isinstance(normalized, bool):
        return "true" if normalized else "false"
    return str(normalized)


def diff_snapshots(
    previous_rows: Iterable[Mapping[str, Any]],
    current_rows: Iterable[Mapping[str, Any]],
    *,
    detected_at: datetime,
    watched_fields: tuple[str, ...] = WATCHED_FIELDS,
) -> list[dict[str, Any]]:
    """Return one change row per (player, changed field).

    Players absent from the previous snapshot produce no rows. A first sighting
    is not a change, and emitting one would flood the table on the first run
    and whenever Sleeper adds a batch of players.
    """
    previous_by_id = {
        str(row.get("sleeper_player_id")): row
        for row in previous_rows
        if row.get("sleeper_player_id") is not None
    }

    changes: list[dict[str, Any]] = []
    for current in current_rows:
        player_id = current.get("sleeper_player_id")
        if player_id is None:
            continue
        previous = previous_by_id.get(str(player_id))
        if previous is None:
            continue

        for field in watched_fields:
            before, after = previous.get(field), current.get(field)
            if not _changed(before, after):
                continue

            changes.append({
                "detected_at": detected_at,
                "sleeper_player_id": str(player_id),
                "gsis_id": _as_text(current.get("gsis_id")),
                "player_name": _as_text(current.get("player_name")),
                "position": _as_text(current.get("position")),
                "team": _as_text(current.get("team")),
                "previous_team": _as_text(previous.get("team")),
                "field_name": field,
                "old_value": _as_text(before),
                "new_value": _as_text(after),
                "triggers_news_check": field in NEWS_TRIGGER_FIELDS,
            })

    return changes


def teams_needing_news(changes: Iterable[Mapping[str, Any]]) -> list[str]:
    """Distinct teams to fetch feeds for, from news-triggering changes only.

    Deduplicated by team, not by player: ten Bills changes cost one request.
    A team change contributes both the old and new team, since either beat
    writer may have the story.
    """
    teams: set[str] = set()
    for change in changes:
        if not change.get("triggers_news_check"):
            continue
        for key in ("team", "previous_team"):
            value = _normalize(change.get(key))
            if value:
                teams.add(str(value))
    return sorted(teams)


def players_needing_news(changes: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Distinct players behind news-triggering changes, for feed matching."""
    seen: dict[str, dict[str, Any]] = {}
    for change in changes:
        if not change.get("triggers_news_check"):
            continue
        player_id = change.get("sleeper_player_id")
        if player_id and player_id not in seen:
            seen[player_id] = {key: change.get(key) for key in IDENTITY_FIELDS}
    return list(seen.values())


def compute_age(birth_date: Any, as_of: date) -> float | None:
    """Age in years from a birth date, or None when unknown.

    Age feeds the dynasty and value curves, so a wrong age is worse than a
    missing one: None is propagated rather than defaulted.
    """
    if birth_date is None:
        return None
    if isinstance(birth_date, datetime):
        birth_date = birth_date.date()
    elif isinstance(birth_date, str):
        try:
            birth_date = date.fromisoformat(birth_date.strip()[:10])
        except ValueError:
            logger.debug("Unparseable birth_date: %r", birth_date)
            return None
    if not isinstance(birth_date, date):
        return None
    if birth_date > as_of:
        logger.warning("birth_date %s is in the future; treating age as unknown", birth_date)
        return None
    return round((as_of - birth_date).days / 365.25, 2)


def summarize(changes: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Counts for job logging and the run result payload."""
    changes = list(changes)
    by_field: dict[str, int] = {}
    for change in changes:
        field = str(change.get("field_name"))
        by_field[field] = by_field.get(field, 0) + 1
    return {
        "change_count": len(changes),
        "news_trigger_count": sum(1 for c in changes if c.get("triggers_news_check")),
        "player_count": len({c.get("sleeper_player_id") for c in changes}),
        "by_field": dict(sorted(by_field.items())),
    }
