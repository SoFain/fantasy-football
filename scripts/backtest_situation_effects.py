"""Walk-forward backtest of the situation-effect findings.

The BQML study (run_situation_ml_study.py) fits on all 2016-2025 transitions
at once and reports in-sample coefficients — descriptive, not predictive. This
script answers the harder question: would the situation features have helped
*before* the answer was known?

For each holdout season S (2020-2025), fit ordinary least squares on
transitions strictly before S and predict season S:

    baseline:  ppg_next ~ ppg_prev + games_prev + age
    situation: baseline + team_changed + qb_delta + qb_changed

The gap between the two models' held-out errors is the empirical value of the
situation features. Also reported: mover-only error (adjustments would only
touch movers), within-season Spearman rank correlation (rank order is what a
board actually needs), and coefficient stability across training windows
(a sign that flips year to year is noise, not policy material).

GNG parity: every cell runs in both scoring scales.

Read-only against BigQuery; fits happen locally (numpy lstsq). Report lands in
build/situation-study/situation_backtest_report.json.

Usage:
    python scripts/backtest_situation_effects.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

PROJECT = "fantasy-football-498121"
BRAIN = "fantasy_football_brain"
POSITIONS = ("WR", "RB", "TE")
HOLDOUT_SEASONS = range(2020, 2026)
MIN_GAMES = 4

BRANCH_ROOT = Path(__file__).resolve().parents[1]

SCALES = {
    "standard": {"label": "ppg_next", "prev": "ppg_prev", "qb_delta": "qb_quality_delta"},
    "gng": {"label": "gng_ppg_next", "prev": "gng_ppg_prev", "qb_delta": "qb_quality_delta_gng"},
}

BASELINE_FEATURES = ("ppg_prev", "games_prev", "age")
SITUATION_FEATURES = BASELINE_FEATURES + ("team_changed", "qb_delta", "qb_changed")

PULL_SQL = f"""
SELECT situation_for_season, position, games_prev, age_at_season,
       team_changed, qb_changed,
       ppg_prev, ppg_next, qb_quality_delta,
       gng_ppg_prev, gng_ppg_next, qb_quality_delta_gng
FROM `{PROJECT}.{BRAIN}.analytics_player_situation`
WHERE situation_for_season < 2026
  AND position IN {POSITIONS!r}
  AND games_prev >= {MIN_GAMES}
  AND age_at_season IS NOT NULL
"""


def pull_rows(client) -> list[dict]:
    return [dict(row) for row in client.query(PULL_SQL).result()]


def design(rows: list[dict], scale: str, features: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Feature matrix (with intercept) and label vector for one scale."""
    cols = SCALES[scale]
    values = {
        "ppg_prev": [r[cols["prev"]] for r in rows],
        "games_prev": [r["games_prev"] for r in rows],
        "age": [r["age_at_season"] for r in rows],
        "team_changed": [1.0 if r["team_changed"] else 0.0 for r in rows],
        "qb_delta": [r[cols["qb_delta"]] or 0.0 for r in rows],
        "qb_changed": [1.0 if r["qb_changed"] else 0.0 for r in rows],
    }
    x = np.column_stack([np.ones(len(rows))] + [np.asarray(values[f], dtype=float) for f in features])
    y = np.asarray([r[cols["label"]] for r in rows], dtype=float)
    return x, y


def fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(x, y, rcond=None)[0]


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman rho via average ranks (scipy-free)."""

    def ranks(v: np.ndarray) -> np.ndarray:
        order = np.argsort(v, kind="stable")
        r = np.empty(len(v), dtype=float)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r[order[i : j + 1]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return r

    ra, rb = ranks(a), ranks(b)
    if np.std(ra) == 0 or np.std(rb) == 0:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def usable(rows: list[dict], scale: str) -> list[dict]:
    cols = SCALES[scale]
    return [r for r in rows if r[cols["label"]] is not None and r[cols["prev"]] is not None]


def walk_forward(rows: list[dict], position: str, scale: str) -> dict:
    """All holdout years for one position/scale cell."""
    pool = usable([r for r in rows if r["position"] == position], scale)
    years, coef_track = [], {"team_changed": [], "qb_delta": []}
    for season in HOLDOUT_SEASONS:
        train = [r for r in pool if r["situation_for_season"] < season]
        test = [r for r in pool if r["situation_for_season"] == season]
        if len(train) < 100 or len(test) < 20:
            continue

        xb_tr, y_tr = design(train, scale, BASELINE_FEATURES)
        xs_tr, _ = design(train, scale, SITUATION_FEATURES)
        xb_te, y_te = design(test, scale, BASELINE_FEATURES)
        xs_te, _ = design(test, scale, SITUATION_FEATURES)

        beta_b, beta_s = fit(xb_tr, y_tr), fit(xs_tr, y_tr)
        pred_b, pred_s = xb_te @ beta_b, xs_te @ beta_s

        movers = np.asarray([r["team_changed"] is True for r in test])
        coef = dict(zip(("intercept",) + SITUATION_FEATURES, beta_s))
        coef_track["team_changed"].append(round(float(coef["team_changed"]), 3))
        coef_track["qb_delta"].append(round(float(coef["qb_delta"]), 3))
        years.append({
            "season": season,
            "n_train": len(train),
            "n_test": len(test),
            "n_movers": int(movers.sum()),
            "mae_baseline": round(float(np.abs(pred_b - y_te).mean()), 3),
            "mae_situation": round(float(np.abs(pred_s - y_te).mean()), 3),
            "mae_movers_baseline": round(float(np.abs(pred_b[movers] - y_te[movers]).mean()), 3) if movers.any() else None,
            "mae_movers_situation": round(float(np.abs(pred_s[movers] - y_te[movers]).mean()), 3) if movers.any() else None,
            "spearman_baseline": round(spearman(pred_b, y_te), 3),
            "spearman_situation": round(spearman(pred_s, y_te), 3),
        })

    def mean(key: str) -> float:
        return round(float(np.mean([y[key] for y in years if y[key] is not None])), 3)

    return {
        "position": position,
        "scale": scale,
        "years": years,
        "summary": {
            "mae_baseline": mean("mae_baseline"),
            "mae_situation": mean("mae_situation"),
            "mae_movers_baseline": mean("mae_movers_baseline"),
            "mae_movers_situation": mean("mae_movers_situation"),
            "spearman_baseline": mean("spearman_baseline"),
            "spearman_situation": mean("spearman_situation"),
            "situation_wins_mae": sum(y["mae_situation"] < y["mae_baseline"] for y in years),
            "situation_wins_mover_mae": sum(
                y["mae_movers_situation"] < y["mae_movers_baseline"]
                for y in years
                if y["mae_movers_situation"] is not None
            ),
            "n_years": len(years),
            "coef_team_changed_by_year": coef_track["team_changed"],
            "coef_qb_delta_by_year": coef_track["qb_delta"],
            "coef_team_changed_sign_stable": len({c > 0 for c in coef_track["team_changed"]}) == 1,
            "coef_qb_delta_sign_stable": len({c > 0 for c in coef_track["qb_delta"]}) == 1,
        },
    }


def main() -> int:
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT)
    rows = pull_rows(client)
    print(f"pulled {len(rows)} historical transitions")

    results = [walk_forward(rows, position, scale) for scale in SCALES for position in POSITIONS]

    out_dir = BRANCH_ROOT / "build" / "situation-study"
    out_dir.mkdir(parents=True, exist_ok=True)
    artifact = out_dir / "situation_backtest_report.json"
    artifact.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2),
        encoding="utf-8",
    )
    print(f"report: {artifact}\n")

    for r in results:
        s = r["summary"]
        print(
            f"{r['position']} [{r['scale']}]  ({s['n_years']} holdout years)\n"
            f"  MAE all:    {s['mae_baseline']:.3f} -> {s['mae_situation']:.3f}"
            f"  (situation wins {s['situation_wins_mae']}/{s['n_years']})\n"
            f"  MAE movers: {s['mae_movers_baseline']:.3f} -> {s['mae_movers_situation']:.3f}"
            f"  (wins {s['situation_wins_mover_mae']}/{s['n_years']})\n"
            f"  Spearman:   {s['spearman_baseline']:.3f} -> {s['spearman_situation']:.3f}\n"
            f"  team_changed coef by year: {s['coef_team_changed_by_year']}"
            f" (sign stable: {s['coef_team_changed_sign_stable']})\n"
            f"  qb_delta coef by year:     {s['coef_qb_delta_by_year']}"
            f" (sign stable: {s['coef_qb_delta_sign_stable']})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
