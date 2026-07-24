"""Estimate situation effect sizes with BigQuery ML.

Trains one linear regression per position (WR, RB, TE) over the historical
rows of analytics_player_situation (2016-2025 transitions): next-season
standard PPG as the label, with prior PPG, games, and age as controls so the
situation features are measured against a fair baseline (mean reversion is
real and must be controlled for, not attributed to the move).

The coefficients on team_changed and qb_quality_delta ARE the empirical
answer to "how much should a situation move a ranking": e.g. a qb_delta
coefficient of 0.25 means each +1.0 PPG of QB-quality upgrade predicts
+0.25 PPG for the receiver next season, holding his own production constant.

This is the study, not the adjustment. Its output is a report for owner
review; converting coefficients into bounded Phase-3 rank adjustments is a
formula change under the runbook and needs sign-off.

Models land in the advanced-metrics dataset as situation_effect_v0_<pos>.

Usage:
    python scripts/run_situation_ml_study.py            # train + report
    python scripts/run_situation_ml_study.py --report-only
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "fantasy-football-498121"
BRAIN = "fantasy_football_brain"
METRICS = "fantasy_football_advanced_metrics"
POSITIONS = ("WR", "RB", "TE")
MIN_GAMES = 4

BRANCH_ROOT = Path(__file__).resolve().parents[1]


def model_id(position: str) -> str:
    return f"{PROJECT}.{METRICS}.situation_effect_v0_{position.lower()}"


def training_sql(position: str) -> str:
    return f"""
    SELECT
      ppg_next,
      ppg_prev,
      games_prev,
      age_at_season,
      CAST(team_changed AS INT64) AS team_changed_i,
      IFNULL(qb_quality_delta, 0.0) AS qb_delta,
      CAST(qb_changed AS INT64) AS qb_changed_i
    FROM `{PROJECT}.{BRAIN}.analytics_player_situation`
    WHERE situation_for_season < 2026
      AND position = '{position}'
      AND ppg_next IS NOT NULL
      AND ppg_prev IS NOT NULL
      AND age_at_season IS NOT NULL
      AND games_prev >= {MIN_GAMES}
    """


def train(client, position: str) -> None:
    sql = f"""
    CREATE OR REPLACE MODEL `{model_id(position)}`
    OPTIONS (
      model_type = 'linear_reg',
      input_label_cols = ['ppg_next'],
      data_split_method = 'NO_SPLIT'
    ) AS {training_sql(position)}
    """
    client.query(sql).result()


def report(client, position: str) -> dict:
    weights = {
        row["processed_input"]: round(row["weight"], 4)
        for row in client.query(
            f"SELECT processed_input, weight FROM ML.WEIGHTS(MODEL `{model_id(position)}`)"
        ).result()
    }
    evaluation = dict(next(iter(client.query(
        f"SELECT * FROM ML.EVALUATE(MODEL `{model_id(position)}`, ({training_sql(position)}))"
    ).result())))
    sample = dict(next(iter(client.query(
        f"SELECT COUNT(*) AS n, COUNTIF(team_changed_i = 1) AS movers FROM ({training_sql(position)})"
    ).result())))
    return {
        "position": position,
        "n": int(sample["n"]),
        "movers": int(sample["movers"]),
        "r2": round(float(evaluation.get("r2_score", 0.0)), 3),
        "mae_ppg": round(float(evaluation.get("mean_absolute_error", 0.0)), 2),
        "weights": weights,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report-only", action="store_true", help="Skip training; report existing models.")
    args = parser.parse_args()

    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT)
    results = []
    for position in POSITIONS:
        if not args.report_only:
            print(f"training situation_effect_v0_{position.lower()}...", flush=True)
            train(client, position)
        results.append(report(client, position))

    out_dir = BRANCH_ROOT / "build" / "situation-study"
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = out_dir / "situation_effect_v0_report.json"
    artifact.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2),
        encoding="utf-8",
    )

    print(f"\nreport: {artifact}")
    for r in results:
        w = r["weights"]
        print(
            f"\n{r['position']}: n={r['n']} (movers={r['movers']}), r2={r['r2']}, mae={r['mae_ppg']} ppg\n"
            f"  team_changed:  {w.get('team_changed_i'):+.3f} ppg\n"
            f"  qb_delta:      {w.get('qb_delta'):+.3f} ppg per +1.0 QB ppg\n"
            f"  qb_changed:    {w.get('qb_changed_i'):+.3f} ppg\n"
            f"  age (per yr):  {w.get('age_at_season'):+.3f} ppg\n"
            f"  ppg_prev:      {w.get('ppg_prev'):+.3f} (persistence; 1.0 = no mean reversion)"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
