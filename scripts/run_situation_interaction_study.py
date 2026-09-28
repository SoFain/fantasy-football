"""Situation v1 study: two owner hypotheses about movers, tested head-to-head.

Owner-raised 2026-07-24 (the D.J. Moore case):
  H1 — a QB upgrade helps a MOVER more than the pooled additive model says.
  H2 — moving to a team with a great record last year is itself an upgrade
       ("feels like a good upgrade but it does need to be tested").

    Model A (v0, additive):   ppg_next ~ controls + team_changed + qb_delta
    Model B (H1):             A + team_changed * qb_delta
    Model C (H1 + H2):        B + team_winpct_to + winpct_delta

team_winpct_to is every player's team prior-season win share (environment);
winpct_delta is destination minus origin win share, nonzero only for movers —
the direct "moved to a better team" signal. Both use the stats season's
records, knowable at decision time (no leakage). Records come from nflreadpy
schedules (REG games, ties = half a win) and are cached to the study artifact
directory for reproducibility and later productionization.

Decision-grade evidence is out-of-sample: walk-forward (fit <=S-1, predict S,
2020-2025), scored on held-out MOVERS — the only players an adjustment
touches. A richer model earns a re-pin recommendation ONLY if it beats the
simpler one in a majority of years; full-sample coefficients are reported for
interpretation. Re-pinning EFFECTS in apply_situation_adjustments.py stays a
formula change: owner sign-off required. Both scoring scales (GNG parity).
Read-only against BigQuery; fits are local numpy OLS.

Usage:
    python scripts/run_situation_interaction_study.py
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
MIN_TEAM_QUALITY_COVERAGE = 0.95

BRANCH_ROOT = Path(__file__).resolve().parents[1]

SCALES = {
    "standard": {"label": "ppg_next", "prev": "ppg_prev", "qb_delta": "qb_quality_delta"},
    "gng": {"label": "gng_ppg_next", "prev": "gng_ppg_prev", "qb_delta": "qb_quality_delta_gng"},
}

BASE = ("ppg_prev", "games_prev", "age")
ADDITIVE = BASE + ("team_changed", "qb_delta", "qb_changed")
INTERACTION = ADDITIVE + ("team_x_qb",)
TEAM_QUALITY = INTERACTION + ("team_winpct_to", "winpct_delta")

MODELS = {"A_additive": ADDITIVE, "B_qb_interaction": INTERACTION, "C_team_quality": TEAM_QUALITY}

PULL_SQL = f"""
SELECT situation_for_season, position, games_prev, age_at_season,
       team_changed, qb_changed, team_from, team_to,
       ppg_prev, ppg_next, qb_quality_delta,
       gng_ppg_prev, gng_ppg_next, qb_quality_delta_gng
FROM `{PROJECT}.{BRAIN}.analytics_player_situation`
WHERE situation_for_season < 2026
  AND position IN {POSITIONS!r}
  AND games_prev >= {MIN_GAMES}
  AND age_at_season IS NOT NULL
