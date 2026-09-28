"""Fit and evaluate the availability base-rate model (code only, no language model).

Reads availability_labels_hist (QB/RB/WR/TE, REG, rows not excluded for team
change, release, or non-injury reasons). Chooses the smoothing strength k on a
2022-2023 validation split of a 2016-2021 fit, refits on 2016-2023, and
evaluates on the 2024-2025 holdout against a status-only baseline.

Writes the versioned artifact docs/availability-base-rates-v1.json (counts,
k, and holdout metrics). Read-only on BigQuery.

  python scripts/fit_availability_base_rates.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.availability_base_rates import (  # noqa: E402
    ARTIFACT_PATH,
    MODEL_VERSION,
    NEXT_CHAIN,
    PLAY_CHAIN,
    ROSTER_CHAIN,
    STATUS_ONLY_CHAIN,
    brier,
    calibration_table,
    count_binary,
    count_buckets,
    log_loss,
    multiclass_scores,
    predict_binary,
    predict_buckets,
)
from src.availability_bq import client, query, table_id  # noqa: E402
from src.availability_labels import MISSED_BUCKETS  # noqa: E402

K_GRID = (1, 2, 5, 10, 20, 50, 100, 200)
FIT_SEASONS = (2016, 2023)
VALIDATION_SEASONS = (2022, 2023)
HOLDOUT_SEASONS = (2024, 2025)


def in_seasons(rows: list[dict], bounds: tuple[int, int]) -> list[dict]:
    return [r for r in rows if bounds[0] <= r["season"] <= bounds[1]]


def binary_eval(tables: dict, chain, k: float, rows: list[dict], target: str, depth: int | None = None) -> dict:
    scored = [r for r in rows if r.get(target) is not None]
    probs = [predict_binary(tables, chain, k, r, depth) for r in scored]
    outcomes = [int(bool(r[target])) for r in scored]
    return {
        "n": len(scored),
        "brier": round(brier(probs, outcomes), 5),
        "log_loss": round(log_loss(probs, outcomes), 5),
        "calibration": calibration_table(probs, outcomes),
    }


def bucket_eval(tables: dict, chain, k: float, rows: list[dict], depth: int | None = None) -> dict:
    scored = [r for r in rows if r.get("missed_bucket") is not None]
    dists = [predict_buckets(tables, chain, k, r, depth) for r in scored]
    labels = [MISSED_BUCKETS.index(r["missed_bucket"]) for r in scored]
    return {"n": len(scored), **multiclass_scores(dists, labels)}


def roster_counts(bq, bounds: tuple[int, int]) -> dict:
    rows = query(
        bq,
        f"""
WITH tg AS (
  SELECT season, team, week, LEAD(week) OVER (PARTITION BY season, team ORDER BY week) AS next_week
  FROM `{table_id('availability_team_games')}` WHERE game_type = 'REG'
),
r AS (
  SELECT DISTINCT gsis_id, season, week, team, status
  FROM `{table_id('raw_nflverse_rosters_weekly')}`
  WHERE season BETWEEN {bounds[0]} AND {bounds[1]} AND position IN ('QB','RB','WR','TE') AND gsis_id IS NOT NULL
),
reported AS (
  SELECT DISTINCT gsis_id, season, week FROM `{table_id('raw_nflverse_injuries')}` WHERE gsis_id IS NOT NULL
),
played AS (
  SELECT DISTINCT gsis_id, season, week FROM `{table_id('availability_player_games')}` WHERE game_type = 'REG'
)
SELECT r.status AS roster_status, COUNT(*) AS n, COUNTIF(p.gsis_id IS NOT NULL) AS played_next
FROM r
JOIN tg ON r.season = tg.season AND r.team = tg.team AND r.week = tg.week AND tg.next_week IS NOT NULL
LEFT JOIN reported i ON r.gsis_id = i.gsis_id AND r.season = i.season AND r.week = i.week
LEFT JOIN played p ON r.gsis_id = p.gsis_id AND r.season = p.season AND p.week = tg.next_week
WHERE i.gsis_id IS NULL
GROUP BY 1
""",
    )
    total_n = sum(int(r["n"]) for r in rows)
    total_hits = sum(int(r["played_next"]) for r in rows)
    return {
        "ALL": {"ALL": [total_n, total_hits]},
        "roster_status": {str(r["roster_status"]): [int(r["n"]), int(r["played_next"])] for r in rows},
    }


def main() -> int:
    bq = client()
    rows = query(
        bq,
        f"""
SELECT season, week, report_status, practice_status, prev_week_state, body_part_group, position_group,
  played_this_game, played_next_game, missed_bucket
