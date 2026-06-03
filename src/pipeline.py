import sys
import argparse
import logging
from datetime import datetime

from src.extract import get_pbp_data, get_weekly_data, get_team_data, get_draft_picks_data, get_players_data, get_contracts_data, get_ngs_passing_data, get_ngs_rushing_data, get_ngs_receiving_data, get_ftn_charting_data, get_snap_counts_data, get_injury_reports_data
from src.transform import transform_pbp_data, transform_weekly_data, transform_team_data, transform_draft_picks_data, transform_players_data, transform_contracts_data, transform_standard_seasonal_data
from src.load import get_bigquery_client, create_dataset_if_not_exists, load_df_to_partitioned_table
from src.materialize import materialize_all

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
        
        logger.info("Extracting draft picks data...")
        draft_df_raw = get_draft_picks_data()
        
        logger.info("Extracting player roster data...")
        players_df_raw = get_players_data()
        
        logger.info("Extracting player contract data...")
        contracts_df_raw = get_contracts_data()
        
        logger.info("Extracting NGS passing data...")
        ngs_passing_raw = get_ngs_passing_data(seasons)
        
        logger.info("Extracting NGS rushing data...")
        ngs_rushing_raw = get_ngs_rushing_data(seasons)
        
        logger.info("Extracting NGS receiving data...")
        ngs_receiving_raw = get_ngs_receiving_data(seasons)
        
        logger.info("Extracting FTN charting data...")
        ftn_raw = get_ftn_charting_data(seasons)
        
        logger.info("Extracting snap counts data...")
        snap_counts_raw = get_snap_counts_data(seasons)
        
        logger.info("Extracting injury reports data...")
        injury_reports_raw = get_injury_reports_data(seasons)
        
        # -------------------------------------------------------------
        # STEP 2: TRANSFORMATION
        # -------------------------------------------------------------
        logger.info("--- Starting Step 2: Transformation ---")
        
        pbp_df_clean = transform_pbp_data(pbp_df_raw)
        weekly_df_clean = transform_weekly_data(weekly_df_raw)
        loaded_seasons = sorted(
            {int(season) for season in (pbp_df_clean["season"].unique() if not pbp_df_clean.empty else [])}
            | {int(season) for season in (weekly_df_clean["season"].unique() if not weekly_df_clean.empty else [])}
        )
        if loaded_seasons != seasons:
            logger.info(f"Using loaded seasons {loaded_seasons} for derived/static tables instead of requested seasons {seasons}.")

        team_df_clean = transform_team_data(team_df_raw, loaded_seasons)
        draft_df_clean = transform_draft_picks_data(draft_df_raw, loaded_seasons)
        players_df_clean = transform_players_data(players_df_raw, loaded_seasons)
        contracts_df_clean = transform_contracts_data(contracts_df_raw, loaded_seasons)
        ngs_passing_clean = transform_standard_seasonal_data(ngs_passing_raw, loaded_seasons, "NGS Passing")
        ngs_rushing_clean = transform_standard_seasonal_data(ngs_rushing_raw, loaded_seasons, "NGS Rushing")
        ngs_receiving_clean = transform_standard_seasonal_data(ngs_receiving_raw, loaded_seasons, "NGS Receiving")
        ftn_clean = transform_standard_seasonal_data(ftn_raw, loaded_seasons, "FTN Charting")
        snap_counts_clean = transform_standard_seasonal_data(snap_counts_raw, loaded_seasons, "Snap Counts")
        injury_reports_clean = transform_standard_seasonal_data(injury_reports_raw, loaded_seasons, "Injury Reports")

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

        # Load draft picks
        load_df_to_partitioned_table(
            client=bq_client,
            df=draft_df_clean,
            dataset_id=dataset_id,
            table_name="draft_picks",
            write_disposition=write_disposition
        )

        # Load player rosters
        load_df_to_partitioned_table(
            client=bq_client,
            df=players_df_clean,
            dataset_id=dataset_id,
            table_name="player_rosters",
            write_disposition=write_disposition
        )

        # Load player contracts
        load_df_to_partitioned_table(
            client=bq_client,
            df=contracts_df_clean,
            dataset_id=dataset_id,
            table_name="player_contracts",
            write_disposition=write_disposition
        )

        # Load NGS and FTN datasets
        load_df_to_partitioned_table(client=bq_client, df=ngs_passing_clean, dataset_id=dataset_id, table_name="ngs_passing", write_disposition=write_disposition)
        load_df_to_partitioned_table(client=bq_client, df=ngs_rushing_clean, dataset_id=dataset_id, table_name="ngs_rushing", write_disposition=write_disposition)
        load_df_to_partitioned_table(client=bq_client, df=ngs_receiving_clean, dataset_id=dataset_id, table_name="ngs_receiving", write_disposition=write_disposition)
        load_df_to_partitioned_table(client=bq_client, df=ftn_clean, dataset_id=dataset_id, table_name="ftn_charting", write_disposition=write_disposition)
        
        # Load snap counts and injury reports
        load_df_to_partitioned_table(client=bq_client, df=snap_counts_clean, dataset_id=dataset_id, table_name="weekly_snap_counts", write_disposition=write_disposition)
        load_df_to_partitioned_table(client=bq_client, df=injury_reports_clean, dataset_id=dataset_id, table_name="injury_reports", write_disposition=write_disposition)

        logger.info("--- Starting Step 4: Materializing AI vs Vibes truth table ---")
        materialize_all(bq_client, dataset_id=dataset_name)
        logger.info("Successfully materialized AI vs Vibes analytics tables.")

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
