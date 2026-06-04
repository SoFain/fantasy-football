import argparse
import json
import logging
from datetime import datetime, timezone

import pandas as pd
from google.cloud import bigquery

from src.ingest_news import sleeper_get
from src.load import create_dataset_if_not_exists, get_bigquery_project


logger = logging.getLogger("ingest_sleeper_league")

SLEEPER_BASE_URL = "https://api.sleeper.app/v1"

SLEEPER_TABLE_SCHEMAS = {
    "sleeper_leagues": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("name", "STRING"), ("status", "STRING"), ("sport", "STRING"), ("season_type", "STRING"),
        ("total_rosters", "INTEGER"), ("scoring_settings_json", "STRING"), ("roster_positions_json", "STRING"),
        ("settings_json", "STRING"),
    ],
    "sleeper_league_users": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("user_id", "STRING"), ("username", "STRING"), ("display_name", "STRING"), ("team_name", "STRING"),
        ("is_viewer_team", "BOOLEAN"),
    ],
    "sleeper_rosters": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("roster_id", "INTEGER"), ("owner_id", "STRING"), ("username", "STRING"), ("display_name", "STRING"),
        ("team_name", "STRING"), ("is_viewer_team", "BOOLEAN"), ("wins", "INTEGER"), ("losses", "INTEGER"),
        ("ties", "INTEGER"), ("points_for", "FLOAT"), ("points_for_decimal", "FLOAT"),
        ("points_against", "FLOAT"), ("points_against_decimal", "FLOAT"), ("waiver_position", "INTEGER"),
        ("raw_settings_json", "STRING"),
    ],
    "sleeper_roster_players": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("roster_id", "INTEGER"), ("owner_id", "STRING"), ("is_viewer_team", "BOOLEAN"),
        ("sleeper_player_id", "STRING"), ("player_name", "STRING"), ("position", "STRING"), ("team", "STRING"),
        ("gsis_id", "STRING"), ("status", "STRING"), ("injury_status", "STRING"),
        ("is_starter", "BOOLEAN"), ("is_taxi", "BOOLEAN"), ("is_reserve", "BOOLEAN"),
    ],
    "sleeper_matchups": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("roster_id", "INTEGER"), ("matchup_id", "INTEGER"), ("owner_id", "STRING"), ("username", "STRING"),
        ("display_name", "STRING"), ("team_name", "STRING"), ("is_viewer_team", "BOOLEAN"), ("points", "FLOAT"),
    ],
    "sleeper_lineups": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("roster_id", "INTEGER"), ("matchup_id", "INTEGER"), ("owner_id", "STRING"),
        ("is_viewer_team", "BOOLEAN"), ("sleeper_player_id", "STRING"), ("player_name", "STRING"),
        ("position", "STRING"), ("team", "STRING"), ("gsis_id", "STRING"), ("is_starter", "BOOLEAN"),
        ("points", "FLOAT"),
    ],
    "sleeper_available_players": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("sleeper_player_id", "STRING"), ("player_name", "STRING"), ("position", "STRING"), ("team", "STRING"),
        ("gsis_id", "STRING"), ("status", "STRING"), ("injury_status", "STRING"),
        ("depth_chart_position", "STRING"), ("depth_chart_order", "INTEGER"), ("fantasy_positions_json", "STRING"),
    ],
    "sleeper_viewer_team_snapshots": [
        ("snapshot_at", "TIMESTAMP"), ("league_id", "STRING"), ("season", "INTEGER"), ("week", "INTEGER"),
        ("viewer_roster_id", "INTEGER"), ("viewer_owner_id", "STRING"), ("viewer_username", "STRING"),
        ("viewer_display_name", "STRING"), ("viewer_team_name", "STRING"), ("matchup_id", "INTEGER"),
        ("points", "FLOAT"), ("starters_json", "STRING"), ("players_json", "STRING"),
    ],
}


def fetch_json(path):
    response = sleeper_get(f"{SLEEPER_BASE_URL}{path}")
    return response.json()


def player_name(player_data):
    return " ".join(
        part for part in [player_data.get("first_name"), player_data.get("last_name")]
        if part
    ).strip() or player_data.get("full_name")


