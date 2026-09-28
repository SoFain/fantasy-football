"""Candidate injury text for the availability pilot.

Sources (headlines and short summaries, for internal classification only):
  - DraftSharks injury news RSS, the same public feed the GNG site's news wire
    uses. New items are archived in availability_text_items at first sight so
    later runs and retro checks see the text as it was first collected.
  - team_news_items (team blog RSS, collected daily since 2026-08-07).

Matching is deliberately loose (full name, feed keywords, or surname within the
player's own team feed). The Jev relevance question drops items that are not
about the player's injury, so this stage favors recall.
"""

from __future__ import annotations

import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Iterable

DRAFTSHARKS_INJURY_FEED_URL = "https://www.draftsharks.com/rss/injury-news"
DRAFTSHARKS_SOURCE = "draftsharks_injury_news"
TEAM_NEWS_SOURCE = "team_news_items"
MAX_FEED_BYTES = 1_048_576
SUMMARY_CHARS = 300
SNIPPET_RADIUS = 220
NAME_SUFFIXES = {"jr", "sr", "ii", "iii", "iv", "v"}
MEDIA_NS = "{http://search.yahoo.com/mrss/}"


def clean_text(value: str | None) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", value or ""))
    return re.sub(r"\s+", " ", text).strip()


def name_tokens(name: str) -> list[str]:
    tokens = re.sub(r"[^a-z0-9 ]+", " ", (name or "").lower().replace("'", "")).split()
    return [t for t in tokens if t not in NAME_SUFFIXES]


def normalized(text: str) -> str:
    return " " + " ".join(re.sub(r"[^a-z0-9 ]+", " ", (text or "").lower().replace("'", "")).split()) + " "


def parse_draftsharks_rss(xml_text: str, fetched_at: datetime) -> list[dict]:
    root = ET.fromstring(xml_text)
    items: list[dict] = []
    for node in root.iter("item"):
        link = (node.findtext("link") or "").strip()
        pub = node.findtext("pubDate")
        if not link or not pub:
            continue
        keywords = [k.strip() for k in (node.findtext(f"{MEDIA_NS}keywords") or "").split(",") if k.strip()]
        items.append(
            {
                "source": DRAFTSHARKS_SOURCE,
                "feed_url": DRAFTSHARKS_INJURY_FEED_URL,
                "item_url": link,
                "title": clean_text(node.findtext("title"))[:300],
                "summary": clean_text(node.findtext("description"))[:SUMMARY_CHARS],
                "keywords": keywords,
                "published_at": parsedate_to_datetime(pub).astimezone(timezone.utc).isoformat(),
                "first_seen_at": fetched_at.astimezone(timezone.utc).isoformat(),
            }
        )
    return items


