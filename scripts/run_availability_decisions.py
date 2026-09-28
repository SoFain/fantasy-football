"""Availability decision pilot: one Jev call per injured player, log-only.

Writes only availability_decisions_daily and availability_decision_misses (and
archives new DraftSharks items in availability_text_items). Never touches a
ranking, board, candidate, unified, or safety table. Not part of the daily chain.

Live (today, every Sleeper-injured QB/RB/WR/TE with a team):
  python scripts/run_availability_decisions.py --live [--dry-run] [--limit N] [--force]

Retro (state rebuilt as of the last Sleeper snapshot before each kickoff, text
published before that snapshot only):
  python scripts/run_availability_decisions.py --retro-season 2026 --weeks 1-3 [--dry-run]

A row is idempotent per decision_date, run_mode, player, and target game: an
unchanged input hash is skipped, a changed one replaces the earlier row.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.availability_base_rates import (  # noqa: E402
    PLAY_CHAIN,
    BaseRateModel,
    predict_binary,
    predict_buckets,
)
from src.availability_bq import client, load_rows, query, replace_key_rows, table_id  # noqa: E402
from src.availability_decisions import (  # noqa: E402
    DECISION_KEY,
    EASTERN,
    JEV_MODEL,
    Case,
    build_questions,
    build_state,
    decision_row,
    decision_schema,
    input_hash,
    long_date,
    miss_schema,
)
from src.availability_labels import (  # noqa: E402
    MISSED_BUCKETS,
    SKILL_POSITIONS,
    InjuryRow,
    TeamGame,
    build_label_rows,
    normalize_practice_status,
    normalize_report_status,
    team_schedule,
)
from src.availability_text import archive_new_items, fetch_draftsharks, load_candidate_text, match_player_items  # noqa: E402

SECRET_FILE = Path(r"E:\cbs-league-history\.secrets\typesafe-ai-api.txt")
NON_INJURY_SLEEPER_STATUSES = {"Sus", "DNR", ""}
SLEEPER_TO_ROSTER_STATUS = {"IR": "RES", "PUP": "PUP"}
PRACTICE_WORDS = {"DNP": "did not practice", "LP": "limited participation", "FP": "full participation", "NONE": "no practice status listed"}
TEXT_WINDOW_DAYS = 10
# Sleeper and nflverse disagree on one franchise code; normalize Sleeper to nflverse at read time.
SLEEPER_TEAM_ALIASES = {"LAR": "LA"}


def api_key() -> str:
    key = os.environ.get("TYPESAFE_API_KEY") or (SECRET_FILE.read_text(encoding="utf-8").strip() if SECRET_FILE.exists() else "")
    if not key:
        raise SystemExit("TYPESAFE_API_KEY is not set and the secret file is missing")
    return key


def load_season(bq, season: int) -> dict[str, Any]:
    games = query(
        bq,
        f"SELECT * FROM `{table_id('availability_team_games')}` WHERE season = {season} AND game_type = 'REG'",
    )
    names = {r["team"]: r["team_name"] for r in query(bq, f"SELECT team, team_name FROM `{table_id('raw_nflverse_teams')}`")}
    reports = query(
        bq,
        f"""
SELECT season, week, team, gsis_id, player_name, position, report_status, practice_status,
  COALESCE(JSON_VALUE(raw_payload_json, '$.report_primary_injury'), JSON_VALUE(raw_payload_json, '$.practice_primary_injury')) AS primary_injury,
  COALESCE(JSON_VALUE(raw_payload_json, '$.report_secondary_injury'), JSON_VALUE(raw_payload_json, '$.practice_secondary_injury')) AS secondary_injury
FROM `{table_id('raw_nflverse_injuries')}`
WHERE season = {season} AND JSON_VALUE(raw_payload_json, '$.game_type') = 'REG' AND gsis_id IS NOT NULL
  AND (report_status IS NOT NULL OR practice_status IS NOT NULL)