def normalize_lookup(value):
    return str(value or "").lower().strip()


def resolve_viewer_roster(rosters, users, roster_id=None, username=None, display_name=None, team_name=None):
    if roster_id:
        roster_id_int = int(roster_id)
        for roster in rosters:
            if roster.get("roster_id") == roster_id_int:
                return roster
        raise RuntimeError(f"No Sleeper roster found for roster_id={roster_id}.")

    owner_id = None
    if username or display_name or team_name:
        wanted_username = normalize_lookup(username) if username else None
        wanted_display_name = normalize_lookup(display_name) if display_name else None
        wanted_team_name = normalize_lookup(team_name) if team_name else None
        for user in users:
            metadata = user.get("metadata") or {}
            if wanted_username and normalize_lookup(user.get("username")) == wanted_username:
                owner_id = user.get("user_id")
                break
            if wanted_display_name and normalize_lookup(user.get("display_name")) == wanted_display_name:
                owner_id = user.get("user_id")
                break
            if wanted_team_name and normalize_lookup(metadata.get("team_name")) == wanted_team_name:
                owner_id = user.get("user_id")
                break

    if not owner_id:
        raise RuntimeError("Could not resolve viewer team. Provide roster_id, username, display_name, or team_name.")

    for roster in rosters:
        if roster.get("owner_id") == owner_id:
            return roster

    raise RuntimeError(f"No Sleeper roster found for owner_id={owner_id}.")


def user_by_id(users):
    return {user.get("user_id"): user for user in users}


def matchup_by_roster(matchups):
    return {matchup.get("roster_id"): matchup for matchup in matchups}


