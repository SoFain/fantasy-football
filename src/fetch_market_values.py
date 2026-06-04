import argparse
import json
import logging
import urllib.request
import urllib.error
from google.cloud import bigquery
from src.load import get_bigquery_project

logger = logging.getLogger("fetch_market_values")

TABLE_ID = "market_values"

def fetch_fantasycalc_values(is_dynasty=True):
    logger.info(f"Fetching current {'dynasty' if is_dynasty else 'redraft'} values from FantasyCalc API...")
    url = f"https://api.fantasycalc.com/values/current?isDynasty={str(is_dynasty).lower()}&numQbs=1&numTeams=12&ppr=1"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode("utf-8"))
            return data
    except urllib.error.HTTPError as e:
        logger.error(f"Failed to fetch values from FantasyCalc (Status {e.code}): {e.reason}")
        return None
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return None

def upload_to_bigquery(values_data, project_id, dataset_id):
    if not values_data:
        return
    
    logger.info("Preparing data for BigQuery...")
    rows_to_insert = []
    
    for item in values_data:
        player_info = item.get("player", {})
        player_name = player_info.get("name")
        position = player_info.get("position")
        team = player_info.get("maybeTeam")
        
        if not player_name:
            continue
            
        rows_to_insert.append({
            "player_display_name": player_name,
            "position": position,
            "team": team,
            "market_value": item.get("value"),
            "overall_rank": item.get("overallRank"),
            "position_rank": item.get("positionRank"),
            "redraft_value": item.get("redraftValue"),
            "tier": item.get("maybeTier"),
        })
        
    logger.info(f"Loaded {len(rows_to_insert)} players. Connecting to BigQuery...")
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_id}.{TABLE_ID}"
    
    # Define Table Schema
    schema = [
        bigquery.SchemaField("player_display_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("position", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("team", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("market_value", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("overall_rank", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("position_rank", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("redraft_value", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("tier", "INTEGER", mode="NULLABLE"),
    ]
    
    # Create table if it doesn't exist
    try:
        table = bigquery.Table(table_ref, schema=schema)
        # Use overwrite/recreate daily
        client.delete_table(table_ref, not_found_ok=True)
        table = client.create_table(table)
        logger.info(f"Recreated table {table_ref} successfully.")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        return

    # Insert Rows in chunks of 500
    chunk_size = 500
    for i in range(0, len(rows_to_insert), chunk_size):
        chunk = rows_to_insert[i:i + chunk_size]
        errors = client.insert_rows_json(table_ref, chunk)
        if errors:
            logger.error(f"Errors occurred during BigQuery insert: {errors}")
            return
            
    logger.info(f"Successfully uploaded {len(rows_to_insert)} player values to {table_ref}!")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    parser = argparse.ArgumentParser(description="Ingest player market values from FantasyCalc and load them into BigQuery.")
    parser.add_argument("--redraft", action="store_true", help="Fetch redraft values instead of dynasty.")
    parser.add_argument("--dataset", default="fantasy_football_brain", help="BigQuery dataset name.")
    args = parser.parse_args()
    
    project_id = get_bigquery_project()
    
    is_dynasty = not args.redraft
    data = fetch_fantasycalc_values(is_dynasty=is_dynasty)
    if data:
        upload_to_bigquery(data, project_id, args.dataset)

if __name__ == "__main__":
    main()
