import logging
import os
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError, Conflict, NotFound
import pandas as pd

logger = logging.getLogger(__name__)
DEFAULT_BIGQUERY_PROJECT = "fantasy-football-498121"

PLAYER_ID_STRING_FIELDS = {
    "player_id",
    "passer_player_id",
    "rusher_player_id",
    "receiver_player_id",
    "lateral_receiver_player_id",
    "lateral_rusher_player_id",
    "lateral_sack_player_id",
    "lateral_interception_player_id",
    "lateral_punt_returner_player_id",
    "lateral_kickoff_returner_player_id",
    "interception_player_id",
    "sack_player_id",
    "fantasy_player_id",
}


def get_bigquery_project():
    return (
        os.environ.get("BQ_PROJECT")
        or os.environ.get("GCP_PROJECT")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or DEFAULT_BIGQUERY_PROJECT
    )

def get_bigquery_client():
    """
    Initializes and returns a Google BigQuery client.
    Uses default credentials from the environment.
    """
    try:
        client = bigquery.Client(project=get_bigquery_project())
        logger.info(f"Initialized BigQuery client with project: {client.project}")
        return client
    except Exception as e:
        logger.error("Failed to initialize BigQuery client. Ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")
        raise e

def create_dataset_if_not_exists(client, dataset_name="fantasy_football_brain", location="US"):
    """
    Creates the dataset if it does not already exist in the BigQuery project.
    """
    dataset_id = f"{client.project}.{dataset_name}"
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = location

    try:
        client.get_dataset(dataset_id)
        logger.info(f"BigQuery Dataset '{dataset_id}' already exists.")
    except Exception:
        try:
            client.create_dataset(dataset, timeout=30)
            logger.info(f"Successfully created BigQuery Dataset '{dataset_id}' in location {location}.")
        except Conflict:
            logger.info(f"BigQuery Dataset '{dataset_id}' was created concurrently.")
        except Exception as e:
            logger.error(f"Error creating dataset '{dataset_id}': {e}")
            raise e
            
    return dataset_id


def is_player_id_column(column_name):
    return column_name in PLAYER_ID_STRING_FIELDS or column_name.endswith("_player_id")


def get_schema_aware_append_policy():
    return {
        "enabled_for_write_disposition": "WRITE_APPEND",
        "known_player_id_string_fields": sorted(PLAYER_ID_STRING_FIELDS),
        "wildcard_string_fields": ["*_player_id when the existing BigQuery schema type is STRING"],
        "numeric_stats_policy": "Numeric stat columns are not cast to string unless the existing BigQuery schema explicitly says STRING.",
        "table_schema_lookup": "Existing BigQuery table schema is fetched immediately before append loads.",
    }


def _schema_type(field):
    return str(getattr(field, "field_type", "") or getattr(field, "type", "")).upper()


def _schema_name(field):
    return str(getattr(field, "name", ""))


def _is_missing(value):
    return pd.isna(value)


def _stringify_bigquery_value(value):
    if _is_missing(value):
        return pd.NA
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def _coerce_to_string(series):
    return series.map(_stringify_bigquery_value).astype("string")


def _coerce_to_integer(series, field_name):
    numeric = pd.to_numeric(series, errors="coerce")
    invalid = series.notna() & numeric.isna()
    if invalid.any():
        examples = series[invalid].head(3).tolist()
        raise ValueError(f"Column '{field_name}' cannot be safely coerced to INTEGER. Examples: {examples}")
    return numeric.astype("Int64")


def _coerce_to_float(series, field_name):
    numeric = pd.to_numeric(series, errors="coerce")
    invalid = series.notna() & numeric.isna()
    if invalid.any():
        examples = series[invalid].head(3).tolist()
        raise ValueError(f"Column '{field_name}' cannot be safely coerced to FLOAT. Examples: {examples}")
    return numeric


