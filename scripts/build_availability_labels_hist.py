"""Build the availability pilot's history tables (reproducible, read-only on raw tables).

Writes only pilot tables in fantasy_football_brain:
  availability_team_games     nflverse schedule, one row per team per game, kickoff in UTC
  availability_player_games   who took a snap in which game (the "played" signal), GSIS keyed
  availability_labels_hist    one row per official injury report entry (REG), features plus labels

Usage:
  python scripts/build_availability_labels_hist.py            # dry run: counts only, no writes
  python scripts/build_availability_labels_hist.py --apply    # replace the three pilot tables
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.availability_bq import DATASET, PROJECT, client, load_rows, query, table_id  # noqa: E402
from src.availability_labels import InjuryRow, TeamGame, build_label_rows, team_schedule  # noqa: E402
from src.nflverse_staging import identity_candidate_cte  # noqa: E402

LABEL_VERSION = "availability_labels_v1"
FIRST_SEASON = 2014
EASTERN = ZoneInfo("America/New_York")


def team_game_rows(last_season: int) -> list[dict]:
    import nflreadpy as nfl

    frame = nfl.load_schedules(list(range(FIRST_SEASON, last_season + 1))).to_pandas()
    rows: list[dict] = []
    for game in frame.to_dict("records"):
        kickoff = None
        if game.get("gameday") and game.get("gametime"):
            local = datetime.strptime(f"{game['gameday']} {game['gametime']}", "%Y-%m-%d %H:%M")
            kickoff = local.replace(tzinfo=EASTERN).astimezone(timezone.utc).isoformat()
        completed = game.get("home_score") is not None and game.get("home_score") == game.get("home_score")
        for side, other in (("home", "away"), ("away", "home")):
            score = game.get(f"{side}_score")
            opp_score = game.get(f"{other}_score")
            rows.append(
                {
                    "season": int(game["season"]),
                    "week": int(game["week"]),
                    "game_type": game["game_type"],
                    "game_id": game["game_id"],
                    "team": game[f"{side}_team"],
                    "opponent": game[f"{other}_team"],
                    "is_home": side == "home",
                    "gameday": game.get("gameday"),
                    "gametime_et": game.get("gametime"),
                    "weekday": game.get("weekday"),
                    "kickoff_utc": kickoff,
                    "completed": bool(completed),
                    "team_score": None if score != score else score,
                    "opponent_score": None if opp_score != opp_score else opp_score,
                }
            )
    return rows


def player_games_sql(last_season: int) -> str:
    """Snap rows (any offense, defense, or special teams snap) keyed to GSIS.

    Identity: the staging identity CTE (PFR id through rosters and player
    bridges), then a unique normalized name within the same season, week,
    and team from the weekly roster for rookies the player bridge lacks.
    """
    cte = identity_candidate_cte(PROJECT, DATASET, FIRST_SEASON, last_season, None, None)
    snaps = f"`{PROJECT}.{DATASET}.raw_nflverse_snap_counts`"
    rosters = f"`{PROJECT}.{DATASET}.raw_nflverse_rosters_weekly`"
    return f"""
WITH {cte},
snap AS (
  SELECT season, week, game_id, team, player_id AS pfr_player_id, player_name, position,
    COALESCE(offense_snaps, 0) AS offense_snaps, COALESCE(defense_snaps, 0) AS defense_snaps,
    COALESCE(st_snaps, 0) AS st_snaps,
    JSON_VALUE(raw_payload_json, '$.game_type') AS game_type,
    LOWER(REGEXP_REPLACE(TRIM(player_name), r'[^A-Za-z0-9]+', ' ')) AS norm_name
  FROM {snaps}
  WHERE season BETWEEN {FIRST_SEASON} AND {last_season}
),
by_pfr AS (
  SELECT season, week, team, pfr_id, ANY_VALUE(gsis_id) AS gsis_id
  FROM identity_candidates WHERE pfr_id IS NOT NULL AND gsis_id IS NOT NULL
  GROUP BY 1, 2, 3, 4
),
by_name AS (
  SELECT season, week, team, LOWER(REGEXP_REPLACE(TRIM(player_name), r'[^A-Za-z0-9]+', ' ')) AS norm_name,
    ANY_VALUE(COALESCE(gsis_id, player_id)) AS name_gsis_id
  FROM {rosters}
  WHERE season BETWEEN {FIRST_SEASON} AND {last_season}
  GROUP BY 1, 2, 3, 4
  HAVING COUNT(DISTINCT COALESCE(gsis_id, player_id)) = 1
)
SELECT
  s.season, s.week, s.game_id, s.game_type, s.team,
  COALESCE(p.gsis_id, n.name_gsis_id) AS gsis_id,
  CASE WHEN p.gsis_id IS NOT NULL THEN 'pfr_id' WHEN n.name_gsis_id IS NOT NULL THEN 'name_team_week' END AS match_method,
  s.pfr_player_id, s.player_name, s.position, s.offense_snaps, s.defense_snaps, s.st_snaps,
  CURRENT_TIMESTAMP() AS built_at
