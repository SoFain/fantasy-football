"""Build auditable review events from Sleeper injury-status changes."""

from __future__ import annotations

from datetime import datetime


CRITICAL_INJURY_STATUSES = {"OUT", "IR"}


def normalize_injury_status(value):
    return str(value or "").strip().upper()


def build_injury_review_events(previous_by_player_id, current_records, detected_at: datetime):
    """Return only newly critical Sleeper status transitions for owner or Pigskin review."""

    events = []
    for record in current_records:
        sleeper_player_id = str(record.get("sleeper_player_id") or "").strip()
        current_status = normalize_injury_status(record.get("injury_status"))
        previous_status = normalize_injury_status(previous_by_player_id.get(sleeper_player_id))
        if not sleeper_player_id or current_status not in CRITICAL_INJURY_STATUSES:
            continue
        if current_status == previous_status:
            continue

        events.append({
            "event_id": f"{sleeper_player_id}:{current_status}:{detected_at.isoformat()}",
            "sleeper_player_id": sleeper_player_id,
            "player_name": record.get("player_name"),
            "team": record.get("team"),
            "position": record.get("position"),
            "previous_injury_status": previous_status or None,
            "injury_status": current_status,
            "detected_at": detected_at,
            "source_name": "sleeper_players_nfl",
            "review_status": "PENDING",
            "requires_pigskin_investigation": True,
            "ranking_action": "NO_AUTOMATIC_RANK_CHANGE",
        })
    return events
