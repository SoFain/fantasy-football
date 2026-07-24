"""Build succinct GNG scoring context for the active 2026 positional boards."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from google.cloud import bigquery

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_gng_2026_candidate_boards import FORMULAS, build_query  # noqa: E402
from scripts.run_gng_position_candidate_expansion import percent_ranks  # noqa: E402


DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_BRAIN_DATASET = "fantasy_football_brain"
DEFAULT_METRICS_DATASET = "fantasy_football_advanced_metrics"
DEFAULT_TABLE = "gng_2026_rank_context"
CONTEXT_VERSION = "gng-rank-context-v2"
WRITE_GATE = "ALLOW_GNG_RANK_CONTEXT_PUBLISH"
MAX_CONTEXT_LENGTH = 320

METRIC_LABELS = {
    "passing_yards": "passing-yard volume",
    "passing_fd_expected": "expected passing first downs",
    "qb_rushing": "QB rushing",
    "qb_ngs_efficiency": "NGS passing efficiency",
    "passing_cpoe": "completion rate over expected",
    "attempts": "pass attempts",
    "gng_weighted_opp": "GNG-weighted opportunity",
    "target_share": "target share",
    "wopr": "WOPR",
    "receiving_fd_expected": "expected receiving first downs",
    "rushing_fd_expected": "expected rushing first downs",
    "goal_line_opps": "goal-line opportunity",
    "snap_share": "snap share",
    "xfp_share": "expected fantasy-point share",
    "opportunity_quality": "opportunity quality",
    "snap_stability": "snap stability",
    "availability": "availability",
    "first_down_any": "first-down production",
    "ngs_any": "NGS efficiency",
}

METRIC_FAMILIES = {
    "QB": {
        "passing_yards": "volume",
        "passing_fd_expected": "volume",
        "attempts": "volume",
        "qb_rushing": "rushing",
        "qb_ngs_efficiency": "efficiency",
        "passing_cpoe": "efficiency",
    },
    "RB": {
        "gng_weighted_opp": "workload",
        "snap_share": "workload",
        "target_share": "receiving",
        "wopr": "receiving",
        "receiving_fd_expected": "receiving",
        "rushing_fd_expected": "rushing",
        "goal_line_opps": "rushing",
    },
    "WR": {
        "gng_weighted_opp": "opportunity",
        "xfp_share": "opportunity",
        "opportunity_quality": "opportunity",
        "receiving_fd_expected": "first_down",
        "target_share": "target",
        "wopr": "target",
        "snap_share": "role",
        "snap_stability": "role",
        "availability": "role",
    },
    "TE": {
        "gng_weighted_opp": "opportunity",
        "xfp_share": "opportunity",
        "opportunity_quality": "opportunity",
        "first_down_any": "first_down",
        "snap_share": "role",
        "snap_stability": "role",
        "availability": "role",
        "ngs_any": "efficiency",
    },
}


def canonical_player_id(value: Any) -> str:
    return re.sub(r"^(?:gsis|sleeper):", "", str(value or "").strip())


def ordinal_percentile(value: float) -> str:
    percentile = max(0, min(100, round(value * 100)))
    if 10 <= percentile % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(percentile % 10, "th")
    return f"{percentile}{suffix} percentile"


def driver_sentence(
    position: str,
    player_name: str,
    field: str,
    percentile: float,
) -> str:
    owner = player_name + ("'" if player_name.endswith("s") else "'s")
    label = METRIC_LABELS[field]
    grade = ordinal_percentile(percentile)

    if position == "QB":
        if field == "qb_rushing":
            return (
                f"{owner} {label} ({grade}) is the separator, adding a second scoring path "
                "beyond five-point passing TDs."
            )
        if METRIC_FAMILIES[position][field] == "volume":
            return (
                f"{owner} {label} ({grade}) creates repeat shots at GNG's 25-completion and "
                "300-yard bonuses."
            )
        return (
            f"{owner} {label} ({grade}) supports the passing case, though GNG still charges "
            "for sacks and interceptions."
        )

    if position == "RB":
        if field in {"target_share", "wopr"}:
            return (
                f"{owner} {label} ({grade}) is a receiving edge, but GNG pays only 0.1 per "
                "catch; the role must become yards or first downs."
            )
        if field == "receiving_fd_expected":
            return (
                f"{owner} {label} ({grade}) earns direct GNG credit even with catches worth "
                "only 0.1."
            )
        if METRIC_FAMILIES[position][field] == "rushing":
            return (
                f"{owner} {label} ({grade}) maps to GNG first-down scoring and the 20-carry "
                "bonus."
            )
        return (
            f"{owner} {label} ({grade}) puts the 20-carry and 100-yard bonuses in play."
        )

    if position == "WR":
        family = METRIC_FAMILIES[position][field]
        if family == "target":
            return (
                f"{owner} {label} ({grade}) commands volume, but 0.2 per WR catch means those "
                "targets need to become yards or first downs."
            )
        if family == "first_down":
            return (
                f"{owner} {label} ({grade}) earns direct GNG credit and keeps the 100-yard "
                "bonus within reach."
            )
        if family == "role":
            return (
                f"{owner} {label} ({grade}) keeps scoring chances on the field; GNG gives WRs "
                "only 0.2 per catch, so empty volume is muted."
            )
        return (
            f"{owner} {label} ({grade}) supports first-down and 100-yard upside; WR catches "
            "themselves earn only 0.2."
        )

    family = METRIC_FAMILIES[position][field]
    if family == "first_down":
        return (
            f"{owner} {label} ({grade}) earns direct GNG credit, while TE catches add 0.3."
        )
    if family == "role":
        return (
            f"{owner} {label} ({grade}) keeps routes available; GNG's 0.3 per TE catch cannot "
            "make up for lost snaps."
        )
    if family == "efficiency":
        return (
            f"{owner} {label} ({grade}) adds payoff in a format where TE catches earn only 0.3."
        )
    return (
        f"{owner} {label} ({grade}) supports the 0.3-per-catch TE edge and first-down scoring."
    )


def support_sentence(position: str, field: str, percentile: float) -> str:
    family = METRIC_FAMILIES[position][field]
    support_kind = {
        "volume": "Bonus-volume support",
        "rushing": "Rushing support",
        "efficiency": "Efficiency support",
        "workload": "Workload support",
        "receiving": "Receiving support",
        "opportunity": "High-value volume support",
        "first_down": "First-down support",
        "target": "Target-control support",
        "role": "Role support",
    }[family]
    return (
        f"{support_kind} comes from {METRIC_LABELS[field]} "
        f"({ordinal_percentile(percentile)})."
    )


def limiter_sentence(field: str, percentile: float) -> str:
    label = METRIC_LABELS[field]
    grade = ordinal_percentile(percentile)
    if percentile < 0.5:
        return f"{label[0].upper() + label[1:]} ({grade}) is the clear drag."
    if percentile < 0.7:
        return f"The soft spot is {label} at the {grade}."
    return f"{label[0].upper() + label[1:]} is still {grade}, even as the lowest input."


def metric_summary(
    position: str,
    player_name: str,
    row: dict[str, Any],
) -> tuple[str, list[tuple[str, float]], list[str]]:
    _, weights = FORMULAS[position]
    available = [
        (field, float(row[f"p_{field}"]), weight)
        for field, weight in weights.items()
        if field != "profile" and row.get(f"p_{field}") is not None
    ]
    missing = [
        field
        for field in weights
        if field != "profile" and row.get(f"p_{field}") is None
    ]
    if not available:
        return (
            f"{player_name} has no advanced metric history available for this formula.",
            [],
            missing,
        )

    signature = max(available, key=lambda item: (item[1], item[2], item[0]))
    signature_family = METRIC_FAMILIES[position][signature[0]]
    secondary_pool = [
        item
        for item in available
        if item[0] != signature[0]
        and METRIC_FAMILIES[position][item[0]] != signature_family
    ]
    if not secondary_pool:
        secondary_pool = [item for item in available if item[0] != signature[0]]
    secondary = max(
        secondary_pool or [signature],
        key=lambda item: (item[1] * item[2], item[1], item[2], item[0]),
    )
    contributor_fields = {signature[0], secondary[0]}
    limiter_pool = [item for item in available if item[0] not in contributor_fields]
    limiter = min(limiter_pool or available, key=lambda item: (item[1], item[0]))

    audit_metrics = [(signature[0], signature[1]), (secondary[0], secondary[1])]
    audit_metrics.append((limiter[0], limiter[1]))
    summary = " ".join(
        (
            driver_sentence(position, player_name, signature[0], signature[1]),
            support_sentence(position, secondary[0], secondary[1]),
            limiter_sentence(limiter[0], limiter[1]),
        )
    )
    return summary, audit_metrics, missing


def veteran_context(
    position: str, player_name: str, row: dict[str, Any]
) -> tuple[str, list[tuple[str, float]], list[str]]:
    return metric_summary(position, player_name, row)


def rookie_context(position: str, player_name: str) -> str:
    base = (
        f"{player_name}'s rank is provisional: market and Sleeper depth-chart placement stand "
        "in for NFL advanced metrics."
    )
    if position == "QB":
        return f"{base} Five-point passing TDs and sack penalties will matter once pro volume arrives."
    if position == "RB":
        return f"{base} GNG's 0.1 per catch and workload bonuses will test that market slot."
    if position == "WR":
        return f"{base} With only 0.2 per WR catch, early yards and first downs will matter most."
    return f"{base} The 0.3 TE catch rate and first-down scoring will shape the NFL fit."


def add_percentiles(metric_rows: list[dict[str, Any]]) -> None:
    for position, (_, weights) in FORMULAS.items():
        position_rows = [row for row in metric_rows if row.get("position") == position]
        for field in weights:
            ranks = percent_ranks(position_rows, field)
            for index, row in enumerate(position_rows):
                row[f"p_{field}"] = ranks.get(index)


def build_context_rows(
    active_rows: list[dict[str, Any]],
    metric_rows: list[dict[str, Any]],
    generated_at: str,
) -> list[dict[str, Any]]:
    add_percentiles(metric_rows)
    metrics_by_key = {
        (str(row["position"]), canonical_player_id(row["player_id"])): row
        for row in metric_rows
    }
    contexts = []
    for active in active_rows:
        position = str(active["position"])
        formula_id = FORMULAS[position][0]
        if active.get("model_name") != formula_id:
            raise ValueError(
                f"Active {position} formula mismatch for {active['player_name']}: "
                f"{active.get('model_name')!r} != {formula_id!r}"
            )

        rank_source = str(active.get("rank_source") or "")
        player_name = str(active["player_name"])
        metric_row = metrics_by_key.get((position, canonical_player_id(active["player_id"])))
        if rank_source == "market_rookie_overlay":
            context = rookie_context(position, player_name)
            audit_metrics: list[tuple[str, float]] = []
            missing = list(FORMULAS[position][1])
            metric_status = "rookie_no_nfl_history"
        elif metric_row is None:
            raise ValueError(
                f"Missing formula metric row for active {position} {active['player_name']} "
                f"({active['player_id']})"
            )
        else:
            context, audit_metrics, missing = veteran_context(
                position, player_name, metric_row
            )
            metric_status = "current_formula_inputs"

        if len(context) > MAX_CONTEXT_LENGTH:
            raise ValueError(
                f"Context exceeds {MAX_CONTEXT_LENGTH} characters for {active['player_name']}: "
                f"{len(context)}"
            )
        contexts.append(
            {
                "generated_at": generated_at,
                "context_version": CONTEXT_VERSION,
                "scoring_profile_id": "gng_keeper",
                "player_id": str(active["player_id"]),
                "player_name": player_name,
                "current_team": active.get("current_team"),
                "position": position,
                "rank": int(active["rank"]),
                "rank_source": rank_source,
                "formula_id": formula_id,
                "context": context,
                "primary_metric": audit_metrics[0][0] if audit_metrics else None,
                "primary_percentile": audit_metrics[0][1] if audit_metrics else None,
                "secondary_metric": audit_metrics[1][0] if len(audit_metrics) > 1 else None,
                "secondary_percentile": audit_metrics[1][1] if len(audit_metrics) > 1 else None,
                "limiter_metric": audit_metrics[2][0] if len(audit_metrics) > 2 else None,
                "limiter_percentile": audit_metrics[2][1] if len(audit_metrics) > 2 else None,
                "missing_metrics": "|".join(missing) or None,
                "metric_source_status": metric_status,
            }
        )
    return contexts


def validate_context_rows(
    active_rows: list[dict[str, Any]], contexts: list[dict[str, Any]]
) -> None:
    if len(contexts) != len(active_rows):
        raise ValueError(f"Context row count mismatch: {len(contexts)} != {len(active_rows)}")
    active_keys = {
        (str(row["position"]), str(row["player_id"]), int(row["rank"])) for row in active_rows
    }
    context_keys = {
        (str(row["position"]), str(row["player_id"]), int(row["rank"])) for row in contexts
    }
    if active_keys != context_keys:
        raise ValueError("Context rows do not preserve the active GNG positional queues")
    if len(context_keys) != len(contexts):
        raise ValueError("Context rows contain duplicate position/player/rank keys")
    if any(not str(row.get("context") or "").strip() for row in contexts):
        raise ValueError("Context rows contain blank public text")
    for position in FORMULAS:
        driver_metrics = {
            row["primary_metric"]
            for row in contexts
            if row["position"] == position and row["primary_metric"] is not None
        }
        if len(driver_metrics) < 2:
            raise ValueError(
                f"GNG {position} context uses fewer than two metric-driven archetypes"
            )


def active_rank_query(project: str, brain_dataset: str) -> str:
    return f"""