""",
    )
    snaps = query(
        bq,
        f"SELECT gsis_id, week, game_id, team, offense_snaps, st_snaps FROM `{table_id('availability_player_games')}` "
        f"WHERE season = {season} AND game_type = 'REG' AND gsis_id IS NOT NULL",
    )
    roster = query(
        bq,
        f"""
SELECT gsis_id, week, team, status, JSON_VALUE(raw_payload_json, '$.sleeper_id') AS sleeper_id,
  LOWER(REGEXP_REPLACE(player_name, r'[^A-Za-z]', '')) AS name_key
FROM `{table_id('raw_nflverse_rosters_weekly')}` WHERE season = {season} AND gsis_id IS NOT NULL
""",
    )
    loaded_games = {r["game_id"] for r in snaps}
    by_name: dict[tuple[str, str], set[str]] = {}
    for r in roster:
        by_name.setdefault((r["name_key"], r["team"]), set()).add(r["gsis_id"])
    return {
        "season": season,
        "games": games,
        "team_names": names,
        "schedule": team_schedule(TeamGame(season, g["team"], g["week"], g["game_id"]) for g in games),
        "reports": reports,
        "reports_by_player": _group(reports, "gsis_id"),
        "played": {(r["gsis_id"], season, int(r["week"])): r["team"] for r in snaps},
        "snaps": {(r["gsis_id"], r["game_id"]): r for r in snaps},
        "loaded_games": loaded_games,
        "roster": {(r["gsis_id"], season, int(r["week"])): (r["team"], r["status"]) for r in roster},
        "sleeper_to_gsis": {r["sleeper_id"]: r["gsis_id"] for r in roster if r["sleeper_id"]},
        "name_team_to_gsis": {k: next(iter(v)) for k, v in by_name.items() if len(v) == 1},
    }


def _group(rows: list[dict], key: str) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for row in rows:
        out.setdefault(row[key], []).append(row)
    return out


def sleeper_rows(bq, since: datetime, until: datetime) -> list[dict]:
    from google.cloud import bigquery

    rows = query(
        bq,
        f"""
SELECT snapshot_at, sleeper_player_id, gsis_id, player_name, position, team, status, injury_status,
  injury_body_part, injury_notes, practice_participation
