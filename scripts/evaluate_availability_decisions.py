"""Score availability decisions against what happened (read-only).

Joins availability_decisions_daily to snap-count outcomes in
availability_player_games. A decision is scored once its target game has snap
data; games missed are counted only over loaded games, and a still-open
absence is scored against every bucket it can still end in.

  python scripts/evaluate_availability_decisions.py --run-mode retro
  python scripts/evaluate_availability_decisions.py --run-mode live --since 2026-09-27

Compares, on the same rows: the base-rate prior alone, and the prior plus
Jev under the fixed rule in availability_decisions.combined_play_probability.
Refresh outcomes first with the 2026 raw load and build_availability_labels_hist.py --apply.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.availability_base_rates import EPS, brier, log_loss  # noqa: E402
from src.availability_bq import client, query, table_id  # noqa: E402
from src.availability_labels import MISSED_BUCKETS, game_outcome  # noqa: E402


def load_rows(bq, run_mode: str, since: str | None) -> list[dict]:
    where = f"run_mode = '{run_mode}'" + (f" AND decision_date >= '{since}'" if since else "")
    return query(bq, f"SELECT * FROM `{table_id('availability_decisions_daily')}` WHERE {where}")


def outcomes(bq, decisions: list[dict]) -> dict[tuple[str, str], dict]:
    seasons = sorted({int(d["season"]) for d in decisions})
    if not seasons:
        return {}
    season_list = ",".join(str(s) for s in seasons)
    games = query(
        bq,
        f"SELECT season, team, week, game_id FROM `{table_id('availability_team_games')}` "
        f"WHERE game_type = 'REG' AND season IN ({season_list}) ORDER BY season, team, week",
    )
    loaded = {r["game_id"] for r in query(bq, f"SELECT DISTINCT game_id FROM `{table_id('availability_player_games')}` WHERE season IN ({season_list})")}
    ids = sorted({d["gsis_id"] for d in decisions})
    played_rows = query(
        bq,
        f"SELECT gsis_id, game_id FROM `{table_id('availability_player_games')}` WHERE season IN ({season_list}) "
        f"AND gsis_id IN UNNEST({json.dumps(ids)})",
    )
    played: dict[str, set[str]] = {}
    for r in played_rows:
        played.setdefault(r["gsis_id"], set()).add(r["game_id"])
    by_team: dict[tuple[int, str], list[str]] = {}
    for g in games:
        by_team.setdefault((int(g["season"]), g["team"]), []).append(g["game_id"])
    out = {}
    for d in decisions:
        schedule = by_team.get((int(d["season"]), d["team"]), [])
        if d["target_game_id"] not in schedule:
            continue
        remaining = schedule[schedule.index(d["target_game_id"]):]
        season_complete = all(g in loaded for g in schedule)
        result = game_outcome(remaining, played.get(d["gsis_id"], set()), loaded, season_complete)
        if result is not None:
            out[(d["gsis_id"], d["target_game_id"])] = result
    return out


def set_log_loss(dists: list[dict], possible: list[list[str]]) -> float:
    total = 0.0
    for dist, allowed in zip(dists, possible):
        total -= math.log(max(sum(float(dist.get(b, 0.0)) for b in allowed), EPS))
    return round(total / max(len(dists), 1), 4)


def play_block(rows: list[dict]) -> dict:
    if not rows:
        return {"n": 0}
    y = [int(r["outcome"]["played"]) for r in rows]
    prior = [float(r["prior_play_prob"]) for r in rows]
    combined = [float(r["combined_play_prob"]) for r in rows]
    calls = [r for r in rows if r["availability"] in ("will_play", "will_miss")]
    jev_correct = sum(1 for r in calls if (r["availability"] == "will_play") == r["outcome"]["played"])
    base_correct = sum(1 for r in calls if (float(r["prior_play_prob"]) >= 0.5) == r["outcome"]["played"])
    gtd = [r for r in rows if r["availability"] == "game_time_decision"]
    return {
        "n": len(rows),
        "played_rate": round(sum(y) / len(y), 3),
        "prior": {"brier": round(brier(prior, y), 4), "log_loss": round(log_loss(prior, y), 4)},
        "prior_plus_jev": {"brier": round(brier(combined, y), 4), "log_loss": round(log_loss(combined, y), 4)},
        "rows_where_jev_changed_probability": sum(1 for p, c in zip(prior, combined) if abs(p - c) > 1e-9),
        "availability_answered": sum(1 for r in rows if not r["availability_blank"]),
        "availability_blank": sum(1 for r in rows if r["availability_blank"]),
        "hard_calls": {
            "n": len(calls),
            "jev_correct": jev_correct,
            "base_rate_correct_same_rows": base_correct,
        },
        "game_time_decision": {"n": len(gtd), "played": sum(1 for r in gtd if r["outcome"]["played"])},
    }


def absence_block(rows: list[dict]) -> dict:
    scored = [r for r in rows if r["prior_bucket_probs_json"]]
    if not scored:
        return {"n": 0}
    possible = [r["outcome"]["possible_buckets"] for r in scored]
    prior = [json.loads(r["prior_bucket_probs_json"]) for r in scored]
    jev_or_prior = [
        json.loads(r["absence_probs_json"]) if (not r["absence_blank"] and r["relevant_text_count"] and r["absence_probs_json"]) else p
        for r, p in zip(scored, prior)
    ]
    answered = [r for r in scored if not r["absence_blank"]]
    return {
        "n": len(scored),
        "resolved": sum(1 for r in scored if r["outcome"]["bucket"] is not None),
        "prior_set_log_loss": set_log_loss(prior, possible),
        "prior_plus_jev_set_log_loss": set_log_loss(jev_or_prior, possible),
        "jev_answered": len(answered),
        "jev_answer_consistent_with_outcome": sum(1 for r in answered if r["absence"] in r["outcome"]["possible_buckets"]),
        "prior_top_consistent_same_rows": sum(
            1 for r in answered
            if max(MISSED_BUCKETS, key=lambda b: json.loads(r["prior_bucket_probs_json"])[b]) in r["outcome"]["possible_buckets"]
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-mode", choices=["live", "retro"], default="live")
    parser.add_argument("--since", help="First decision_date to include (YYYY-MM-DD).")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    args = parser.parse_args(argv)

    bq = client()
    decisions = load_rows(bq, args.run_mode, args.since)
    results = outcomes(bq, decisions)
    scored = []
    for d in decisions:
        outcome = results.get((d["gsis_id"], d["target_game_id"]))
        if outcome is not None:
            scored.append({**d, "outcome": outcome})
    designated = [r for r in scored if r["prior_lane"] == "report_this_game" and r["designation"] in ("Out", "Doubtful", "Questionable")]
    report = {
        "run_mode": args.run_mode,
        "decisions": len(decisions),
        "scored": len(scored),
        "pending_outcome": len(decisions) - len(scored),
        "by_week_scored": dict(sorted(Counter(int(r["target_week"]) for r in scored).items())),
        "play_next_game": {
            "all": play_block(scored),
            "with_relevant_text": play_block([r for r in scored if r["relevant_text_count"]]),
            "official_designation_out_doubtful_questionable": play_block(designated),
            "questionable_only": play_block([r for r in designated if r["designation"] == "Questionable"]),
            "by_lane": {lane: play_block([r for r in scored if r["prior_lane"] == lane]) for lane in sorted({r["prior_lane"] for r in scored})},
        },
        "absence": {
            "all_with_prior_distribution": absence_block(scored),
            "with_relevant_text": absence_block([r for r in scored if r["relevant_text_count"]]),
        },
        "trend_answered": sum(1 for r in scored if not r["trend_blank"]),
        "jev_input_tokens": sum(int(d["input_tokens"] or 0) for d in decisions),
        "jev_cost_usd": round(sum(float(d["cost_usd"] or 0) for d in decisions), 6),
    }
    text = json.dumps(report, indent=1, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
