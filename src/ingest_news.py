import requests
import pandas as pd
from google.cloud import bigquery
import logging
import time
import json
from datetime import datetime, timezone

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
    snapshot_at = datetime.now(timezone.utc)

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

    current_player_records = []
    fantasy_positions = {"QB", "RB", "WR", "TE", "K", "DEF"}
    for player_id, player in players_map.items():
        position = player.get("position")
        if position not in fantasy_positions:
            continue

        player_name = (
            " ".join(
                part for part in [player.get("first_name"), player.get("last_name")]
                if part
            ).strip()
            or player.get("full_name")
            or player.get("search_full_name")
        )
        current_player_records.append({
            "snapshot_at": snapshot_at,
            "sleeper_player_id": str(player_id),
            "gsis_id": player.get("gsis_id"),
            "player_name": player_name,
            "position": position,
            "team": player.get("team"),
            "active": player.get("active"),
            "status": player.get("status"),
            "injury_status": player.get("injury_status"),
            "fantasy_positions_json": json.dumps(player.get("fantasy_positions") or [], sort_keys=True),
            "depth_chart_position": player.get("depth_chart_position"),
            "depth_chart_order": player.get("depth_chart_order"),
            "search_rank": player.get("search_rank"),
            "years_exp": player.get("years_exp"),
        })

    client = bigquery.Client(project=get_bigquery_project())
    project_id = client.project

    current_players_df = pd.DataFrame(current_player_records)
    if not current_players_df.empty:
        current_players_table_id = f"{project_id}.fantasy_football_brain.sleeper_players_current"
        current_players_schema = [
            bigquery.SchemaField("snapshot_at", "TIMESTAMP"),
            bigquery.SchemaField("sleeper_player_id", "STRING"),
            bigquery.SchemaField("gsis_id", "STRING"),
            bigquery.SchemaField("player_name", "STRING"),
            bigquery.SchemaField("position", "STRING"),
            bigquery.SchemaField("team", "STRING"),
            bigquery.SchemaField("active", "BOOLEAN"),
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("injury_status", "STRING"),
            bigquery.SchemaField("fantasy_positions_json", "STRING"),
            bigquery.SchemaField("depth_chart_position", "STRING"),
            bigquery.SchemaField("depth_chart_order", "INTEGER"),
            bigquery.SchemaField("search_rank", "INTEGER"),
            bigquery.SchemaField("years_exp", "INTEGER"),
        ]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=current_players_schema,
            autodetect=False,
        )
        job = client.load_table_from_dataframe(current_players_df, current_players_table_id, job_config=job_config)
        job.result()
        logger.info(
            "Successfully loaded %s current Sleeper player rows to %s",
            len(current_players_df),
            current_players_table_id,
        )

    df = pd.DataFrame(records)
    if df.empty:
        logger.warning("No valid trending records found after validation.")
        return

    # Convert to appropriate types
    df['trend_count'] = df['trend_count'].astype(int)
    
    logger.info(f"Processed {len(df)} trending records. Pushing to BigQuery...")
    
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
