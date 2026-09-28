"""Team beat-writer news feeds, fetched in response to player status changes.

These are SB Nation team blogs. They are commentary, not an authoritative
injury source: treat items as context to investigate a flag, never as the flag
itself. The authoritative status is whatever Sleeper reports.

Feeds are only fetched for teams that actually had a watched change, so a quiet
day costs zero requests and the worst case is 32.

Parsing uses the standard library rather than a feedparser dependency. SB
Nation serves Atom; the RSS branch is there because feed formats drift.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Iterable, Mapping
from xml.etree import ElementTree

logger = logging.getLogger("team_news_feeds")

# Keyed by the team abbreviations used in sleeper_players_current.
TEAM_FEEDS: dict[str, str] = {
    # AFC East
    "BUF": "https://www.buffalorumblings.com/rss/index.xml",
    "MIA": "https://www.thephinsider.com/rss/index.xml",
    "NE": "https://www.patspulpit.com/rss/index.xml",
    "NYJ": "https://www.ganggreennation.com/rss/index.xml",
    # AFC North
    "BAL": "https://www.baltimorebeatdown.com/rss/index.xml",
    "CIN": "https://www.cincyjungle.com/rss/index.xml",
    "CLE": "https://www.dawgsbynature.com/rss/index.xml",
    "PIT": "https://www.behindthesteelcurtain.com/rss/index.xml",
    # AFC South
    "HOU": "https://www.battleredblog.com/rss/index.xml",
    "IND": "https://www.stampedeblue.com/rss/index.xml",
    "JAX": "https://www.bigcatcountry.com/rss/index.xml",
    "TEN": "https://www.musiccitymiracles.com/rss/index.xml",
    # AFC West
    "DEN": "https://www.milehighreport.com/rss/index.xml",
    "KC": "https://www.arrowheadpride.com/rss/index.xml",
    "LV": "https://www.silverandblackpride.com/rss/index.xml",
    "LAC": "https://www.boltsfromtheblue.com/rss/index.xml",
    # NFC East
    "DAL": "https://www.bloggingtheboys.com/rss/index.xml",
    "NYG": "https://www.bigblueview.com/rss/index.xml",
    "PHI": "https://www.bleedinggreennation.com/rss/index.xml",
    "WAS": "https://www.hogshaven.com/rss/index.xml",
    # NFC North
    "CHI": "https://www.windycitygridiron.com/rss/index.xml",
    "DET": "https://www.prideofdetroit.com/rss/index.xml",
    "GB": "https://www.acmepackingcompany.com/rss/index.xml",
    "MIN": "https://www.dailynorseman.com/rss/index.xml",
    # NFC South
    "ATL": "https://www.thefalcoholic.com/rss/index.xml",
    "CAR": "https://www.catscratchreader.com/rss/index.xml",
    "NO": "https://www.canalstreetchronicles.com/rss/index.xml",
    "TB": "https://www.bucsnation.com/rss/index.xml",
    # NFC West
    "ARI": "https://www.revengeofthebirds.com/rss/index.xml",
    "LAR": "https://www.turfshowtimes.com/rss/index.xml",
    "SF": "https://www.ninersnation.com/rss/index.xml",
    "SEA": "https://www.fieldgulls.com/rss/index.xml",
}

ATOM_NS = "{http://www.w3.org/2005/Atom}"

DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_ITEMS_PER_TEAM = 25
# Beat coverage of a status change lands within a day or two. Older items are
# almost always unrelated to the change that triggered the fetch.
DEFAULT_MAX_ITEM_AGE_DAYS = 7

_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}


def normalize_name(value: str | None) -> str:
    """Casefold, strip accents and punctuation, drop generational suffixes.

    Apostrophes are deleted rather than spaced, so "Ja'Marr" normalizes to
    "jamarr" and still matches a feed that writes it without the apostrophe.
    Hyphens and periods become spaces, so "Amon-Ra St. Brown" keeps its word
    boundaries.
    """
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(value))
    ascii_only = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    without_apostrophes = re.sub(r"['’ʼ`]", "", ascii_only.lower())
    cleaned = re.sub(r"[^a-z\s]", " ", without_apostrophes)
    parts = [p for p in cleaned.split() if p and p not in _SUFFIXES]
    return " ".join(parts)


def _text(node: Any, *paths: str) -> str | None:
    for path in paths:
        found = node.find(path)
        if found is not None:
            if found.text and found.text.strip():
                return found.text.strip()
            href = found.get("href")
            if href:
                return href.strip()
    return None


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    try:
        # Atom: ISO 8601, often with a trailing Z.
        return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        pass
    try:
        # RSS: RFC 822.
        return parsedate_to_datetime(text).astimezone(timezone.utc)
    except (TypeError, ValueError):
        logger.debug("Unparseable feed timestamp: %r", value)
        return None


def parse_feed(xml_text: str) -> list[dict[str, Any]]:
    """Parse an Atom or RSS document into normalized item dictionaries.

    Returns an empty list for malformed XML rather than raising: one broken
    feed must not fail the whole run.
    """
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        logger.warning("Skipping unparseable feed: %s", exc)
        return []

    items: list[dict[str, Any]] = []

    for entry in root.findall(f"{ATOM_NS}entry"):
        items.append({
            "title": _text(entry, f"{ATOM_NS}title"),
            "url": _text(entry, f"{ATOM_NS}link"),
            "summary": _text(entry, f"{ATOM_NS}summary", f"{ATOM_NS}content"),
            "author": _text(entry, f"{ATOM_NS}author/{ATOM_NS}name"),
            "published_at": _parse_timestamp(
                _text(entry, f"{ATOM_NS}published", f"{ATOM_NS}updated")
            ),
        })

    for item in root.findall(".//item"):
        items.append({
            "title": _text(item, "title"),
            "url": _text(item, "link"),
            "summary": _text(item, "description"),
            "author": _text(item, "author"),
            "published_at": _parse_timestamp(_text(item, "pubDate")),
        })

    return [item for item in items if item.get("title") or item.get("url")]


def filter_recent(
    items: Iterable[Mapping[str, Any]],
    *,
    now: datetime,
    max_age_days: int = DEFAULT_MAX_ITEM_AGE_DAYS,
    max_items: int = DEFAULT_MAX_ITEMS_PER_TEAM,
) -> list[dict[str, Any]]:
    """Newest first, dropping anything older than the window.

    Items with no parseable timestamp are kept: a missing date is more likely a
    feed quirk than an old article, and dropping them loses real coverage.
    """
    kept = []
    for item in items:
        published = item.get("published_at")
        if published is not None:
            age_days = (now - published).total_seconds() / 86400
            if age_days > max_age_days:
                continue
        kept.append(dict(item))
    kept.sort(key=lambda i: (i.get("published_at") is not None, i.get("published_at") or now), reverse=True)
    return kept[:max_items]


def match_players(
    items: Iterable[Mapping[str, Any]],
    players: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Attach matching players to each item by full-name match.

    Full name only. Last-name matching produces far too many false positives on
    team blogs, where surnames like "Smith" or "Williams" appear constantly.
    """
    indexed = []
    for player in players:
        normalized = normalize_name(player.get("player_name"))
        if normalized and " " in normalized:
            indexed.append((normalized, player))

    matched = []
    for item in items:
        haystack = normalize_name(f"{item.get('title') or ''} {item.get('summary') or ''}")
        hits = [player for name, player in indexed if name in haystack]
        enriched = dict(item)
        enriched["matched_players"] = hits
        matched.append(enriched)
    return matched


def fetch_team_feed(
    team: str,
    *,
    timeout: int = DEFAULT_TIMEOUT_SECONDS,
    session: Any | None = None,
) -> list[dict[str, Any]]:
    """Fetch and parse one team's feed. Returns [] on any network failure."""
    url = TEAM_FEEDS.get(team)
    if not url:
        logger.warning("No configured news feed for team %r", team)
        return []

    import requests

    getter = session.get if session is not None else requests.get
    try:
        response = getter(url, timeout=timeout, headers={"User-Agent": "pigskin-news/1.0"})
        response.raise_for_status()
    except Exception as exc:
        # One unreachable blog must not fail the run for the other 31 teams.
        logger.warning("Failed to fetch %s feed at %s: %s", team, url, exc)
        return []

    items = parse_feed(response.text)
    for item in items:
        item["team"] = team
        item["feed_url"] = url
    return items