FROM `{table_id('availability_labels_hist')}`
WHERE position_group != 'OTHER' AND NOT excluded_from_fit AND season BETWEEN 2016 AND 2025
""",
    )
    for r in rows:
        r["played_this_game"] = bool(r["played_this_game"])

    # 1. Choose k on validation.
    inner_fit = in_seasons(rows, (FIT_SEASONS[0], VALIDATION_SEASONS[0] - 1))
    validation = in_seasons(rows, VALIDATION_SEASONS)
    inner_tables = count_binary(inner_fit, PLAY_CHAIN, "played_this_game")
    k_scores = {
        k: binary_eval(inner_tables, PLAY_CHAIN, k, validation, "played_this_game")["log_loss"] for k in K_GRID
    }
    k = min(k_scores, key=k_scores.get)

    # 2. Refit on 2016-2023.
    fit_rows = in_seasons(rows, FIT_SEASONS)
    holdout = in_seasons(rows, HOLDOUT_SEASONS)
    tables = {
        "play_this_game": count_binary(fit_rows, PLAY_CHAIN, "played_this_game"),
        "bucket_this_game": count_buckets(fit_rows, PLAY_CHAIN),
        "play_next_game": count_binary(fit_rows, NEXT_CHAIN, "played_next_game"),
        "roster_next_game": roster_counts(bq, FIT_SEASONS),
    }

    # 3. Holdout evaluation against the status-only baseline.
    listed_with_designation = [r for r in holdout if r["report_status"] in ("Out", "Doubtful", "Questionable")]
    questionable = [r for r in holdout if r["report_status"] == "Questionable"]
    metrics = {
        "k_validation_log_loss": {str(key): value for key, value in k_scores.items()},
        "play_this_game": {
            "model": binary_eval(tables["play_this_game"], PLAY_CHAIN, k, holdout, "played_this_game"),
            "status_only": binary_eval(tables["play_this_game"], STATUS_ONLY_CHAIN, k, holdout, "played_this_game"),
        },
        "play_this_game_questionable_only": {
            "model": binary_eval(tables["play_this_game"], PLAY_CHAIN, k, questionable, "played_this_game"),
            "status_only": binary_eval(tables["play_this_game"], STATUS_ONLY_CHAIN, k, questionable, "played_this_game"),
        },
        "play_this_game_with_designation": {
            "model": binary_eval(tables["play_this_game"], PLAY_CHAIN, k, listed_with_designation, "played_this_game"),
            "status_only": binary_eval(tables["play_this_game"], STATUS_ONLY_CHAIN, k, listed_with_designation, "played_this_game"),
        },
        "bucket_this_game": {
            "model": bucket_eval(tables["bucket_this_game"], PLAY_CHAIN, k, holdout),
            "status_only": bucket_eval(tables["bucket_this_game"], STATUS_ONLY_CHAIN, k, holdout),
        },
        "play_next_game": {
            "model": binary_eval(tables["play_next_game"], NEXT_CHAIN, k, holdout, "played_next_game"),
            "status_only": binary_eval(tables["play_next_game"], NEXT_CHAIN[:2], k, holdout, "played_next_game"),
        },
    }
    for name, lane in metrics.items():
        if name not in ("play_this_game", "k_validation_log_loss"):
            for side in lane.values():
                side.pop("calibration", None)

    artifact = {
        "model_version": MODEL_VERSION,
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_table": "fantasy_football_brain.availability_labels_hist",
        "population": "QB/RB/WR/TE, REG, official report entry, excluded_from_fit = FALSE",
        "fit_seasons": list(FIT_SEASONS),
        "k_selected_on": {"fit": [FIT_SEASONS[0], VALIDATION_SEASONS[0] - 1], "validation": list(VALIDATION_SEASONS)},
        "holdout_seasons": list(HOLDOUT_SEASONS),
        "k": k,
        "estimator": "cell = (hits + k * parent) / (n + k); global level uses a (1, 1) prior",
        "chains": {
            "play_this_game": [list(level) for level in PLAY_CHAIN],
            "bucket_this_game": [list(level) for level in PLAY_CHAIN],
            "play_next_game": [list(level) for level in NEXT_CHAIN],
            "roster_next_game": [list(level) for level in ROSTER_CHAIN],
        },
        "buckets": list(MISSED_BUCKETS),
        "fit_rows": len(fit_rows),
        "holdout_rows": len(holdout),
        "metrics": metrics,
        "tables": tables,
    }
    ARTIFACT_PATH.write_text(json.dumps(artifact, indent=1, sort_keys=False) + "\n", encoding="utf-8")
    print(json.dumps({key: artifact[key] for key in artifact if key != "tables"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
