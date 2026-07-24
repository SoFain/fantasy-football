"""Daily automated board refresh: the rankings runbook encoded as a fail-closed chain.

Re-runs the APPROVED formulas on fresh data and re-promotes all four profiles.
This never changes a formula: formula changes still require backtests, owner
review, and a new version per the runbook. What was previously a human walking
through docs/rankings-production-runbook.md is executed here in the same order,
with the same write gates, and any failure stops the chain before the next
write.

The fable pipeline scripts live in the main checkout (this file runs from the
platform branch until the branches are reconciled), so every stage resolves
against PIGSKIN_MAIN_ROOT, default E:\\Fantasy Football.

Stages (mirroring the runbook):

  0. Refresh the post-formula safety context from today's saved Sleeper
     snapshot (zero API calls; the 07:00 ingest is the single /players caller).
  1. Focused unit tests.
  2. Current-player coverage gate (read-only; exits 2 on a blocking loss).
  3. Dry-run every positional promoter. All must pass before any write.
  4. Apply positional promotions, each behind its own ALLOW_* write gate.
  5. Validate active positional rows against the runbook's release invariants.
  6. Build and promote unified Top 150 boards (dry-run, then apply).
  7. Validate unified boards: 150 unique contiguous rows per profile.
  8. Build GNG rank context (dry-run, then apply).
  9. Generate all public profiles locally; require four profiles, 150 rows
     each, zero warnings.

Publication is deliberately NOT here: the daily wrapper runs this first and
only proceeds to publish + site import when this exits 0, so a mid-chain
failure leaves the public feed and the site on the last complete release
(runbook: Recovery).

Exit codes, consumed by scripts/daily_publish_and_import.ps1 in the main
checkout:

    0  refresh complete; publish the new boards
    1  a gate tripped BEFORE any write (tests, coverage, a dry-run guardrail
       such as the QB24 cutline). Boards are untouched; publishing the
       last-approved state is safe and keeps the manifest fresh.
    3  a failure AFTER writes began. Do not publish; see runbook Recovery.

Usage:
    python scripts/run_daily_board_refresh.py --dry-only   # no writes anywhere
    python scripts/run_daily_board_refresh.py --apply      # the full chain
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

MAIN_ROOT = Path(os.environ.get("PIGSKIN_MAIN_ROOT", r"E:\Fantasy Football"))
PYTHON = sys.executable
OUT = MAIN_ROOT / "output" / "board-refresh"

# Flipped the moment stage 4 starts. Decides the failure exit code: a failure
# before any write is recoverable by simply not refreshing today; a failure
# after writes began must block publication (runbook: Recovery).
WRITES_BEGAN = False

PROJECT = "fantasy-football-498121"
BRAIN = "fantasy_football_brain"
METRICS = "fantasy_football_advanced_metrics"

# Runbook "Current positional row contracts".
ROW_CONTRACTS = {
    "standard": {"QB": 45, "RB": 85, "WR": 100, "TE": 35},
    "ppr": {"QB": 45, "RB": 80, "WR": 100, "TE": 35},
    "half_ppr": {"QB": 45, "RB": 80, "WR": 100, "TE": 35},
    "gng_keeper": {"QB": 45, "RB": 80, "WR": 100, "TE": 35},
}

TEST_MODULES = [
    "tests.test_promote_ppr_fable_v1_positional",
    "tests.test_build_unified_ppr_fable_v1_top100",
    "tests.test_promote_unified_fable_v1_standard_top100",
    "tests.test_public_rankings_feed",
]


def run(
    label: str,
    args: list[str],
    *,
    env_extra: dict[str, str] | None = None,
    ok_codes: tuple[int, ...] = (0,),
) -> None:
    """Run one stage command from the main checkout; raise on failure.

    Write gates are passed per-stage and never exported globally, so a gate
    opened for one promoter cannot leak into another.
    """
    env = os.environ.copy()
    if env_extra:
        env.update(env_extra)
    print(f"--- {label}: {' '.join(args)}", flush=True)
    result = subprocess.run(args, cwd=MAIN_ROOT, env=env)
    if result.returncode not in ok_codes:
        raise RuntimeError(f"stage failed: {label} (exit {result.returncode})")


def script(name: str) -> str:
    return str(MAIN_ROOT / "scripts" / name)


def bq_rows(sql: str) -> list[dict]:
    from google.cloud import bigquery

    client = bigquery.Client(project=PROJECT)
    return [dict(row) for row in client.query(sql).result()]


def assert_context_fresh() -> None:
    """The safety layer must be built from today's snapshot before promotion."""
    rows = bq_rows(
        f"SELECT MAX(fetched_at) AS fetched_at FROM `{PROJECT}.{METRICS}.sleeper_current_player_context`"
    )
    fetched_at = rows[0]["fetched_at"]
    if fetched_at is None or fetched_at.date() != datetime.now(timezone.utc).date():
        raise RuntimeError(
            f"sleeper_current_player_context is stale (fetched_at={fetched_at}). "
            "The 07:00 ingest-sleeper-news job must succeed before boards refresh."
        )
    print(f"--- safety context fresh: {fetched_at}", flush=True)


