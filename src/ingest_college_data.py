import argparse
import json
import logging
import os
import urllib.request
import urllib.error
import pandas as pd
from google.cloud import bigquery
from src.load import get_bigquery_project

logger = logging.getLogger("ingest_college_data")

TABLE_ID = "college_player_stats"

def fetch_cfbd_category_stats(season, category, api_key):
    url = f"https://api.collegefootballdata.com/stats/player/season?year={season}&category={category}"
    logger.info(f"Fetching CFBD stats for {season} ({category})...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        logger.error(f"CFBD API error for category {category} (Status {e.code}): {e.reason}")
        return None
    except Exception as e:
        logger.error(f"Error fetching CFBD data: {e}")
        return None

def get_mock_college_stats(season):
    logger.info(f"Generating high-fidelity mock college stats for season {season}...")
    mock_data = [
        # QBs
        {"player_name": "Caleb Williams", "position": "QB", "team": "USC", "conference": "Pac-12", "games": 12, "passing_yards": 3633.0, "passing_tds": 30.0, "rushing_yards": 136.0, "rushing_tds": 11.0, "receptions": 0.0, "receiving_yards": 0.0, "receiving_tds": 0.0},
        {"player_name": "Jayden Daniels", "position": "QB", "team": "LSU", "conference": "SEC", "games": 12, "passing_yards": 3812.0, "passing_tds": 40.0, "rushing_yards": 1134.0, "rushing_tds": 10.0, "receptions": 0.0, "receiving_yards": 0.0, "receiving_tds": 0.0},
        {"player_name": "Drake Maye", "position": "QB", "team": "North Carolina", "conference": "ACC", "games": 12, "passing_yards": 3608.0, "passing_tds": 24.0, "rushing_yards": 449.0, "rushing_tds": 9.0, "receptions": 0.0, "receiving_yards": 0.0, "receiving_tds": 0.0},
        # WRs
        {"player_name": "Marvin Harrison Jr.", "position": "WR", "team": "Ohio State", "conference": "Big Ten", "games": 12, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 58.0, "rushing_tds": 0.0, "receptions": 67.0, "receiving_yards": 1211.0, "receiving_tds": 14.0},
        {"player_name": "Malik Nabers", "position": "WR", "team": "LSU", "conference": "SEC", "games": 13, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 2.0, "rushing_tds": 0.0, "receptions": 89.0, "receiving_yards": 1569.0, "receiving_tds": 14.0},
        {"player_name": "Rome Odunze", "position": "WR", "team": "Washington", "conference": "Pac-12", "games": 15, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 14.0, "rushing_tds": 1.0, "receptions": 92.0, "receiving_yards": 1640.0, "receiving_tds": 13.0},
        {"player_name": "Brian Thomas Jr.", "position": "WR", "team": "LSU", "conference": "SEC", "games": 13, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 0.0, "rushing_tds": 0.0, "receptions": 68.0, "receiving_yards": 1177.0, "receiving_tds": 17.0},
        {"player_name": "Xavier Worthy", "position": "WR", "team": "Texas", "conference": "Big 12", "games": 14, "passing_yards": 35.0, "passing_tds": 1.0, "rushing_yards": 35.0, "rushing_tds": 0.0, "receptions": 75.0, "receiving_yards": 1014.0, "receiving_tds": 5.0},
        # TEs
        {"player_name": "Brock Bowers", "position": "TE", "team": "Georgia", "conference": "SEC", "games": 10, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 28.0, "rushing_tds": 1.0, "receptions": 56.0, "receiving_yards": 714.0, "receiving_tds": 6.0},
        # RBs
        {"player_name": "Jonathon Brooks", "position": "RB", "team": "Texas", "conference": "Big 12", "games": 11, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 1139.0, "rushing_tds": 10.0, "receptions": 25.0, "receiving_yards": 286.0, "receiving_tds": 1.0},
        {"player_name": "Trey Benson", "position": "RB", "team": "Florida State", "conference": "ACC", "games": 13, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 906.0, "rushing_tds": 14.0, "receptions": 20.0, "receiving_yards": 227.0, "receiving_tds": 1.0},
        {"player_name": "Blake Corum", "position": "RB", "team": "Michigan", "conference": "Big Ten", "games": 15, "passing_yards": 0.0, "passing_tds": 0.0, "rushing_yards": 1245.0, "rushing_tds": 27.0, "receptions": 16.0, "receiving_yards": 117.0, "receiving_tds": 0.0},
    ]
    df = pd.DataFrame(mock_data)
    df["season"] = int(season)
    return df

def parse_cfbd_stats(season, api_key):
    categories = ["passing", "rushing", "receiving"]
    
    # Store aggregated stats per player/team/conference
    # Key: (player_name, team, conference) -> dict of stats
    player_map = {}
    
    for category in categories:
        records = fetch_cfbd_category_stats(season, category, api_key)
        if not records:
            continue
            
        for item in records:
            player_name = item.get("player")
            team = item.get("team")
            conference = item.get("conference")
            
            if not player_name or not team:
                continue
                
            key = (player_name, team, conference)
            if key not in player_map:
                player_map[key] = {
                    "player_name": player_name,
                    "team": team,
                    "conference": conference,
                    "games": None,
                    "passing_yards": 0.0,
                    "passing_tds": 0.0,
                    "rushing_yards": 0.0,
                    "rushing_tds": 0.0,
                    "receptions": 0.0,
                    "receiving_yards": 0.0,
                    "receiving_tds": 0.0,
                    "position": None
                }
            
            p_data = player_map[key]
            stat_type = item.get("statType")
            stat_val = float(item.get("stat") or 0)
            
            if category == "passing":
                p_data["position"] = "QB"
                if stat_type == "YDS":
                    p_data["passing_yards"] = stat_val
                elif stat_type == "TD":
                    p_data["passing_tds"] = stat_val
            elif category == "rushing":
                if p_data["position"] is None:
                    p_data["position"] = "RB"
                if stat_type == "YDS":
                    p_data["rushing_yards"] = stat_val
                elif stat_type == "TD":
                    p_data["rushing_tds"] = stat_val
            elif category == "receiving":
                if p_data["position"] is None or p_data["position"] == "RB":
                    # If they run and catch, it might be RB or WR. We default to WR if they have receiving yards.
                    p_data["position"] = "WR"
                if stat_type == "REC":
                    p_data["receptions"] = stat_val
                elif stat_type == "YDS":
                    p_data["receiving_yards"] = stat_val
                elif stat_type == "TD":
                    p_data["receiving_tds"] = stat_val
                    
    if not player_map:
        return pd.DataFrame()
        
    df = pd.DataFrame(player_map.values())
    df["season"] = int(season)
    
    # Clean up positions or fill missing columns if needed
    return df

def upload_to_bigquery(df, project_id, dataset_name):
    if df.empty:
        logger.warning("No stats found to upload.")
        return
        
    client = bigquery.Client(project=project_id)
    table_ref = f"{project_id}.{dataset_name}.{TABLE_ID}"
    
    logger.info(f"Uploading {len(df)} records to BigQuery: {table_ref}...")
    
    # We will delete the partition/season data first to prevent duplicate rows on re-run
    season = int(df["season"].iloc[0])
    try:
        delete_query = f"DELETE FROM `{table_ref}` WHERE season = {season}"
        client.query(delete_query).result()
        logger.info(f"Deleted existing records for season {season}.")
    except Exception as e:
        logger.warning(f"Could not execute pre-cleanup query: {e}")
        
    # Configure load job
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema=[
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
    )
    
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    logger.info(f"Successfully loaded {len(df)} rows into '{table_ref}'!")

def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    parser = argparse.ArgumentParser(description="Ingest college stats from CFBD API and load to BigQuery.")
    parser.add_argument("--season", required=True, type=int, help="Target season/year.")
    parser.add_argument("--api-key", help="CFBD API Key. Pass 'mock' to generate realistic test data.")
    parser.add_argument("--dataset", default="fantasy_football_brain", help="BigQuery dataset name.")
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("CFBD_API_KEY")
    project_id = get_bigquery_project()
    
    if not api_key:
        logger.error(
            "No API key provided. Please pass --api-key, set the CFBD_API_KEY environment variable, "
            "or use 'mock' as the key to generate test data."
        )
        return
        
    if api_key.strip().lower() == "mock":
        df = get_mock_college_stats(args.season)
    else:
        df = parse_cfbd_stats(args.season, api_key.strip())
        
    if not df.empty:
        # Reorder and filter columns to match schema
        cols = ["season", "player_name", "position", "team", "conference", "games", 
                "passing_yards", "passing_tds", "rushing_yards", "rushing_tds", 
                "receptions", "receiving_yards", "receiving_tds"]
        for c in cols:
            if c not in df.columns:
                df[c] = None
        df = df[cols]
        upload_to_bigquery(df, project_id, args.dataset)
    else:
        logger.warning("No data retrieved.")

if __name__ == "__main__":
    main()
