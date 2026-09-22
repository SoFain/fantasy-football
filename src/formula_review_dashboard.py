"""Read-only helpers for the 2026 formula comparison dashboard."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FORMULA_REVIEW_DOC_PATH = PROJECT_ROOT / "docs" / "rebuild" / "live-2026-ranking-review-boards.md"

PROFILE_OPTIONS = (
    {"id": "standard", "label": "Standard", "heading": "Standard Review Boards"},
    {"id": "half_ppr", "label": "Half PPR", "heading": "Half PPR Review Boards"},
    {"id": "ppr", "label": "PPR", "heading": "PPR Review Boards"},
    {"id": "gng_keeper", "label": "GNG Keeper", "heading": "GNG Keeper Review Boards"},
)

MODEL_TABLES = {
    "Current Pigskin: live baseline": "Current Pigskin Top 50 Overall",
    "Enriched Logistic Elite: review-only challenger": "BQML Logistic Top 50 Overall",
    "Enriched Linear Points: context only": "BQML Linear Points Top 50 Overall",
    "Side-by-side top 100": "Side-by-Side Top 100 Overall",
}

POSITION_TABLES = {
    "Overall": "Side-by-Side Top 100 Overall",
    "QB": "QB Board Top 45",
    "RB": "RB Board Top 80",
    "WR": "WR Board Top 100",
    "TE": "TE Board Top 35",
}

MOVEMENT_TABLES = {
    "Logistic risers": "Logistic Risers",
    "Logistic fallers": "Logistic Fallers",
    "Cutline crossings": "Cutline Crossings",
    "TE35 watch band": "TE35 Watch Band",
}

RISK_FILTERS = (
    "movement over 20 ranks",
    "high missingness",
    "null current team",
    "questionable/out/injured",
    "missing from Current Pigskin",
    "missing from BQML",
)


def load_formula_review_markdown(path: Path = FORMULA_REVIEW_DOC_PATH) -> str:
    """Load the committed owner-review board Markdown."""

    return path.read_text(encoding="utf-8")


def build_formula_review_payload(markdown_text: str) -> dict[str, object]:
    """Parse top-level dashboard metadata from the review-board Markdown."""

    review_version = ""
    match = re.search(r"Review version:\s*`([^`]+)`", markdown_text)
    if match:
        review_version = match.group(1)

    profile_decisions = parse_table_after_heading(markdown_text, "Profile Decision Summary")
    model_summary = parse_table_after_heading(markdown_text, "Model Summary")
    candidate_coverage = parse_table_after_heading(markdown_text, "Candidate Coverage")

    return {
        "review_version": review_version,
        "profile_decisions": profile_decisions,
        "model_summary": model_summary,
        "candidate_coverage": candidate_coverage,
        "profiles": PROFILE_OPTIONS,
        "data_source": str(FORMULA_REVIEW_DOC_PATH),
    }


def get_profile_decision(payload: dict[str, object], profile_id: str) -> dict[str, str]:
    decisions = payload.get("profile_decisions") or []
    for row in decisions:
        if row.get("Scoring profile") == profile_id:
            return row
    return {}


def get_profile_model_summary(payload: dict[str, object], profile_id: str, model: str) -> dict[str, str]:
    rows = payload.get("model_summary") or []
    for row in rows:
        if row.get("Profile") == profile_id and row.get("Model") == model:
            return row
    return {}


def get_profile_table(markdown_text: str, profile_id: str, table_heading: str) -> list[dict[str, str]]:
    section = get_profile_section(markdown_text, profile_id)
    if not section:
        return []
    return parse_table_after_heading(section, table_heading)


def get_profile_section(markdown_text: str, profile_id: str) -> str:
    option = next((item for item in PROFILE_OPTIONS if item["id"] == profile_id), None)
    if not option:
        return ""

    heading = f"# {option['heading']}"
    start = markdown_text.find(heading)
    if start < 0:
        return ""
    next_heading = markdown_text.find("\n# ", start + len(heading))
    if next_heading < 0:
        return markdown_text[start:]
    return markdown_text[start:next_heading]


def parse_table_after_heading(markdown_text: str, heading: str) -> list[dict[str, str]]:
    lines = markdown_text.splitlines()
    heading_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.strip() in {f"## {heading}", f"### {heading}"}
        ),
        None,
    )
    if heading_index is None:
        return []

    table_lines: list[str] = []
    for line in lines[heading_index + 1 :]:
        stripped = line.strip()
        if not stripped:
            if table_lines:
                break
            continue
        if stripped.startswith("|"):
            table_lines.append(stripped)
            continue
        if table_lines:
            break
    return parse_markdown_table(table_lines)


def parse_markdown_table(table_lines: Iterable[str]) -> list[dict[str, str]]:
    rows = list(table_lines)
    if len(rows) < 2:
        return []

    headers = _split_markdown_row(rows[0])
    data_rows = []
    for line in rows[2:]:
        cells = _split_markdown_row(line)
        if len(cells) < len(headers):
            cells.extend([""] * (len(headers) - len(cells)))
        data_rows.append(dict(zip(headers, cells[: len(headers)])))
    return data_rows


def filter_formula_review_rows(rows: Iterable[dict[str, str]], selected_filters: Iterable[str]) -> list[dict[str, str]]:
    active_filters = set(selected_filters)
    filtered = list(rows)
    if not active_filters:
        return filtered

    return [row for row in filtered if _row_matches_filters(row, active_filters)]


def _row_matches_filters(row: dict[str, str], active_filters: set[str]) -> bool:
    checks = []
    if "movement over 20 ranks" in active_filters:
        checks.append(abs(_number(row.get("Delta"))) > 20)
    if "high missingness" in active_filters:
        checks.append(_percent(row.get("Missing %")) >= 70)
    if "null current team" in active_filters:
        team = row.get("Team") or row.get("Current team") or row.get("sleeper_current_team") or ""
        checks.append(team.strip().lower() in {"", "null", "none", "unknown"})
    if "questionable/out/injured" in active_filters:
        status_text = " ".join(str(value).lower() for value in row.values())
        checks.append(any(term in status_text for term in ("questionable", "injured", "out")))
    if "missing from Current Pigskin" in active_filters:
        current_fields = [row.get("Current"), row.get("Current rank"), row.get("Current TE rank")]
        checks.append(any(str(value or "").strip() == "" for value in current_fields))
    if "missing from BQML" in active_filters:
        bqml_fields = [row.get("Logistic"), row.get("Linear"), row.get("Logistic rank"), row.get("Linear rank")]
        checks.append(any(str(value or "").strip() == "" for value in bqml_fields))
    return any(checks)


def _split_markdown_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _number(value: object) -> float:
    try:
        return float(str(value or "0").replace("+", "").replace(",", ""))
    except ValueError:
        return 0.0


def _percent(value: object) -> float:
    try:
        return float(str(value or "0").replace("%", "").replace(",", ""))
    except ValueError:
        return 0.0
