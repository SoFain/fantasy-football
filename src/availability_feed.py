"""Public `availability` feed dataset (schema availability-1.0), built from the day's decisions.

Context only: nothing here reads or writes a ranking, board, candidate, unified,
or safety table. The object is content-addressed like the other feed datasets
(`v1/datasets/availability/sha256-<digest>.json`). The chain uploads it and the
publisher lists it in the manifest `datasets` block; when the artifacts are
absent the publisher carries the previous object forward.

Text fields are null whenever Jev was below its threshold or no candidate item
was judged relevant. Every number comes from code or the stored decision row.
`base_rate` and `text` are always objects with every key present (the site
importer rejects the whole object otherwise); a player without a Sleeper id or
a base-rate prior is left out and counted in the manifest entry warning.
"""

from __future__ import annotations

import json
import os
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from src.availability_decisions import QUESTION_SET_VERSION, Case
from src.availability_labels import MISSED_BUCKETS
from src.coaching_staff import canonical_json_bytes, sha256_hex

DATASET_ID = "availability"
SCHEMA_VERSION = "availability-1.0"
DEFAULT_BUCKET = "fantasy-football-498121-public-rankings"
FEED_DIR = Path(__file__).resolve().parents[1] / "build" / "feeds"
MAX_SOURCES = 3
# Sleeper and nflverse disagree on one franchise code; the feed uses Sleeper codes.
NFLVERSE_TO_SLEEPER_TEAM = {"LA": "LAR"}
PRACTICE_LABELS = {"DNP": "Did Not Participate", "LP": "Limited", "FP": "Full"}
SOURCE_LABELS = {"draftsharks_injury_news": "DraftSharks", "team_news_items": "Team news feed"}
DESIGNATION_SOURCES = ("sleeper", "official_report", "team_roster")
TEXT_ENUMS = {
    "availability": ("will_play", "game_time_decision", "will_miss"),
    "absence": MISSED_BUCKETS,
    "trend": ("improving", "unchanged", "worsening", "unknown"),
}
LANE_CAVEATS = {
    "report_last_game": "No official injury report for this game yet; the base rate uses his report for his last game.",
    "roster_status": "He is not on an official injury report; the base rate uses his reserve-list roster status.",
    "sleeper_designation_only": "No official injury report entry; the base rate uses the Sleeper designation alone with practice unknown.",
}
SOURCE_CAVEATS = {
    "official_report": "Sleeper data is not collected for this position; the designation is from the official injury report.",
    "team_roster": "Sleeper data is not collected for this position; the designation is from the team's weekly roster.",
}
PLAYER_KEYS = {
    "gsis_id", "sleeper_player_id", "player_name", "team", "position", "designation", "designation_source",
    "practice", "body_part", "next_game", "base_rate", "text", "caveats",
}
TEXT_KEYS = {
    "availability", "availability_confidence", "absence", "absence_confidence", "trend", "trend_confidence",
    "relevant_items", "sources",
}
TOP_KEYS = {"schema_version", "generated_at", "decision_date", "season", "week", "models", "players"}
ISO_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$")
GSIS_RE = re.compile(r"^00-\d{7}$")


def iso_utc(value: datetime | str) -> str:
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sleeper_team(code: str | None) -> str | None:
    return NFLVERSE_TO_SLEEPER_TEAM.get(code, code) if code else None


def current_week(games: Iterable[dict], now: datetime) -> int:
    """Week of the league's next kickoff; a game that started in the last four hours still counts."""
    weeks = sorted((g["kickoff_utc"], int(g["week"])) for g in games)
    if not weeks:
        raise ValueError("No regular-season schedule rows")
    cutoff = now.timestamp() - 4 * 3600
    return next((week for kickoff, week in weeks if kickoff.timestamp() > cutoff), weeks[-1][1])


def _prob(value: float | None) -> float | None:
    return None if value is None else round(float(value), 3)


def text_block(row: dict | None) -> tuple[dict[str, Any], list[str]]:
    """Gate the stored decision into the public text block. Blank or textless answers stay null."""
    relevant = int(row["relevant_text_count"] or 0) if row else 0
    block: dict[str, Any] = {}
    below = []
    for question in TEXT_ENUMS:
        value = None
        if row is not None and relevant > 0:
            if row.get(f"{question}_blank"):
                below.append(question)
            else:
                value = row.get(question)
        block[question] = value
        block[f"{question}_confidence"] = _prob(row.get(f"{question}_confidence")) if value is not None else None
    items = json.loads(row["text_items_json"] or "[]") if row else []
    kept = sorted((i for i in items if i.get("relevant")), key=lambda i: i["published_at"], reverse=True)
    block["relevant_items"] = relevant
    block["sources"] = [
        {
            "source": SOURCE_LABELS.get(i["source"], i["source"]),
            "url": i["item_url"],
            "published_at": iso_utc(i["published_at"]),
        }
        for i in kept[:MAX_SOURCES]
    ]
    caveats = []
    if row is None:
        caveats.append("The text classifier call failed today; text fields are blank.")
    elif relevant == 0:
        caveats.append("No relevant news text was found; text fields are blank.")
    elif below:
        caveats.append("The text classifier was below its confidence threshold for: " + ", ".join(below) + ".")
    return block, caveats


