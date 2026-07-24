"""Load current NFL coaching staff from the curated CSV into BigQuery.

Reads data/coaching_staff.csv, expands it to the full 32-team x 8-role grid via
src.coaching_staff, and writes coaching_staff_current with a full truncate.

Curated-CSV ingest, mirroring src/ingest_rookie_scouting.py. The CSV is the
reviewable source of truth; see the coaching_staff_current contract for why the
Wikipedia source is not scraped live.
"""

from __future__ import annotations

import argparse
import csv
import logging
from datetime import datetime, timezone
from pathlib import Path

from google.cloud import bigquery

from src.coaching_staff import DEFAULT_SOURCE, prepare_rows
from src.load import get_bigquery_project

logger = logging.getLogger("ingest_coaching_staff")

TABLE_NAME = "coaching_staff_current"
DEFAULT_SOURCE_URL = (
    "https://en.wikipedia.org/wiki/Wikipedia:WikiProject_National_Football_League/"
    "List_of_current_NFL_staffs"
)

SCHEMA = [
    bigquery.SchemaField("snapshot_at", "TIMESTAMP", mode="REQUIRED"),
    bigquery.SchemaField("team_abbr", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("team_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("conference", "STRING"),
    bigquery.SchemaField("division", "STRING"),
    bigquery.SchemaField("role", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("role_title", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("role_rank", "INT64", mode="REQUIRED"),
    bigquery.SchemaField("coach_name", "STRING"),
    bigquery.SchemaField("raw_title", "STRING"),
    bigquery.SchemaField("is_vacant", "BOOL", mode="REQUIRED"),
    bigquery.SchemaField("verification_status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source", "STRING"),
    bigquery.SchemaField("source_url", "STRING"),
    bigquery.SchemaField("notes", "STRING"),
    bigquery.SchemaField("missing_fields_json", "STRING"),
]


def read_csv_rows(csv_path) -> list[dict]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Coaching staff CSV not found: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_coaching_staff(
    csv_path,
    dataset_name: str = "fantasy_football_brain",
    source_url: str = DEFAULT_SOURCE_URL,
    client=None,
    snapshot_at=None,
):
    snapshot_at = snapshot_at or datetime.now(timezone.utc)
    rows = prepare_rows(
        read_csv_rows(csv_path),
        snapshot_at=snapshot_at.isoformat(),
        source_url=source_url,
        source=DEFAULT_SOURCE,
    )

    client = client or bigquery.Client(project=get_bigquery_project())
    table_id = f"{client.project}.{dataset_name}.{TABLE_NAME}"
    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
    )
    logger.info("Loading %s coaching staff rows into %s...", len(rows), table_id)
    client.load_table_from_json(rows, table_id, job_config=job_config).result()

    vacancies = sum(1 for row in rows if row["is_vacant"])
    logger.info("Loaded %s rows (%s vacant/unfilled) to %s.", len(rows), vacancies, table_id)
    return {"row_count": len(rows), "vacant": vacancies}


def _default_csv() -> str:
    return str(Path(__file__).resolve().parents[1] / "data" / "coaching_staff.csv")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Load current NFL coaching staff into BigQuery.")
    parser.add_argument("--csv", default=_default_csv(), help="Path to the coaching staff CSV.")
    parser.add_argument("--dataset", default="fantasy_football_brain", help="BigQuery dataset name.")
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL, help="Provenance URL recorded on every row.")
    args = parser.parse_args()
    load_coaching_staff(args.csv, dataset_name=args.dataset, source_url=args.source_url)


if __name__ == "__main__":
    main()
