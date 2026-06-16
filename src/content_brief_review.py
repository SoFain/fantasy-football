"""Read and review helpers for deterministic content brief output tables."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from google.cloud import bigquery

from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_LIMIT = 50
MAX_LIMIT = 500
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("CONTENT_BRIEF_REVIEW_MAX_BYTES_BILLED", "1000000000"))
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")

RUNS_TABLE = "content_brief_runs"
BRIEFS_TABLE = "content_briefs"
ITEMS_TABLE = "content_brief_items"

READABLE_CONTENT_BRIEF_TABLES = frozenset({RUNS_TABLE, BRIEFS_TABLE, ITEMS_TABLE})
REVIEW_STATUS_VALUES = frozenset({"draft", "reviewed", "approved", "archived"})


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def list_content_brief_runs(
    *,
    brief_type: str | None = None,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    status: str | None = None,
    limit: int = DEFAULT_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return recent content brief generation run rows."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_list_content_brief_runs_query(
        project_id=client.project,
        dataset_id=dataset_id,
        brief_type=brief_type,
        season=season,
        week=week,
        scoring_profile_id=scoring_profile_id,
        league_type_id=league_type_id,
        roster_format_id=roster_format_id,
        status=status,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def list_content_briefs(
    *,
    brief_type: str | None = None,
    review_status: str | None = None,
    season: int | None = None,
    week: int | None = None,
    model_run_id: str | None = None,
    content_brief_run_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> list[dict[str, Any]]:
    """Return recent content brief rows with bounded filters."""

    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_list_content_briefs_query(
        project_id=client.project,
        dataset_id=dataset_id,
        brief_type=brief_type,
        review_status=review_status,
        season=season,
        week=week,
        model_run_id=model_run_id,
        content_brief_run_id=content_brief_run_id,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def get_content_brief_detail(
    content_brief_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Return one brief and its linked item rows."""

    if not _clean_optional(content_brief_id):
        raise ValueError("content_brief_id is required")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_get_content_brief_detail_query(
        project_id=client.project,
        dataset_id=dataset_id,
        content_brief_id=content_brief_id,
    )
    rows = _query_rows(client, sql, job_config)
    if not rows:
        return {"brief": None, "items": [], "empty": True}
    items = list_content_brief_items(content_brief_id, client=client, dataset_id=dataset_id)
    return {"brief": rows[0], "items": items, "empty": False}


def list_content_brief_items(
    content_brief_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    limit: int = MAX_LIMIT,
) -> list[dict[str, Any]]:
    """Return item rows for one content brief."""

    if not _clean_optional(content_brief_id):
        raise ValueError("content_brief_id is required")
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_list_content_brief_items_query(
        project_id=client.project,
        dataset_id=dataset_id,
        content_brief_id=content_brief_id,
        limit=limit,
    )
    return _query_rows(client, sql, job_config)