"""


def build_team_winpct(schedule_rows: list[dict]) -> dict[tuple[int, str], float]:
    """(season, team) -> REG-season win share, ties counting half."""
    wins: dict[tuple[int, str], float] = {}
    games: dict[tuple[int, str], int] = {}
    for g in schedule_rows:
        if g.get("game_type") != "REG":
            continue
        home, away = g["home_team"], g["away_team"]
        hs, as_ = g.get("home_score"), g.get("away_score")
        if hs is None or as_ is None:
            continue
        season = int(g["season"])
        for team in (home, away):
            games[(season, team)] = games.get((season, team), 0) + 1
            wins.setdefault((season, team), 0.0)
        if hs == as_:
            wins[(season, home)] += 0.5
            wins[(season, away)] += 0.5
        else:
            wins[(season, home if hs > as_ else away)] += 1.0
    return {k: round(wins[k] / games[k], 4) for k in games}


def load_team_winpct(first_season: int, last_season: int) -> dict[tuple[int, str], float]:
    import nflreadpy

    schedules = nflreadpy.load_schedules(list(range(first_season, last_season + 1)))
    return build_team_winpct(schedules.to_dicts())


def enrich_with_team_quality(rows: list[dict], winpct: dict[tuple[int, str], float]) -> float:
    """Attach team_winpct_to / winpct_delta in place; return join coverage."""
    hit = 0
    for r in rows:
        season = r["stats_season"] if "stats_season" in r else r["situation_for_season"] - 1
        to_q = winpct.get((season, r.get("team_to")))
        from_q = winpct.get((season, r.get("team_from")))
        if to_q is not None and from_q is not None:
            hit += 1
            r["team_winpct_to"] = to_q
            r["winpct_delta"] = round(to_q - from_q, 4) if r["team_changed"] else 0.0
        else:
            r["team_winpct_to"] = None
            r["winpct_delta"] = None
    return hit / len(rows) if rows else 0.0


def design(rows: list[dict], scale: str, features: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
    cols = SCALES[scale]
    team = np.asarray([1.0 if r["team_changed"] else 0.0 for r in rows])
    qb = np.asarray([float(r[cols["qb_delta"]] or 0.0) for r in rows])

    def column(name: str) -> np.ndarray:
        if name == "team_changed":
            return team
        if name == "qb_delta":
            return qb
        if name == "team_x_qb":
            return team * qb
        if name == "ppg_prev":
            return np.asarray([float(r[cols["prev"]]) for r in rows])
        if name == "age":
            return np.asarray([float(r["age_at_season"]) for r in rows])
        if name == "qb_changed":
            return np.asarray([1.0 if r["qb_changed"] else 0.0 for r in rows])
        return np.asarray([float(r[name] or 0.0) for r in rows])

    x = np.column_stack([np.ones(len(rows))] + [column(f) for f in features])
    y = np.asarray([float(r[cols["label"]]) for r in rows])
    return x, y


def fit(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return np.linalg.lstsq(x, y, rcond=None)[0]


def usable(rows: list[dict], scale: str, features: tuple[str, ...]) -> list[dict]:
    cols = SCALES[scale]
    rows = [r for r in rows if r[cols["label"]] is not None and r[cols["prev"]] is not None]
    if "team_winpct_to" in features:
        rows = [r for r in rows if r.get("team_winpct_to") is not None]
    return rows


def mover_effect(coef: dict, qb_delta: float, winpct_delta: float = 0.0) -> float:
    """Model C's predicted PPG effect of moving, given the upgrade profile."""
    return (
        coef["team_changed"]
        + (coef["qb_delta"] + coef.get("team_x_qb", 0.0)) * qb_delta
        + coef.get("winpct_delta", 0.0) * winpct_delta
    )