SELECT
  position,
  rank,
  player_id,
  player_name,
  current_team,
  rank_source,
  model_name
FROM `{project}.{brain_dataset}.analytics_pigskin_rankings`
WHERE is_active
  AND scoring_profile_id = 'gng_keeper'
  AND position IN ('QB', 'RB', 'WR', 'TE')
ORDER BY position, rank
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--brain-dataset", default=DEFAULT_BRAIN_DATASET)
    parser.add_argument("--metrics-dataset", default=DEFAULT_METRICS_DATASET)
    parser.add_argument("--table", default=DEFAULT_TABLE)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "output" / "gng-2026-rank-context.json",
    )
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    client = bigquery.Client(project=args.project)
    active_rows = [
        dict(row)
        for row in client.query(
            active_rank_query(args.project, args.brain_dataset)
        ).result()
    ]
    metric_rows = [
        dict(row)
        for row in client.query(
            build_query(args.project, args.brain_dataset, args.metrics_dataset)
        ).result()
    ]
    generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    contexts = build_context_rows(active_rows, metric_rows, generated_at)
    validate_context_rows(active_rows, contexts)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(contexts, indent=2) + "\n", encoding="utf-8")

    if args.apply:
        if os.environ.get(WRITE_GATE) != "true":
            raise RuntimeError(f"Set {WRITE_GATE}=true before using --apply")
        table_id = f"{args.project}.{args.metrics_dataset}.{args.table}"
        config = bigquery.LoadJobConfig(
            write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
            schema=[
                bigquery.SchemaField("generated_at", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("context_version", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("scoring_profile_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("player_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("player_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("current_team", "STRING"),
                bigquery.SchemaField("position", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("rank", "INT64", mode="REQUIRED"),
                bigquery.SchemaField("rank_source", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("formula_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("context", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("primary_metric", "STRING"),
                bigquery.SchemaField("primary_percentile", "FLOAT64"),
                bigquery.SchemaField("secondary_metric", "STRING"),
                bigquery.SchemaField("secondary_percentile", "FLOAT64"),
                bigquery.SchemaField("limiter_metric", "STRING"),
                bigquery.SchemaField("limiter_percentile", "FLOAT64"),
                bigquery.SchemaField("missing_metrics", "STRING"),
                bigquery.SchemaField("metric_source_status", "STRING", mode="REQUIRED"),
            ],
        )
        client.load_table_from_json(contexts, table_id, job_config=config).result()

    summary = {
        position: {
            "rows": sum(row["position"] == position for row in contexts),
            "rookie_contexts": sum(
                row["position"] == position
                and row["metric_source_status"] == "rookie_no_nfl_history"
                for row in contexts
            ),
            "max_context_length": max(
                len(row["context"]) for row in contexts if row["position"] == position
            ),
            "driver_metrics": sorted(
                {
                    row["primary_metric"]
                    for row in contexts
                    if row["position"] == position and row["primary_metric"] is not None
                }
            ),
        }
        for position in FORMULAS
    }
    print(
        json.dumps(
            {
                "applied": args.apply,
                "context_version": CONTEXT_VERSION,
                "output": str(args.output),
                "summary": summary,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
