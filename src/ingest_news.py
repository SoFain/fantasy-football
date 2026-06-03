import requests
import pandas as pd
from google.cloud import bigquery
import logging
import time

from src.load import get_bigquery_project

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ingest_news')

SLEEPER_MAX_CALLS_PER_MINUTE = 900
_sleeper_call_timestamps = []


def sleeper_get(url):
    now = time.monotonic()
    cutoff = now - 60
    while _sleeper_call_timestamps and _sleeper_call_timestamps[0] < cutoff:
        _sleeper_call_timestamps.pop(0)

    if len(_sleeper_call_timestamps) >= SLEEPER_MAX_CALLS_PER_MINUTE:
        sleep_for = 60 - (now - _sleeper_call_timestamps[0])
        logger.warning("Sleeper API throttle reached. Sleeping %.2f seconds.", max(sleep_for, 0))
        time.sleep(max(sleep_for, 0))
        now = time.monotonic()
        cutoff = now - 60
        while _sleeper_call_timestamps and _sleeper_call_timestamps[0] < cutoff:
            _sleeper_call_timestamps.pop(0)

    response = requests.get(url, timeout=30)
    _sleeper_call_timestamps.append(time.monotonic())
    response.raise_for_status()
    return response


def load_realtime_news():
    logger.info("Fetching Sleeper global player map...")
    players_resp = sleeper_get("https://api.sleeper.app/v1/players/nfl")
    players_map = players_resp.json()

    logger.info("Fetching Sleeper trending add/drop vectors...")
    add_resp = sleeper_get("https://api.sleeper.app/v1/players/nfl/trending/add?lookback_hours=24&limit=50")
    drop_resp = sleeper_get("https://api.sleeper.app/v1/players/nfl/trending/drop?lookback_hours=24&limit=50")
    
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
    
    client = bigquery.Client(project=get_bigquery_project())
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
