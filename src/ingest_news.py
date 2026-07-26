import requests
import pandas as pd
from google.cloud import bigquery
import logging
import time
import json
from datetime import datetime, timezone

from src.load import get_bigquery_project
from src.sleeper_injury_reviews import build_injury_review_events
from src.player_status_changes import compute_age

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ingest_news')

SLEEPER_MAX_CALLS_PER_MINUTE = 900
_sleeper_call_timestamps = []


def _parse_birth_date(value):
    """Sleeper sends YYYY-MM-DD, but empty strings and nulls both appear."""
    if not value:
        return None
    try:
        return datetime.strptime(str(value).strip()[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        logger.debug("Unparseable Sleeper birth_date: %r", value)
        return None


def _clean_int(value):
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _clean_str(value):
    if value is None:
        return None
    text = str(value).strip()
    return text or None


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


PLAYERS_ENDPOINT = "https://api.sleeper.app/v1/players/nfl?active=true"


def _snapshot_exists_today(client, as_of_date):
    """True when sleeper_players_history already holds a snapshot for today.

    Returns False if the table is missing or empty, so the first run after the
    migration proceeds.
    """
    table_id = f"{client.project}.fantasy_football_brain.sleeper_players_history"
    from google.cloud import bigquery

    sql = f"""
    SELECT COUNT(1) AS n
    FROM `{table_id}`
    WHERE DATE(snapshot_at) = @as_of
    """
    try:
        job = client.query(
            sql,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[bigquery.ScalarQueryParameter("as_of", "DATE", as_of_date)]
            ),
        )
        return next(iter(job.result())).n > 0
    except Exception as exc:
        logger.info("Could not check for today's snapshot (%s); proceeding.", exc)
        return False


def load_realtime_news(force=False, client=None):
    # Only /v1/players/ is rate-limited to once per day by Sleeper; it is ~5MB.
    # This job is its single caller, and everything else reads the saved
    # snapshot. Other Sleeper endpoints (trending, league, rosters, matchups)
    # have no such limit. The guard makes once-per-day a property of the code,
    # not just the schedule: a manual re-run or retry on the same day is a no-op
    # unless forced. Trending shares this daily cadence only because it is
    # enriched from the same player map.
    if client is None:
        client = bigquery.Client(project=get_bigquery_project())

    snapshot_at = datetime.now(timezone.utc)
    if not force and _snapshot_exists_today(client, snapshot_at.date()):
        logger.info(
            "Sleeper snapshot already exists for %s; skipping. Pass force=True to override.",
            snapshot_at.date(),
        )
        return

    # active=true returns only active players and a much smaller payload, per the
    # Sleeper players endpoint docs. Every ingested row therefore has
    # active=true; a player leaving the active set drops out of the snapshot
    # rather than flipping the field.
    logger.info("Fetching Sleeper active player map...")
    players_resp = sleeper_get(PLAYERS_ENDPOINT)
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
        birth_date = _parse_birth_date(player.get("birth_date"))
        current_player_records.append({
            "snapshot_at": snapshot_at,
            "sleeper_player_id": str(player_id),
            "gsis_id": player.get("gsis_id"),
            "player_name": player_name,
            "position": position,
            "team": player.get("team"),
            # The endpoint is filtered to active=true, so this is always true.
            # Default to True rather than trusting a possibly-absent field.
            "active": player.get("active", True) if player.get("active") is not None else True,
            "status": player.get("status"),
            "injury_status": player.get("injury_status"),
            "injury_body_part": player.get("injury_body_part"),
            "injury_notes": player.get("injury_notes"),
            "practice_participation": player.get("practice_participation"),
            "fantasy_positions_json": json.dumps(player.get("fantasy_positions") or [], sort_keys=True),
            "depth_chart_position": player.get("depth_chart_position"),
            "depth_chart_order": player.get("depth_chart_order"),
            "search_rank": player.get("search_rank"),
            "years_exp": player.get("years_exp"),
            "birth_date": birth_date,
            "age": compute_age(birth_date, snapshot_at.date()),
            "number": _clean_int(player.get("number")),
            "height": _clean_str(player.get("height")),
            "weight": _clean_str(player.get("weight")),
            "college": _clean_str(player.get("college")),
        })

    project_id = client.project

    previous_statuses = {}
    injury_events = []
    current_players_table_id = f"{project_id}.fantasy_football_brain.sleeper_players_current"
    try:
        previous_query = f"""
        SELECT sleeper_player_id, injury_status
        FROM `{current_players_table_id}`
        """
        previous_statuses = {
            str(row.sleeper_player_id): row.injury_status
            for row in client.query(previous_query).result()
        }
    except Exception as ex:
        logger.info("No prior Sleeper player snapshot available for injury review: %s", ex)

    current_players_df = pd.DataFrame(current_player_records)
    if not current_players_df.empty:
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
            bigquery.SchemaField("birth_date", "DATE"),
            bigquery.SchemaField("age", "FLOAT"),
            bigquery.SchemaField("number", "INTEGER"),
            bigquery.SchemaField("height", "STRING"),
            bigquery.SchemaField("weight", "STRING"),
            bigquery.SchemaField("college", "STRING"),
            bigquery.SchemaField("injury_body_part", "STRING"),
            bigquery.SchemaField("injury_notes", "STRING"),
            bigquery.SchemaField("practice_participation", "STRING"),
        ]
        job_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=current_players_schema,
            autodetect=False,
        )
        # Append to history BEFORE truncating current. History is what makes
        # day-over-day change detection possible; the truncating table cannot
        # support it because yesterday's rows are gone by the time the next
        # run reads them.
        history_table_id = f"{project_id}.fantasy_football_brain.sleeper_players_history"
        # The history DDL declares snapshot_at and sleeper_player_id NOT NULL.
        # A load-job schema must match column modes exactly, and SchemaField
        # defaults to NULLABLE, so mark those two REQUIRED here.
        history_schema = [
            bigquery.SchemaField(f.name, f.field_type, mode="REQUIRED")
            if f.name in ("snapshot_at", "sleeper_player_id") else f
            for f in current_players_schema
        ]
        history_config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
            schema=history_schema,
            autodetect=False,
        )
        client.load_table_from_dataframe(
            current_players_df, history_table_id, job_config=history_config
        ).result()
        logger.info(
            "Appended %s Sleeper player rows to %s", len(current_players_df), history_table_id
        )

        job = client.load_table_from_dataframe(current_players_df, current_players_table_id, job_config=job_config)
        job.result()
        logger.info(
            "Successfully loaded %s current Sleeper player rows to %s",
            len(current_players_df),
            current_players_table_id,
        )

        injury_events = build_injury_review_events(
            previous_statuses,
            current_player_records,
            snapshot_at,
        )
        if injury_events:
            review_table_id = f"{project_id}.fantasy_football_brain.sleeper_injury_review_queue"
            review_job = client.load_table_from_json(
                injury_events,
                review_table_id,
                job_config=bigquery.LoadJobConfig(
                    write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                ),
            )
            review_job.result()
            logger.info("Queued %s OUT/IR Sleeper injury reviews.", len(injury_events))

    df = pd.DataFrame(records)
    if df.empty:
        logger.warning("No valid trending records found after validation.")
        return {"current_player_count": len(current_player_records), "injury_review_count": len(injury_events) if current_player_records else 0}

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
    return {"current_player_count": len(current_player_records), "injury_review_count": len(injury_events) if current_player_records else 0}

if __name__ == "__main__":
    load_realtime_news()
