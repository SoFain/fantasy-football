"""Fit next-game missed-bucket lanes for the availability feed (code only, no language model).

The v1 and other-positions artifacts give a games-missed distribution only for
the lanes that have an official report for the target game. The feed needs one
for every player, so this fits two more lanes, counted from the team's NEXT game:

  bucket_next_game         this week's report plus whether he played this game (NEXT_CHAIN)
  roster_bucket_next_game  weekly roster status while not on the report (ROSTER_CHAIN)

Same estimator, seasons (fit 2016-2023, holdout 2024-2025), exclusions, and k as
each population's artifact. The outcome uses src.availability_labels.game_outcome
over every later team game, so byes are not games and censoring follows the v1
rules. The existing artifacts are not modified. Read-only on BigQuery.

  python scripts/fit_availability_next_buckets.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.availability_base_rates import (  # noqa: E402
    NEXT_BUCKETS_PATH,
    NEXT_BUCKETS_VERSION,
    NEXT_CHAIN,
    POPULATIONS,
    ROSTER_CHAIN,
    count_buckets,
    load_artifact,
    multiclass_scores,
    predict_buckets,
)
from src.availability_bq import client, query, table_id  # noqa: E402
from src.availability_labels import MISSED_BUCKETS, SKILL_POSITIONS, game_outcome  # noqa: E402

FIT_SEASONS = (2016, 2023)
HOLDOUT_SEASONS = (2024, 2025)


def next_bucket(schedule: dict, played: set, gsis_id: str, season: int, team: str, week: int) -> str | None:
    games = schedule.get((season, team), [])
    later = [game_id for w, game_id in games if w > week]
    if not later:
        return None
    outcome = game_outcome(later, {g for g in later if (gsis_id, g) in played}, set(later), season_complete=True)
    return outcome["bucket"] if outcome else None


def bucket_eval(tables: dict, chain, k: float, rows: list[dict]) -> dict:
    dists = [predict_buckets(tables, chain, k, r) for r in rows]
    labels = [MISSED_BUCKETS.index(r["missed_bucket"]) for r in rows]
    return {"n": len(rows), **multiclass_scores(dists, labels)}


def main() -> int:
    bq = client()
    bounds = (FIT_SEASONS[0], HOLDOUT_SEASONS[1])
    schedule: dict[tuple[int, str], list[tuple[int, str]]] = {}
    for g in query(bq, f"SELECT season, team, week, game_id FROM `{table_id('availability_team_games')}` "
                       f"WHERE game_type = 'REG' AND season BETWEEN {bounds[0]} AND {bounds[1]}"):
        schedule.setdefault((int(g["season"]), g["team"]), []).append((int(g["week"]), g["game_id"]))
    for games in schedule.values():
        games.sort()
    played = {(r["gsis_id"], r["game_id"]) for r in query(
        bq, f"SELECT DISTINCT gsis_id, game_id FROM `{table_id('availability_player_games')}` "
            f"WHERE game_type = 'REG' AND gsis_id IS NOT NULL AND season BETWEEN {bounds[0]} AND {bounds[1]}")}
    labels = query(bq, f"""
SELECT gsis_id, season, week, team, position_group, report_status, practice_status, played_this_game
FROM `{table_id('availability_labels_hist')}`
WHERE NOT excluded_from_fit AND season BETWEEN {bounds[0]} AND {bounds[1]}
""")
    skill_list = ",".join(f"'{p}'" for p in SKILL_POSITIONS)
    roster = query(bq, f"""
WITH r AS (
  SELECT DISTINCT gsis_id, season, week, team, status, position IN ({skill_list}) AS is_skill
  FROM `{table_id('raw_nflverse_rosters_weekly')}`
  WHERE season BETWEEN {bounds[0]} AND {bounds[1]} AND gsis_id IS NOT NULL AND position IS NOT NULL
),
reported AS (SELECT DISTINCT gsis_id, season, week FROM `{table_id('raw_nflverse_injuries')}` WHERE gsis_id IS NOT NULL)
SELECT r.* FROM r LEFT JOIN reported i USING (gsis_id, season, week)
WHERE i.gsis_id IS NULL AND r.status != 'ACT'
""")

    populations = {}
    for name, spec in POPULATIONS.items():
        k = float(load_artifact(spec["path"])["k"])
        report_rows, roster_rows = [], []
        for r in labels:
            if (r["position_group"] != "OTHER") != (name == "skill"):
                continue
            bucket = next_bucket(schedule, played, r["gsis_id"], int(r["season"]), r["team"], int(r["week"]))
            if bucket is not None:
                report_rows.append({**r, "played_this_game": bool(r["played_this_game"]), "missed_bucket": bucket})
        for r in roster:
            if bool(r["is_skill"]) != (name == "skill"):
                continue
            bucket = next_bucket(schedule, played, r["gsis_id"], int(r["season"]), r["team"], int(r["week"]))
            if bucket is not None:
                roster_rows.append({"season": int(r["season"]), "roster_status": r["status"], "missed_bucket": bucket})

        def split(rows, seasons):
            return [r for r in rows if seasons[0] <= int(r["season"]) <= seasons[1]]

        tables = {
            "bucket_next_game": count_buckets(split(report_rows, FIT_SEASONS), NEXT_CHAIN),
            "roster_bucket_next_game": count_buckets(split(roster_rows, FIT_SEASONS), ROSTER_CHAIN),
        }
        report_holdout, roster_holdout = split(report_rows, HOLDOUT_SEASONS), split(roster_rows, HOLDOUT_SEASONS)
        populations[name] = {
            "base_artifact": spec["model_version"],
            "k": k,
            "fit_rows": {"bucket_next_game": len(split(report_rows, FIT_SEASONS)), "roster_bucket_next_game": len(split(roster_rows, FIT_SEASONS))},
            "metrics": {
                "bucket_next_game": {
                    "model": bucket_eval(tables["bucket_next_game"], NEXT_CHAIN, k, report_holdout),
                    "status_only": bucket_eval(tables["bucket_next_game"], NEXT_CHAIN[:2], k, report_holdout),
                },
                "roster_bucket_next_game": {
                    "model": bucket_eval(tables["roster_bucket_next_game"], ROSTER_CHAIN, k, roster_holdout),
                    "global_only": bucket_eval(tables["roster_bucket_next_game"], ROSTER_CHAIN[:1], k, roster_holdout),
                },
            },
            "tables": tables,
        }

    artifact = {
        "model_version": NEXT_BUCKETS_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_tables": [
            "fantasy_football_brain.availability_labels_hist",
            "fantasy_football_brain.raw_nflverse_rosters_weekly (not on the report, status not ACT)",
        ],
        "target": "missed bucket counted from the team's next regular-season game (byes are not games)",
        "fit_seasons": list(FIT_SEASONS),
        "holdout_seasons": list(HOLDOUT_SEASONS),
        "estimator": "cell = (counts + k * parent) / (n + k); global level uses a uniform (1 each) prior; k from each population's artifact",
        "chains": {
            "bucket_next_game": [list(level) for level in NEXT_CHAIN],
            "roster_bucket_next_game": [list(level) for level in ROSTER_CHAIN],
        },
        "buckets": list(MISSED_BUCKETS),
        "populations": populations,
    }
    NEXT_BUCKETS_PATH.write_text(json.dumps(artifact, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({n: {"fit_rows": p["fit_rows"], "metrics": p["metrics"]} for n, p in populations.items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
