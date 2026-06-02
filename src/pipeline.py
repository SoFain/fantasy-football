import sys
import argparse
import logging
from datetime import datetime

from src.extract import get_pbp_data, get_weekly_data, get_team_data
from src.transform import transform_pbp_data, transform_weekly_data, transform_team_data
from src.load import get_bigquery_client, create_dataset_if_not_exists, load_df_to_partitioned_table

def setup_logging():
    """
    Sets up structured logging for the data pipeline.
    Logs will output to both console and a log file.
    """
    log_format = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("pipeline_execution.log", encoding="utf-8")
        ]
    )
    # Reduce noise from external libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)

def run_pipeline(seasons, write_disposition="WRITE_TRUNCATE", dataset_name="fantasy_football_brain"):
    """
    Orchestrates the ETL process for NFL statistics:
    1. Extract PBP, Weekly, and Team Data (with caching and backoff).
    2. Transform and clean schemas for BigQuery compatibility.
    3. Load data into BigQuery with Range Partitioning on the 'season' column.
    """
    logger = logging.getLogger("src.pipeline")
    logger.info("=" * 60)
    logger.info(f"Starting NFL Data Pipeline execution at {datetime.now()}")
    logger.info(f"Target Seasons: {seasons}")
    logger.info(f"Write Disposition: {write_disposition}")
    logger.info(f"Dataset Name: {dataset_name}")
    logger.info("=" * 60)

    try:
        # -------------------------------------------------------------
        # STEP 1: EXTRACTION
        # -------------------------------------------------------------
        logger.info("--- Starting Step 1: Extraction ---")
        
        logger.info(f"Extracting play-by-play data for seasons {seasons}...")
        pbp_df_raw = get_pbp_data(seasons)
        
        logger.info(f"Extracting weekly player metrics data for seasons {seasons}...")
        weekly_df_raw = get_weekly_data(seasons)
        
        logger.info("Extracting team descriptions...")
        team_df_raw = get_team_data()
        
        # -------------------------------------------------------------
        # STEP 2: TRANSFORMATION
        # -------------------------------------------------------------
        logger.info("--- Starting Step 2: Transformation ---")
        
        pbp_df_clean = transform_pbp_data(pbp_df_raw)
        weekly_df_clean = transform_weekly_data(weekly_df_raw)
        team_df_clean = transform_team_data(team_df_raw, seasons)

        # -------------------------------------------------------------
        # STEP 3: LOADING TO BIGQUERY
        # -------------------------------------------------------------
        logger.info("--- Starting Step 3: Loading ---")
        
        bq_client = get_bigquery_client()
        dataset_id = create_dataset_if_not_exists(bq_client, dataset_name=dataset_name)

        # Load play-by-play table
        load_df_to_partitioned_table(
            client=bq_client,
            df=pbp_df_clean,
            dataset_id=dataset_id,
            table_name="play_by_play",
            write_disposition=write_disposition
        )

        # Load weekly player metrics table
        load_df_to_partitioned_table(
            client=bq_client,
            df=weekly_df_clean,
            dataset_id=dataset_id,
            table_name="weekly_metrics",
            write_disposition=write_disposition
        )

        # Load team descriptions table
        load_df_to_partitioned_table(
            client=bq_client,
            df=team_df_clean,
            dataset_id=dataset_id,
            table_name="team_descriptions",
            write_disposition=write_disposition
        )

        logger.info("=" * 60)
        logger.info(f"NFL Data Pipeline finished successfully at {datetime.now()}!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"Pipeline execution FAILED at {datetime.now()}: {e}", exc_info=True)
        logger.error("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    setup_logging()
    
    current_year = datetime.now().year
    # Default to past 5 years including current year if we are in/after season
    default_seasons = list(range(2020, min(current_year + 1, 2027)))
    
    parser = argparse.ArgumentParser(description="NFL Data Pipeline to Google BigQuery")
    parser.add_argument(
        "--seasons",
        type=str,
        default=",".join(map(str, default_seasons)),
        help="Comma-separated list of NFL seasons to ingest (e.g. 2020,2021,2022)"
    )
    parser.add_argument(
        "--write-disposition",
        type=str,
        default="WRITE_TRUNCATE",
        choices=["WRITE_TRUNCATE", "WRITE_APPEND"],
        help="BigQuery load job write disposition (WRITE_TRUNCATE or WRITE_APPEND)"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="fantasy_football_brain",
        help="Google BigQuery dataset name to upload tables into"
    )

    args = parser.parse_args()
    
    # Parse seasons argument
    try:
        seasons_list = [int(s.strip()) for s in args.seasons.split(",") if s.strip()]
    except ValueError:
        print("Error: Seasons list must contain only comma-separated integers.")
        sys.exit(1)

    run_pipeline(
        seasons=seasons_list,
        write_disposition=args.write_disposition,
        dataset_name=args.dataset
    )
