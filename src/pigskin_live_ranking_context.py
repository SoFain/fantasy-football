"""Live ranking context helpers for grounded Pigskin chat answers."""

from __future__ import annotations

import re
from typing import Any

from src import player_profile_ranking_profiles as profiles


DEFAULT_RANKING_CONTEXT_LIMIT = 10
MAX_RANKING_CONTEXT_LIMIT = 50

TOP_N_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "fifteen": 15,
    "twenty": 20,
    "twenty five": 25,
    "twenty-five": 25,
}

PROFILE_PATTERNS = (
    ("gng_keeper", re.compile(r"\bgng(?:\s+keeper)?\b|\bkeeper\b", re.IGNORECASE)),
    ("half_ppr", re.compile(r"\bhalf[-\s]?ppr\b", re.IGNORECASE)),
    ("ppr", re.compile(r"\bppr\b", re.IGNORECASE)),
    ("standard", re.compile(r"\bstandard\b", re.IGNORECASE)),
)


def is_live_ranking_question(prompt: str) -> bool:
    text = str(prompt or "").lower()
    if not text.strip():
        return False
    ranking_terms = (
        "top ",
        "top-",
        "rank",
        "ranking",
        "rankings",
        "current ranks",
        "current ranking",
        "your ranks",
        "your rankings",
        "overall players",
        "overall board",
        "draft board",
    )
    return any(term in text for term in ranking_terms)


def parse_requested_limit(prompt: str) -> int:
    text = str(prompt or "").lower()
    numeric_match = re.search(r"\btop[-\s]+(\d{1,3})\b", text)
    if numeric_match:
        return _clamp_limit(int(numeric_match.group(1)))
    for word, value in TOP_N_WORDS.items():
        if re.search(rf"\btop[-\s]+{re.escape(word)}\b", text):
            return _clamp_limit(value)
    if "top players" in text or "top overall" in text or "overall players" in text:
        return DEFAULT_RANKING_CONTEXT_LIMIT
    return DEFAULT_RANKING_CONTEXT_LIMIT


def parse_scoring_profile(prompt: str) -> str:
    text = str(prompt or "")
    for profile_id, pattern in PROFILE_PATTERNS:
        if pattern.search(text):
            return profile_id
    return profiles.PLAYER_PROFILE_SCORING_PROFILE_DEFAULT


def parse_board(prompt: str) -> str:
    text = str(prompt or "").upper()
    if "OVERALL" in text or "ALL" in text or "DRAFT BOARD" in text:
        return profiles.PLAYER_PROFILE_DEFAULT_BOARD
    for position in ("QB", "RB", "WR", "TE"):
        if re.search(rf"\b{position}\b", text):
            return position
    return profiles.PLAYER_PROFILE_DEFAULT_BOARD


def build_live_ranking_context_request(prompt: str) -> dict[str, Any] | None:
    if not is_live_ranking_question(prompt):
        return None
    return {
        "scoring_profile_id": parse_scoring_profile(prompt),
        "board": parse_board(prompt),
        "limit": parse_requested_limit(prompt),
    }


def format_live_ranking_context_for_prompt(
    rankings: list[dict[str, Any]],
    *,
    scoring_profile_id: str,
    board: str,
    requested_limit: int,
) -> str:
    if not rankings:
        return (
            "### Live Ranking Board Context ###\n"
            f"Requested board: {scoring_profile_id} {board}, top {requested_limit}.\n"
            "The live Current Pigskin ranking rows were not available. "
            "Do not guess, synthesize, or infer the ranking order. Tell the user the live board was unavailable."
        )

    lines = [
        "### Live Ranking Board Context ###",
        f"Active source: Current Pigskin live rows from analytics_pigskin_rankings.",
        f"Scoring profile: {scoring_profile_id}.",
        f"Board: {board}.",
        f"Requested limit: {requested_limit}.",
        "Use the rows below as the source of truth.",
        "Preserve this exact board order. Do not reorder by formula weights, position, media consensus, BQML output, or vibes.",
        "Do not claim BQML, NGS, Stats02, PBP, injury, availability, or a formula champion is active.",
        "For factual rank-defense answers, do not use bracketed stage directions such as [mocking], [laughs], [deadpan], or [sarcastic].",
        "",
        "| board_rank | player | pos | team | position_rank | score | tier | rationale | risk_flags |",
        "|---:|---|---|---|---:|---:|---|---|---|",
    ]
    for row in rankings:
        lines.append(
            "| {board_rank} | {player} | {position} | {team} | {position_rank} | {score} | {tier} | {rationale} | {risk_flags} |".format(
                board_rank=_clean_cell(row.get("board_rank")),
                player=_clean_cell(row.get("player_name")),
                position=_clean_cell(row.get("position")),
                team=_clean_cell(row.get("team") or row.get("current_team") or row.get("sleeper_team")),
                position_rank=_clean_cell(row.get("position_rank") or row.get("pigskin_rank")),
                score=_format_number(row.get("pigskin_score") or row.get("pigskin_ranking_score")),
                tier=_clean_cell(row.get("tier") or row.get("pigskin_tier")),
                rationale=_clean_cell(row.get("rank_rationale")),
                risk_flags=_clean_cell(row.get("risk_flags")),
            )
        )
    return "\n".join(lines)


def _clamp_limit(value: int) -> int:
    return max(1, min(MAX_RANKING_CONTEXT_LIMIT, int(value)))


def _format_number(value: Any) -> str:
    if value is None:
        return ""
    try:
        return f"{float(value):.2f}"
    except (TypeError, ValueError):
        return _clean_cell(value)


def _clean_cell(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("|", "/").replace("\n", " ").strip()
    return text[:240]