def build_records(league_id, week, league, users, rosters, matchups, players_map, viewer_roster):
    snapshot_at = datetime.now(timezone.utc)
    season = int(league.get("season") or datetime.now(timezone.utc).year)
    viewer_roster_id = viewer_roster.get("roster_id")
    users_lookup = user_by_id(users)
    matchups_lookup = matchup_by_roster(matchups)
    viewer_user = users_lookup.get(viewer_roster.get("owner_id"), {})
    viewer_matchup = matchups_lookup.get(viewer_roster_id, {})

    league_rows = [{
        "snapshot_at": snapshot_at,
        "league_id": str(league_id),
        "season": season,
        "week": int(week),
        "name": league.get("name"),
        "status": league.get("status"),
        "sport": league.get("sport"),
        "season_type": league.get("season_type"),
        "total_rosters": league.get("total_rosters"),
        "scoring_settings_json": json.dumps(league.get("scoring_settings") or {}, sort_keys=True),
        "roster_positions_json": json.dumps(league.get("roster_positions") or [], sort_keys=True),
        "settings_json": json.dumps(league.get("settings") or {}, sort_keys=True),
    }]

    user_rows = []
    for user in users:
        user_rows.append({
            "snapshot_at": snapshot_at,
            "league_id": str(league_id),
            "season": season,
            "week": int(week),
            "user_id": user.get("user_id"),
            "username": user.get("username"),
            "display_name": user.get("display_name"),
            "team_name": (user.get("metadata") or {}).get("team_name"),
            "is_viewer_team": user.get("user_id") == viewer_roster.get("owner_id"),
        })

    roster_rows = []
    roster_player_rows = []
    rostered_player_ids = set()
    for roster in rosters:
        owner = users_lookup.get(roster.get("owner_id"), {})
        is_viewer_team = roster.get("roster_id") == viewer_roster_id
        roster_rows.append({
            "snapshot_at": snapshot_at,
            "league_id": str(league_id),
            "season": season,
            "week": int(week),
            "roster_id": roster.get("roster_id"),
            "owner_id": roster.get("owner_id"),
            "username": owner.get("username"),
            "display_name": owner.get("display_name"),
            "team_name": (owner.get("metadata") or {}).get("team_name"),
            "is_viewer_team": is_viewer_team,
            "wins": (roster.get("settings") or {}).get("wins"),
            "losses": (roster.get("settings") or {}).get("losses"),
            "ties": (roster.get("settings") or {}).get("ties"),
            "points_for": (roster.get("settings") or {}).get("fpts"),
            "points_for_decimal": (roster.get("settings") or {}).get("fpts_decimal"),
            "points_against": (roster.get("settings") or {}).get("fpts_against"),
            "points_against_decimal": (roster.get("settings") or {}).get("fpts_against_decimal"),
            "waiver_position": (roster.get("settings") or {}).get("waiver_position"),
            "raw_settings_json": json.dumps(roster.get("settings") or {}, sort_keys=True),
        })

        starters = set(str(player_id) for player_id in roster.get("starters") or [])
        taxi = set(str(player_id) for player_id in roster.get("taxi") or [])
        reserve = set(str(player_id) for player_id in roster.get("reserve") or [])
        for player_id in roster.get("players") or []:
            player_id = str(player_id)
            rostered_player_ids.add(player_id)
            player = players_map.get(player_id, {})
            roster_player_rows.append({
                "snapshot_at": snapshot_at,
                "league_id": str(league_id),
                "season": season,
                "week": int(week),
                "roster_id": roster.get("roster_id"),
                "owner_id": roster.get("owner_id"),
                "is_viewer_team": is_viewer_team,
                "sleeper_player_id": player_id,
                "player_name": player_name(player),
                "position": player.get("position"),
                "team": player.get("team"),
                "gsis_id": player.get("gsis_id"),
                "status": player.get("status"),
                "injury_status": player.get("injury_status"),
                "is_starter": player_id in starters,
                "is_taxi": player_id in taxi,
                "is_reserve": player_id in reserve,
            })

    matchup_rows = []
    lineup_rows = []
    for matchup in matchups:
        roster_id = matchup.get("roster_id")
        roster = next((item for item in rosters if item.get("roster_id") == roster_id), {})
        owner = users_lookup.get(roster.get("owner_id"), {})
        is_viewer_team = roster_id == viewer_roster_id
        matchup_rows.append({
            "snapshot_at": snapshot_at,
            "league_id": str(league_id),
            "season": season,
            "week": int(week),
            "roster_id": roster_id,
            "matchup_id": matchup.get("matchup_id"),
            "owner_id": roster.get("owner_id"),
            "username": owner.get("username"),
            "display_name": owner.get("display_name"),
            "team_name": (owner.get("metadata") or {}).get("team_name"),
            "is_viewer_team": is_viewer_team,
            "points": matchup.get("points"),
        })

        starters = set(str(player_id) for player_id in matchup.get("starters") or [])
        player_points = matchup.get("players_points") or {}
        for player_id in matchup.get("players") or []:
            player_id = str(player_id)
            player = players_map.get(player_id, {})
            lineup_rows.append({
                "snapshot_at": snapshot_at,
                "league_id": str(league_id),
                "season": season,
                "week": int(week),
                "roster_id": roster_id,
                "matchup_id": matchup.get("matchup_id"),
                "owner_id": roster.get("owner_id"),
                "is_viewer_team": is_viewer_team,
                "sleeper_player_id": player_id,
                "player_name": player_name(player),
                "position": player.get("position"),
                "team": player.get("team"),
                "gsis_id": player.get("gsis_id"),
                "is_starter": player_id in starters,
                "points": player_points.get(player_id),
            })

    fantasy_positions = {"QB", "RB", "WR", "TE", "K", "DEF"}
    available_player_rows = []
    for player_id, player in players_map.items():
        player_id = str(player_id)
        position = player.get("position")
        if player_id in rostered_player_ids or position not in fantasy_positions:
            continue
        if player.get("active") is False and player.get("status") not in {"Active", "ACT", None}:
            continue

        available_player_rows.append({
            "snapshot_at": snapshot_at,
            "league_id": str(league_id),
            "season": season,
            "week": int(week),
            "sleeper_player_id": player_id,
            "player_name": player_name(player),
            "position": position,
            "team": player.get("team"),
            "gsis_id": player.get("gsis_id"),
            "status": player.get("status"),
            "injury_status": player.get("injury_status"),
            "depth_chart_position": player.get("depth_chart_position"),
            "depth_chart_order": player.get("depth_chart_order"),
            "fantasy_positions_json": json.dumps(player.get("fantasy_positions") or [], sort_keys=True),
        })

    viewer_summary_rows = [{
        "snapshot_at": snapshot_at,
        "league_id": str(league_id),
        "season": season,
        "week": int(week),
        "viewer_roster_id": viewer_roster_id,
        "viewer_owner_id": viewer_roster.get("owner_id"),
        "viewer_username": viewer_user.get("username"),
        "viewer_display_name": viewer_user.get("display_name"),
        "viewer_team_name": (viewer_user.get("metadata") or {}).get("team_name"),
        "matchup_id": viewer_matchup.get("matchup_id"),
        "points": viewer_matchup.get("points"),
        "starters_json": json.dumps(viewer_roster.get("starters") or [], sort_keys=True),
        "players_json": json.dumps(viewer_roster.get("players") or [], sort_keys=True),
    }]

    return {
        "sleeper_leagues": league_rows,
        "sleeper_league_users": user_rows,
        "sleeper_rosters": roster_rows,
        "sleeper_roster_players": roster_player_rows,
        "sleeper_matchups": matchup_rows,
        "sleeper_lineups": lineup_rows,
        "sleeper_available_players": available_player_rows,
        "sleeper_viewer_team_snapshots": viewer_summary_rows,
    }