FROM snap s
LEFT JOIN by_pfr p ON s.season = p.season AND s.week = p.week AND s.team = p.team AND s.pfr_player_id = p.pfr_id
LEFT JOIN by_name n ON s.season = n.season AND s.week = n.week AND s.team = n.team AND s.norm_name = n.norm_name
WHERE s.offense_snaps + s.defense_snaps + s.st_snaps > 0
"""


def team_game_schema() -> list:
    from google.cloud import bigquery as b

    return [
        b.SchemaField("season", "INT64"), b.SchemaField("week", "INT64"), b.SchemaField("game_type", "STRING"),
        b.SchemaField("game_id", "STRING"), b.SchemaField("team", "STRING"), b.SchemaField("opponent", "STRING"),
        b.SchemaField("is_home", "BOOL"), b.SchemaField("gameday", "DATE"), b.SchemaField("gametime_et", "STRING"),
        b.SchemaField("weekday", "STRING"), b.SchemaField("kickoff_utc", "TIMESTAMP"), b.SchemaField("completed", "BOOL"),
        b.SchemaField("team_score", "FLOAT64"), b.SchemaField("opponent_score", "FLOAT64"),
    ]


def label_schema() -> list:
    from google.cloud import bigquery as b

    s, i, bo = "STRING", "INT64", "BOOL"
    fields = [
        ("gsis_id", s), ("season", i), ("week", i), ("team", s), ("game_id", s), ("player_name", s),
        ("position", s), ("position_group", s), ("report_status", s), ("practice_status", s),
        ("primary_body_part", s), ("secondary_body_part", s), ("body_part_group", s),
        ("prev_week_state", s), ("prev_week_status", s), ("episode_id", s), ("weeks_in_episode", i),
        ("team_game_index", i), ("team_games_in_season", i), ("games_remaining", i), ("roster_status", s),
        ("era_pre_2016", bo), ("played_this_game", bo), ("played_next_game", bo),
        ("games_missed_until_return", i), ("return_week", i), ("censored", bo), ("censor_reason", s),
        ("missed_bucket", s), ("flag_team_change", bo), ("flag_cut", bo), ("flag_not_injury_related", bo),
        ("excluded_from_fit", bo), ("label_version", s), ("built_at", "TIMESTAMP"),
    ]
    return [b.SchemaField(name, kind) for name, kind in fields]


def complete_weeks(bq, last_season: int) -> dict[int, int]:
    """Per season, the last week whose every REG game has snap rows (outcomes known)."""
    rows = query(
        bq,
        f"""
