"""Load manual rookie scouting metrics from CSV into BigQuery.

Replaces the CSV uploader that lived in the retired Streamlit Data Ops tab.
The UI offered interactive column mapping; this expects the CSV to already use
the canonical column names, which `data/sample_rookie_scouting.csv` does.

This is an append-only source write. Scouting data is manually curated, so
loading the same file twice will duplicate rows; use `--replace-season` to
overwrite a season instead.
"""

import argparse
import logging
from pathlib import Path

import pandas as pd
from google.cloud import bigquery

from src.load import get_bigquery_project


logger = logging.getLogger("ingest_rookie_scouting")

TABLE_NAME = "rookie_scouting_metrics"

SCHEMA = [
    bigquery.SchemaField("season", "INTEGER", mode="REQUIRED", description="The year the player was drafted / rookie season"),
    bigquery.SchemaField("player_name", "STRING", mode="REQUIRED"),
    bigquery.SchemaField("position", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("college", "STRING", mode="NULLABLE"),
    bigquery.SchemaField("yards_after_contact_per_attempt", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("yards_per_route_run", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("college_target_share", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("catch_radius_grade", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("success_rate_vs_man", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("success_rate_vs_zone", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("success_rate_vs_press", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("avg_separation_inches", "FLOAT", mode="NULLABLE"),
    bigquery.SchemaField("data_source", "STRING", mode="NULLABLE"),
]

REQUIRED_COLUMNS = tuple(field.name for field in SCHEMA if field.mode == "REQUIRED")
FLOAT_COLUMNS = tuple(field.name for field in SCHEMA if field.field_type == "FLOAT")
STRING_COLUMNS = tuple(field.name for field in SCHEMA if field.field_type == "STRING")


def prepare_rookie_scouting_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and coerce a raw CSV frame to the table schema.

    Kept separate from the load so it can be tested without BigQuery.
    """
    missing = sorted(set(REQUIRED_COLUMNS) - set(df.columns))
    if missing:
        raise ValueError(f"Missing required rookie scouting columns: {missing}")

    out = df.copy()

    # Unknown columns would fail the load job; drop them rather than guess.
    known = {field.name for field in SCHEMA}
    extra = sorted(set(out.columns) - known)
    if extra:
        logger.warning("Ignoring unrecognized columns: %s", extra)
        out = out.drop(columns=extra)

    for column in known - set(out.columns):
        out[column] = None

    out["season"] = pd.to_numeric(out["season"], errors="coerce").astype("Int64")
    if out["season"].isna().any():
        bad = out.loc[out["season"].isna(), "player_name"].tolist()
        raise ValueError(f"Rows have a non-numeric season: {bad}")

    out["player_name"] = out["player_name"].astype("string").str.strip()
    if (out["player_name"].isna() | (out["player_name"] == "")).any():
        raise ValueError("Rows have an empty player_name")

    for column in FLOAT_COLUMNS:
        out[column] = pd.to_numeric(out[column], errors="coerce").astype("float64")
    for column in STRING_COLUMNS:
        out[column] = out[column].astype("string").str.strip()

    return out[[field.name for field in SCHEMA]]


def load_rookie_scouting(
    csv_path,
    dataset_name: str = "fantasy_football_brain",
    replace_season: bool = False,
    client=None,
):
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"Rookie scouting CSV not found: {path}")

    df = prepare_rookie_scouting_frame(pd.read_csv(path))
    if df.empty:
        logger.warning("No rookie scouting rows found in %s.", path)
        return None

    client = client or bigquery.Client(project=get_bigquery_project())
    table_id = f"{client.project}.{dataset_name}.{TABLE_NAME}"

    if replace_season:
        seasons = sorted({int(value) for value in df["season"].tolist()})
        logger.info("Deleting existing rows for seasons %s in %s...", seasons, table_id)
        job = client.query(
            f"DELETE FROM `{table_id}` WHERE season IN UNNEST(@seasons)",
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ArrayQueryParameter("seasons", "INT64", seasons)]
            ),
        )
        job.result()

    job_config = bigquery.LoadJobConfig(
        schema=SCHEMA,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    logger.info("Loading %s rookie scouting rows into %s...", len(df), table_id)
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()

    table = client.get_table(table_id)
    logger.info("Successfully loaded %s rows to %s.", len(df), table_id)
    return table


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Load manual Pigskin rookie scouting metrics into BigQuery.")
    parser.add_argument(
        "--csv",
        default=str(Path(__file__).resolve().parents[1] / "data" / "sample_rookie_scouting.csv"),
        help="Path to the rookie scouting CSV file.",
    )
    parser.add_argument("--dataset", default="fantasy_football_brain", help="BigQuery dataset name.")
    parser.add_argument(
        "--replace-season",
        action="store_true",
        help="Delete existing rows for the CSV's seasons before appending.",
    )
    args = parser.parse_args()
    load_rookie_scouting(args.csv, dataset_name=args.dataset, replace_season=args.replace_season)


if __name__ == "__main__":
    main()
