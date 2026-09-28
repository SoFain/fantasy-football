"""BigQuery access for the availability pilot.

The pilot may create and replace only its own ``availability_*`` tables in
``fantasy_football_brain``. Every write goes through ``load_rows`` or
``replace_key_rows``, which refuse any other table name.
"""

from __future__ import annotations

import json
import os
import uuid
from typing import Any, Iterable

PROJECT = os.environ.get("BQ_PROJECT") or "fantasy-football-498121"
DATASET = "fantasy_football_brain"
TABLE_PREFIX = "availability_"


def table_id(name: str) -> str:
    return f"{PROJECT}.{DATASET}.{name}"


def assert_pilot_table(name: str) -> None:
    if not name.startswith(TABLE_PREFIX) or "." in name:
        raise ValueError(f"availability pilot may write only {TABLE_PREFIX}* tables, got {name!r}")


def client() -> Any:
    from google.cloud import bigquery

    return bigquery.Client(project=PROJECT)


def query(bq: Any, sql: str, params: list[Any] | None = None) -> list[dict]:
    from google.cloud import bigquery

    config = bigquery.QueryJobConfig(query_parameters=params or [])
    return [dict(row) for row in bq.query(sql, job_config=config).result()]


def _json_ready(rows: Iterable[dict]) -> list[dict]:
    return json.loads(json.dumps(list(rows), default=str))


def load_rows(bq: Any, name: str, rows: list[dict], schema: list[Any], *, truncate: bool) -> int:
    """Committed load job (never streaming) into a pilot table."""
    from google.cloud import bigquery

    assert_pilot_table(name)
    disposition = bigquery.WriteDisposition.WRITE_TRUNCATE if truncate else bigquery.WriteDisposition.WRITE_APPEND
    config = bigquery.LoadJobConfig(
        schema=schema,
        write_disposition=disposition,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    bq.load_table_from_json(_json_ready(rows), table_id(name), job_config=config).result()
    return len(rows)


def replace_key_rows(bq: Any, name: str, rows: list[dict], schema: list[Any], key_fields: list[str]) -> int:
    """Idempotent upsert: stage with a load job, then one MERGE that replaces matching keys."""
    assert_pilot_table(name)
    if not rows:
        return 0
    from google.cloud import bigquery

    bq.create_table(bigquery.Table(table_id(name), schema=schema), exists_ok=True)
    stage = f"{TABLE_PREFIX}stage_{name[len(TABLE_PREFIX):]}_{uuid.uuid4().hex[:10]}"
    load_rows(bq, stage, rows, schema, truncate=True)
    try:
        columns = [field.name for field in schema]
        on = " AND ".join(f"t.`{k}` = s.`{k}`" for k in key_fields)
        updates = ", ".join(f"`{c}` = s.`{c}`" for c in columns if c not in key_fields)
        insert_cols = ", ".join(f"`{c}`" for c in columns)
        insert_vals = ", ".join(f"s.`{c}`" for c in columns)
        bq.query(
            f"""
MERGE `{table_id(name)}` t
USING `{table_id(stage)}` s
ON {on}
WHEN MATCHED THEN UPDATE SET {updates}
WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
"""
        ).result()
    finally:
        bq.delete_table(table_id(stage), not_found_ok=True)
    return len(rows)
