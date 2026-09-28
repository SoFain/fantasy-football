"""Jev decision stage for the availability pilot (log-only, context only).

Code builds every fact in the state: dates, weekdays, day counts, schedule,
games remaining, recent snap history, and the base-rate prior as plain text.
Jev answers only judgment questions over that state and the candidate text.
Below a question's confidence threshold the field is left blank and the miss
is logged; nothing downstream may read a blank field.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

QUESTION_SET_VERSION = "availability_qs_v1"
JEV_MODEL = "jev-latest"
# Jev bills input tokens only (docs.typesafe.ai/models, jev-1.13.0: $0.042 per million input tokens).
USD_PER_INPUT_TOKEN = 0.042 / 1_000_000
EASTERN = ZoneInfo("America/New_York")
MAX_TEXT_ITEMS = 8

AVAILABILITY_OPTIONS = {
    "will_play": "He is expected to play in his next game.",
    "game_time_decision": "It is genuinely uncertain whether he will play in his next game; the decision is expected close to kickoff.",
    "will_miss": "He is expected to miss his next game, or he has already been ruled out of it.",
}
ABSENCE_OPTIONS = {
    "0": "He is expected to miss no games: he plays in his next game.",
    "1": "He is expected to miss exactly one game: the next game, then return for the game after it.",
    "2_4": "He is expected to miss a few games: more than one game but no more than about a month.",
    "5_plus_or_season": "He is expected to miss a long stretch: five or more games, a long injured reserve stay, or the rest of the season.",
}
TREND_OPTIONS = {
    "improving": "The newest information shows him getting healthier, for example practicing more, a better designation, or positive recovery news.",
    "unchanged": "The newest information shows no change from before.",
    "worsening": "The newest information shows a setback, for example practicing less, a worse designation, a new injury, surgery, or injured reserve.",
    "unknown": "The state does not contain enough information to tell the direction.",
}
# Thresholds are fixed before any retro scoring, from TypeSafe's published guidance
# (confidence = (n * peak - 1) / (n - 1)). Context-only use means a wrong value costs a
# misleading sentence, not a rank move, so the floors sit a little above the docs' 0.5
# "genuinely uncertain" floor for the 3-way availability call and at it for the 4-way calls.
THRESHOLDS = {
    "availability": 0.60,  # 3 options: top option needs probability >= 0.733
    "absence": 0.50,       # 4 options: top option needs probability >= 0.625
    "trend": 0.50,         # 4 options: top option needs probability >= 0.625
    "relevance": 0.50,     # noul: keep an item when P(yes) >= 0.5 (both errors equally costly)
}


def long_date(value: date | datetime) -> str:
    if isinstance(value, datetime):
        value = value.astimezone(EASTERN).date()
    return f"{value.strftime('%A')}, {value.strftime('%B')} {value.day}, {value.year}"


def day_phrase(days: int) -> str:
    if days == 0:
        return "today"
    if days == 1:
        return "tomorrow"
    if days == -1:
        return "yesterday"
    return f"in {days} days" if days > 0 else f"{-days} days ago"


def days_between(earlier: datetime | date, later: datetime | date) -> int:
    def as_date(v: datetime | date) -> date:
        return v.astimezone(EASTERN).date() if isinstance(v, datetime) else v

    return (as_date(later) - as_date(earlier)).days


def percent(p: float) -> str:
    return f"{round(100 * p)} percent"


def prior_text(prior_play: float, prior_buckets: dict[str, float] | None, lane_description: str) -> str:
    text = f"Historical base rate ({lane_description}): {percent(prior_play)} of comparable players played the next game."
    if prior_buckets:
        text += (
            f" Games missed from the next game: none {percent(prior_buckets['0'])}, one {percent(prior_buckets['1'])},"
            f" two to four {percent(prior_buckets['2_4'])}, five or more or the rest of the season"
            f" {percent(prior_buckets['5_plus_or_season'])}."
        )
    return text


@dataclass
class Case:
    """Every fact about one injured player, assembled by code before any model call."""

    gsis_id: str
    sleeper_player_id: str | None
    player_name: str
    team: str
    team_name: str
    position: str
    as_of: datetime
    season: int
    target_week: int
    target_game_id: str
    kickoff_utc: datetime
    opponent_name: str
    is_home: bool
    games_remaining: int
    official_report: str
    sleeper_status: str | None
    sleeper_body_part: str | None
    sleeper_note: str | None
    sleeper_practice: str | None
    sleeper_listed_since: datetime | None
    recent_games: list[str]
    prior_lane: str
    prior_lane_description: str
    prior_play: float
    prior_buckets: dict[str, float] | None
    text_items: list[dict]
    designation: str
    practice_status: str
    body_part: str | None
    # Feed and provenance fields; none of them enters the Jev state for a skill player.
    opponent: str = ""
    sleeper_collected: bool = True  # False for positions the Sleeper snapshot does not store
    designation_source: str = "sleeper"  # sleeper, official_report, or team_roster
    base_rate_version: str = ""
    # Missed-bucket distribution from the next game for the public feed. Equals prior_buckets
    # when that lane has one; otherwise it comes from the next-game bucket lanes. Never in the state.
    feed_buckets: dict[str, float] | None = None


def build_state(case: Case) -> dict[str, Any]:
    kickoff_days = days_between(case.as_of, case.kickoff_utc)
    sleeper: dict[str, Any] = {
        "injury_designation": case.sleeper_status or "none listed",
        "body_part": case.sleeper_body_part or "not listed",
        "note": case.sleeper_note or "none",
        "practice_participation": case.sleeper_practice or "not listed",
    }
    if not case.sleeper_collected:
        sleeper = {"availability": "Sleeper data is not collected for this position."}
    elif case.sleeper_listed_since is not None:
        since_days = days_between(case.sleeper_listed_since, case.as_of)
        sleeper["listed_with_this_designation_since"] = (
            f"{long_date(case.sleeper_listed_since)} ({since_days} days before today)"
        )
    items = []
    for index, item in enumerate(case.text_items[:MAX_TEXT_ITEMS]):
        age = days_between(item["published_at"], case.as_of)
        items.append(
            {
                "id": f"news_items[{index}]",
                "source": "DraftSharks injury news" if item["source"] == "draftsharks_injury_news" else "team blog feed",
                "published": f"{long_date(item['published_at'])} ({day_phrase(-age) if age else 'today'})",
                "headline": item["title"],
                "text": item["text"],
            }
        )
    return {
        "player": {"name": case.player_name, "team": case.team_name, "position": case.position},
        "today": long_date(case.as_of),
        "next_game": {
            "season_and_week": f"{case.season} regular season, Week {case.target_week}",
            "date": f"{long_date(case.kickoff_utc)} ({day_phrase(kickoff_days)})",
            "opponent": case.opponent_name,
            "location": "home" if case.is_home else "away",
        },
        "team_regular_season_games_remaining_including_next": case.games_remaining,
        "official_injury_report": case.official_report,
        "sleeper": sleeper,
        "recent_games": case.recent_games or ["No earlier game this season."],
        "base_rate_prior": prior_text(case.prior_play, case.prior_buckets, case.prior_lane_description),
        "news_items": items,
    }


def build_questions(case: Case, item_count: int) -> dict[str, dict[str, Any]]:
    name = case.player_name
    questions: dict[str, dict[str, Any]] = {
        "availability": {
            "type": "choice",
            "instructions": f"Using the whole state, what is {name}'s availability for the game in `next_game`?",
            "criteria": AVAILABILITY_OPTIONS,
        },
        "absence": {
            "type": "choice",
            "instructions": f"Using the whole state, how many of his team's games is {name} expected to miss, counting from the game in `next_game`?",
            "criteria": ABSENCE_OPTIONS,
        },
        "trend": {
            "type": "choice",
            "instructions": f"Using the most recent information in the state, which way is {name}'s injury situation moving?",
            "criteria": TREND_OPTIONS,
        },
    }
    for index in range(min(item_count, MAX_TEXT_ITEMS)):
        questions[f"relevance_{index}"] = {
            "type": "noul",
            "instructions": f"Is `news_items[{index}]` about {name}'s own current injury or his availability to play?",
            "criteria": {
                "true": f"The item reports on {name}'s injury, practice participation, recovery, or whether he will play.",
                "false": f"The item is about someone else, or mentions {name} without any information about his injury or availability.",
            },
        }
    return questions


def input_hash(state: dict, questions: dict, model: str = JEV_MODEL) -> str:
    payload = json.dumps(
        {"state": state, "questions": questions, "model": model, "question_set": QUESTION_SET_VERSION},
        sort_keys=True,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def gate_choice(answer: dict | None, threshold: float) -> dict[str, Any]:
    """Apply a confidence floor. Below it the value is blank (None) and flagged."""
    if not answer:
        return {"value": None, "confidence": None, "probabilities": None, "blank": True, "top": None}
    confidence = float(answer.get("confidence") or 0.0)
    blank = confidence < threshold
    return {
        "value": None if blank else answer.get("choice"),
        "confidence": confidence,
        "probabilities": answer.get("probabilities"),
        "blank": blank,
        "top": answer.get("choice"),
    }


def relevant_items(case: Case, answers: dict[str, dict]) -> list[dict]:
    out = []
    for index, item in enumerate(case.text_items[:MAX_TEXT_ITEMS]):
        noul = (answers.get(f"relevance_{index}") or {}).get("noul")
        out.append(
            {
                "source": item["source"],
                "item_url": item["item_url"],
                "published_at": item["published_at"].isoformat() if isinstance(item["published_at"], datetime) else item["published_at"],
                "title": item["title"],
                "summary": item["text"][:300],
                "match": item.get("match"),
                "relevance": noul,
                "relevant": noul is not None and noul >= THRESHOLDS["relevance"],
            }
        )
    return out


def combined_play_probability(prior_play: float, availability: dict[str, Any], has_relevant_text: bool) -> float:
    """Fixed a priori combination rule used only for scoring what the text adds.

    When the availability answer is blank or no candidate item was judged
    relevant, the base rate stands. Otherwise Jev's will_play and will_miss
    mass is taken as stated and its game_time_decision mass is handed back to
    the base rate, which already encodes the designation. Not fitted on any data.
    """
    probabilities = availability.get("probabilities")
    if availability.get("blank") or not has_relevant_text or not probabilities:
        return prior_play
    return float(probabilities.get("will_play", 0.0)) + float(probabilities.get("game_time_decision", 0.0)) * prior_play


def decision_row(
    case: Case,
    *,
    run_mode: str,
    decision_date: date,
    state_hash: str,
    response: dict[str, Any],
    base_rate_version: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    answers = response.get("answers") or {}
    gated = {q: gate_choice(answers.get(q), THRESHOLDS[q]) for q in ("availability", "absence", "trend")}
    items = relevant_items(case, answers)
    relevant_count = sum(1 for i in items if i["relevant"])
    usage = response.get("usage") or {}
    input_tokens = int(usage.get("input_tokens") or 0)
    created_at = datetime.now().astimezone().isoformat()
    row = {
        "decision_date": decision_date.isoformat(),
        "run_mode": run_mode,
        "as_of_ts": case.as_of.isoformat(),
        "season": case.season,
        "target_week": case.target_week,
        "target_game_id": case.target_game_id,
        "kickoff_utc": case.kickoff_utc.isoformat(),
        "gsis_id": case.gsis_id,
        "sleeper_player_id": case.sleeper_player_id,
        "player_name": case.player_name,
        "team": case.team,
        "position": case.position,
        "designation": case.designation,
        "practice_status": case.practice_status,
        "body_part": case.body_part,
        "sleeper_injury_status": case.sleeper_status,
        "sleeper_injury_notes": case.sleeper_note,
        "prior_lane": case.prior_lane,
        "prior_play_prob": round(case.prior_play, 5),
        "prior_bucket_probs_json": json.dumps(case.prior_buckets) if case.prior_buckets else None,
        "combined_play_prob": round(combined_play_probability(case.prior_play, gated["availability"], relevant_count > 0), 5),
        "text_item_count": len(items),
        "relevant_text_count": relevant_count,
        "text_items_json": json.dumps(items, default=str),
        "question_set_version": QUESTION_SET_VERSION,
        "thresholds_json": json.dumps(THRESHOLDS, sort_keys=True),
        "base_rate_model_version": base_rate_version,
        "jev_model_version": response.get("model"),
        "request_id": response.get("request_id"),
        "input_hash": state_hash,
        "input_tokens": input_tokens,
        "output_tokens": int(usage.get("output_tokens") or 0),
        "cost_usd": round(input_tokens * USD_PER_INPUT_TOKEN, 8),
        "created_at": created_at,
    }
    misses = []
    for question, gate in gated.items():
        row[question] = gate["value"]
        row[f"{question}_probs_json"] = json.dumps(gate["probabilities"]) if gate["probabilities"] else None
        row[f"{question}_confidence"] = gate["confidence"]
        row[f"{question}_blank"] = gate["blank"]
        if gate["blank"]:
            misses.append(
                {
                    "decision_date": row["decision_date"],
                    "run_mode": run_mode,
                    "gsis_id": case.gsis_id,
                    "target_game_id": case.target_game_id,
                    "question": question,
                    "top_choice": gate["top"],
                    "confidence": gate["confidence"],
                    "threshold": THRESHOLDS[question],
                    "probs_json": row[f"{question}_probs_json"],
                    "question_set_version": QUESTION_SET_VERSION,
                    "jev_model_version": response.get("model"),
                    "created_at": created_at,
                }
            )
    return row, misses


def decision_schema() -> list:
    from google.cloud import bigquery as b

    s, i, f, bo, t = "STRING", "INT64", "FLOAT64", "BOOL", "TIMESTAMP"
    fields = [
        ("decision_date", "DATE"), ("run_mode", s), ("as_of_ts", t), ("season", i), ("target_week", i),
        ("target_game_id", s), ("kickoff_utc", t), ("gsis_id", s), ("sleeper_player_id", s), ("player_name", s),
        ("team", s), ("position", s), ("designation", s), ("practice_status", s), ("body_part", s),
        ("sleeper_injury_status", s), ("sleeper_injury_notes", s), ("prior_lane", s), ("prior_play_prob", f),
        ("prior_bucket_probs_json", s), ("combined_play_prob", f),
        ("availability", s), ("availability_probs_json", s), ("availability_confidence", f), ("availability_blank", bo),
        ("absence", s), ("absence_probs_json", s), ("absence_confidence", f), ("absence_blank", bo),
        ("trend", s), ("trend_probs_json", s), ("trend_confidence", f), ("trend_blank", bo),
        ("text_item_count", i), ("relevant_text_count", i), ("text_items_json", s),
        ("question_set_version", s), ("thresholds_json", s), ("base_rate_model_version", s),
        ("jev_model_version", s), ("request_id", s), ("input_hash", s), ("input_tokens", i), ("output_tokens", i),
        ("cost_usd", f), ("created_at", t),
    ]
    return [b.SchemaField(name, kind) for name, kind in fields]


def miss_schema() -> list:
    from google.cloud import bigquery as b

    s, f, t = "STRING", "FLOAT64", "TIMESTAMP"
    fields = [
        ("decision_date", "DATE"), ("run_mode", s), ("gsis_id", s), ("target_game_id", s), ("question", s),
        ("top_choice", s), ("confidence", f), ("threshold", f), ("probs_json", s),
        ("question_set_version", s), ("jev_model_version", s), ("created_at", t),
    ]
    return [b.SchemaField(name, kind) for name, kind in fields]


DECISION_KEY = ["decision_date", "run_mode", "gsis_id", "target_game_id"]
MISS_KEY = ["decision_date", "run_mode", "gsis_id", "target_game_id", "question"]