def load_rows(client, dataset_id, table_name, rows):
    if not rows:
        logger.warning("No rows generated for %s. Skipping.", table_name)
        return

    df = pd.DataFrame(rows)
    schema = [
        bigquery.SchemaField(column_name, column_type)
        for column_name, column_type in SLEEPER_TABLE_SCHEMAS[table_name]
    ]
    df = df[[field.name for field in schema]]
    table_id = f"{dataset_id}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        schema=schema,
        autodetect=False,
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    job.result()
    logger.info("Loaded %s rows into %s.", len(df), table_id)


def ingest_sleeper_league(league_id, week, roster_id=None, username=None, display_name=None, team_name=None, dataset_name="fantasy_football_brain"):
    logger.info("Fetching Sleeper league %s.", league_id)
    league = fetch_json(f"/league/{league_id}")
    users = fetch_json(f"/league/{league_id}/users")
    rosters = fetch_json(f"/league/{league_id}/rosters")
    matchups = fetch_json(f"/league/{league_id}/matchups/{week}")
    players_map = fetch_json("/players/nfl")

    viewer_roster = resolve_viewer_roster(
        rosters,
        users,
        roster_id=roster_id,
        username=username,
        display_name=display_name,
        team_name=team_name,
    )
    records = build_records(league_id, week, league, users, rosters, matchups, players_map, viewer_roster)

    client = bigquery.Client(project=get_bigquery_project())
    dataset_id = create_dataset_if_not_exists(client, dataset_name)
    for table_name, rows in records.items():
        load_rows(client, dataset_id, table_name, rows)

    logger.info(
        "Sleeper viewer team snapshot loaded. league_id=%s roster_id=%s week=%s",
        league_id,
        viewer_roster.get("roster_id"),
        week,
    )


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Load a Sleeper league and viewer team snapshot into BigQuery.")
    parser.add_argument("--league-id", required=True, help="Sleeper league ID.")
    parser.add_argument("--week", required=True, type=int, help="NFL/Sleeper scoring week to fetch matchups for.")
    parser.add_argument("--roster-id", help="Sleeper roster_id for the viewer team.")
    parser.add_argument("--username", help="Sleeper username for the viewer team owner.")
    parser.add_argument("--display-name", help="Sleeper display_name for the viewer team owner.")
    parser.add_argument("--team-name", help="Sleeper team name from user metadata.")
    parser.add_argument("--dataset", default="fantasy_football_brain", help="BigQuery dataset name.")
    args = parser.parse_args()

    ingest_sleeper_league(
        args.league_id,
        args.week,
        roster_id=args.roster_id,
        username=args.username,
        display_name=args.display_name,
        team_name=args.team_name,
        dataset_name=args.dataset,
    )


if __name__ == "__main__":
    main()
