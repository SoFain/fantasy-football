import requests
import pandas as pd
from google.cloud import bigquery
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ingest_news')

def load_realtime_news():
    logger.info("Fetching Sleeper global player map...")
    players_resp = requests.get("https://api.sleeper.app/v1/players/nfl")
    players_resp.raise_for_status()
    players_map = players_resp.json()

    logger.info("Fetching Sleeper trending add/drop vectors...")
    add_resp = requests.get("https://api.sleeper.app/v1/players/nfl/trending/add?lookback_hours=24&limit=50")
    drop_resp = requests.get("https://api.sleeper.app/v1/players/nfl/trending/drop?lookback_hours=24&limit=50")
    add_resp.raise_for_status()
    drop_resp.raise_for_status()
    
    trending_adds = add_resp.json()
    trending_drops = drop_resp.json()

    records = []
    
    # Process adds
    for item in trending_adds:
        player_id = item.get("player_id")
        count = item.get("count", 0)
        p_data = players_map.get(str(player_id), {})
        
        # Validation checks
        gsis_id = p_data.get("gsis_id")
        team = p_data.get("team")
        position = p_data.get("position")
        
        if not gsis_id and not team:
            continue
            
        records.append({
            "player_id": player_id,
            "gsis_id": gsis_id,
            "player_name": f"{p_data.get('first_name', '')} {p_data.get('last_name', '')}".strip(),
            "position": position,
            "team": team,
            "trend_type": "ADD",
            "trend_count": count
        })

    # Process drops
    for item in trending_drops:
        player_id = item.get("player_id")
        count = item.get("count", 0)
        p_data = players_map.get(str(player_id), {})
        
        # Validation checks
        gsis_id = p_data.get("gsis_id")
        team = p_data.get("team")
        position = p_data.get("position")
        
        if not gsis_id and not team:
            continue
            
        records.append({
            "player_id": player_id,
            "gsis_id": gsis_id,
            "player_name": f"{p_data.get('first_name', '')} {p_data.get('last_name', '')}".strip(),
            "position": position,
            "team": team,
            "trend_type": "DROP",
            "trend_count": count
        })

    df = pd.DataFrame(records)
    if df.empty:
        logger.warning("No valid trending records found after validation.")
        return

    # Convert to appropriate types
    df['trend_count'] = df['trend_count'].astype(int)
    
    logger.info(f"Processed {len(df)} trending records. Pushing to BigQuery...")
    
    client = bigquery.Client()
    project_id = client.project
    table_id = f"{project_id}.fantasy_football_brain.realtime_player_news"

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    
    job = client.load_table_from_dataframe(
        df, table_id, job_config=job_config
    )
    job.result()
    
    table = client.get_table(table_id)
    logger.info(f"Successfully loaded {table.num_rows} rows and {len(table.schema)} columns to {table_id}")

if __name__ == "__main__":
    load_realtime_news()
