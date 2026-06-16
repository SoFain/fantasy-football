"""BigQuery query guardrails for Streamlit and Pigskin chat."""

from __future__ import annotations

import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

from google.cloud import bigquery

from src.pigskin_chat_schema import (
    PIGSKIN_CHAT_ALLOWED_TABLES,
    PIGSKIN_CHAT_BLOCKED_TABLES,
)

logger = logging.getLogger(__name__)

APP_LABEL = "ai-vs-meatbags"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("BQ_MAX_BYTES_BILLED", "2000000000"))
PIGSKIN_MAX_BYTES_BILLED = int(
    os.environ.get("PIGSKIN_BQ_MAX_BYTES_BILLED", str(DEFAULT_MAX_BYTES_BILLED))
)

_FROM_JOIN_RE = re.compile(
    r"\b(?:FROM|JOIN)\s+(`[^`]+`|[A-Za-z0-9_:\-]+(?:\.[A-Za-z0-9_\-]+){0,2})",
    flags=re.IGNORECASE,
)
_CTE_RE = re.compile(
    r"(?:\bWITH|,)\s+([A-Za-z_][A-Za-z0-9_]*)\s+AS\s*\(",
    flags=re.IGNORECASE,
)
_IGNORED_TABLE_TOKENS = {"unnest"}


@dataclass(frozen=True)
class PigskinSqlPolicyResult:
    referenced_tables: tuple[str, ...]
    blocked_tables: tuple[str, ...]
    non_allowed_tables: tuple[str, ...]


class PigskinQueryRejected(ValueError):
    """Raised when Pigskin tries to execute SQL outside its curated contract."""

    def __init__(self, message: str, policy_result: PigskinSqlPolicyResult):
        super().__init__(message)
        self.policy_result = policy_result


def _environment_label() -> str:
    return (
        os.environ.get("APP_ENV")
        or os.environ.get("ENVIRONMENT")
        or os.environ.get("K_SERVICE")
        or "local"
    )


def _label_value(value: str) -> str:
    value = re.sub(r"[^a-z0-9_-]+", "-", str(value).lower()).strip("-_")
    return (value or "unknown")[:63]


def _query_job_config(
    *,
    component: str,
    query_name: str,
    query_parameters: Iterable[Any] | None = None,
    maximum_bytes_billed: int | None = None,
    dry_run: bool = False,
    allow_large_query: bool = False,
    use_query_cache: bool = True,
) -> bigquery.QueryJobConfig:
    job_config = bigquery.QueryJobConfig(
        dry_run=dry_run,
        labels={
            "app": _label_value(APP_LABEL),
            "component": _label_value(component),
            "environment": _label_value(_environment_label()),
            "query_name": _label_value(query_name),
        },
        query_parameters=list(query_parameters or []),
        use_query_cache=use_query_cache,
    )

    if maximum_bytes_billed is not None:
        job_config.maximum_bytes_billed = maximum_bytes_billed
    elif not allow_large_query:
        job_config.maximum_bytes_billed = DEFAULT_MAX_BYTES_BILLED

    return job_config


def run_bigquery_query(
    client: bigquery.Client,
    sql_query: str,
    *,
    component: str,
    query_name: str,
    query_parameters: Iterable[Any] | None = None,
    maximum_bytes_billed: int | None = None,
    dry_run: bool = False,
    allow_large_query: bool = False,
    use_query_cache: bool = True,
) -> bigquery.job.QueryJob:
    """Run a BigQuery SQL query with labels, byte caps, and structured logs."""

    job_config = _query_job_config(
        component=component,
        query_name=query_name,
        query_parameters=query_parameters,
        maximum_bytes_billed=maximum_bytes_billed,
        dry_run=dry_run,
        allow_large_query=allow_large_query,
        use_query_cache=use_query_cache,
    )
    start = time.perf_counter()
    blocked = False

    try:
        job = client.query(sql_query, job_config=job_config)
        if not dry_run:
            job.result()
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.info(
            "bigquery_query_complete",
            extra={
                "query_name": query_name,
                "component": component,
                "bytes_processed": getattr(job, "total_bytes_processed", None),
                "cache_hit": getattr(job, "cache_hit", None),
                "duration_ms": duration_ms,
                "blocked": blocked,
                "dry_run": dry_run,
            },
        )
        return job
    except Exception:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        logger.exception(
            "bigquery_query_failed",
            extra={
                "query_name": query_name,
                "component": component,
                "duration_ms": duration_ms,
                "blocked": blocked,
                "dry_run": dry_run,
            },
        )
        raise


