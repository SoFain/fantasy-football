"""Current NFL coaching staff: canonical roles, team reference, and rendering.

This is the first coaching layer: current staff only. Coaching styles and
historical records are deliberately later layers and are not modeled here.

The eight roles below are the ones the platform tracks for agent context. The
Sleeper/nflreadpy pipelines have nothing on coaching, so this is a separate,
manually curated reference sourced from the Wikipedia "List of current NFL
staffs" page. Curated rather than scraped on purpose: the source is 32 separate
transcluded templates with inconsistent role labels, and shipping a wrong
"current" coach to agents is worse than shipping a known gap. The CSV is the
reviewable source of truth; every row carries provenance and a verification
status so unverified seed data is never mistaken for confirmed data.

Pure functions only: no BigQuery, no network, no filesystem. The ingest and
feed jobs wrap these.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

# team_abbr -> (full name, conference, division). Matches team_descriptions.team_abbr
# and the abbreviations used across the Sleeper and news-feed layers.
NFL_TEAMS: dict[str, tuple[str, str, str]] = {
    "BUF": ("Buffalo Bills", "AFC", "AFC East"),
    "MIA": ("Miami Dolphins", "AFC", "AFC East"),
    "NE": ("New England Patriots", "AFC", "AFC East"),
    "NYJ": ("New York Jets", "AFC", "AFC East"),
    "BAL": ("Baltimore Ravens", "AFC", "AFC North"),
    "CIN": ("Cincinnati Bengals", "AFC", "AFC North"),
    "CLE": ("Cleveland Browns", "AFC", "AFC North"),
    "PIT": ("Pittsburgh Steelers", "AFC", "AFC North"),
    "HOU": ("Houston Texans", "AFC", "AFC South"),
    "IND": ("Indianapolis Colts", "AFC", "AFC South"),
    "JAX": ("Jacksonville Jaguars", "AFC", "AFC South"),
    "TEN": ("Tennessee Titans", "AFC", "AFC South"),
    "DEN": ("Denver Broncos", "AFC", "AFC West"),
    "KC": ("Kansas City Chiefs", "AFC", "AFC West"),
    "LV": ("Las Vegas Raiders", "AFC", "AFC West"),
    "LAC": ("Los Angeles Chargers", "AFC", "AFC West"),
    "DAL": ("Dallas Cowboys", "NFC", "NFC East"),
    "NYG": ("New York Giants", "NFC", "NFC East"),
    "PHI": ("Philadelphia Eagles", "NFC", "NFC East"),
    "WAS": ("Washington Commanders", "NFC", "NFC East"),
    "CHI": ("Chicago Bears", "NFC", "NFC North"),
    "DET": ("Detroit Lions", "NFC", "NFC North"),
    "GB": ("Green Bay Packers", "NFC", "NFC North"),
    "MIN": ("Minnesota Vikings", "NFC", "NFC North"),
    "ATL": ("Atlanta Falcons", "NFC", "NFC South"),
    "CAR": ("Carolina Panthers", "NFC", "NFC South"),
    "NO": ("New Orleans Saints", "NFC", "NFC South"),
    "TB": ("Tampa Bay Buccaneers", "NFC", "NFC South"),
    "ARI": ("Arizona Cardinals", "NFC", "NFC West"),
    "LAR": ("Los Angeles Rams", "NFC", "NFC West"),
    "SF": ("San Francisco 49ers", "NFC", "NFC West"),
    "SEA": ("Seattle Seahawks", "NFC", "NFC West"),
}

# (role_key, display title, ordering rank). The order is the reporting chain the
# owner specified, and rank drives display and feed ordering.
CANONICAL_ROLES: tuple[tuple[str, str, int], ...] = (
    ("head_coach", "Head Coach", 1),
    ("senior_assistant", "Senior Assistant", 2),
    ("offensive_coordinator", "Offensive Coordinator", 3),
    ("defensive_coordinator", "Defensive Coordinator", 4),
    ("quarterbacks_coach", "Quarterbacks Coach", 5),
    ("running_backs_coach", "Running Backs Coach", 6),
    ("wide_receivers_coach", "Wide Receivers Coach", 7),
    ("offensive_line_coach", "Offensive Line Coach", 8),
)

ROLE_KEYS: tuple[str, ...] = tuple(role for role, _, _ in CANONICAL_ROLES)
ROLE_TITLES: dict[str, str] = {role: title for role, title, _ in CANONICAL_ROLES}
ROLE_RANKS: dict[str, int] = {role: rank for role, _, rank in CANONICAL_ROLES}

# Wikipedia and common labels mapped to canonical role keys. "Senior assistant"
# and "Assistant head coach" are the same tier on different teams, so both map
# to senior_assistant. Extend this as new source labels appear rather than
# inventing new roles.
ROLE_ALIASES: dict[str, str] = {
    "head coach": "head_coach",
    "senior assistant": "senior_assistant",
    "assistant head coach": "senior_assistant",
    "offensive coordinator": "offensive_coordinator",
    "defensive coordinator": "defensive_coordinator",
    "quarterbacks": "quarterbacks_coach",
    "quarterbacks coach": "quarterbacks_coach",
    "running backs": "running_backs_coach",
    "running backs coach": "running_backs_coach",
    "wide receivers": "wide_receivers_coach",
    "wide receivers coach": "wide_receivers_coach",
    "offensive line": "offensive_line_coach",
    "offensive line coach": "offensive_line_coach",
}

VERIFICATION_PENDING = "pending"
VERIFICATION_VERIFIED = "verified"
VALID_VERIFICATION = {VERIFICATION_PENDING, VERIFICATION_VERIFIED}

DEFAULT_SOURCE = "wikipedia_wikiproject_nfl_staffs"


def normalize_role(label: str | None) -> str | None:
    """Map a source role label to a canonical role key, or None if unknown."""
    if not label:
        return None
    key = str(label).strip().lower()
    if key in ROLE_KEYS:
        return key
    return ROLE_ALIASES.get(key)


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def prepare_rows(
    csv_rows: Iterable[Mapping[str, Any]],
    *,
    snapshot_at: Any,
    source_url: str,
    source: str = DEFAULT_SOURCE,
) -> list[dict[str, Any]]:
    """Validate and normalize CSV rows into coaching_staff_current table rows.

    Emits one row per (team, role) for all 32 teams and all 8 roles, so the
    table always has the full 256-row grid. A team/role missing from the CSV is
    emitted as vacant with a missing flag rather than dropped, so agents can
    tell "no coach listed" from "team not covered".

    Raises on structural problems the operator must fix (unknown team, unknown
    role, duplicate team/role) rather than silently guessing.
    """
    supplied: dict[tuple[str, str], dict[str, Any]] = {}
    for index, raw in enumerate(csv_rows):
        team = _clean(raw.get("team_abbr"))
        if team is None:
            raise ValueError(f"Row {index}: team_abbr is required.")
        team = team.upper()
        if team not in NFL_TEAMS:
            raise ValueError(f"Row {index}: unknown team_abbr {team!r}.")

        role = normalize_role(raw.get("role"))
        if role is None:
            raise ValueError(f"Row {index}: unknown role {raw.get('role')!r} for {team}.")

        key = (team, role)
        if key in supplied:
            raise ValueError(f"Duplicate row for {team} / {role}.")

        status = (_clean(raw.get("verification_status")) or VERIFICATION_PENDING).lower()
        if status not in VALID_VERIFICATION:
            raise ValueError(f"Row {index}: invalid verification_status {status!r}.")

        supplied[key] = {
            "coach_name": _clean(raw.get("coach_name")),
            "raw_title": _clean(raw.get("raw_title")),
            "verification_status": status,
            "notes": _clean(raw.get("notes")),
        }

    rows: list[dict[str, Any]] = []
    for team_abbr, (team_name, conference, division) in NFL_TEAMS.items():
        for role_key in ROLE_KEYS:
            supplied_row = supplied.get((team_abbr, role_key), {})
            coach_name = supplied_row.get("coach_name")
            is_vacant = coach_name is None
            missing_fields = []
            if is_vacant:
                missing_fields.append("missing_coach_name")
            # A filled-but-pending row is real data awaiting confirmation, not a gap.
            status = supplied_row.get("verification_status", VERIFICATION_PENDING)
            if not is_vacant and status == VERIFICATION_PENDING:
                missing_fields.append("unverified")

            rows.append({
                "snapshot_at": snapshot_at,
                "team_abbr": team_abbr,
                "team_name": team_name,
                "conference": conference,
                "division": division,
                "role": role_key,
                "role_title": ROLE_TITLES[role_key],
                "role_rank": ROLE_RANKS[role_key],
                "coach_name": coach_name,
                "raw_title": supplied_row.get("raw_title"),
                "is_vacant": is_vacant,
                "verification_status": status,
                "source": source,
                "source_url": source_url,
                "notes": supplied_row.get("notes"),
                "missing_fields_json": _json_list(missing_fields),
            })
    return rows


def _json_list(values: list[str]) -> str:
    import json

    return json.dumps(values, sort_keys=True)


DATASET_ID = "coaching_staff"
DATASET_SCHEMA_VERSION = "1.0"


def canonical_json_bytes(obj: Any) -> bytes:
    """Deterministic UTF-8 JSON bytes: sorted keys, compact, trailing newline.

    The public feed is content-addressed by the SHA-256 of the exact bytes
    uploaded, so serialization must be stable across runs and machines.
    """
    return (json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def build_dataset(
    rows: Iterable[Mapping[str, Any]],
    *,
    source_generated_at: str,
    source_url: str,
) -> dict[str, Any]:
    """Build the coaching staff dataset payload for the JSON feed.

    Shaped to sit alongside the public ranking boards: teams grouped, roles in
    canonical order, vacant roles retained with a null coach so the shape is
    stable every publish rather than fields appearing and vanishing.
    """
    by_team: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        by_team.setdefault(str(row["team_abbr"]), []).append(row)

    teams = []
    vacant_count = 0
    pending_count = 0
    for team_abbr, (name, conference, division) in NFL_TEAMS.items():
        team_rows = sorted(by_team.get(team_abbr, []), key=lambda r: r["role_rank"])
        if not team_rows:
            continue
        coaches = []
        for row in team_rows:
            is_vacant = bool(row.get("is_vacant"))
            status = str(row.get("verification_status", VERIFICATION_PENDING))
            if is_vacant:
                vacant_count += 1
            if not is_vacant and status == VERIFICATION_PENDING:
                pending_count += 1
            coaches.append({
                "role": row["role"],
                "title": row["role_title"],
                "rank": row["role_rank"],
                "coach_name": row.get("coach_name"),
                "vacant": is_vacant,
                "verification_status": status,
            })
        teams.append({
            "team_abbr": team_abbr,
            "team_name": name,
            "conference": conference,
            "division": division,
            "coaches": coaches,
        })

    return {
        "dataset": DATASET_ID,
        "schema_version": DATASET_SCHEMA_VERSION,
        "title": "Current NFL Coaching Staffs",
        "description": (
            "Current coaching staff for all 32 NFL teams across eight roles "
            "(head coach, senior assistant, coordinators, position coaches). "
            "First coaching layer: current staff only, for agent context."
        ),
        "roles": [{"role": r, "title": t, "rank": k} for r, t, k in CANONICAL_ROLES],
        "source_url": source_url,
        "source_generated_at": source_generated_at,
        "team_count": len(teams),
        "vacant_count": vacant_count,
        "pending_count": pending_count,
        "teams": teams,
    }


def dataset_version(source_generated_at: str) -> str:
    """A human-readable version tag, mirroring the boards' board_version."""
    compact = "".join(ch for ch in source_generated_at if ch.isdigit())
    return f"{DATASET_ID}-{DATASET_SCHEMA_VERSION}-{compact[:14]}"


def manifest_entry(
    *,
    content: bytes,
    object_name: str,
    url: str,
    source_generated_at: str,
    dataset: Mapping[str, Any],
    warnings: list[str] | None = None,
) -> dict[str, Any]:
    """Manifest descriptor for the coaching staff dataset.

    Field-compatible with the ranking board entries in the live manifest so the
    external publisher can list it the same way (under a `datasets` key rather
    than `profiles`). The publisher owns the mutable manifest; this only
    describes the immutable object so the two never race.
    """
    return {
        "dataset": DATASET_ID,
        "dataset_version": dataset_version(source_generated_at),
        "schema_version": DATASET_SCHEMA_VERSION,
        "source_generated_at": source_generated_at,
        "object": object_name,
        "url": url,
        "sha256": sha256_hex(content),
        "bytes": len(content),
        "team_count": dataset.get("team_count", 0),
        "vacant_count": dataset.get("vacant_count", 0),
        "pending_count": dataset.get("pending_count", 0),
        "warnings": warnings or [],
    }