def study_cell(rows: list[dict], position: str, scale: str) -> dict:
    # One pool for all three models so walk-forward comparisons are like-for-like.
    pool = usable([r for r in rows if r["position"] == position], scale, TEAM_QUALITY)

    x_full, y_full = design(pool, scale, TEAM_QUALITY)
    beta = fit(x_full, y_full)
    coef = dict(zip(("intercept",) + TEAM_QUALITY, (round(float(b), 4) for b in beta)))

    years = []
    for season in HOLDOUT_SEASONS:
        train = [r for r in pool if r["situation_for_season"] < season]
        test = [r for r in pool if r["situation_for_season"] == season]
        if len(train) < 100 or len(test) < 20:
            continue
        movers = np.asarray([r["team_changed"] is True for r in test])
        if not movers.any():
            continue
        entry = {"season": season, "n_test_movers": int(movers.sum())}
        for model_name, features in MODELS.items():
            x_tr, y_tr = design(train, scale, features)
            x_te, y_te = design(test, scale, features)
            pred = x_te @ fit(x_tr, y_tr)
            entry[f"mae_movers_{model_name}"] = round(
                float(np.abs(pred[movers] - y_te[movers]).mean()), 3
            )
        years.append(entry)

    def wins(challenger: str, incumbent: str) -> int:
        return sum(
            y[f"mae_movers_{challenger}"] < y[f"mae_movers_{incumbent}"] for y in years
        )

    b_beats_a = wins("B_qb_interaction", "A_additive")
    c_beats_a = wins("C_team_quality", "A_additive")
    c_beats_b = wins("C_team_quality", "B_qb_interaction")
    n_years = len(years)
    best = "A_additive"
    if b_beats_a > n_years / 2:
        best = "B_qb_interaction"
    if c_beats_a > n_years / 2 and (best == "A_additive" or c_beats_b > n_years / 2):
        best = "C_team_quality"

    return {
        "position": position,
        "scale": scale,
        "n": len(pool),
        "coefficients": coef,
        "mover_qb_slope_additive": coef["qb_delta"],
        "mover_qb_slope_interaction": round(coef["qb_delta"] + coef["team_x_qb"], 4),
        "example_mover_qb_plus5": round(mover_effect(coef, 5.0), 3),
        "example_mover_qb_minus5": round(mover_effect(coef, -5.0), 3),
        "example_mover_qb_plus5_to_300_better_team": round(mover_effect(coef, 5.0, 0.300), 3),
        "walk_forward": years,
        "wins": {"B_over_A": b_beats_a, "C_over_A": c_beats_a, "C_over_B": c_beats_b},
        "n_years": n_years,
        "best_model": best,
        "earns_repin": best != "A_additive",
    }


def main() -> int:
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT)
    rows = [dict(row) for row in client.query(PULL_SQL).result()]
    print(f"pulled {len(rows)} historical transitions")

    seasons = sorted({r["situation_for_season"] for r in rows})
    winpct = load_team_winpct(seasons[0] - 1, seasons[-1] - 1)
    coverage = enrich_with_team_quality(rows, winpct)
    print(f"team-quality join coverage: {coverage:.1%}")
    if coverage < MIN_TEAM_QUALITY_COVERAGE:
        raise RuntimeError(
            f"team-quality coverage {coverage:.1%} below {MIN_TEAM_QUALITY_COVERAGE:.0%}: "
            "check team-code alignment between the mart and nflreadpy schedules"
        )

    out_dir = BRANCH_ROOT / "build" / "situation-study"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "team_winpct.json").write_text(
        json.dumps({f"{s}_{t}": v for (s, t), v in sorted(winpct.items())}, indent=2),
        encoding="utf-8",
    )

    results = [study_cell(rows, position, scale) for scale in SCALES for position in POSITIONS]

    artifact = out_dir / "situation_interaction_v1_report.json"
    artifact.write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2),
        encoding="utf-8",
    )
    print(f"report: {artifact}\n")

    for r in results:
        c = r["coefficients"]
        w = r["wins"]
        print(
            f"{r['position']} [{r['scale']}]  n={r['n']}\n"
            f"  team_changed:        {c['team_changed']:+.3f} PPG\n"
            f"  qb_delta (stayers):  {c['qb_delta']:+.4f} per +1 QB PPG\n"
            f"  team_x_qb:           {c['team_x_qb']:+.4f}  -> mover slope {r['mover_qb_slope_interaction']:+.4f}\n"
            f"  team_winpct_to:      {c['team_winpct_to']:+.3f} PPG per +1.000 win share\n"
            f"  winpct_delta:        {c['winpct_delta']:+.3f} PPG per +1.000 mover win-share jump\n"
            f"  mover examples: QB+5 {r['example_mover_qb_plus5']:+.2f} | QB-5 {r['example_mover_qb_minus5']:+.2f}"
            f" | QB+5 & +.300 team {r['example_mover_qb_plus5_to_300_better_team']:+.2f} PPG\n"
            f"  walk-forward mover MAE wins: B>A {w['B_over_A']}/{r['n_years']},"
            f" C>A {w['C_over_A']}/{r['n_years']}, C>B {w['C_over_B']}/{r['n_years']}"
            f"  -> best: {r['best_model']}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