FROM `{table_id('sleeper_players_history')}`
WHERE snapshot_at >= @since AND snapshot_at <= @until AND position IN ('QB','RB','WR','TE')
""",
        [bigquery.ScalarQueryParameter("since", "TIMESTAMP", since), bigquery.ScalarQueryParameter("until", "TIMESTAMP", until)],
    )
    for row in rows:
        row["team"] = SLEEPER_TEAM_ALIASES.get(row["team"], row["team"])
    return rows


def resolve_gsis(ctx: dict, row: dict) -> str | None:
    import re

    if row.get("gsis_id"):
        return row["gsis_id"]
    if row.get("sleeper_player_id") in ctx["sleeper_to_gsis"]:
        return ctx["sleeper_to_gsis"][row["sleeper_player_id"]]
    key = (re.sub(r"[^a-z]", "", (row.get("player_name") or "").lower()), row.get("team"))
    return ctx["name_team_to_gsis"].get(key)


def listed_since(history: list[dict], as_of: datetime, status: str | None) -> datetime | None:
    """Earliest snapshot in the unbroken run of this designation ending at as_of."""
    if not status:
        return None
    since = None
    for snap in sorted((h for h in history if h["snapshot_at"] <= as_of), key=lambda h: h["snapshot_at"], reverse=True):
        if snap.get("injury_status") != status:
            break
        since = snap["snapshot_at"]
    return since


def report_sentence(row: dict, week: int, label: str) -> str:
    status = normalize_report_status(row.get("report_status"))
    practice = PRACTICE_WORDS[normalize_practice_status(row.get("practice_status"))]
    designation = "no game designation" if status == "NONE" else f"designation {status}"
    injury = row.get("primary_injury") or "injury not listed"
    return f"{label} Week {week} official injury report: {designation}; practice: {practice}; injury: {injury}."


def build_case(ctx: dict, model: BaseRateModel, sleeper: dict | None, gsis_id: str, team: str, game: dict,
               as_of: datetime, history: list[dict], text_pool: list[dict]) -> tuple[Case | None, str]:
    season = ctx["season"]
    schedule = ctx["schedule"].get((season, team), [])
    target_week = int(game["week"])
    prior_games = [g for g in ctx["games"] if g["team"] == team and g["kickoff_utc"] < as_of]
    prior_games.sort(key=lambda g: g["week"])
    last_game = prior_games[-1] if prior_games else None
    reports = ctx["reports_by_player"].get(gsis_id, [])
    this_report = next((r for r in reports if int(r["week"]) == target_week and r["team"] == team), None)
    last_report = next((r for r in reports if last_game and int(r["week"]) == int(last_game["week"]) and r["team"] == team), None)
    sleeper_status = (sleeper or {}).get("injury_status") or None
    name = (sleeper or {}).get("player_name") or (this_report or last_report or {}).get("player_name") or gsis_id
    position = (sleeper or {}).get("position") or (this_report or last_report or {}).get("position")

    def features_for(row: dict, horizon_week: int) -> dict:
        labels = build_label_rows(
            [InjuryRow(season, int(r["week"]), r["team"], gsis_id, r["player_name"], r["position"], r["report_status"],
                       r["practice_status"], r["primary_injury"], r["secondary_injury"]) for r in reports],
            ctx["schedule"], ctx["played"], ctx["roster"], last_observed_week={season: horizon_week},
        )
        return next((l for l in labels if l["week"] == int(row["week"])), None)

    prior_buckets = None
    this_features = features_for(this_report, target_week) if this_report is not None else None
    last_features = features_for(last_report, int(last_game["week"])) if last_report is not None else None
    if this_features is not None:
        features = this_features
        lane = "report_this_game"
        description = "official final injury report for this game, from 2016 to 2023 regular-season reports"
        # The previous game's outcome is a feature only once its snap counts are loaded.
        prev_unknown = features["prev_week_state"] != "NOT_LISTED" and (
            last_game is None or last_game["game_id"] not in ctx["loaded_games"]
        )
        depth = 2 if prev_unknown else None
        tables = model.artifact["tables"]
        prior_play = predict_binary(tables["play_this_game"], PLAY_CHAIN, model.k, features, depth)
        prior_buckets = dict(zip(MISSED_BUCKETS, predict_buckets(tables["bucket_this_game"], PLAY_CHAIN, model.k, features, depth)))
        official = report_sentence(this_report, target_week, "Final")
        designation, practice, body = features["report_status"], features["practice_status"], this_report["primary_injury"]
    elif last_features is not None:
        features = last_features
        loaded = last_game["game_id"] in ctx["loaded_games"]
        features["played_this_game"] = features["played_this_game"] if loaded else None
        lane = "report_last_game"
        description = "his official report for his last game and whether he played it, from 2016 to 2023"
        prior_play = model.play_next_game(features)
        official = f"No official injury report for Week {target_week} yet. " + report_sentence(last_report, int(last_game["week"]), "Final")
        designation, practice, body = features["report_status"], features["practice_status"], last_report["primary_injury"]
    else:
        roster_weeks = sorted(w for (g, s, w) in ctx["roster"] if g == gsis_id and w <= target_week)
        roster_status = ctx["roster"][(gsis_id, season, roster_weeks[-1])][1] if roster_weeks else None
        if roster_status and roster_status != "ACT":
            lane, key = "roster_status", roster_status
        elif sleeper_status in SLEEPER_TO_ROSTER_STATUS:
            lane, key = "roster_status", SLEEPER_TO_ROSTER_STATUS[sleeper_status]
        elif sleeper_status in ("Out", "Doubtful", "Questionable"):
            lane, key = "sleeper_designation_only", sleeper_status
        else:
            return None, f"no_prior_lane:{sleeper_status}"
        if lane == "roster_status":
            description = f"players on the weekly roster with status {key} and not on the injury report, 2016 to 2023"
            prior_play = model.roster_next_game(key)
        else:
            description = f"official reports with designation {key} (practice unknown), 2016 to 2023"
            f = {"report_status": key}
            prior_play = predict_binary(model.artifact["tables"]["play_this_game"], PLAY_CHAIN, model.k, f, depth=1)
            prior_buckets = dict(zip(MISSED_BUCKETS, predict_buckets(model.artifact["tables"]["bucket_this_game"], PLAY_CHAIN, model.k, f, depth=1)))
        official = "He was not on the official injury report for his last game or for this game."
        designation, practice, body = sleeper_status or "NONE", (sleeper or {}).get("practice_participation") or "NONE", (sleeper or {}).get("injury_body_part")

    recent = []
    for g in prior_games[-2:]:
        when = f"Week {g['week']} ({long_date(g['kickoff_utc'])}) vs {ctx['team_names'].get(g['opponent'], g['opponent'])}"
        snap = ctx["snaps"].get((gsis_id, g["game_id"]))
        if g["game_id"] not in ctx["loaded_games"]:
            recent.append(f"{when}: snap counts not available yet.")
        elif snap:
            recent.append(f"{when}: he played ({int(snap['offense_snaps'])} offensive snaps).")
        else:
            recent.append(f"{when}: he did not play.")

    games_remaining = sum(1 for g in schedule if g.week >= target_week)
    case = Case(
        gsis_id=gsis_id,
        sleeper_player_id=(sleeper or {}).get("sleeper_player_id"),
        player_name=name,
        team=team,
        team_name=f"{ctx['team_names'].get(team, team)} ({team})",
        position=position or "",
        as_of=as_of,
        season=season,
        target_week=target_week,
        target_game_id=game["game_id"],
        kickoff_utc=game["kickoff_utc"],
        opponent_name=ctx["team_names"].get(game["opponent"], game["opponent"]),
        is_home=bool(game["is_home"]),
        games_remaining=games_remaining,
        official_report=official,
        sleeper_status=sleeper_status,
        sleeper_body_part=(sleeper or {}).get("injury_body_part"),
        sleeper_note=(sleeper or {}).get("injury_notes"),
        sleeper_practice=(sleeper or {}).get("practice_participation"),
        sleeper_listed_since=listed_since(history, as_of, sleeper_status),
        recent_games=recent,
        prior_lane=lane,
        prior_lane_description=description,
        prior_play=prior_play,
        prior_buckets=prior_buckets,
        text_items=match_player_items(name, team, text_pool, as_of, TEXT_WINDOW_DAYS),
        designation=designation,
        practice_status=practice,
        body_part=body,
    )
    return case, lane


def live_cases(bq, model: BaseRateModel, now: datetime) -> tuple[list[Case], Counter]:
    try:
        archived = archive_new_items(bq, fetch_draftsharks(now))
        print(json.dumps({"draftsharks_new_items_archived": archived}))
    except Exception as exc:  # the feed is optional context; a failure must not stop the run
        print(json.dumps({"draftsharks_fetch_error": str(exc)[:300]}))
    season = now.year if now.month >= 3 else now.year - 1
    ctx = load_season(bq, season)
    history = sleeper_rows(bq, now - timedelta(days=30), now)
    latest = max(h["snapshot_at"] for h in history)
    by_player = _group(history, "sleeper_player_id")
    text_pool = load_candidate_text(bq, now - timedelta(days=TEXT_WINDOW_DAYS), now + timedelta(minutes=1))
    cases, skipped = [], Counter()
    for row in (h for h in history if h["snapshot_at"] == latest):
        status = row.get("injury_status")
        if not status or status in NON_INJURY_SLEEPER_STATUSES or not row.get("team"):
            continue
        gsis_id = resolve_gsis(ctx, row)
        if not gsis_id:
            skipped["no_gsis"] += 1
            continue
        upcoming = sorted((g for g in ctx["games"] if g["team"] == row["team"] and g["kickoff_utc"] > now), key=lambda g: g["kickoff_utc"])
        if not upcoming:
            skipped["no_upcoming_game"] += 1
            continue
        case, lane = build_case(ctx, model, row, gsis_id, row["team"], upcoming[0], now, by_player.get(row["sleeper_player_id"], []), text_pool)
        if case is None:
            skipped[lane] += 1
        else:
            cases.append(case)
    return cases, skipped


def retro_cases(bq, model: BaseRateModel, season: int, weeks: list[int]) -> tuple[list[Case], Counter]:
    ctx = load_season(bq, season)
    games = [g for g in ctx["games"] if int(g["week"]) in weeks]
    first, last = min(g["kickoff_utc"] for g in games), max(g["kickoff_utc"] for g in games)
    history = sleeper_rows(bq, first - timedelta(days=30), last)
    snapshot_times = sorted({h["snapshot_at"] for h in history})
    by_player = _group(history, "sleeper_player_id")
    text_pool = load_candidate_text(bq, first - timedelta(days=TEXT_WINDOW_DAYS + 1), last)
    cases, skipped = [], Counter()
    for game in games:
        before = [t for t in snapshot_times if t < game["kickoff_utc"]]
        if not before:
            skipped["no_snapshot_before_kickoff"] += 1
            continue
        as_of = before[-1]
        snapshot = {h["sleeper_player_id"]: h for h in history if h["snapshot_at"] == as_of and h.get("team") == game["team"]}
        chosen: dict[str, dict | None] = {}
        for row in snapshot.values():
            status = row.get("injury_status")
            if status and status not in NON_INJURY_SLEEPER_STATUSES:
                gsis_id = resolve_gsis(ctx, row)
                if gsis_id:
                    chosen[gsis_id] = row
                else:
                    skipped["no_gsis"] += 1
        sleeper_by_gsis = {resolve_gsis(ctx, r): r for r in snapshot.values()}
        for report in ctx["reports"]:
            if (int(report["week"]) == int(game["week"]) and report["team"] == game["team"]
                    and report["position"] in SKILL_POSITIONS
                    and normalize_report_status(report["report_status"]) in ("Out", "Doubtful", "Questionable")):
                chosen.setdefault(report["gsis_id"], sleeper_by_gsis.get(report["gsis_id"]))
        for gsis_id, row in chosen.items():
            history_rows = by_player.get(row["sleeper_player_id"], []) if row else []
            case, lane = build_case(ctx, model, row, gsis_id, game["team"], game, as_of, history_rows, text_pool)
            if case is None:
                skipped[lane] += 1
            else:
                cases.append(case)
    return cases, skipped


def call_jev(jev, case: Case) -> tuple[dict, dict, dict]:
    state = build_state(case)
    questions = build_questions(case, len(case.text_items))
    response = jev.system_one(state=state, questions=questions, model=JEV_MODEL)
    payload = {
        "model": response.model,
        "usage": response.usage.model_dump() if response.usage else {},
        "answers": {key: answer.model_dump() for key, answer in response.answers.items()},
        "request_id": response.request_id,
    }
    return state, questions, payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--retro-season", type=int)
    parser.add_argument("--weeks", default="1-3", help="Retro weeks, for example 1-3")
    parser.add_argument("--dry-run", action="store_true", help="Build cases and print sample states; no Jev calls, no writes.")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--force", action="store_true", help="Call Jev even when an identical input hash exists for the day.")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args(argv)

    bq = client()
    model = BaseRateModel.load()
    now = datetime.now(timezone.utc)
    if args.live:
        run_mode = "live"
        cases, skipped = live_cases(bq, model, now)
    else:
        run_mode = "retro"
        low, _, high = args.weeks.partition("-")
        cases, skipped = retro_cases(bq, model, args.retro_season, list(range(int(low), int(high or low) + 1)))
    cases.sort(key=lambda c: (c.kickoff_utc, c.team, c.player_name))
    if args.limit:
        cases = cases[: args.limit]
    summary: dict[str, Any] = {
        "run_mode": run_mode,
        "cases": len(cases),
        "skipped": dict(skipped),
        "lanes": dict(Counter(c.prior_lane for c in cases)),
        "cases_with_text": sum(1 for c in cases if c.text_items),
    }
    if args.dry_run:
        summary["sample_state"] = build_state(cases[0]) if cases else None
        summary["sample_questions"] = sorted(build_questions(cases[0], len(cases[0].text_items))) if cases else None
        print(json.dumps(summary, indent=1, default=str))
        return 0

    from google.cloud import bigquery
    from typesafe_sdk import TypeSafeClient

    bq.create_table(bigquery.Table(table_id("availability_decisions_daily"), schema=decision_schema()), exists_ok=True)
    bq.create_table(bigquery.Table(table_id("availability_decision_misses"), schema=miss_schema()), exists_ok=True)
    existing = {
        (str(r["decision_date"]), r["gsis_id"], r["target_game_id"]): r["input_hash"]
        for r in query(bq, f"SELECT decision_date, gsis_id, target_game_id, input_hash FROM `{table_id('availability_decisions_daily')}` WHERE run_mode = '{run_mode}'")
    }

    def decision_day(case: Case) -> str:
        return (now if args.live else case.as_of).astimezone(EASTERN).date().isoformat()

    todo = []
    for case in cases:
        state_hash = input_hash(build_state(case), build_questions(case, len(case.text_items)))
        if not args.force and existing.get((decision_day(case), case.gsis_id, case.target_game_id)) == state_hash:
            continue
        todo.append((case, state_hash))
    summary["unchanged_skipped"] = len(cases) - len(todo)

    rows, misses, failures = [], [], []
    with TypeSafeClient(api_key=api_key(), model=JEV_MODEL) as jev, ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [(case, state_hash, pool.submit(call_jev, jev, case)) for case, state_hash in todo]
        for case, state_hash, future in futures:
            try:
                _, _, payload = future.result()
            except Exception as exc:
                failures.append({"gsis_id": case.gsis_id, "error": type(exc).__name__})
                continue
            day = datetime.fromisoformat(decision_day(case)).date()
            row, row_misses = decision_row(
                case, run_mode=run_mode, decision_date=day, state_hash=state_hash, response=payload, base_rate_version=model.version
            )
            rows.append(row)
            misses.extend(row_misses)

    if rows:
        replace_key_rows(bq, "availability_decisions_daily", rows, decision_schema(), DECISION_KEY)
        keys = [f"{r['decision_date']}|{r['gsis_id']}|{r['target_game_id']}" for r in rows]
        bq.query(
            f"DELETE FROM `{table_id('availability_decision_misses')}` WHERE run_mode = @mode "
            "AND CONCAT(CAST(decision_date AS STRING), '|', gsis_id, '|', target_game_id) IN UNNEST(@keys)",
            job_config=bigquery.QueryJobConfig(query_parameters=[
                bigquery.ScalarQueryParameter("mode", "STRING", run_mode),
                bigquery.ArrayQueryParameter("keys", "STRING", keys),
            ]),
        ).result()
        if misses:
            load_rows(bq, "availability_decision_misses", misses, miss_schema(), truncate=False)

    summary.update(
        {
            "jev_calls": len(rows),
            "failures": failures,
            "input_tokens": sum(r["input_tokens"] for r in rows),
            "output_tokens": sum(r["output_tokens"] for r in rows),
            "cost_usd": round(sum(r["cost_usd"] for r in rows), 6),
            "blank": {q: sum(1 for r in rows if r[f"{q}_blank"]) for q in ("availability", "absence", "trend")},
            "jev_model_versions": sorted({r["jev_model_version"] for r in rows if r["jev_model_version"]}),
        }
    )
    print(json.dumps(summary, indent=1, default=str))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
