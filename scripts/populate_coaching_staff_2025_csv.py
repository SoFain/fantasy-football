"""Populate data/coaching_staff_2025.csv from Wikipedia's 2025 season pages.

The current-staffs page only ever shows the present staff, so coaching-change
detection needs a season baseline. Each "2025 <Team> season" article carries
the head coach in its {{Infobox NFL team season}} `coach` parameter; that is
the one staff role reliably recorded per season, so the 2025 baseline is
head-coach-only. Offensive coordinators are not in the infobox and stay out
of change detection until a better historical source is curated.

Mid-season changes list multiple names; all are kept ('A; B') so the change
flag can ask "was the 2026 head coach any of the 2025 head coaches".

Usage:
    python scripts/populate_coaching_staff_2025_csv.py            # report
    python scripts/populate_coaching_staff_2025_csv.py --write    # rewrite CSV
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.coaching_staff import NFL_TEAMS  # noqa: E402

SEASON = 2025
PAGE_URL = "https://en.wikipedia.org/wiki/{year}_{name}_season?action=raw"
USER_AGENT = "PigskinCoachingStaff/1.0 (fantasy football research; contact: repo owner)"

COACH_PARAM = re.compile(r"^\|\s*coach\s*=\s*(.+)$", re.MULTILINE)
WIKILINK = re.compile(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]")
TEMPLATE = re.compile(r"\{\{[^{}]*\}\}")
HTML_TAG = re.compile(r"<[^>]+>")


def clean_coach_value(value: str) -> str:
    """'[[A]]<br>[[B]] {{small|(interim)}}' -> 'A; B'."""
    value = value.replace("<br>", ";").replace("<br/>", ";").replace("<br />", ";")
    value = WIKILINK.sub(r"\1", value)
    value = TEMPLATE.sub("", value)
    value = HTML_TAG.sub("", value)
    value = re.sub(r"\((?:interim|acting)[^)]*\)", "", value, flags=re.IGNORECASE)
    parts = [re.sub(r"\s+", " ", part).strip(" ,;") for part in value.split(";")]
    return "; ".join(part for part in parts if part)


def parse_head_coach(wikitext: str) -> str | None:
    match = COACH_PARAM.search(wikitext)
    if not match:
        return None
    return clean_coach_value(match.group(1)) or None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--csv", default=str(REPO_ROOT / "data" / "coaching_staff_2025.csv"))
    args = parser.parse_args()

    import requests

    session = requests.Session()
    rows, failures = [], []
    for abbr, (team_name, _conf, _div) in NFL_TEAMS.items():
        url = PAGE_URL.format(year=SEASON, name=team_name.replace(" ", "_"))
        try:
            response = session.get(url, timeout=30, headers={"User-Agent": USER_AGENT})
            response.raise_for_status()
            head_coach = parse_head_coach(response.text)
        except Exception as exc:
            failures.append(f"{abbr}: {exc}")
            head_coach = None
        if head_coach:
            rows.append({
                "season": SEASON, "team_abbr": abbr, "role": "head_coach",
                "coach_name": head_coach, "verification_status": "verified",
                "notes": f"parsed from Wikipedia {SEASON} season page {date.today().isoformat()}",
            })
            print(f"  {abbr}: {head_coach}")
        else:
            failures.append(f"{abbr}: no coach parameter parsed")
        time.sleep(0.3)

    if failures:
        print("FAILURES:\n  " + "\n  ".join(failures))
        return 1
    print(f"Parsed {len(rows)}/32 head coaches for {SEASON}.")

    if args.write:
        with open(args.csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "season", "team_abbr", "role", "coach_name", "verification_status", "notes",
            ])
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {args.csv}")
    else:
        print("Dry run: pass --write to update the CSV.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