def validate_positional() -> None:
    """Runbook 'Release Invariants' for the active positional rows."""
    rows = bq_rows(f"""
        SELECT
          scoring_profile_id, position, COUNT(*) AS row_count,
          MIN(rank) AS min_rank, MAX(rank) AS max_rank,
          COUNT(DISTINCT rank) AS distinct_ranks,
          COUNTIF(current_team IS NULL) AS teamless_rows,
          COUNTIF(pigskin_verdict IS NULL OR pigskin_verdict='') AS missing_verdicts,
          MIN(IF(position IN ('RB','WR','TE'), ranking_score, NULL)) AS min_skill_score,
          MAX(IF(position IN ('RB','WR','TE'), ranking_score, NULL)) AS max_skill_score
        FROM `{PROJECT}.{BRAIN}.analytics_pigskin_rankings`
        WHERE is_active AND position IN ('QB','RB','WR','TE')
        GROUP BY scoring_profile_id, position
    """)
    seen = {(r["scoring_profile_id"], r["position"]): r for r in rows}
    problems: list[str] = []
    for profile, contract in ROW_CONTRACTS.items():
        for position, expected in contract.items():
            row = seen.get((profile, position))
            if row is None:
                problems.append(f"{profile}/{position}: no active rows")
                continue
            if row["row_count"] != expected:
                problems.append(f"{profile}/{position}: {row['row_count']} rows, contract {expected}")
            if not (row["min_rank"] == 1 and row["max_rank"] == row["row_count"] == row["distinct_ranks"]):
                problems.append(f"{profile}/{position}: ranks not contiguous 1..{row['row_count']}")
            if row["teamless_rows"]:
                problems.append(f"{profile}/{position}: {row['teamless_rows']} teamless rows")
            if row["missing_verdicts"]:
                problems.append(f"{profile}/{position}: {row['missing_verdicts']} missing verdicts")
            if position in ("RB", "WR", "TE") and row["min_skill_score"] is not None:
                if row["min_skill_score"] < 50 or row["max_skill_score"] > 99:
                    problems.append(
                        f"{profile}/{position}: score range "
                        f"{row['min_skill_score']}-{row['max_skill_score']} outside 50-99"
                    )
    if problems:
        raise RuntimeError("positional invariants failed:\n  " + "\n  ".join(problems))
    print("--- positional invariants pass", flush=True)


def validate_unified() -> None:
    rows = bq_rows(f"""
        SELECT scoring_profile_id, COUNT(*) AS n, COUNT(DISTINCT player_id) AS distinct_players,
               MIN(overall_rank) AS min_rank, MAX(overall_rank) AS max_rank,
               COUNT(DISTINCT overall_rank) AS distinct_ranks
        FROM `{PROJECT}.{BRAIN}.unified_draft_rankings_current`
        GROUP BY scoring_profile_id
    """)
    seen = {r["scoring_profile_id"]: r for r in rows}
    problems = []
    for profile in ROW_CONTRACTS:
        row = seen.get(profile)
        if row is None:
            problems.append(f"{profile}: missing unified board")
        elif not (
            row["n"] == row["distinct_players"] == row["distinct_ranks"] == 150
            and row["min_rank"] == 1
            and row["max_rank"] == 150
        ):
            problems.append(f"{profile}: not 150 unique contiguous rows ({row})")
    if problems:
        raise RuntimeError("unified invariants failed:\n  " + "\n  ".join(problems))
    print("--- unified invariants pass", flush=True)


