import argparse
import logging
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

from src.load import get_bigquery_project


logger = logging.getLogger("ingest_context_events")


SCHEMA = [
    bigquery.SchemaField("event_id", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("season", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("start_week", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("end_week", "INTEGER", mode="REQUIRED"),
    bigquery.SchemaField("team", "STRING"),
    bigquery.SchemaField("event_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("subject_player_id", "STRING"),
    bigquery.SchemaField("subject_name", "STRING"),
    bigquery.SchemaField("subject_position", "STRING"),
    bigquery.SchemaField("affected_player_id", "STRING"),
    bigquery.SchemaField("affected_player_name", "STRING"),
    bigquery.SchemaField("affected_unit", "STRING"),
    bigquery.SchemaField("causal_status", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("confidence_score", "FLOAT"),
    bigquery.SchemaField("source_type", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("source_label", "STRING"),
    bigquery.SchemaField("source_url", "STRING"),
    bigquery.SchemaField("summary", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("analysis_instruction", "STRING"),
    bigquery.SchemaField("active", "BOOLEAN", mode="REQUIRED"),
    bigquery.SchemaField("created_at", "DATE"),
]


def load_context_events(csv_path, dataset_name="fantasy_football_brain"):
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Context events CSV not found: {path}")

    df = pd.read_csv(path)
    if df.empty:
        logger.warning("No context events found in %s.", path)
        return None

    required_columns = {field.name for field in SCHEMA if field.mode == "REQUIRED"}
    missing = sorted(required_columns - set(df.columns))
    if missing:
        raise ValueError(f"Missing required context event columns: {missing}")

    df["season"] = df["season"].astype("int64")
    df["start_week"] = df["start_week"].astype("int64")
    df["end_week"] = df["end_week"].astype("int64")
    df["confidence_score"] = df["confidence_score"].astype("float64")
    df["active"] = df["active"].astype("bool")
    df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce").dt.date

    client = bigquery.Client(project=get_bigquery_project())
    table_id = f"{client.project}.{dataset_name}.analytics_context_events"
    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )

    logger.info("Loading %s context events into %s...", len(df), table_id)
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    logger.info("Successfully loaded %s rows and %s columns to %s.", table.num_rows, len(table.schema), table_id)
    return table


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Load curated AI vs Vibes context events into BigQuery.")
    parser.add_argument(
        "--csv",
        default=str(Path(__file__).resolve().parents[1] / "data" / "context_events.csv"),
        help="Path to the context events CSV file.",
    )
    parser.add_argument(
        "--dataset",
        default="fantasy_football_brain",
        help="BigQuery dataset name.",
    )
    args = parser.parse_args()
    load_context_events(args.csv, dataset_name=args.dataset)


if __name__ == "__main__":
    main()