def _coerce_to_boolean(series, field_name):
    if pd.api.types.is_bool_dtype(series):
        return series

    true_values = {"true", "1", "yes", "y", "t"}
    false_values = {"false", "0", "no", "n", "f"}

    def parse(value):
        if _is_missing(value):
            return pd.NA
        if isinstance(value, bool):
            return value
        lowered = str(value).strip().lower()
        if lowered in true_values:
            return True
        if lowered in false_values:
            return False
        raise ValueError(value)

    parsed = []
    invalid_examples = []
    for value in series:
        try:
            parsed.append(parse(value))
        except ValueError:
            invalid_examples.append(value)
            parsed.append(pd.NA)

    if invalid_examples:
        raise ValueError(
            f"Column '{field_name}' cannot be safely coerced to BOOLEAN. "
            f"Examples: {invalid_examples[:3]}"
        )

    return pd.Series(parsed, index=series.index, dtype="boolean")


def build_schema_compatibility_report(df, table_name, write_disposition, existing_schema=None):
    schema_by_name = {
        _schema_name(field): _schema_type(field)
        for field in (existing_schema or [])
        if _schema_name(field)
    }
    dataframe_fields = set(df.columns)
    target_fields = set(schema_by_name)
    new_dataframe_fields = sorted(dataframe_fields - target_fields) if schema_by_name else []
    fields_missing = sorted(target_fields - dataframe_fields) if schema_by_name else []
    incompatible_fields = []

    for column in sorted(dataframe_fields & target_fields):
        target_type = schema_by_name[column]
        source_dtype = str(df[column].dtype)
        if target_type in {"INTEGER", "INT64"}:
            numeric = pd.to_numeric(df[column], errors="coerce")
            if (df[column].notna() & numeric.isna()).any():
                incompatible_fields.append(
                    {
                        "field": column,
                        "target_type": target_type,
                        "source_dtype": source_dtype,
                        "reason": "non-numeric values cannot be coerced to INTEGER",
                    }
                )
        elif target_type in {"FLOAT", "FLOAT64", "NUMERIC", "BIGNUMERIC"}:
            numeric = pd.to_numeric(df[column], errors="coerce")
            if (df[column].notna() & numeric.isna()).any():
                incompatible_fields.append(
                    {
                        "field": column,
                        "target_type": target_type,
                        "source_dtype": source_dtype,
                        "reason": "non-numeric values cannot be coerced to numeric target type",
                    }
                )

    safe_to_proceed = bool(schema_by_name) and not incompatible_fields and not new_dataframe_fields
    return {
        "table_name": table_name,
        "write_disposition": write_disposition,
        "existing_schema_found": bool(schema_by_name),
        "fields_coerced": [],
        "fields_missing_in_dataframe": fields_missing,
        "new_dataframe_fields_not_in_target": new_dataframe_fields,
        "incompatible_fields": incompatible_fields,
        "safe_to_proceed": safe_to_proceed,
    }


def coerce_dataframe_to_existing_schema(df, table_name, write_disposition, existing_schema):
    report = build_schema_compatibility_report(
        df=df,
        table_name=table_name,
        write_disposition=write_disposition,
        existing_schema=existing_schema,
    )
    if report["incompatible_fields"]:
        return df, report

    out = df.copy()
    schema_by_name = {
        _schema_name(field): _schema_type(field)
        for field in existing_schema
        if _schema_name(field)
    }
    coerced = []

    for column in sorted(set(out.columns) & set(schema_by_name)):
        target_type = schema_by_name[column]
        before_dtype = str(out[column].dtype)
        try:
            if target_type == "STRING":
                out[column] = _coerce_to_string(out[column])
            elif target_type in {"INTEGER", "INT64"}:
                out[column] = _coerce_to_integer(out[column], column)
            elif target_type in {"FLOAT", "FLOAT64", "NUMERIC", "BIGNUMERIC"}:
                out[column] = _coerce_to_float(out[column], column)
            elif target_type in {"BOOLEAN", "BOOL"}:
                out[column] = _coerce_to_boolean(out[column], column)
        except ValueError as exc:
            report["incompatible_fields"].append(
                {
                    "field": column,
                    "target_type": target_type,
                    "source_dtype": before_dtype,
                    "reason": str(exc),
                }
            )
            continue

        after_dtype = str(out[column].dtype)
        if before_dtype != after_dtype:
            coerced.append(
                {
                    "field": column,
                    "target_type": target_type,
                    "source_dtype": before_dtype,
                    "coerced_dtype": after_dtype,
                    "player_id_like": is_player_id_column(column),
                }
            )

    report["fields_coerced"] = coerced
    report["safe_to_proceed"] = (
        report["existing_schema_found"]
        and not report["incompatible_fields"]
        and not report["new_dataframe_fields_not_in_target"]
    )
    return out, report


