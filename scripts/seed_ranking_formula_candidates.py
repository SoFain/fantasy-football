"""Seed draft ranking formula candidates for controlled backtest review."""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src import ranking_formula_backtests as rfb


FORMULA_VERSION = "ranking_formula_v0_2026_001"
FORMULA_SET_ID = "ranking_formula_set_v0_2026_001"
FORMULA_SET_VERSION = "formula_set_v0_2026_001"
FORMULA_SET_NAME = "Initial 2026 Draft Ranking Formula Set"

BASELINE_CANDIDATES = {
    "QB": "ranking_formula_qb_balanced_v0_2026_001",
    "RB": "ranking_formula_rb_balanced_v0_2026_001",
    "WR": "ranking_formula_wr_balanced_v0_2026_001",
    "TE": "ranking_formula_te_balanced_v0_2026_001",
}


def build_seed_payload() -> dict[str, Any]:
    candidate_rows = [
        _candidate(
            "QB",
            "balanced",
            "QB Balanced Baseline",
            {
                "recent_points_avg": 0.30,
                "passing_epa_per_play": 0.25,
                "passing_success_rate": 0.20,
                "cpoe": 0.10,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "QB",
            "volume",
            "QB Volume Opportunity",
            {
                "recent_points_avg": 0.25,
                "dropbacks": 0.30,
                "rushing_attempts": 0.15,
                "usage_volume": 0.15,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "QB",
            "efficiency",
            "QB Efficiency Upside",
            {
                "passing_epa_per_play": 0.35,
                "passing_success_rate": 0.25,
                "cpoe": 0.20,
                "team_epa_per_play": 0.10,
                "pigskin_context_score": 0.10,
            },
        ),
        _candidate(
            "RB",
            "balanced",
            "RB Balanced Baseline",
            {
                "recent_points_avg": 0.30,
                "usage_volume": 0.25,
                "rush_success_rate": 0.15,
                "receiving_usage": 0.15,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "RB",
            "volume",
            "RB Volume Opportunity",
            {
                "carries": 0.30,
                "targets": 0.20,
                "goal_line_opportunities": 0.20,
                "usage_volume": 0.20,
                "pigskin_context_score": 0.10,
            },
        ),
        _candidate(
            "RB",
            "efficiency",
            "RB Efficiency Upside",
            {
                "rush_success_rate": 0.30,
                "receiving_usage": 0.20,
                "epa_per_play": 0.20,
                "success_rate": 0.15,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "WR",
            "balanced",
            "WR Balanced Baseline",
            {
                "recent_points_avg": 0.30,
                "targets": 0.25,
                "air_yards": 0.15,
                "receiving_epa": 0.15,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "WR",
            "volume",
            "WR Volume Opportunity",
            {
                "targets": 0.35,
                "air_yards": 0.25,
                "red_zone_targets": 0.15,
                "usage_volume": 0.15,
                "pigskin_context_score": 0.10,
            },
        ),
        _candidate(
            "WR",
            "efficiency",
            "WR Efficiency Upside",
            {
                "receiving_epa": 0.30,
                "receiving_yards": 0.20,
                "epa_per_play": 0.20,
                "success_rate": 0.15,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "TE",
            "balanced",
            "TE Balanced Baseline",
            {
                "recent_points_avg": 0.30,
                "targets": 0.25,
                "receiving_yards": 0.15,
                "team_pass_rate": 0.15,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "TE",
            "volume",
            "TE Volume Opportunity",
            {
                "targets": 0.35,
                "red_zone_targets": 0.20,
                "air_yards": 0.15,
                "usage_volume": 0.15,
                "pigskin_context_score": 0.15,
            },
        ),
        _candidate(
            "TE",
            "efficiency",
            "TE Efficiency Upside",
            {
                "receiving_epa": 0.30,
                "receiving_yards": 0.20,
                "team_pass_rate": 0.15,
                "epa_per_play": 0.15,
                "pigskin_context_score": 0.20,
            },
        ),
    ]
    formula_set_row = {
        "formula_set_id": FORMULA_SET_ID,
        "formula_set_name": FORMULA_SET_NAME,
        "formula_set_version": FORMULA_SET_VERSION,
        "qb_candidate_id": BASELINE_CANDIDATES["QB"],
        "rb_candidate_id": BASELINE_CANDIDATES["RB"],
        "wr_candidate_id": BASELINE_CANDIDATES["WR"],
        "te_candidate_id": BASELINE_CANDIDATES["TE"],
        "status": "draft",
        "description": "Initial draft grouping for backtest-only ranking formula evaluation.",
        "created_by": rfb.CREATED_BY,
        "created_at": _now(),
        "updated_at": None,
        "notes": "Backtest-only draft set. Not a champion selection.",
    }
    _validate_payload(candidate_rows, formula_set_row)
    return {"candidate_rows": candidate_rows, "formula_set_row": formula_set_row}


def apply_seed(
    *,
    project_id: str = rfb.DEFAULT_PROJECT,
    dataset_id: str = rfb.DEFAULT_DATASET,
    client: Any | None = None,
) -> dict[str, Any]:
    rfb.require_write_authorization()
    payload = build_seed_payload()
    if client is None:
        from google.cloud import bigquery

        client = bigquery.Client(project=project_id)
    for row in payload["candidate_rows"]:
        client.query(
            _candidate_merge_sql(project_id, dataset_id),
            job_config=_job_config(row, rfb.RANKING_TABLES["ranking_formula_candidates"]),
        ).result()
    client.query(
        _formula_set_merge_sql(project_id, dataset_id),
        job_config=_job_config(payload["formula_set_row"], rfb.RANKING_TABLES["ranking_formula_sets"]),
    ).result()
    return {
        "wrote": True,
        "candidate_count": len(payload["candidate_rows"]),
        "formula_set_count": 1,
        "candidate_ids": [row["candidate_id"] for row in payload["candidate_rows"]],
        "formula_set_id": payload["formula_set_row"]["formula_set_id"],
        "target_tables": ["ranking_formula_candidates", "ranking_formula_sets"],
    }


def summarize_payload(payload: Mapping[str, Any], *, wrote: bool) -> dict[str, Any]:
    candidates = list(payload["candidate_rows"])
    position_counts = Counter(row["position"] for row in candidates)
    return {
        "dry_run": not wrote,
        "wrote": wrote,
        "candidate_count": len(candidates),
        "candidate_count_by_position": dict(sorted(position_counts.items())),
        "candidate_ids": [row["candidate_id"] for row in candidates],
        "formula_set_id": payload["formula_set_row"]["formula_set_id"],
        "formula_set_candidate_ids": {
            "QB": payload["formula_set_row"]["qb_candidate_id"],
            "RB": payload["formula_set_row"]["rb_candidate_id"],
            "WR": payload["formula_set_row"]["wr_candidate_id"],
            "TE": payload["formula_set_row"]["te_candidate_id"],
        },
        "target_tables": ["ranking_formula_candidates", "ranking_formula_sets"],
        "non_target_tables": [
            "ranking_backtest_runs",
            "ranking_backtest_results",
            "ranking_backtest_candidate_summaries",
            "ranking_formula_champions",
        ],
    }


def _candidate(position: str, style: str, name: str, weights: Mapping[str, float]) -> dict[str, Any]:
    formula = {
        "version": FORMULA_VERSION,
        "position": position,
        "score_expression": "weighted_linear",
        "features": list(weights),
        "weights": dict(weights),
        "normalization": {"method": "position_percentile"},
        "source_flags": {},
    }
    return rfb.build_candidate_row(
        formula,
        formula_name=name,
        candidate_id=f"ranking_formula_{position.lower()}_{style}_v0_2026_001",
        formula_set_id=FORMULA_SET_ID,
        target_name="top_12_position",
        status="draft",
    )


def _validate_payload(candidate_rows: list[dict[str, Any]], formula_set_row: Mapping[str, Any]) -> None:
    if len(candidate_rows) != 12:
        raise ValueError("seed payload must contain 12 candidates")
    counts = Counter(row["position"] for row in candidate_rows)
    if counts != {"QB": 3, "RB": 3, "WR": 3, "TE": 3}:
        raise ValueError(f"unexpected candidate counts: {dict(counts)}")
    candidate_ids = {row["candidate_id"] for row in candidate_rows}
    if len(candidate_ids) != len(candidate_rows):
        raise ValueError("candidate IDs must be unique")
    for row in candidate_rows:
        if row["status"] != "draft":
            raise ValueError("all candidate rows must be draft")
        formula = json.loads(row["formula_json"])
        rfb.validate_formula(formula)
        if any(feature in rfb.BLOCKED_METRIC_FEATURES for feature in formula["features"]):
            raise ValueError("seed payload must not use blocked metrics")
    expected_refs = {
        formula_set_row["qb_candidate_id"],
        formula_set_row["rb_candidate_id"],
        formula_set_row["wr_candidate_id"],
        formula_set_row["te_candidate_id"],
    }
    if not expected_refs.issubset(candidate_ids):
        raise ValueError("formula set must reference seeded baseline candidates")
    if formula_set_row["status"] != "draft":
        raise ValueError("formula set must be draft")


def _candidate_merge_sql(project_id: str, dataset_id: str) -> str:
    return _merge_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        table_name="ranking_formula_candidates",
        key_fields=("candidate_id",),
    )


def _formula_set_merge_sql(project_id: str, dataset_id: str) -> str:
    return _merge_sql(
        project_id=project_id,
        dataset_id=dataset_id,
        table_name="ranking_formula_sets",
        key_fields=("formula_set_id",),
    )


def _merge_sql(*, project_id: str, dataset_id: str, table_name: str, key_fields: tuple[str, ...]) -> str:
    fields = rfb.RANKING_TABLES[table_name]
    select_sql = ",\n        ".join(_select_expr(field) for field in fields)
    conditions = " AND ".join(f"target.{field} = source.{field}" for field in key_fields)
    update_fields = [field for field in fields if field not in key_fields]
    update_sql = ",\n        ".join(f"{field} = source.{field}" for field in update_fields)
    insert_fields = ", ".join(fields)
    insert_values = ", ".join(f"source.{field}" for field in fields)
    return f"""
MERGE `{rfb.table_id(project_id, dataset_id, table_name)}` target
USING (
    SELECT
        {select_sql}
) source
ON {conditions}
WHEN MATCHED THEN UPDATE SET
        {update_sql}
WHEN NOT MATCHED THEN INSERT ({insert_fields})
VALUES ({insert_values})
""".strip()


def _select_expr(field: str) -> str:
    if field in {"created_at", "updated_at"}:
        return f"@{field} AS {field}"
    return f"@{field} AS {field}"


def _job_config(row: Mapping[str, Any], fields: tuple[str, ...]) -> Any:
    from google.cloud import bigquery

    params = []
    for field in fields:
        value = row.get(field)
        param_type = "TIMESTAMP" if field in {"created_at", "updated_at"} else "STRING"
        if param_type == "TIMESTAMP" and isinstance(value, str):
            value = datetime.fromisoformat(value)
        params.append(bigquery.ScalarQueryParameter(field, param_type, value))
    return bigquery.QueryJobConfig(query_parameters=params)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Seed draft ranking formula candidates.")
    parser.add_argument("--apply", action="store_true", help="Write draft seed rows with the ranking write gate enabled.")
    parser.add_argument("--project", default=rfb.DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=rfb.DEFAULT_DATASET)
    args = parser.parse_args(argv)

    payload = build_seed_payload()
    if not args.apply:
        print(json.dumps(summarize_payload(payload, wrote=False), indent=2, sort_keys=True))
        return 0

    result = apply_seed(project_id=args.project, dataset_id=args.dataset)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
