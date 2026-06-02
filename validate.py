import sys
import logging
from google.cloud import bigquery
from google.api_core.exceptions import NotFound

# Set up logging for validation script
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("validate")

def run_dry_run(client, query):
    """ Runs a dry-run query to determine how many bytes it will scan. """
    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
    try:
        query_job = client.query(query, job_config=job_config)
        return query_job.total_bytes_processed
    except Exception as e:
        logger.error(f"Dry run failed: {e}")
        return None

def validate_partitioning(client, table_ref):
    """ Retrieves table metadata and checks if range partitioning is properly configured. """
    try:
        table = client.get_table(table_ref)
        partitioning = table.range_partitioning
        
        if partitioning is not None:
            logger.info(f"✔ Table '{table.table_id}' is Partitioned!")
            logger.info(f"   - Partitioning Column: '{partitioning.field}'")
            if partitioning.range_:
                logger.info(f"   - Range: Start={partitioning.range_.start}, End={partitioning.range_.end}, Interval={partitioning.range_.interval}")
            else:
                logger.warning("   - Range configuration not found.")
            return True
        else:
            logger.error(f"❌ Table '{table.table_id}' is NOT Range Partitioned.")
            return False
    except NotFound:
        logger.error(f"❌ Table '{table_ref}' was not found.")
        return False
    except Exception as e:
        logger.error(f"Error validating partitioning for '{table_ref}': {e}")
        return False

def validate_pipeline_upload(dataset_name="fantasy_football_brain"):
    """
    Main validation function that performs a sweep over the created dataset and tables.
    Checks:
    - Dataset presence.
    - Tables: play_by_play, weekly_metrics, team_descriptions.
    - Setup of range partitioning on the 'season' column.
    - Row counts by season (without SELECT *).
    - Dry-run validation of query pruning.
    """
    logger.info("=" * 60)
    logger.info(f"Starting BigQuery Schema & Partition Verification Sweep")
    logger.info("=" * 60)

    try:
        client = bigquery.Client()
    except Exception as e:
        logger.error(f"Could not initialize BigQuery Client. Make sure GOOGLE_APPLICATION_CREDENTIALS is set: {e}")
        sys.exit(1)

    dataset_ref = f"{client.project}.{dataset_name}"
    
    # 1. Verify Dataset existence
    try:
        client.get_dataset(dataset_ref)
        logger.info(f"✔ Dataset '{dataset_ref}' exists.")
    except NotFound:
        logger.error(f"❌ Dataset '{dataset_ref}' was not found. Please run the pipeline script first to create it.")
        sys.exit(1)
        
    tables = ["play_by_play", "weekly_metrics", "team_descriptions"]
    all_valid = True

    for t_name in tables:
        logger.info("-" * 50)
        table_ref = f"{dataset_ref}.{t_name}"
        
        # 2. Check and print partitioning metadata
        is_partitioned = validate_partitioning(client, table_ref)
        if not is_partitioned:
            all_valid = False
            continue
            
        # 3. Retrieve row counts per season using non-SELECT * aggregation
        logger.info(f"Querying record counts grouped by season for '{t_name}'...")
        count_query = f"""
            SELECT season, COUNT(1) as record_count
            FROM `{table_ref}`
            GROUP BY season
            ORDER BY season
        """
        try:
            query_job = client.query(count_query)
            results = query_job.result()
            
            rows = list(results)
            if not rows:
                logger.warning(f"   No data rows found in '{t_name}'.")
            else:
                for row in rows:
                    logger.info(f"   Season: {row['season']} | Row Count: {row['record_count']}")
        except Exception as e:
            logger.error(f"❌ Failed to query counts for '{t_name}': {e}")
            all_valid = False
            continue

        # 4. Demonstrate partition pruning (Dry-run cost control)
        # Compare full table scan query vs partitioned/filtered query
        full_query = f"SELECT COUNT(1) FROM `{table_ref}`"
        pruned_query = f"SELECT COUNT(1) FROM `{table_ref}` WHERE season = 2020"
        
        full_bytes = run_dry_run(client, full_query)
        pruned_bytes = run_dry_run(client, pruned_query)
        
        if full_bytes is not None and pruned_bytes is not None:
            logger.info("   Partition Pruning Demonstration (Dry-Run Bytes Scanned):")
            logger.info(f"   - Full Table Scan: {full_bytes} bytes")
            logger.info(f"   - Partition-Filtered Scan (season = 2020): {pruned_bytes} bytes")
            if pruned_bytes < full_bytes:
                logger.info(f"   ✔ Pruning active! Reduced scan size by {((full_bytes - pruned_bytes) / full_bytes) * 100:.1f}%.")
            elif full_bytes == 0:
                logger.info("   - Table is empty, no scanned bytes registered.")
            else:
                logger.info("   - Scanned bytes are equal (table size may be small enough to fall within minimum BigQuery billing tiers).")

    logger.info("=" * 60)
    if all_valid:
        logger.info("Verification sweep completed successfully. Everything looks correct!")
    else:
        logger.info("Verification sweep finished with errors. Please check logs.")
    logger.info("=" * 60)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Validate BigQuery pipeline schema and partitioning setup.")
    parser.add_argument(
        "--dataset",
        type=str,
        default="fantasy_football_brain",
        help="The BigQuery dataset name to validate"
    )
    args = parser.parse_args()
    validate_pipeline_upload(dataset_name=args.dataset)