def prepare_dataframe_for_bigquery_load(client, df, table_id, table_name, write_disposition):
    if write_disposition != "WRITE_APPEND":
        return df, None, None

    try:
        table = client.get_table(table_id)
    except NotFound:
        report = {
            "table_name": table_name,
            "write_disposition": write_disposition,
            "existing_schema_found": False,
            "fields_coerced": [],
            "fields_missing_in_dataframe": [],
            "new_dataframe_fields_not_in_target": [],
            "incompatible_fields": [],
            "safe_to_proceed": True,
        }
        logger.info(f"No existing BigQuery table schema found for '{table_id}'. Append load will use autodetect.")
        return df, report, None

    coerced_df, report = coerce_dataframe_to_existing_schema(
        df=df,
        table_name=table_name,
        write_disposition=write_disposition,
        existing_schema=table.schema,
    )
    logger.info(f"Schema compatibility report for '{table_id}': {report}")
    if not report["safe_to_proceed"]:
        raise ValueError(f"Append schema compatibility check failed for '{table_id}': {report}")

    load_schema = [field for field in table.schema if field.name in coerced_df.columns]
    return coerced_df, report, load_schema

def load_df_to_partitioned_table(client, df, dataset_id, table_name, write_disposition="WRITE_TRUNCATE"):
    """
    Loads a pandas DataFrame into a BigQuery table partitioned by 'season'.
    - Configures Range Partitioning on the 'season' column (2000 to 2050, interval 1).
    - Enforces the integer schema on the partition column to prevent autodetect failures.
    - Captures and logs detailed connection and schema mismatch errors.
    """
    if df.empty:
        logger.warning(f"DataFrame for table '{table_name}' is empty. Skipping upload.")
        return

    table_id = f"{dataset_id}.{table_name}"
    
    # 1. Force the 'season' column in pandas to be an integer type before shipping
    try:
        df['season'] = df['season'].astype('int64')
    except Exception as e:
        logger.error(f"Could not cast 'season' column to int64 in pandas: {e}")
        raise e
        
    df, schema_report, append_schema = prepare_dataframe_for_bigquery_load(
        client=client,
        df=df,
        table_id=table_id,
        table_name=table_name,
        write_disposition=write_disposition,
    )
    if schema_report and schema_report["fields_coerced"]:
        logger.info(f"Coerced fields before append load for '{table_id}': {schema_report['fields_coerced']}")

    # Configure range partitioning on 'season'
    range_partitioning = bigquery.RangePartitioning(
        field="season",
        range_=bigquery.PartitionRange(start=2000, end=2050, interval=1)
    )

    if append_schema is None:
        # Hardcode the schema for just the 'season' column.
        # Autodetect will handle the rest of the columns when no target schema exists.
        schema_overrides = [
            bigquery.SchemaField("season", "INTEGER", mode="REQUIRED")
        ]
        autodetect = True
    else:
        schema_overrides = append_schema
        autodetect = False

    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        range_partitioning=range_partitioning,
        schema=schema_overrides,
        autodetect=autodetect
    )

    logger.info(f"Starting load job for '{table_id}' with write disposition: {write_disposition}...")
    job = None
    try:
        # Start the load job from the dataframe
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        # Wait for the job to complete
        job.result()
        logger.info(f"Successfully loaded {len(df)} rows into partitioned table '{table_id}'.")
    except GoogleAPIError as e:
        logger.error(f"Google BigQuery API Error loading table '{table_id}': {e}")
        # Safeguard if job wasn't created or lacks errors attribute
        if job and hasattr(job, 'errors') and job.errors:
            logger.error(f"Detailed BigQuery job error messages:")
            for err in job.errors:
                logger.error(f" - {err.get('message')}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error loading table '{table_id}': {e}")
        raise e
