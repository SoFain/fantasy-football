"""Apply Situation adjustments to the live boards (Phase 3, owner-approved).

Converts the validated situation-effect findings into bounded rank moves on the
standard and gng_keeper WR/RB/TE boards. Doctrine: facts -> flags -> owner-gated
bounded adjustments; this is the third step, approved for rollout 2026-07-24
after the walk-forward backtest (situation model beats baseline on movers in
22/24 position/scale/year cells, coefficient signs stable in all 36 windows).

Model (v1 forms per scale/position, owner-approved 2026-07-25; see EFFECTS):

    delta_ppg = team*moved + (qb + moved*qb_mover_extra)*qb_delta
                + moved*winpct_mover*(winpct_to - winpct_from)

Age is deliberately absent: the fable formula already carries an
age-availability component, so re-applying age here would double-count.
QB boards are never touched: the effect study covers WR/RB/TE only, and the
QB cutline machinery (QB6/QB24 owner guards) stays sovereign.

PPG deltas become rank slots through the board's own local production density
(how many PPG separate neighbors at that rank), capped at +/-4 slots — the
same movement cap the guarded QB blend uses. Players then swap slots on the
FIXED score ladder: the score multiset per board never changes, so every
release invariant (bounds, contiguity, GNG's 0.5-step scale) survives by
construction.

Provenance: moved players get llm_adjustment_code SITUATION_V0 (appended to
any existing code), a self-describing detail/evidence pair, and a rationale
suffix. Ripple-displaced neighbors keep their own provenance untouched.

Fail-closed: the full outcome is computed and validated locally BEFORE any
write; boards already carrying SITUATION_V0 refuse to re-adjust (idempotency —
promoters must rebuild first, as the daily chain does).

Usage:
    python scripts/apply_situation_adjustments.py            # dry-run report
    python scripts/apply_situation_adjustments.py --apply    # requires ALLOW_SITUATION_ADJUSTMENTS=true
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT = "fantasy-football-498121"
BRAIN = "fantasy_football_brain"
METRICS = "fantasy_football_advanced_metrics"
TABLE = f"{PROJECT}.{BRAIN}.analytics_pigskin_rankings"
SITUATION = f"{PROJECT}.{BRAIN}.analytics_player_situation"
STAGING = f"{PROJECT}.{BRAIN}.situation_adjustments_staging"
# The GNG pipeline's source of truth: the unified builder, the GNG promoter,
# and the review-table rebuild all read this table, and the promoter derives
# the live score from rank (100 - 0.5*rank). Adjusted GNG ranks must be
# mirrored here or stage 6's artifact-vs-active preflight refuses the day.
GNG_MIRROR = f"{PROJECT}.{METRICS}.gng_2026_positional_boards_with_rookies"

BRANCH_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = Path(os.environ.get("PIGSKIN_MAIN_ROOT", r"E:\Fantasy Football")) / "output" / "board-refresh"

CODE = "SITUATION_V1"
CODE_FAMILY = "SITUATION_V"  # idempotency guard matches any pinned version
CAP_SLOTS = 4              # matches the guarded QB blend's movement cap
DENSITY_WINDOW = 5         # ranks each side when estimating local PPG density
MIN_PPG_STEP = 0.05        # density floor: flat regions can't produce huge jumps
MIN_DELTA_PPG = 0.10       # dead-band: sub-noise deltas (model MAE ~2 PPG) never move anyone
POSITIONS = ("WR", "RB", "TE")

# Pinned policy coefficients (PPG), owner-approved 2026-07-25 from the v1
# interaction study (walk-forward validated per cell; see
# docs/rebuild/situation-layer.md):
#   WR both scales — v0 additive (richer forms did not validate).
#   RB standard    — QB-interaction form (mover QB slope = qb + qb_mover_extra);
#                    RB gng keeps v0 (3/6, unvalidated).
#   TE both scales — team-quality form. winpct_mover is the counterfactual
#                    differential (C_winpct_delta + C_winpct_to): a mover swaps
#                    origin environment for destination, so both fitted slopes
#                    ride the same delta. Stayers are never touched by it.
# delta_ppg = team*moved + (qb + moved*qb_mover_extra)*qb_delta
#             + moved*winpct_mover*(winpct_to - winpct_from)
# Re-pinning is a formula change: new walk-forward + owner sign-off.
EFFECTS = {
    "standard": {
        "WR": {"team": -0.778, "qb": 0.022},
        "RB": {"team": -0.527, "qb": -0.0035, "qb_mover_extra": 0.1096},
        "TE": {"team": -0.485, "qb": 0.0278, "qb_mover_extra": -0.0062, "winpct_mover": -0.483},
    },
    "gng": {
        "WR": {"team": -0.562, "qb": 0.020},
        "RB": {"team": -0.328, "qb": 0.057},
        "TE": {"team": -0.376, "qb": 0.0268, "qb_mover_extra": -0.0102, "winpct_mover": -0.449},
    },
}
PROFILE_SCALE = {"standard": "standard", "gng_keeper": "gng"}
SCALE_COLS = {
    "standard": {"qb_delta": "qb_quality_delta", "ppg_prev": "ppg_prev"},
    "gng": {"qb_delta": "qb_quality_delta_gng", "ppg_prev": "gng_ppg_prev"},
}

# 2025 REG-season win shares (ties = half), nflreadpy schedules, pinned for
# the season. Sleeper-coded destinations normalize through TEAM_ALIASES.
TEAM_ALIASES = {"LAR": "LA"}
WINPCT_2025 = {
    "ARI": 0.1765, "ATL": 0.4706, "BAL": 0.4706, "BUF": 0.7059, "CAR": 0.4706, "CHI": 0.6471, "CIN": 0.3529, "CLE": 0.2941,
    "DAL": 0.4412, "DEN": 0.8235, "DET": 0.5294, "GB": 0.5588, "HOU": 0.7059, "IND": 0.4706, "JAX": 0.7647, "KC": 0.3529,
    "LA": 0.7059, "LAC": 0.6471, "LV": 0.1765, "MIA": 0.4118, "MIN": 0.5294, "NE": 0.8235, "NO": 0.3529, "NYG": 0.2353,
    "NYJ": 0.1765, "PHI": 0.6471, "PIT": 0.5882, "SEA": 0.8235, "SF": 0.7059, "TB": 0.4706, "TEN": 0.1765, "WAS": 0.2941,
}


def winpct(team: str | None) -> float | None:
    if team is None:
        return None
    return WINPCT_2025.get(TEAM_ALIASES.get(team, team))


def pull_board(client, profile: str, position: str) -> list[dict]:
    cols = SCALE_COLS[PROFILE_SCALE[profile]]
    sql = f"""
    SELECT r.player_id, r.player_name, r.rank, r.ranking_score,
           r.llm_adjustment_code,
           s.team_changed, s.team_from, s.team_to, s.qb_changed, s.qb_to,
           s.{cols['qb_delta']} AS qb_delta, s.{cols['ppg_prev']} AS ppg_prev,
           s.flags_json, s.metric_basis
    FROM `{TABLE}` r
    LEFT JOIN `{SITUATION}` s
      ON s.player_id_internal = r.player_id AND s.situation_for_season = 2026
    WHERE r.is_active AND r.scoring_profile_id = '{profile}' AND r.position = '{position}'
    ORDER BY r.rank
    """
    return [dict(row) for row in client.query(sql).result()]


def local_step(ppg_by_rank: list[float | None], idx: int) -> float:
    """PPG separating neighbors near this rank; floored, never negative."""
    known = [(i, v) for i, v in enumerate(ppg_by_rank) if v is not None]
    if len(known) < 2:
        return MIN_PPG_STEP
    lo = max(0, idx - DENSITY_WINDOW)
    hi = min(len(ppg_by_rank) - 1, idx + DENSITY_WINDOW)
    above = [v for i, v in known if lo <= i <= idx]
    below = [v for i, v in known if idx <= i <= hi]
    if not above or not below:
        return MIN_PPG_STEP
    span = max(1, hi - lo)
    slope = (max(above) - min(below)) / span
    return max(MIN_PPG_STEP, slope)


def plan_board(rows: list[dict], profile: str, position: str) -> dict:
    """Compute the full post-adjustment board. Pure; no I/O."""
    eff = EFFECTS[PROFILE_SCALE[profile]][position]
    ladder = [r["ranking_score"] for r in rows]  # score by slot, fixed
    ppg_by_rank = [r["ppg_prev"] for r in rows]

    plans = []
    for i, r in enumerate(rows):
        moved_team = bool(r["team_changed"])
        qb_delta = r["qb_delta"] if r["qb_delta"] is not None else 0.0
        qb_slope = eff["qb"] + (eff.get("qb_mover_extra", 0.0) if moved_team else 0.0)
        delta_ppg = (eff["team"] if moved_team else 0.0) + qb_slope * qb_delta
        wp_delta = None
        if moved_team and "winpct_mover" in eff:
            wp_to, wp_from = winpct(r["team_to"]), winpct(r["team_from"])
            if wp_to is not None and wp_from is not None:
                wp_delta = round(wp_to - wp_from, 4)
                delta_ppg += eff["winpct_mover"] * wp_delta
        slots = 0
        if r["team_changed"] is not None and abs(delta_ppg) >= MIN_DELTA_PPG:
            step = local_step(ppg_by_rank, i)
            slots = round(delta_ppg / step)
            slots = max(-CAP_SLOTS, min(CAP_SLOTS, slots))
        plans.append({
            "row": r, "old_rank": r["rank"], "slots": slots,
            "target": r["rank"] - slots,  # positive delta_ppg -> up the board
            "delta_ppg": round(delta_ppg, 3), "moved_team": moved_team, "qb_delta": qb_delta,
            "qb_slope": round(qb_slope, 4), "wp_delta": wp_delta,
        })

    order = sorted(plans, key=lambda p: (p["target"], p["old_rank"]))
    for new_rank, p in enumerate(order, start=1):
        p["new_rank"] = new_rank
        p["new_score"] = ladder[new_rank - 1]

    adjusted = [p for p in order if p["slots"] != 0]
    return {"profile": profile, "position": position, "all": order, "adjusted": adjusted}


def validate_plan(plan: dict) -> list[str]:
    rows = plan["all"]
    problems = []
    n = len(rows)
    if sorted(p["new_rank"] for p in rows) != list(range(1, n + 1)):
        problems.append(f"{plan['profile']}/{plan['position']}: new ranks not contiguous 1..{n}")
    if sorted(p["new_score"] for p in rows) != sorted(p["row"]["ranking_score"] for p in rows):
        problems.append(f"{plan['profile']}/{plan['position']}: score multiset changed")
    for p in rows:
        if abs(p["target"] - p["old_rank"]) > CAP_SLOTS:
            problems.append(f"{p['row']['player_name']}: intent exceeds cap")
        if p["slots"] == 0 and abs(p["new_rank"] - p["old_rank"]) > CAP_SLOTS:
            problems.append(f"{p['row']['player_name']}: ripple displacement exceeds cap")
    return problems


def provenance(p: dict, profile: str, position: str) -> dict:
    r = p["row"]
    scale = PROFILE_SCALE[profile]
    eff = EFFECTS[scale][position]
    bits = []
    if p["moved_team"]:
        bits.append(f"team {r['team_from']}->{r['team_to']} {eff['team']:+.2f} PPG")
    if p["qb_delta"]:
        bits.append(
            f"QB delta {p['qb_delta']:+.2f} PPG x {p['qb_slope']:.3f}"
            f" = {p['qb_slope'] * p['qb_delta']:+.2f}"
        )
    if p["wp_delta"] is not None and p["wp_delta"] != 0:
        bits.append(
            f"team record {p['wp_delta']:+.3f} win share x {eff['winpct_mover']:.3f}"
            f" = {eff['winpct_mover'] * p['wp_delta']:+.2f}"
        )
    detail = (
        f"Situation v1 [{scale}]: " + "; ".join(bits)
        + f"; net {p['delta_ppg']:+.2f} PPG -> {position}{p['old_rank']}->{position}{p['new_rank']}"
        + f" (cap {CAP_SLOTS})."
    )
    evidence = f"metric_basis {r['metric_basis']}; flags {r['flags_json']}; v1 study walk-forward, owner-approved 2026-07-25"
    return {
        "scoring_profile_id": profile, "position": position, "player_id": r["player_id"],
        "new_rank": p["new_rank"], "new_score": p["new_score"],
        "moved": p["slots"] != 0, "realized_delta": p["new_rank"] - p["old_rank"],
        "detail": detail if p["slots"] != 0 else None,
        "evidence": evidence if p["slots"] != 0 else None,
        "note": f" | {detail}" if p["slots"] != 0 else None,
    }


def refuse_if_already_adjusted(client) -> None:
    sql = f"""
    SELECT scoring_profile_id, COUNT(*) AS n FROM `{TABLE}`
    WHERE is_active AND llm_adjustment_code LIKE '%{CODE_FAMILY}%'
      AND scoring_profile_id IN ('standard', 'gng_keeper')
    GROUP BY 1
    """
    hit = [dict(r) for r in client.query(sql).result()]
    if hit:
        raise RuntimeError(
            f"boards already carry {CODE} ({hit}); promoters must rebuild before re-adjusting"
        )


def write(client, staged: list[dict]) -> None:
    from google.cloud import bigquery

    schema = [
        bigquery.SchemaField("scoring_profile_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("position", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("player_id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("new_rank", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("new_score", "FLOAT", mode="REQUIRED"),
        bigquery.SchemaField("moved", "BOOLEAN", mode="REQUIRED"),
        bigquery.SchemaField("realized_delta", "INTEGER", mode="REQUIRED"),
        bigquery.SchemaField("detail", "STRING"),
        bigquery.SchemaField("evidence", "STRING"),
        bigquery.SchemaField("note", "STRING"),
    ]
    job = client.load_table_from_json(
        staged, STAGING,
        job_config=bigquery.LoadJobConfig(schema=schema, write_disposition="WRITE_TRUNCATE"),
    )
    job.result()

    client.query(f"""
    MERGE `{TABLE}` t
    USING `{STAGING}` s
      ON t.player_id = s.player_id AND t.scoring_profile_id = s.scoring_profile_id
     AND t.position = s.position AND t.is_active
    WHEN MATCHED THEN UPDATE SET
      rank = s.new_rank,
      ranking_score = s.new_score,
      llm_adjustment_code = IF(s.moved,
        IF(t.llm_adjustment_code IS NULL, '{CODE}', CONCAT(t.llm_adjustment_code, '+{CODE}')),
        t.llm_adjustment_code),
      llm_adjustment_detail = IF(s.moved,
        IF(t.llm_adjustment_detail IS NULL, s.detail, CONCAT(t.llm_adjustment_detail, ' | ', s.detail)),
        t.llm_adjustment_detail),
      llm_adjustment_evidence = IF(s.moved,
        IF(t.llm_adjustment_evidence IS NULL, s.evidence, CONCAT(t.llm_adjustment_evidence, ' | ', s.evidence)),
        t.llm_adjustment_evidence),
      llm_rank_delta = IF(s.moved AND t.llm_rank_delta IS NULL, s.realized_delta, t.llm_rank_delta),
      rank_rationale = IF(s.moved, CONCAT(COALESCE(t.rank_rationale, ''), s.note), t.rank_rationale)
    """).result()

    client.query(f"""
    MERGE `{GNG_MIRROR}` t
    USING `{STAGING}` s
      ON t.player_id = s.player_id AND t.position = s.position
     AND s.scoring_profile_id = 'gng_keeper'
    WHEN MATCHED THEN UPDATE SET rank = s.new_rank
    """).result()
    mirror_rows = [dict(r) for r in client.query(f"""
    SELECT position, COUNT(*) AS n, COUNT(DISTINCT rank) AS distinct_ranks,
           MIN(rank) AS lo, MAX(rank) AS hi
    FROM `{GNG_MIRROR}` GROUP BY position
    """).result()]
    broken = [
        r for r in mirror_rows
        if not (r["n"] == r["distinct_ranks"] == r["hi"] and r["lo"] == 1)
    ]
    if broken:
        raise RuntimeError(f"gng mirror ranks not contiguous after merge: {broken}")

    client.query(f"DROP TABLE `{STAGING}`").result()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Write the adjustments (gated).")
    args = parser.parse_args()
    if args.apply and os.environ.get("ALLOW_SITUATION_ADJUSTMENTS") != "true":
        print("refusing --apply without ALLOW_SITUATION_ADJUSTMENTS=true", file=sys.stderr)
        return 2

    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT)
    refuse_if_already_adjusted(client)

    plans, problems = [], []
    for profile in PROFILE_SCALE:
        for position in POSITIONS:
            plan = plan_board(pull_board(client, profile, position), profile, position)
            problems.extend(validate_plan(plan))
            plans.append(plan)
    if problems:
        raise RuntimeError("situation adjustment plan invalid:\n  " + "\n  ".join(problems))

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report_lines = [f"# Situation adjustments {stamp} ({CODE})", ""]
    staged, moved_total = [], 0
    for plan in plans:
        staged.extend(provenance(p, plan["profile"], plan["position"]) for p in plan["all"])
        moved = [p for p in plan["adjusted"] if p["new_rank"] != p["old_rank"]]
        moved_total += len(moved)
        report_lines.append(f"## {plan['profile']} {plan['position']} — {len(moved)} moved")
        for p in sorted(moved, key=lambda p: p["new_rank"]):
            r = p["row"]
            report_lines.append(
                f"- {r['player_name']}: {p['old_rank']} -> {p['new_rank']}"
                f" ({p['delta_ppg']:+.2f} PPG; team={p['moved_team']}, qbΔ={p['qb_delta']:+.2f}"
                f"×{p['qb_slope']:.3f}"
                + (f", recordΔ={p['wp_delta']:+.3f}" if p["wp_delta"] else "")
                + ")"
            )
        report_lines.append("")
    artifact = OUT_DIR / f"situation-adjustments-{stamp}.md"
    artifact.write_text("\n".join(report_lines), encoding="utf-8")
    print("\n".join(report_lines))
    print(f"report: {artifact}")

    if not args.apply:
        print(f"DRY RUN: {moved_total} moves planned; no writes made")
        return 0

    write(client, staged)
    print(f"applied: {moved_total} moves across standard+gng_keeper WR/RB/TE")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"SITUATION ADJUSTMENTS FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
