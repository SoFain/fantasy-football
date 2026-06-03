import logging
import os
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError, Conflict

logger = logging.getLogger(__name__)
DEFAULT_BIGQUERY_PROJECT = "fantasy-football-498121"


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
        
    # Configure range partitioning on 'season'
    range_partitioning = bigquery.RangePartitioning(
        field="season",
        range_=bigquery.PartitionRange(start=2000, end=2050, interval=1)
    )

    # 2. Hardcode the schema for just the 'season' column. 
    # Autodetect will handle the rest of the 100+ columns, but 'season' is locked down.
    schema_overrides = [
        bigquery.SchemaField("season", "INTEGER", mode="REQUIRED")
    ]

    # Configure the load job
    job_config = bigquery.LoadJobConfig(
        write_disposition=write_disposition,
        range_partitioning=range_partitioning,
        schema=schema_overrides,
        autodetect=True  # Safely discovers the rest of the columns
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