def query_to_dataframe(
    client: bigquery.Client,
    sql_query: str,
    *,
    component: str,
    query_name: str,
    query_parameters: Iterable[Any] | None = None,
    maximum_bytes_billed: int | None = None,
    allow_large_query: bool = False,
    use_query_cache: bool = True,
):
    job = run_bigquery_query(
        client,
        sql_query,
        component=component,
        query_name=query_name,
        query_parameters=query_parameters,
        maximum_bytes_billed=maximum_bytes_billed,
        allow_large_query=allow_large_query,
        use_query_cache=use_query_cache,
    )
    return job.to_dataframe()


def _strip_sql_literals_and_comments(sql_query: str) -> str:
    sql_query = re.sub(r"--[^\n]*", " ", sql_query)
    sql_query = re.sub(r"/\*.*?\*/", " ", sql_query, flags=re.DOTALL)
    sql_query = re.sub(r"'(?:''|[^'])*'", "''", sql_query)
    sql_query = re.sub(r'"(?:""|[^"])*"', '""', sql_query)
    return sql_query


def _normalize_table_identifier(identifier: str) -> str:
    identifier = identifier.strip().strip("`").rstrip(",;)")
    if identifier.startswith("("):
        return ""
    return identifier.split(".")[-1].lower()


def _cte_names(sql_query: str) -> set[str]:
    return {match.group(1).lower() for match in _CTE_RE.finditer(sql_query)}


def extract_bigquery_table_references(
    sql_query: str,
    *,
    known_tables: Iterable[str] | None = None,
) -> tuple[str, ...]:
    """Extract table references from BigQuery SQL conservatively."""

    known = {name.lower() for name in (known_tables or [])}
    scrubbed_sql = _strip_sql_literals_and_comments(sql_query)
    ctes = _cte_names(scrubbed_sql)
    references: set[str] = set()

    for match in re.finditer(r"`([^`]+)`", scrubbed_sql):
        raw_identifier = match.group(1)
        table_name = _normalize_table_identifier(raw_identifier)
        if "." in raw_identifier or table_name in known:
            references.add(table_name)

    for match in _FROM_JOIN_RE.finditer(scrubbed_sql):
        table_name = _normalize_table_identifier(match.group(1))
        if table_name:
            references.add(table_name)

    for table_name in known:
        if re.search(rf"\b{re.escape(table_name)}\b", scrubbed_sql, flags=re.IGNORECASE):
            references.add(table_name)

    references -= ctes
    references -= _IGNORED_TABLE_TOKENS
    return tuple(sorted(references))


def validate_pigskin_sql(sql_query: str) -> PigskinSqlPolicyResult:
    allowed_tables = {name.lower() for name in PIGSKIN_CHAT_ALLOWED_TABLES}
    blocked_known = {name.lower() for name in PIGSKIN_CHAT_BLOCKED_TABLES}
    known_tables = allowed_tables | blocked_known
    referenced_tables = set(
        extract_bigquery_table_references(sql_query, known_tables=known_tables)
    )
    blocked_tables = referenced_tables & blocked_known
    non_allowed_tables = referenced_tables - allowed_tables

    result = PigskinSqlPolicyResult(
        referenced_tables=tuple(sorted(referenced_tables)),
        blocked_tables=tuple(sorted(blocked_tables)),
        non_allowed_tables=tuple(sorted(non_allowed_tables)),
    )
    if blocked_tables or non_allowed_tables:
        log_pigskin_sql_rejection(sql_query, result)
        problem_tables = sorted(blocked_tables | non_allowed_tables)
        message = (
            "Pigskin SQL was blocked before execution because it referenced "
            f"tables outside the curated Pigskin marts: {', '.join(problem_tables)}. "
            "Use the allowed analytics marts or say the curated data is unavailable."
        )
        raise PigskinQueryRejected(message, result)

    return result


def log_pigskin_sql_rejection(
    sql_query: str,
    policy_result: PigskinSqlPolicyResult,
) -> None:
    logger.warning(
        "pigskin_query_rejected",
        extra={
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "component": "pigskin_chat",
            "query_text": sql_query,
            "referenced_tables": list(policy_result.referenced_tables),
            "blocked_tables": list(policy_result.blocked_tables),
            "non_allowed_tables": list(policy_result.non_allowed_tables),
            "blocked": True,
        },
    )


def pigskin_query_to_dataframe(
    client: bigquery.Client,
    sql_query: str,
    *,
    query_name: str = "pigskin_llm_sql",
):
    validate_pigskin_sql(sql_query)
    return query_to_dataframe(
        client,
        sql_query,
        component="pigskin_chat",
        query_name=query_name,
        maximum_bytes_billed=PIGSKIN_MAX_BYTES_BILLED,
    )
