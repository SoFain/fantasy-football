import logging
from google.cloud import bigquery
from src.load import get_bigquery_project, create_dataset_if_not_exists

logger = logging.getLogger("setup_college_tables")

def create_college_tables(dataset_name="fantasy_football_brain"):
    project_id = get_bigquery_project()
    client = bigquery.Client(project=project_id)
    
    # Ensure dataset exists
    dataset_id = create_dataset_if_not_exists(client, dataset_name)
    
    # 1. Schema for college_player_stats
    college_stats_table_id = f"{dataset_id}.college_player_stats"
    college_stats_schema = [
        bigquery.SchemaField("season", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("player_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("position", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("team", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("conference", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("games", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("passing_yards", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("passing_tds", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("rushing_yards", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("rushing_tds", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("receptions", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("receiving_yards", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("receiving_tds", "FLOAT", mode="NULLABLE"),
    ]
    
    # 2. Schema for rookie_scouting_metrics
    rookie_scouting_table_id = f"{dataset_id}.rookie_scouting_metrics"
    rookie_scouting_schema = [
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
    
    # Function to create partitioned table
    def create_partitioned_table(table_id, schema):
        table = bigquery.Table(table_id, schema=schema)
        table.range_partitioning = bigquery.RangePartitioning(
            field="season",
            range_=bigquery.PartitionRange(start=2000, end=2050, interval=1)
        )
        try:
            client.get_table(table_id)
            logger.info(f"Table '{table_id}' already exists.")
        except Exception:
            try:
                client.create_table(table)
                logger.info(f"Successfully created partitioned table '{table_id}'.")
            except Exception as e:
                logger.error(f"Error creating table '{table_id}': {e}")
                raise e

    logger.info("Setting up college and rookie database tables...")
    create_partitioned_table(college_stats_table_id, college_stats_schema)
    create_partitioned_table(rookie_scouting_table_id, rookie_scouting_schema)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    create_college_tables()
