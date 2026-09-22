"""CSV import and admin read helpers for the Meatbag Claim Ledger."""

from __future__ import annotations

import csv
import io
import json
import os
import re
from typing import Any

from google.cloud import bigquery

from src import claim_ledger
from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
MAX_IMPORT_ROWS = int(os.environ.get("CLAIM_IMPORT_MAX_ROWS", "500"))
MAX_IMPORT_BYTES = int(os.environ.get("CLAIM_IMPORT_MAX_BYTES", str(2 * 1024 * 1024)))
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("CLAIM_IMPORT_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

CSV_COLUMNS = (
    "source_name",
    "source_type",
    "person_name",
    "show_name",
    "source_url",
    "episode_or_video_title",
    "published_at",
    "claimed_at",
    "claim_text",
    "claim_type",
    "claim_direction",
    "time_horizon",
    "season",
    "week",
    "scoring_profile_id",
    "league_type_id",
    "roster_format_id",
    "player_names",
    "team_names",
    "claimed_rank",
    "claimed_projection",
    "claimed_value",
    "notes",
)

OPTIONAL_EXTRA_COLUMNS = ("review_status",)
ALLOWED_REVIEW_STATUSES = claim_ledger.ALLOWED_REVIEW_STATUSES


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def parse_claim_csv(
    content: bytes | str | Any,
    *,
    max_rows: int = MAX_IMPORT_ROWS,
    max_bytes: int = MAX_IMPORT_BYTES,
) -> list[dict[str, Any]]:
    """Parse an admin-provided claim CSV without writing or fetching URLs."""

    text = _read_upload_text(content, max_bytes=max_bytes)
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None:
        raise ValueError("Claim import CSV has no header row")
    normalized_fieldnames = [_normalize_header(name) for name in reader.fieldnames]
    missing = [column for column in CSV_COLUMNS if column not in normalized_fieldnames]
    if missing:
        raise ValueError(f"Missing required CSV columns: {', '.join(missing)}")

    rows = []
    for row_number, raw_row in enumerate(reader, start=2):
        if len(rows) >= max_rows:
            raise ValueError(f"Claim import row limit exceeded: {max_rows}")
        normalized = {
            _normalize_header(key): _clean_cell(value)
            for key, value in raw_row.items()
            if key is not None
        }
        if not any(normalized.values()):
            continue
        rows.append({"row_number": row_number, **normalized})
    return rows


def validate_claim_import_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate import rows and build source, claim, and player input shapes."""

    previews = []
    for index, row in enumerate(rows, start=1):
        errors: list[str] = []
        warnings: list[str] = []
        source_name = _required_text(row, "source_name", errors)
        source_type = _choice(row.get("source_type"), claim_ledger.ALLOWED_SOURCE_TYPES, "source_type", errors)
        claim_text = _required_text(row, "claim_text", errors)
        claim_type = _choice(row.get("claim_type"), claim_ledger.ALLOWED_CLAIM_TYPES, "claim_type", errors)
        claim_direction = _optional_choice(row.get("claim_direction"), claim_ledger.ALLOWED_DIRECTIONS, "claim_direction", errors)
        time_horizon = _choice(row.get("time_horizon"), claim_ledger.ALLOWED_HORIZONS, "time_horizon", errors)
        review_status = _choice(row.get("review_status") or "draft", ALLOWED_REVIEW_STATUSES, "review_status", errors)
        season = _int_field(row.get("season"), "season", errors, required=True)
        week = _int_field(row.get("week"), "week", errors, required=False)
        claimed_rank = _int_field(row.get("claimed_rank"), "claimed_rank", errors, required=False)
        claimed_projection = _float_field(row.get("claimed_projection"), "claimed_projection", errors)
        claimed_value = _float_field(row.get("claimed_value"), "claimed_value", errors)
        player_inputs = [{"display_name": name} for name in _split_multi_value(row.get("player_names"))]
        team_names = [team.upper() for team in _split_multi_value(row.get("team_names"))]

        if review_status != "draft":
            required_for_review = {
                "claim_direction": claim_direction,
                "source_name": source_name,
                "claim_text": claim_text,
                "claim_type": claim_type,
                "time_horizon": time_horizon,
                "season": season,
            }
            missing = [field for field, value in required_for_review.items() if value in (None, "")]
            if not player_inputs and not team_names:
                missing.append("player_names or team_names")
            if missing:
                errors.append(f"review_status {review_status} requires: {', '.join(missing)}")

        if not player_inputs and not team_names:
            warnings.append("claim has no player_names or team_names")

        source_id = _source_id(row)
        preview = {
            "row_number": row.get("row_number", index),
            "source": {
                "source_id": source_id,
                "source_name": source_name,
                "source_type": source_type,
                "person_name": _optional_text(row.get("person_name")),
                "show_name": _optional_text(row.get("show_name")),
                "source_url": _optional_text(row.get("source_url")),
                "notes": _optional_text(row.get("notes")),
            },
            "claim": {
                "claim_text": claim_text,
                "claim_type": claim_type,
                "claim_direction": claim_direction,
                "time_horizon": time_horizon,
                "season": season,
                "week": week,
                "scoring_profile_id": _optional_text(row.get("scoring_profile_id")),
                "league_type_id": _optional_text(row.get("league_type_id")),
                "roster_format_id": _optional_text(row.get("roster_format_id")),
                "claimed_rank": claimed_rank,
                "claimed_projection": claimed_projection,
                "claimed_value": claimed_value,
                "episode_or_video_title": _optional_text(row.get("episode_or_video_title")),
                "source_url": _optional_text(row.get("source_url")),
                "published_at": _optional_text(row.get("published_at")),
                "claimed_at": _optional_text(row.get("claimed_at")),
                "notes": _optional_text(row.get("notes")),
                "review_status": review_status,
            },
            "player_inputs": player_inputs,
            "team_names": team_names,
            "validation_errors": errors,
            "warnings": warnings,
            "missing_data_flags": [],
            "player_resolution_status": "not_resolved",
            "can_write": not errors,
        }
        if season is not None and time_horizon:
            preview["evaluation_window"] = claim_ledger.infer_evaluation_window(
                claim_id=f"preview-{preview['row_number']}",
                time_horizon=time_horizon,
                season=season,
                week=week,
            )
        previews.append(preview)
    return previews


def resolve_import_players(
    preview_rows: list[dict[str, Any]],
    *,
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Resolve player names for preview rows and flag ambiguous or missing matches."""

    resolved_rows = []
    for preview in preview_rows:
        row = dict(preview)
        if row.get("player_inputs"):
            resolution = claim_ledger.resolve_claim_players(
                row["player_inputs"],
                identity_rows=identity_rows,
                client=client,
                dataset_id=dataset_id,
            )
            row["resolved_players"] = resolution["resolved_players"]
            row["disambiguation"] = resolution["disambiguation"]
            missing_flags = list(row.get("missing_data_flags") or [])
            unresolved = [
                player for player in resolution["resolved_players"]
                if not player.get("player_id_internal")
            ]
            if resolution["disambiguation"]:
                missing_flags.append("ambiguous_player_identity")
                row["player_resolution_status"] = "ambiguous"
            elif unresolved:
                missing_flags.append("missing_player_id_internal")
                row["player_resolution_status"] = "unresolved"
            else:
                row["player_resolution_status"] = "resolved"
            row["missing_data_flags"] = sorted(set(missing_flags))
        else:
            row["resolved_players"] = []
            row["disambiguation"] = []
            row["player_resolution_status"] = "no_players"

        if row["player_resolution_status"] in {"ambiguous", "unresolved"} and row["claim"]["review_status"] != "draft":
            row["validation_errors"] = list(row["validation_errors"]) + [
                "ambiguous or unresolved players can only be imported as draft"
            ]
            row["can_write"] = False
        else:
            row["can_write"] = not row["validation_errors"]
        resolved_rows.append(row)
    return resolved_rows


def build_claim_import_preview(
    content: bytes | str | Any,
    *,
    identity_rows: list[dict[str, Any]] | None = None,
    client: Any | None = None,
    dataset_id: str | None = None,
    max_rows: int = MAX_IMPORT_ROWS,
    max_bytes: int = MAX_IMPORT_BYTES,
) -> list[dict[str, Any]]:
    rows = parse_claim_csv(content, max_rows=max_rows, max_bytes=max_bytes)
    previews = validate_claim_import_rows(rows)
    return resolve_import_players(
        previews,
        identity_rows=identity_rows,
        client=client,
        dataset_id=dataset_id,
    )


def write_claim_import_rows(
    preview_rows: list[dict[str, Any]],
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Write valid import rows through claim_ledger helpers."""

    writable = [row for row in preview_rows if row.get("can_write")]
    skipped = [row for row in preview_rows if not row.get("can_write")]
    results = []
    for row in writable:
        source = row["source"]
        claim = row["claim"]
        context = {
            "import_row_number": row.get("row_number"),
            "import_notes": claim.get("notes"),
            "missing_data_flags": row.get("missing_data_flags") or [],
            "player_resolution_status": row.get("player_resolution_status"),
        }
        claim_ledger.register_claim_source(
            source_id=source["source_id"],
            source_name=source["source_name"],
            source_type=source["source_type"],
            person_name=source.get("person_name"),
            show_name=source.get("show_name"),
            source_url=source.get("source_url"),
            notes=source.get("notes"),
            active=True,
            client=client,
            dataset_id=dataset_id,
            dry_run=dry_run,
        )
        results.append(
            claim_ledger.create_fantasy_claim(
                source_id=source["source_id"],
                source_name=source["source_name"],
                claim_source_type=source["source_type"],
                person_name=source.get("person_name"),
                episode_or_video_title=claim.get("episode_or_video_title"),
                source_url=claim.get("source_url") or source.get("source_url"),
                published_at=claim.get("published_at"),
                claimed_at=claim.get("claimed_at"),
                claim_text=claim["claim_text"],
                claim_type=claim["claim_type"],
                claim_direction=claim.get("claim_direction"),
                time_horizon=claim["time_horizon"],
                season=claim["season"],
                week=claim.get("week"),
                scoring_profile_id=claim.get("scoring_profile_id"),
                league_type_id=claim.get("league_type_id"),
                roster_format_id=claim.get("roster_format_id"),
                players=row.get("resolved_players") or row.get("player_inputs") or [],
                teams=row.get("team_names") or [],
                claimed_rank=claim.get("claimed_rank"),
                claimed_projection=claim.get("claimed_projection"),
                claimed_value=claim.get("claimed_value"),
                context=context,
                review_status=claim.get("review_status") or "draft",
                identity_rows=[],
                client=client,
                dataset_id=dataset_id,
                dry_run=dry_run,
            )
        )
    return {
        "dry_run": dry_run,
        "written_count": len(results),
        "skipped_count": len(skipped),
        "results": results,
        "skipped_rows": skipped,
    }


def export_claim_import_errors(preview_rows: list[dict[str, Any]]) -> str:
    """Return a CSV of rows that cannot be written."""

    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["row_number", "source_name", "claim_text", "errors", "warnings"],
    )
    writer.writeheader()
    for row in preview_rows:
        if row.get("validation_errors"):
            writer.writerow(
                {
                    "row_number": row.get("row_number"),
                    "source_name": row.get("source", {}).get("source_name"),
                    "claim_text": row.get("claim", {}).get("claim_text"),
                    "errors": "; ".join(row.get("validation_errors") or []),
                    "warnings": "; ".join(row.get("warnings") or []),
                }
            )
    return output.getvalue()


def list_claim_sources(
    *,
    search: str | None = None,
    active_only: bool = False,
    limit: int = 100,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql = f"""
    SELECT
        source_id,
        source_name,
        source_type,
        person_name,
        show_name,
        channel_name,
        source_url,
        notes,
        active,
        created_at,
        updated_at
    FROM `{_table_id(client.project, dataset_id, claim_ledger.CLAIM_SOURCES_TABLE)}`
    WHERE (@search IS NULL OR LOWER(source_name) LIKE CONCAT('%', LOWER(@search), '%')
        OR LOWER(person_name) LIKE CONCAT('%', LOWER(@search), '%')
        OR LOWER(show_name) LIKE CONCAT('%', LOWER(@search), '%'))
        AND (@active_only = FALSE OR active = TRUE)
    ORDER BY active DESC, source_name ASC
    LIMIT @limit
    """
    return _query_rows(
        client,
        sql,
        _job_config(
            [
                ("search", "STRING", _optional_text(search)),
                ("active_only", "BOOL", bool(active_only)),
                ("limit", "INT64", _clamp_limit(limit)),
            ]
        ),
    )


def get_claim_detail(
    claim_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    claim = claim_ledger.get_claim(claim_id, client=client, dataset_id=dataset_id)
    if not claim:
        return {"claim": None, "players": [], "evaluation_windows": []}
    players_sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, claim_ledger.CLAIM_PLAYERS_TABLE)}`
    WHERE claim_id = @claim_id
    ORDER BY player_role_in_claim, display_name
    LIMIT @limit
    """
    windows_sql = f"""
    SELECT *
    FROM `{_table_id(client.project, dataset_id, claim_ledger.EVALUATION_WINDOWS_TABLE)}`
    WHERE claim_id = @claim_id
    ORDER BY created_at DESC
    LIMIT @limit
    """
    params = _job_config([("claim_id", "STRING", claim_id), ("limit", "INT64", 100)])
    players = _query_rows(client, players_sql, params)
    windows = _query_rows(client, windows_sql, params)
    return {"claim": claim, "players": players, "evaluation_windows": windows}


def _read_upload_text(content: bytes | str | Any, *, max_bytes: int) -> str:
    if hasattr(content, "getvalue"):
        raw = content.getvalue()
    elif hasattr(content, "read"):
        raw = content.read()
    else:
        raw = content
    if isinstance(raw, str):
        byte_len = len(raw.encode("utf-8"))
        text = raw
    else:
        byte_len = len(raw or b"")
        text = bytes(raw or b"").decode("utf-8-sig")
    if byte_len > max_bytes:
        raise ValueError(f"Claim import file is too large. Limit is {max_bytes} bytes")
    return text


def _normalize_header(value: Any) -> str:
    return str(value or "").strip().lower()


def _clean_cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _required_text(row: dict[str, Any], field: str, errors: list[str]) -> str | None:
    value = _optional_text(row.get(field))
    if value is None:
        errors.append(f"{field} is required")
    return value


def _optional_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _choice(value: Any, allowed: set[str], field: str, errors: list[str]) -> str | None:
    text = _optional_text(value)
    if text is None:
        errors.append(f"{field} is required")
        return None
    normalized = text.lower()
    if normalized not in allowed:
        errors.append(f"invalid {field}: {text}")
        return None
    return normalized


def _optional_choice(value: Any, allowed: set[str], field: str, errors: list[str]) -> str | None:
    text = _optional_text(value)
    if text is None:
        return None
    normalized = text.lower()
    if normalized not in allowed:
        errors.append(f"invalid {field}: {text}")
        return None
    return normalized


def _int_field(value: Any, field: str, errors: list[str], *, required: bool) -> int | None:
    text = _optional_text(value)
    if text is None:
        if required:
            errors.append(f"{field} is required")
        return None
    try:
        return int(float(text.replace(",", "")))
    except ValueError:
        errors.append(f"invalid {field}: {text}")
        return None


def _float_field(value: Any, field: str, errors: list[str]) -> float | None:
    text = _optional_text(value)
    if text is None:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        errors.append(f"invalid {field}: {text}")
        return None


def _split_multi_value(value: Any) -> list[str]:
    text = _optional_text(value)
    if text is None:
        return []
    separators = [";", "|", "\n"]
    pattern = "|".join(re.escape(separator) for separator in separators)
    parts = re.split(pattern, text)
    if len(parts) == 1 and "," in text:
        parts = text.split(",")
    return [part.strip() for part in parts if part.strip()]


def _source_id(row: dict[str, Any]) -> str:
    base = row.get("source_name") or row.get("person_name") or row.get("show_name") or "manual_source"
    slug = re.sub(r"[^a-z0-9_]+", "_", str(base).strip().lower()).strip("_")
    if not slug:
        slug = "manual_source"
    if not IDENTIFIER_RE.fullmatch(slug):
        slug = f"source_{slug}"
    return slug[:120]


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else 100
    except (TypeError, ValueError):
        parsed = 100
    return max(1, min(500, parsed))


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    rows = client.query(sql, job_config=job_config).result()
    result = []
    for row in rows:
        if isinstance(row, dict):
            result.append(dict(row))
        elif hasattr(row, "items"):
            result.append(dict(row.items()))
        else:
            result.append(dict(row))
    return result


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, param_type, value)
            for name, param_type, value in params
        ],
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if table_name not in {
        claim_ledger.CLAIM_SOURCES_TABLE,
        claim_ledger.FANTASY_CLAIMS_TABLE,
        claim_ledger.CLAIM_PLAYERS_TABLE,
        claim_ledger.EVALUATION_WINDOWS_TABLE,
    }:
        raise ValueError(f"Unsupported claim import table: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def preview_rows_for_display(preview_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten previews for Streamlit tables and tests."""

    output = []
    for row in preview_rows:
        output.append(
            {
                "row_number": row.get("row_number"),
                "source_name": row.get("source", {}).get("source_name"),
                "claim_type": row.get("claim", {}).get("claim_type"),
                "claim_direction": row.get("claim", {}).get("claim_direction"),
                "time_horizon": row.get("claim", {}).get("time_horizon"),
                "season": row.get("claim", {}).get("season"),
                "week": row.get("claim", {}).get("week"),
                "review_status": row.get("claim", {}).get("review_status"),
                "player_resolution_status": row.get("player_resolution_status"),
                "can_write": row.get("can_write"),
                "errors": "; ".join(row.get("validation_errors") or []),
                "warnings": "; ".join(row.get("warnings") or []),
                "missing_data_flags": json.dumps(row.get("missing_data_flags") or [], sort_keys=True),
            }
        )
    return output