SELECT g.season, g.week, COUNT(DISTINCT g.game_id) AS games, COUNT(DISTINCT p.game_id) AS games_with_snaps
FROM `{table_id('availability_team_games')}` g
LEFT JOIN `{table_id('availability_player_games')}` p USING (season, week, game_id)
WHERE g.game_type = 'REG' AND g.season BETWEEN {FIRST_SEASON} AND {last_season}
GROUP BY 1, 2 ORDER BY 1, 2
""",
    )
    horizon: dict[int, int] = {}
    for row in rows:
        season = int(row["season"])
        if row["games"] == row["games_with_snaps"] and horizon.get(season, row["week"] - 1) == row["week"] - 1:
            horizon[season] = int(row["week"])
    return horizon


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--apply", action="store_true", help="Replace the three pilot tables.")
    parser.add_argument("--last-season", type=int, default=2026)
    args = parser.parse_args(argv)

    bq = client()
    games = team_game_rows(args.last_season)
    summary: dict = {"team_game_rows": len(games), "apply": args.apply}
    if not args.apply:
        count = query(bq, f"SELECT COUNT(*) AS n FROM ({player_games_sql(args.last_season)})")[0]["n"]
        summary["player_game_rows_planned"] = count
        print(json.dumps(summary, indent=2))
        return 0

    load_rows(bq, "availability_team_games", games, team_game_schema(), truncate=True)
    bq.query(
        f"CREATE OR REPLACE TABLE `{table_id('availability_player_games')}` "
        f"CLUSTER BY gsis_id AS {player_games_sql(args.last_season)}"
    ).result()

    horizon = complete_weeks(bq, args.last_season)
    summary["last_complete_week"] = horizon
    injuries = query(
        bq,
        f"""
SELECT season, week, team, gsis_id, player_name, position, report_status, practice_status,
  COALESCE(JSON_VALUE(raw_payload_json, '$.report_primary_injury'), JSON_VALUE(raw_payload_json, '$.practice_primary_injury')) AS primary_injury,
  COALESCE(JSON_VALUE(raw_payload_json, '$.report_secondary_injury'), JSON_VALUE(raw_payload_json, '$.practice_secondary_injury')) AS secondary_injury
FROM `{table_id('raw_nflverse_injuries')}`
WHERE season BETWEEN {FIRST_SEASON} AND {args.last_season}
  AND JSON_VALUE(raw_payload_json, '$.game_type') = 'REG'
  AND gsis_id IS NOT NULL
  AND (report_status IS NOT NULL OR practice_status IS NOT NULL)
""",
    )
    played_rows = query(
        bq,
        f"""
SELECT DISTINCT p.gsis_id, p.season, p.week, p.team
FROM `{table_id('availability_player_games')}` p
JOIN (SELECT DISTINCT gsis_id, season FROM `{table_id('raw_nflverse_injuries')}` WHERE gsis_id IS NOT NULL) i
  USING (gsis_id, season)
WHERE p.game_type = 'REG'
""",
    )
    roster_rows = query(
        bq,
        f"""
SELECT r.gsis_id, r.season, r.week, r.team, r.status
FROM `{table_id('raw_nflverse_rosters_weekly')}` r
JOIN (SELECT DISTINCT gsis_id, season FROM `{table_id('raw_nflverse_injuries')}` WHERE gsis_id IS NOT NULL) i
  USING (gsis_id, season)
""",
    )
    schedule = team_schedule(
        TeamGame(g["season"], g["team"], g["week"], g["game_id"]) for g in games if g["game_type"] == "REG"
    )
    played = {(r["gsis_id"], int(r["season"]), int(r["week"])): r["team"] for r in played_rows}
    roster = {(r["gsis_id"], int(r["season"]), int(r["week"])): (r["team"], r["status"]) for r in roster_rows}
    labels = build_label_rows(
        (
            InjuryRow(int(r["season"]), int(r["week"]), r["team"], r["gsis_id"], r["player_name"], r["position"],
                      r["report_status"], r["practice_status"], r["primary_injury"], r["secondary_injury"])
            for r in injuries
        ),
        schedule,
        played,
        roster,
        last_observed_week={args.last_season: horizon.get(args.last_season, 0)},
    )
    built_at = datetime.now(timezone.utc).isoformat()
    for row in labels:
        row["label_version"] = LABEL_VERSION
        row["built_at"] = built_at
    load_rows(bq, "availability_labels_hist", labels, label_schema(), truncate=True)
    counts = query(
        bq,
        f"""
SELECT
  (SELECT COUNT(*) FROM `{table_id('availability_team_games')}`) AS team_games,
  (SELECT COUNT(*) FROM `{table_id('availability_player_games')}`) AS player_games,
  (SELECT COUNTIF(gsis_id IS NULL) FROM `{table_id('availability_player_games')}`) AS player_games_unmatched,
  (SELECT COUNT(*) FROM `{table_id('availability_labels_hist')}`) AS label_rows
""",
    )[0]
    summary.update({"injury_source_rows": len(injuries), **counts})
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
