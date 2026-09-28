"""Refresh weekly_metrics for one season without touching historical or ranking rows.

Dry-run by default. --apply stages source rows, rejects loss of existing keys,
then replaces only the requested season in one transaction. Upstream columns
outside the existing warehouse contract are reported, not silently added.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from google.cloud import bigquery
import nflreadpy as nfl
import pandas as pd
from src.extract import get_weekly_data
from src.load import coerce_dataframe_to_existing_schema, get_bigquery_client

KEY = ["player_id", "season", "week", "season_type", "team"]


def validate_source(frame: pd.DataFrame, season: int) -> None:
    if frame.empty or not frame.season.eq(season).all():
        raise ValueError("Expected nonempty data for exactly the requested season")
    if frame[["season", "week", "season_type", "team", "game_id"]].isna().any().any() or frame.duplicated(KEY).any():
        raise ValueError("Null identifiers or duplicate player-week-team keys")
    if not frame.week.between(1, 22).all():
        raise ValueError("Unexpected source week")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--season", type=int, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not 2000 <= args.season <= datetime.now().year:
        parser.error("Season must be between 2000 and the current year")
    frame = get_weekly_data([args.season])
    validate_source(frame, args.season)
    schedule = nfl.load_schedules([args.season]).to_pandas()
    completed = schedule.loc[schedule.home_score.notna() & schedule.away_score.notna()]
    pending_games = sorted(set(completed.game_id) - set(frame.game_id))
    client = get_bigquery_client()
    target = f"{client.project}.fantasy_football_brain.weekly_metrics"
    table = client.get_table(target)
    columns = [field.name for field in table.schema]
    missing = sorted(set(columns) - set(frame))
    if missing:
        raise ValueError(f"Source missing warehouse columns: {missing}")
    data, compatibility = coerce_dataframe_to_existing_schema(
        frame[columns], "weekly_metrics", "WRITE_APPEND", table.schema
    )
    if not compatibility["safe_to_proceed"]:
        raise ValueError(f"Incompatible source schema: {compatibility}")
    report = {
        "season": args.season, "rows": len(frame), "applied": False,
        "source_rows_without_player_id": int(frame.player_id.isna().sum()),
        "coverage": frame.groupby("week").agg(rows=("player_id", "size"), games=("game_id", "nunique"), teams=("team", "nunique")).reset_index().to_dict("records"),
        "completed_games_awaiting_source_stats": pending_games,
        "source_columns_outside_existing_contract": sorted(set(frame) - set(columns)),
    }
    if args.apply:
        stage_id = f"{target}_refresh_{uuid.uuid4().hex}"
        stage = bigquery.Table(stage_id, schema=table.schema)
        stage.expires = datetime.now(timezone.utc) + timedelta(hours=2)
        client.create_table(stage)
        try:
            client.load_table_from_dataframe(data, stage_id, job_config=bigquery.LoadJobConfig(schema=table.schema, write_disposition="WRITE_EMPTY")).result()
            names = ", ".join(f"`{name}`" for name in columns)
            keys = ", ".join(f"`{name}`" for name in KEY)
            sql = f"""BEGIN TRANSACTION;
ASSERT NOT EXISTS (
 SELECT {keys} FROM `{target}` WHERE season = @season
 EXCEPT DISTINCT SELECT {keys} FROM `{stage_id}`
) AS 'Source refresh would remove existing player-week rows';
DELETE FROM `{target}` WHERE season = @season;
INSERT INTO `{target}` ({names}) SELECT {names} FROM `{stage_id}`;
COMMIT TRANSACTION;"""
            job = client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter("season", "INT64", args.season)]))
            job.result()
            report.update(applied=True, job_id=job.job_id)
        finally:
            client.delete_table(stage_id, not_found_ok=True)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