def fetch_draftsharks(now: datetime | None = None) -> list[dict]:
    request = urllib.request.Request(
        DRAFTSHARKS_INJURY_FEED_URL, headers={"User-Agent": "PigskinAvailabilityPilot/1.0 (internal classification)"}
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        body = response.read(MAX_FEED_BYTES + 1)
    if len(body) > MAX_FEED_BYTES:
        raise ValueError("DraftSharks feed exceeded the byte cap")
    return parse_draftsharks_rss(body.decode("utf-8", errors="replace"), now or datetime.now(timezone.utc))


def text_item_schema() -> list:
    from google.cloud import bigquery as b

    return [
        b.SchemaField("source", "STRING"), b.SchemaField("feed_url", "STRING"), b.SchemaField("item_url", "STRING"),
        b.SchemaField("title", "STRING"), b.SchemaField("summary", "STRING"),
        b.SchemaField("keywords", "STRING", mode="REPEATED"),
        b.SchemaField("published_at", "TIMESTAMP"), b.SchemaField("first_seen_at", "TIMESTAMP"),
    ]


def archive_new_items(bq: Any, items: list[dict]) -> int:
    """Append items not archived yet. Existing rows are never rewritten (first-seen text wins)."""
    from google.cloud import bigquery

    from src.availability_bq import load_rows, query, table_id

    bq.create_table(bigquery.Table(table_id("availability_text_items"), schema=text_item_schema()), exists_ok=True)
    known = {
        (r["source"], r["item_url"])
        for r in query(bq, f"SELECT source, item_url FROM `{table_id('availability_text_items')}`")
    }
    fresh = [i for i in {(i["source"], i["item_url"]): i for i in items}.values() if (i["source"], i["item_url"]) not in known]
    if fresh:
        load_rows(bq, "availability_text_items", fresh, text_item_schema(), truncate=False)
    return len(fresh)


def load_candidate_text(bq: Any, since: datetime, until: datetime) -> list[dict]:
    from google.cloud import bigquery

    from src.availability_bq import query, table_id

    params = [
        bigquery.ScalarQueryParameter("since", "TIMESTAMP", since),
        bigquery.ScalarQueryParameter("until", "TIMESTAMP", until),
    ]
    rows = query(
        bq,
        f"""
SELECT source, item_url, CAST(NULL AS STRING) AS team, title, summary, keywords, published_at
FROM `{table_id('availability_text_items')}`
WHERE published_at >= @since AND published_at < @until
UNION ALL
SELECT '{TEAM_NEWS_SOURCE}', item_url, ANY_VALUE(team), ANY_VALUE(title), ANY_VALUE(summary), [], MIN(published_at)
FROM `{table_id('team_news_items')}`
WHERE published_at >= @since AND published_at < @until
GROUP BY item_url
""",
        params,
    )
    for row in rows:
        row["title"] = clean_text(row.get("title"))
        row["summary"] = clean_text(row.get("summary"))
    return rows


def snippet(text: str, tokens: list[str]) -> str:
    """Window of text around the first mention of the player's surname (code-cut, not model-cut)."""
    if not text:
        return ""
    lowered = text.lower()
    position = -1
    for token in (" ".join(tokens), tokens[-1] if tokens else ""):
        if token:
            position = lowered.find(token)
            if position >= 0:
                break
    if position < 0:
        return text[: 2 * SNIPPET_RADIUS]
    start = max(0, position - SNIPPET_RADIUS)
    return ("..." if start else "") + text[start : position + SNIPPET_RADIUS] + ("..." if position + SNIPPET_RADIUS < len(text) else "")


def match_player_items(
    player_name: str,
    team: str | None,
    items: Iterable[dict],
    as_of: datetime,
    window_days: int = 10,
    max_items: int = 8,
) -> list[dict]:
    tokens = name_tokens(player_name)
    if len(tokens) < 2:
        return []
    full = " " + " ".join(tokens) + " "
    surname = " " + tokens[-1] + " "
    earliest = as_of - timedelta(days=window_days)
    matches: list[tuple[int, datetime, dict]] = []
    for item in items:
        published = item["published_at"]
        if isinstance(published, str):
            published = datetime.fromisoformat(published)
        if not (earliest <= published < as_of):
            continue
        body = normalized(f"{item.get('title', '')} {item.get('summary', '')}")
        keyword_hit = any(normalized(k) == full for k in item.get("keywords") or [])
        if keyword_hit or full in body:
            strength = 2
        elif item.get("team") == team and len(tokens[-1]) >= 4 and surname in body:
            strength = 1
        else:
            continue
        matches.append((strength, published, item))
    matches.sort(key=lambda m: (m[0], m[1]), reverse=True)
    out = []
    for strength, published, item in matches[:max_items]:
        text = item.get("summary") or ""
        out.append(
            {
                "source": item["source"],
                "item_url": item["item_url"],
                "published_at": published,
                "title": item.get("title", "")[:300],
                "text": snippet(text, tokens) if item["source"] == TEAM_NEWS_SOURCE else text[:SUMMARY_CHARS],
                "match": "name" if strength == 2 else "surname_team_feed",
            }
        )
    out.sort(key=lambda i: i["published_at"])
    return out