def player_object(case: Case, row: dict | None) -> dict[str, Any]:
    text, text_caveats = text_block(row)
    caveats = []
    if case.designation_source in SOURCE_CAVEATS:
        caveats.append(SOURCE_CAVEATS[case.designation_source])
    if case.prior_lane in LANE_CAVEATS:
        caveats.append(LANE_CAVEATS[case.prior_lane])
    if any("snap counts not available yet" in line for line in case.recent_games):
        caveats.append("Snap counts for his most recent game are not loaded yet.")
    caveats.extend(text_caveats)
    designation = case.sleeper_status if case.designation_source == "sleeper" else case.designation
    practice = None if case.practice_status in (None, "", "NONE") else PRACTICE_LABELS.get(case.practice_status, case.practice_status)
    return {
        "gsis_id": case.gsis_id or None,
        "sleeper_player_id": str(case.sleeper_player_id),
        "player_name": case.player_name,
        "team": sleeper_team(case.team),
        "position": case.position,
        "designation": designation,
        "designation_source": case.designation_source,
        "practice": practice,
        "body_part": case.body_part or None,
        "next_game": {"opponent": sleeper_team(case.opponent), "kickoff_utc": iso_utc(case.kickoff_utc)},
        "base_rate": {
            "p_play_next_game": _prob(case.prior_play),
            "missed_bucket": {k: _prob(case.feed_buckets[k]) for k in MISSED_BUCKETS},
        },
        "text": text,
        "caveats": caveats,
    }


def feed_eligible(case: Case) -> bool:
    return bool(case.sleeper_player_id) and case.prior_play is not None and bool(case.feed_buckets)


def build_dataset(
    entries: Iterable[tuple[Case, dict | None]],
    *,
    generated_at: datetime,
    decision_date: date,
    season: int,
    week: int,
    base_rate_versions: Iterable[str],
    jev_models: Iterable[str],
) -> dict[str, Any]:
    players = [player_object(case, row) for case, row in entries if feed_eligible(case)]
    players.sort(key=lambda p: (p["team"] or "", p["player_name"], p["sleeper_player_id"]))
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": iso_utc(generated_at),
        "decision_date": decision_date.isoformat(),
        "season": season,
        "week": week,
        "models": {
            "base_rates": ",".join(dict.fromkeys(v for v in base_rate_versions if v)),
            "jev_question_set": QUESTION_SET_VERSION,
            "jev_model": ",".join(sorted({m for m in jev_models if m})),
        },
        "players": players,
    }


def _check(ok: bool, message: str, errors: list[str]) -> None:
    if not ok:
        errors.append(message)