def validate_local_publish() -> None:
    manifest_path = MAIN_ROOT / "output" / "public-rankings" / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    profiles = manifest.get("profiles", {})
    problems = []
    for profile in ROW_CONTRACTS:
        entry = profiles.get(profile)
        if entry is None:
            problems.append(f"{profile}: missing from local manifest")
        else:
            if entry.get("overall_count") != 150:
                problems.append(f"{profile}: overall_count {entry.get('overall_count')} != 150")
            if entry.get("warnings"):
                problems.append(f"{profile}: warnings {entry['warnings']}")
    if problems:
        raise RuntimeError("local publish validation failed:\n  " + "\n  ".join(problems))
    print("--- local publish validation passes (4 profiles, 150 rows, zero warnings)", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-only", action="store_true", help="Run every non-writing stage and stop.")
    mode.add_argument("--apply", action="store_true", help="Run the full refresh chain.")
    args = parser.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc)
    print(
        f"=== board refresh start {started.isoformat()} mode={'apply' if args.apply else 'dry-only'}",
        flush=True,
    )

    # Stage 0: safety context from today's saved snapshot. Zero Sleeper calls.
    # Runs in both modes: it reads the warehouse and is the freshness gate for
    # everything after it. In dry-only mode we still verify freshness but skip
    # the table write.
    if args.apply:
        run("0 refresh safety context", [
            PYTHON, script("build_sleeper_current_player_context.py"), "--from-warehouse", "--apply",
        ])
    else:
        run("0 dry safety context", [
            PYTHON, script("build_sleeper_current_player_context.py"), "--from-warehouse", "--dry-run",
        ])
    assert_context_fresh()

    # Stage 1: focused tests.
    run("1 focused tests", [PYTHON, "-m", "unittest", *TEST_MODULES])

    # Stage 2: coverage gate. Read-only; exit 2 means an established
    # depth-order-1 player vanished before the boards. Never promote past it.
    run("2 coverage gate", [PYTHON, script("audit_current_player_ranking_coverage.py"), "--fail-on-blocking"])

    # Stage 3: dry-run every positional promoter before any write.
    run("3 dry standard positional", [PYTHON, script("promote_standard_fable_v1_positional.py")])
    run("3 dry standard QB", [PYTHON, script("promote_standard_qb_guarded_75_25.py"), "--dry-run"])
    run("3 dry ppr positional", [PYTHON, script("promote_ppr_fable_v1_positional.py"), "--scoring-profile", "ppr"])
    run("3 dry half_ppr positional", [PYTHON, script("promote_ppr_fable_v1_positional.py"), "--scoring-profile", "half_ppr"])
    run("3 dry gng candidates", [PYTHON, script("build_gng_2026_candidate_boards.py")])
    run("3 dry gng promote", [PYTHON, script("promote_gng_2026_rankings.py")])

    if args.dry_only:
        run("8 dry gng context", [PYTHON, script("build_gng_rank_context.py")])
        run("9 local publish validation", [PYTHON, script("publish_public_rankings.py")])
        validate_local_publish()
        print("=== dry-only refresh complete; no writes were made", flush=True)
        return 0

    # Stage 4: apply positional promotions, one write gate at a time.
    # promote_guarded_qb_to_reception_profiles has no dry mode by design; it
    # archives prior rows first and runs only after standard QB promotion.
    global WRITES_BEGAN
    WRITES_BEGAN = True
    run("4 apply standard positional", [PYTHON, script("promote_standard_fable_v1_positional.py"), "--apply"],
        env_extra={"ALLOW_STANDARD_FABLE_POSITIONAL_REBUILD": "true"})
    run("4 apply standard QB", [PYTHON, script("promote_standard_qb_guarded_75_25.py"), "--apply"],
        env_extra={"ALLOW_STANDARD_QB_GUARDED_PROMOTION": "true"})
    run("4 apply QB to reception profiles", [PYTHON, script("promote_guarded_qb_to_reception_profiles.py")],
        env_extra={"ALLOW_GUARDED_QB_RECEPTION_PROFILE_PROMOTION": "true"})
    run("4 apply ppr positional", [PYTHON, script("promote_ppr_fable_v1_positional.py"), "--scoring-profile", "ppr", "--apply"],
        env_extra={"ALLOW_PPR_FABLE_POSITIONAL_PROMOTION": "true"})
    run("4 apply half_ppr positional", [PYTHON, script("promote_ppr_fable_v1_positional.py"), "--scoring-profile", "half_ppr", "--apply"],
        env_extra={"ALLOW_PPR_FABLE_POSITIONAL_PROMOTION": "true"})
    run("4 apply gng candidates", [PYTHON, script("build_gng_2026_candidate_boards.py"), "--apply"])
    run("4 apply gng promote", [PYTHON, script("promote_gng_2026_rankings.py"), "--apply"],
        env_extra={"ALLOW_GNG_2026_PRODUCTION_PROMOTION": "true"})

    # Stage 5: runbook invariants on what was just promoted.
    validate_positional()

    # Stage 6: unified boards. Build artifacts, dry-run promoters, then apply.
    standard_board = OUT / "unified-standard-top150.json"
    ppr_board = OUT / "unified-ppr-top150.json"
    half_board = OUT / "unified-half-ppr-top150.json"
    gng_board = OUT / "unified-gng-top150.json"
    run("6 build unified standard", [
        PYTHON, script("build_unified_fable_v1_top100.py"),
        "--json-output", str(standard_board), "--markdown-output", str(OUT / "unified-standard-top150.md"),
    ])
    run("6 build unified ppr", [
        PYTHON, script("build_unified_ppr_fable_v1_top100.py"), "--scoring-profile", "ppr",
        "--json-output", str(ppr_board), "--markdown-output", str(OUT / "unified-ppr-top150.md"),
    ])
    run("6 build unified half_ppr", [
        PYTHON, script("build_unified_ppr_fable_v1_top100.py"), "--scoring-profile", "half_ppr",
        "--json-output", str(half_board), "--markdown-output", str(OUT / "unified-half-ppr-top150.md"),
    ])
    run("6 build unified gng", [PYTHON, script("build_unified_gng_2026_top100.py"), "--output", str(gng_board)])
    run("6 dry promote unified standard", [PYTHON, script("promote_unified_fable_v1_standard_top100.py"), "--board", str(standard_board)])
    run("6 dry promote unified ppr", [PYTHON, script("promote_unified_ppr_fable_v1_top100.py"), "--scoring-profile", "ppr", "--board", str(ppr_board)])
    run("6 dry promote unified half_ppr", [PYTHON, script("promote_unified_ppr_fable_v1_top100.py"), "--scoring-profile", "half_ppr", "--board", str(half_board)])
    run("6 dry promote unified gng", [PYTHON, script("promote_unified_gng_2026_top150.py"), "--board", str(gng_board)])
    run("6 apply unified gng board table", [PYTHON, script("build_unified_gng_2026_top100.py"), "--output", str(gng_board), "--apply"])
    run("6 apply unified standard", [PYTHON, script("promote_unified_fable_v1_standard_top100.py"), "--board", str(standard_board), "--apply"],
        env_extra={"ALLOW_UNIFIED_FABLE_V1_TOP100_PROMOTION": "true"})
    run("6 apply unified ppr", [PYTHON, script("promote_unified_ppr_fable_v1_top100.py"), "--scoring-profile", "ppr", "--board", str(ppr_board), "--apply"],
        env_extra={"ALLOW_UNIFIED_PPR_FABLE_V1_TOP100_PROMOTION": "true"})
    run("6 apply unified half_ppr", [PYTHON, script("promote_unified_ppr_fable_v1_top100.py"), "--scoring-profile", "half_ppr", "--board", str(half_board), "--apply"],
        env_extra={"ALLOW_UNIFIED_PPR_FABLE_V1_TOP100_PROMOTION": "true"})
    run("6 apply unified gng", [PYTHON, script("promote_unified_gng_2026_top150.py"), "--board", str(gng_board), "--apply"],
        env_extra={"ALLOW_UNIFIED_GNG_2026_TOP150_PROMOTION": "true"})

    # Stage 7: unified invariants.
    validate_unified()

    # Stage 8: GNG context (presentation stage; must not touch ranking tables).
    run("8 dry gng context", [PYTHON, script("build_gng_rank_context.py")])
    run("8 apply gng context", [PYTHON, script("build_gng_rank_context.py"), "--apply"],
        env_extra={"ALLOW_GNG_RANK_CONTEXT_PUBLISH": "true"})

    # Stage 9: local publish validation. The wrapper publishes only after this.
    run("9 local publish validation", [PYTHON, script("publish_public_rankings.py")])
    validate_local_publish()

    duration = (datetime.now(timezone.utc) - started).total_seconds()
    print(f"=== board refresh complete in {duration:.0f}s; ready to publish", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"BOARD REFRESH FAILED: {exc}", file=sys.stderr, flush=True)
        if WRITES_BEGAN:
            print(
                "Writes had begun: publication must not proceed. "
                "See docs/rankings-production-runbook.md Recovery.",
                file=sys.stderr,
                flush=True,
            )
            raise SystemExit(3)
        print(
            "No writes were made: boards are unchanged. Publishing the "
            "last-approved state remains safe.",
            file=sys.stderr,
            flush=True,
        )
        raise SystemExit(1)