def update_content_brief_review_status(
    content_brief_id: str,
    review_status: str,
    reviewer_notes: str | None = None,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    """Update review status for one brief. Reviewer notes are not persisted until the schema supports them."""

    if not _clean_optional(content_brief_id):
        raise ValueError("content_brief_id is required")
    status = validate_review_status(review_status)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    sql, job_config = build_update_content_brief_review_status_query(
        project_id=client.project,
        dataset_id=dataset_id,
        content_brief_id=content_brief_id,
        review_status=status,
    )
    job = client.query(sql, job_config=job_config)
    job.result()
    return {
        "content_brief_id": content_brief_id,
        "review_status": status,
        "updated": True,
        "reviewer_notes_supported": False,
        "reviewer_notes_ignored": bool(_clean_optional(reviewer_notes)),
        "affected_rows": getattr(job, "num_dml_affected_rows", None),
    }


def export_content_brief_markdown(
    content_brief_id: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> str:
    """Return a markdown export for one content brief."""

    detail = get_content_brief_detail(content_brief_id, client=client, dataset_id=dataset_id)
    brief = detail.get("brief")
    if not brief:
        return f"# Content Brief\n\nNo content brief rows found for `{content_brief_id}`.\n"
    items = detail.get("items") or []
    brief_json = _json_object(brief.get("brief_json"))
    prompt_payload = brief_json.get("llm_prompt_payload_json")

    lines = [
        f"# {brief.get('title') or 'Content Brief'}",
        "",
        f"- content_brief_id: `{brief.get('content_brief_id')}`",
        f"- content_brief_run_id: `{brief.get('content_brief_run_id')}`",
        f"- brief_type: `{brief.get('brief_type')}`",
        f"- season_week: `{brief.get('season')}` / `{brief.get('week')}`",
        f"- model_run_id: `{brief.get('model_run_id') or 'unknown'}`",
        f"- review_status: `{brief.get('review_status')}`",
        f"- token_estimate: `{brief.get('token_estimate')}`",
        f"- source_freshness_json: `{_compact(brief.get('source_freshness_json'))}`",
        f"- missing_data_flags: `{_compact(brief.get('missing_data_flags'))}`",
        "",
        "## Brief Text",
        "",
        str(brief.get("brief_text") or "").strip() or "_No brief text available._",
        "",
    ]

    if items:
        lines.extend(["## Brief Items", ""])
        for item in items:
            lines.extend(
                [
                    f"### {item.get('item_order')}. {item.get('title') or item.get('item_type') or 'Item'}",
                    "",
                    f"- item_type: `{item.get('item_type')}`",
                    f"- player_id_internal: `{item.get('player_id_internal') or ''}`",
                    f"- claim_id: `{item.get('claim_id') or ''}`",
                    f"- trade_review_id: `{item.get('trade_review_id') or ''}`",
                    f"- confidence_score: `{item.get('confidence_score')}`",
                    f"- missing_data_flags: `{_compact(item.get('missing_data_flags'))}`",
                    "",
                    f"Claim: {item.get('claim') or ''}",
                    "",
                    f"Evidence: {item.get('evidence_summary') or ''}",
                    "",
                    f"Counterargument: {item.get('counterargument') or ''}",
                    "",
                    f"Snark hook: {item.get('snark_hook') or ''}",
                    "",
                ]
            )

    if prompt_payload:
        lines.extend(["## Show Writer Payload", "", "```json", _json_dumps(prompt_payload), "```", ""])
    return "\n".join(lines)


def build_content_brief_generation_preview_command(
    *,
    brief_type: str = "full_weekly_show_prep",
    season: int = 2026,
    week: int | None = None,
    scoring_profile_id: str = "ppr",
    league_type_id: str = "redraft",
    roster_format_id: str = "one_qb",
    model_run_id: str | None = None,
) -> list[str]:
    """Return the local dry-run command for deterministic brief generation."""

    command = [
        r".\venv\Scripts\python.exe",
        "-m",
        "src.content_briefs",
        "--brief-type",
        str(brief_type),
        "--season",
        str(int(season)),
        "--scoring-profile",
        str(scoring_profile_id),
        "--league-type",
        str(league_type_id),
        "--roster-format",
        str(roster_format_id),
        "--dry-run",
    ]
    if week is not None:
        command.extend(["--week", str(int(week))])
    if model_run_id:
        command.extend(["--model-run-id", str(model_run_id)])
    return command


def build_list_content_brief_runs_query(
    *,
    project_id: str,
    dataset_id: str,
    brief_type: str | None = None,
    season: int | None = None,
    week: int | None = None,
    scoring_profile_id: str | None = None,
    league_type_id: str | None = None,
    roster_format_id: str | None = None,
    status: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        content_brief_run_id,
        brief_type,
        model_run_id,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        status,
        created_by,
        created_at,
        completed_at,
        error_message,
        notes,
        (
            SELECT COUNT(*)
            FROM `{_table_id(project_id, dataset_id, BRIEFS_TABLE)}` briefs
            WHERE briefs.content_brief_run_id = runs.content_brief_run_id
        ) AS brief_count,
        (
            SELECT COUNT(*)
            FROM `{_table_id(project_id, dataset_id, BRIEFS_TABLE)}` briefs
            JOIN `{_table_id(project_id, dataset_id, ITEMS_TABLE)}` items
              ON briefs.content_brief_id = items.content_brief_id
            WHERE briefs.content_brief_run_id = runs.content_brief_run_id
        ) AS item_count
    FROM `{_table_id(project_id, dataset_id, RUNS_TABLE)}` runs
    WHERE (@brief_type IS NULL OR brief_type = @brief_type)
        AND (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
        AND (@scoring_profile_id IS NULL OR scoring_profile_id = @scoring_profile_id)
        AND (@league_type_id IS NULL OR league_type_id = @league_type_id)
        AND (@roster_format_id IS NULL OR roster_format_id = @roster_format_id)
        AND (@status IS NULL OR status = @status)
    ORDER BY created_at DESC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("brief_type", "STRING", _clean_optional(brief_type)),
            ("season", "INT64", _int_or_none(season)),
            ("week", "INT64", _int_or_none(week)),
            ("scoring_profile_id", "STRING", _clean_optional(scoring_profile_id)),
            ("league_type_id", "STRING", _clean_optional(league_type_id)),
            ("roster_format_id", "STRING", _clean_optional(roster_format_id)),
            ("status", "STRING", _clean_optional(status)),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def build_list_content_briefs_query(
    *,
    project_id: str,
    dataset_id: str,
    brief_type: str | None = None,
    review_status: str | None = None,
    season: int | None = None,
    week: int | None = None,
    model_run_id: str | None = None,
    content_brief_run_id: str | None = None,
    limit: int = DEFAULT_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    status = validate_review_status(review_status) if review_status else None
    sql = f"""
    SELECT
        content_brief_id,
        content_brief_run_id,
        brief_type,
        title,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        model_run_id,
        token_estimate,
        source_freshness_json,
        missing_data_flags,
        review_status,
        created_at,
        updated_at
    FROM `{_table_id(project_id, dataset_id, BRIEFS_TABLE)}`
    WHERE (@brief_type IS NULL OR brief_type = @brief_type)
        AND (@review_status IS NULL OR review_status = @review_status)
        AND (@season IS NULL OR season = @season)
        AND (@week IS NULL OR week = @week)
        AND (@model_run_id IS NULL OR model_run_id = @model_run_id)
        AND (@content_brief_run_id IS NULL OR content_brief_run_id = @content_brief_run_id)
    ORDER BY updated_at DESC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("brief_type", "STRING", _clean_optional(brief_type)),
            ("review_status", "STRING", status),
            ("season", "INT64", _int_or_none(season)),
            ("week", "INT64", _int_or_none(week)),
            ("model_run_id", "STRING", _clean_optional(model_run_id)),
            ("content_brief_run_id", "STRING", _clean_optional(content_brief_run_id)),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def build_get_content_brief_detail_query(
    *,
    project_id: str,
    dataset_id: str,
    content_brief_id: str,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        content_brief_id,
        content_brief_run_id,
        brief_type,
        title,
        season,
        week,
        scoring_profile_id,
        league_type_id,
        roster_format_id,
        model_run_id,
        brief_json,
        brief_text,
        token_estimate,
        source_freshness_json,
        missing_data_flags,
        review_status,
        created_at,
        updated_at
    FROM `{_table_id(project_id, dataset_id, BRIEFS_TABLE)}`
    WHERE content_brief_id = @content_brief_id
    ORDER BY updated_at DESC
    LIMIT 1
    """
    return sql, _job_config([("content_brief_id", "STRING", content_brief_id)])


def build_list_content_brief_items_query(
    *,
    project_id: str,
    dataset_id: str,
    content_brief_id: str,
    limit: int = MAX_LIMIT,
) -> tuple[str, bigquery.QueryJobConfig]:
    sql = f"""
    SELECT
        content_brief_id,
        item_id,
        item_type,
        item_order,
        player_id_internal,
        claim_id,
        trade_review_id,
        packet_id,
        title,
        claim,
        evidence_summary,
        counterargument,
        snark_hook,
        confidence_score,
        source_freshness_json,
        missing_data_flags,
        created_at
    FROM `{_table_id(project_id, dataset_id, ITEMS_TABLE)}`
    WHERE content_brief_id = @content_brief_id
    ORDER BY item_order ASC, item_id ASC
    LIMIT @limit
    """
    return sql, _job_config(
        [
            ("content_brief_id", "STRING", content_brief_id),
            ("limit", "INT64", _clamp_limit(limit)),
        ]
    )


def build_update_content_brief_review_status_query(
    *,
    project_id: str,
    dataset_id: str,
    content_brief_id: str,
    review_status: str,
) -> tuple[str, bigquery.QueryJobConfig]:
    status = validate_review_status(review_status)
    sql = f"""
    UPDATE `{_table_id(project_id, dataset_id, BRIEFS_TABLE)}`
    SET review_status = @review_status,
        updated_at = CURRENT_TIMESTAMP()
    WHERE content_brief_id = @content_brief_id
    """
    return sql, _job_config(
        [
            ("content_brief_id", "STRING", content_brief_id),
            ("review_status", "STRING", status),
        ]
    )


def validate_review_status(value: str) -> str:
    status = str(value or "").strip().lower()
    if status not in REVIEW_STATUS_VALUES:
        raise ValueError(f"Invalid review_status: {value!r}")
    return status


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    rows = client.query(sql, job_config=job_config).result()
    return [_row_to_dict(row) for row in rows]


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[
            bigquery.ScalarQueryParameter(name, type_name, value)
            for name, type_name, value in params
        ],
    )


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if table_name not in READABLE_CONTENT_BRIEF_TABLES:
        raise ValueError(f"Unsupported content brief table: {table_name}")
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "items"):
        return dict(row.items())
    return dict(row)


def _clamp_limit(value: int | str | None) -> int:
    try:
        parsed = int(value) if value is not None else DEFAULT_LIMIT
    except (TypeError, ValueError):
        parsed = DEFAULT_LIMIT
    return max(1, min(MAX_LIMIT, parsed))


def _clean_optional(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).strip()
    return text or None


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _json_object(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if value in (None, ""):
        return {}
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def _json_dumps(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _compact(value: Any, max_chars: int = 240) -> str:
    if value in (None, ""):
        return ""
    text = value if isinstance(value, str) else _json_dumps(value)
    return text if len(text) <= max_chars else f"{text[:max_chars]}..."
