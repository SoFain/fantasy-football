"""Populate data/coaching_staff.csv from the Wikipedia current-NFL-staffs templates.

The index page transcludes 32 per-team templates. This fetches each template's
raw wikitext (`?action=raw`) and parses the "Role – Name" bullet lines
deterministically — no LLM summarization, which proved unreliable for names.

Only the eight canonical roles are extracted; everything else is ignored but a
role's original label line is preserved in raw_title. Rows parsed with a name
are marked verified (deterministic parse of the live source); roles absent from
a team's template stay vacant/pending, which is accurate, not a failure.

Usage:
    python scripts/populate_coaching_staff_csv.py            # fetch, parse, report
    python scripts/populate_coaching_staff_csv.py --write    # also rewrite the CSV
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

from src.coaching_staff import NFL_TEAMS, ROLE_KEYS, normalize_role  # noqa: E402

INDEX_URL = (
    "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Football_League/"
    "List_of_current_NFL_staffs?action=raw"
)
TEMPLATE_URL = "https://en.wikipedia.org/wiki/Template:{name}?action=raw"
USER_AGENT = "PigskinCoachingStaff/1.0 (fantasy football research; contact: repo owner)"

# "* Head coach – [[Sean McDermott]]" — en dash, em dash, or hyphen separators.
BULLET = re.compile(r"^\*+\s*(.+?)\s*[–—-]\s*(.+?)\s*$")
WIKILINK = re.compile(r"\[\[(?:[^|\]]*\|)?([^\]]+)\]\]")
TEMPLATE_BRACES = re.compile(r"\{\{[^{}]*\}\}")
REF_TAG = re.compile(r"<ref[^>]*>.*?</ref>|<ref[^>]*/>", re.DOTALL)
HTML_TAG = re.compile(r"<[^>]+>")


def fetch(url: str, session) -> str:
    response = session.get(url, timeout=30, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()
    return response.text


def discover_templates(index_wikitext: str) -> list[str]:
    """Template names transcluded by the index page, e.g. 'Buffalo Bills staff'."""
    names = re.findall(r"\{\{\s*([^{}|]*?staff[^{}|]*?)\s*\}\}", index_wikitext, flags=re.IGNORECASE)
    seen: list[str] = []
    for name in (n.strip() for n in names):
        if name and name not in seen:
            seen.append(name)
    return seen


def team_abbr_for_template(template_name: str) -> str | None:
    lowered = template_name.lower()
    for abbr, (team_name, _conf, _div) in NFL_TEAMS.items():
        if team_name.lower() in lowered:
            return abbr
    return None


def clean_text(value: str) -> str:
    value = REF_TAG.sub("", value)
    value = WIKILINK.sub(r"\1", value)
    value = TEMPLATE_BRACES.sub("", value)
    value = HTML_TAG.sub("", value)
    value = value.replace("'''", "").replace("''", "")
    return re.sub(r"\s+", " ", value).strip(" \t*:;,")


def roles_in_label(label: str) -> list[str]:
    """Canonical roles named by a label like 'Assistant head coach/running backs'."""
    found: list[str] = []
    for part in re.split(r"[/&]| and ", label):
        cleaned = re.sub(r"^(co-|interim\s+)", "", part.strip().lower())
        role = normalize_role(cleaned)
        if role and role not in found:
            found.append(role)
    return found


def parse_template(wikitext: str) -> dict[str, dict[str, str]]:
    """Extract {role_key: {name, raw_title}} from one team template."""
    staff: dict[str, dict[str, str]] = {}
    for line in wikitext.splitlines():
        match = BULLET.match(line.strip())
        if not match:
            continue
        raw_label, raw_name = match.groups()
        label = clean_text(raw_label)
        name = clean_text(raw_name)
        if not name or name.lower() in {"vacant", "tbd", "tba"}:
            continue
        for role in roles_in_label(label):
            if role in staff:
                # Co-coordinators: keep both names on the single grain row.
                if name not in staff[role]["name"]:
                    staff[role]["name"] += f"; {name}"
                    staff[role]["raw_title"] += f" + {label}"
            else:
                staff[role] = {"name": name, "raw_title": label}
    return staff


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Rewrite data/coaching_staff.csv.")
    parser.add_argument("--csv", default=str(REPO_ROOT / "data" / "coaching_staff.csv"))
    args = parser.parse_args()

    import requests

    session = requests.Session()
    templates = discover_templates(fetch(INDEX_URL, session))
    print(f"Discovered {len(templates)} staff templates on the index page.")

    parsed: dict[str, dict[str, dict[str, str]]] = {}
    for template_name in templates:
        abbr = team_abbr_for_template(template_name)
        if abbr is None:
            print(f"  SKIP unmapped template: {template_name!r}")
            continue
        url = TEMPLATE_URL.format(name=template_name.replace(" ", "_"))
        try:
            staff = parse_template(fetch(url, session))
        except Exception as exc:
            print(f"  ERROR fetching {template_name!r}: {exc}")
            continue
        parsed[abbr] = staff
        time.sleep(0.3)  # be polite; 33 requests total

    missing_teams = sorted(set(NFL_TEAMS) - set(parsed))
    if missing_teams:
        print(f"FAILED: no template parsed for {missing_teams}")
        return 1

    teams_without_hc = sorted(a for a, s in parsed.items() if "head_coach" not in s)
    if teams_without_hc:
        print(f"FAILED: no head coach parsed for {teams_without_hc}")
        return 1

    today = date.today().isoformat()
    filled = vacant = 0
    rows: list[dict[str, str]] = []
    for abbr in NFL_TEAMS:
        staff = parsed[abbr]
        for role in ROLE_KEYS:
            entry = staff.get(role)
            if entry:
                filled += 1
                rows.append({
                    "team_abbr": abbr, "role": role, "coach_name": entry["name"],
                    "raw_title": entry["raw_title"], "verification_status": "verified",
                    "notes": f"parsed from Wikipedia template {today}",
                })
            else:
                vacant += 1
                rows.append({
                    "team_abbr": abbr, "role": role, "coach_name": "",
                    "raw_title": "", "verification_status": "pending",
                    "notes": f"not listed on source page {today}",
                })

    print(f"Parsed {filled} filled roles, {vacant} vacant across {len(parsed)} teams.")
    for abbr in ("BUF", "KC", "PHI"):
        summary = ", ".join(f"{r.split('_')[0]}={s['name']}" for r, s in sorted(parsed[abbr].items()))
        print(f"  {abbr}: {summary}")

    if args.write:
        with open(args.csv, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=[
                "team_abbr", "role", "coach_name", "raw_title", "verification_status", "notes",
            ])
            writer.writeheader()
            writer.writerows(rows)
        print(f"Wrote {len(rows)} rows to {args.csv}")
    else:
        print("Dry run: pass --write to update the CSV.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