def _is_prob(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0.0 <= value <= 1.0 and round(value, 3) == value


def validate_dataset(data: Any) -> None:
    """Raise ValueError listing every violation of the fixed availability-1.0 schema."""
    errors: list[str] = []
    if not isinstance(data, dict):
        raise ValueError("dataset must be an object")
    _check(set(data) == TOP_KEYS, f"top-level keys {sorted(set(data) ^ TOP_KEYS)} differ", errors)
    _check(data.get("schema_version") == SCHEMA_VERSION, "schema_version must be availability-1.0", errors)
    _check(isinstance(data.get("generated_at"), str) and bool(ISO_UTC_RE.match(data["generated_at"])), "generated_at must be ISO 8601 UTC", errors)
    try:
        date.fromisoformat(data.get("decision_date") or "")
        _check(len(data["decision_date"]) == 10, "decision_date must be YYYY-MM-DD", errors)
    except (TypeError, ValueError):
        errors.append("decision_date must be YYYY-MM-DD")
    _check(isinstance(data.get("season"), int) and not isinstance(data.get("season"), bool), "season must be an integer", errors)
    week = data.get("week")
    _check(isinstance(week, int) and not isinstance(week, bool) and 1 <= week <= 22, "week must be an integer 1-22", errors)
    models = data.get("models")
    _check(
        isinstance(models, dict) and set(models) == {"base_rates", "jev_question_set", "jev_model"}
        and all(isinstance(v, str) and v for v in models.values()),
        "models must carry non-empty base_rates, jev_question_set, jev_model",
        errors,
    )
    players = data.get("players")
    if not isinstance(players, list):
        errors.append("players must be a list")
        players = []
    keys = []
    for index, p in enumerate(players):
        where = f"players[{index}]"
        if not isinstance(p, dict):
            errors.append(f"{where} must be an object")
            continue
        _check(set(p) == PLAYER_KEYS, f"{where} keys {sorted(set(p) ^ PLAYER_KEYS)} differ", errors)
        _check(p.get("gsis_id") is None or (isinstance(p["gsis_id"], str) and bool(GSIS_RE.match(p["gsis_id"]))), f"{where}.gsis_id", errors)
        for field in ("sleeper_player_id", "player_name", "team", "position", "designation"):
            _check(isinstance(p.get(field), str) and bool(p[field]), f"{where}.{field} must be a non-empty string", errors)
        _check(p.get("designation_source") in DESIGNATION_SOURCES, f"{where}.designation_source", errors)
        for field in ("practice", "body_part"):
            _check(p.get(field) is None or (isinstance(p[field], str) and bool(p[field])), f"{where}.{field}", errors)
        game = p.get("next_game")
        _check(
            game is None or (
                isinstance(game, dict) and set(game) == {"opponent", "kickoff_utc"}
                and isinstance(game["opponent"], str) and bool(game["opponent"])
                and isinstance(game["kickoff_utc"], str) and bool(ISO_UTC_RE.match(game["kickoff_utc"]))
            ),
            f"{where}.next_game",
            errors,
        )
        base = p.get("base_rate")
        if isinstance(base, dict) and set(base) == {"p_play_next_game", "missed_bucket"}:
            _check(_is_prob(base["p_play_next_game"]), f"{where}.base_rate.p_play_next_game", errors)
            bucket = base["missed_bucket"]
            _check(
                isinstance(bucket, dict) and set(bucket) == set(MISSED_BUCKETS)
                and all(_is_prob(v) for v in bucket.values()) and abs(sum(bucket.values()) - 1.0) <= 0.01,
                f"{where}.base_rate.missed_bucket",
                errors,
            )
        else:
            errors.append(f"{where}.base_rate")
        text = p.get("text")
        if isinstance(text, dict) and set(text) == TEXT_KEYS:
            for question, options in TEXT_ENUMS.items():
                value, confidence = text[question], text[f"{question}_confidence"]
                _check(value is None or value in options, f"{where}.text.{question}", errors)
                _check((value is None) == (confidence is None), f"{where}.text.{question}_confidence must be null exactly when the value is", errors)
                _check(confidence is None or _is_prob(confidence), f"{where}.text.{question}_confidence", errors)
            relevant = text["relevant_items"]
            _check(isinstance(relevant, int) and not isinstance(relevant, bool) and relevant >= 0, f"{where}.text.relevant_items", errors)
            sources = text["sources"]
            _check(isinstance(sources, list) and len(sources) <= MAX_SOURCES, f"{where}.text.sources at most {MAX_SOURCES}", errors)
            for source in sources if isinstance(sources, list) else []:
                _check(
                    isinstance(source, dict) and set(source) == {"source", "url", "published_at"}
                    and isinstance(source["source"], str) and bool(source["source"])
                    and isinstance(source["url"], str) and source["url"].startswith("http")
                    and isinstance(source["published_at"], str) and bool(ISO_UTC_RE.match(source["published_at"])),
                    f"{where}.text.sources entry",
                    errors,
                )
            if isinstance(relevant, int) and isinstance(sources, list):
                _check(len(sources) <= relevant, f"{where}.text.sources exceed relevant_items", errors)
                if relevant == 0:
                    _check(all(text[q] is None for q in TEXT_ENUMS), f"{where}.text must be null without relevant text", errors)
        else:
            errors.append(f"{where}.text")
        caveats = p.get("caveats")
        _check(isinstance(caveats, list) and all(isinstance(c, str) and c for c in caveats), f"{where}.caveats", errors)
        keys.append((p.get("team") or "", p.get("player_name") or "", p.get("sleeper_player_id") or ""))
    _check(keys == sorted(keys), "players must be sorted by team then player_name", errors)
    _check(len({k[2] for k in keys}) == len(keys), "sleeper_player_id must be unique", errors)
    if errors:
        raise ValueError("availability dataset invalid: " + "; ".join(errors[:20]))


def manifest_entry(content: bytes, dataset: dict[str, Any], *, omitted: int, bucket: str = DEFAULT_BUCKET) -> dict[str, Any]:
    digest = sha256_hex(content)
    object_name = f"v1/datasets/{DATASET_ID}/sha256-{digest}.json"
    return {
        "dataset": DATASET_ID,
        "dataset_version": f"{DATASET_ID}-{dataset['decision_date']}-{digest[:12]}",
        "schema_version": SCHEMA_VERSION,
        "source_generated_at": dataset["generated_at"],
        "decision_date": dataset["decision_date"],
        "week": dataset["week"],
        "object": object_name,
        "url": f"https://storage.googleapis.com/{bucket}/{object_name}",
        "sha256": digest,
        "bytes": len(content),
        "player_count": len(dataset["players"]),
        "warnings": [f"{omitted} injured players without a Sleeper id or a base-rate prior were omitted"] if omitted else [],
    }


def write_artifacts(dataset: dict[str, Any], *, omitted: int, out_dir: Path = FEED_DIR) -> dict[str, Any]:
    """Validate, then write the object and its manifest entry (entry last, each atomically)."""
    validate_dataset(dataset)
    content = canonical_json_bytes(dataset)
    entry = manifest_entry(content, dataset, omitted=omitted)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in ((f"{DATASET_ID}.json", content), (f"{DATASET_ID}.manifest-entry.json", canonical_json_bytes(entry))):
        temp = out_dir / f".{name}.tmp"
        temp.write_bytes(payload)
        os.replace(temp, out_dir / name)
    return entry
