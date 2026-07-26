"""Compatibility rollout readiness checks for Streamlit migration flags."""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from google.cloud import bigquery
from google.api_core.exceptions import NotFound

from src.compat_flags import (
    USE_COMPAT_PLAYER_PROFILES,
    USE_COMPAT_SLEEPER_WATCH,
    USE_COMPAT_TRADE_ASSETS,
    USE_COMPAT_TRADE_PLAYER_HISTORY,
    USE_COMPAT_VIEWER_TEAM_CONTEXT,
)
from src.load import get_bigquery_client


DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_MAX_BYTES_BILLED = int(os.environ.get("COMPAT_ROLLOUT_MAX_BYTES_BILLED", "1000000000"))
DEFAULT_SAMPLE_LIMIT = 1000
IDENTIFIER_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PROJECT_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9:.-]*[A-Za-z0-9]$")
REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATIONS_DIR = REPO_ROOT / "bigquery" / "validations"


@dataclass(frozen=True)
class CompatFlagSpec:
    flag_name: str
    object_name: str
    helper_module: str
    ui_area: str
    validation_pattern: str
    required_columns: tuple[str, ...]
    rough_ui_impact: str
    rollback: str


ROLLOUT_ORDER = (
    USE_COMPAT_TRADE_PLAYER_HISTORY,
    USE_COMPAT_TRADE_ASSETS,
    USE_COMPAT_PLAYER_PROFILES,
    USE_COMPAT_SLEEPER_WATCH,
    USE_COMPAT_VIEWER_TEAM_CONTEXT,
)

COMPAT_FLAG_SPECS = {
    USE_COMPAT_TRADE_PLAYER_HISTORY: CompatFlagSpec(
        flag_name=USE_COMPAT_TRADE_PLAYER_HISTORY,
        object_name="compat_trade_player_history",
        helper_module="src.trade_history",
        ui_area="Trade Lab AI outlook player history",
        validation_pattern="compat_trade_player_history",
        required_columns=(
            "player_id_internal",
            "source_player_key",
            "player_display_name",
            "position",
            "team",
            "season",
            "week",
            "scoring_profile_id",
            "total_fantasy_points",
            "fantasy_points_ppr",
            "epa_summary_json",
            "source_freshness_json",
            "missing_data_flags",
        ),
        rough_ui_impact="Low. It replaces capped recent player history in Trade Lab outlook prompts.",
        rollback="Unset USE_COMPAT_TRADE_PLAYER_HISTORY and restart Streamlit or Cloud Run.",
    ),
    USE_COMPAT_TRADE_ASSETS: CompatFlagSpec(
        flag_name=USE_COMPAT_TRADE_ASSETS,
        object_name="compat_trade_assets_current",
        helper_module="src.trade_assets",
        ui_area="Trade Lab asset picker and value board",
        validation_pattern="compat_trade_assets_current",
        required_columns=(
            "player_id_internal",
            "display_name",
            "position",
            "team",
            "market_value",
            "scoring_profile_id",
            "league_type_id",
            "roster_format_id",
            "source_freshness_json",
            "missing_data_flags",
        ),
        rough_ui_impact="Medium. It changes the player asset selector and value context.",
        rollback="Unset USE_COMPAT_TRADE_ASSETS and restart Streamlit or Cloud Run.",
    ),
    USE_COMPAT_PLAYER_PROFILES: CompatFlagSpec(
        flag_name=USE_COMPAT_PLAYER_PROFILES,
        object_name="compat_player_profiles_current",
        helper_module="src.player_profiles",
        ui_area="Player Profiles and Versus Finder profile directory",
        validation_pattern="compat_player_profiles_current",
        required_columns=(
            "player_id_internal",
            "display_name",
            "position",
            "current_team",
            "scoring_profile_id",
            "fantasy_points_current_season",
            "model_run_id",
            "source_freshness_json",
            "missing_data_flags",
        ),
        rough_ui_impact="High. It changes a broad profile surface with many optional fields.",
        rollback="Unset USE_COMPAT_PLAYER_PROFILES and restart Streamlit or Cloud Run.",
    ),
    USE_COMPAT_SLEEPER_WATCH: CompatFlagSpec(
        flag_name=USE_COMPAT_SLEEPER_WATCH,
        object_name="compat_sleeper_watch_candidates",
        helper_module="src.sleeper_watch",
        ui_area="Sleeper Watch segment candidate board",
        validation_pattern="compat_sleeper_watch_candidates",
        required_columns=(
            "player_id_internal",
            "display_name",
            "position",
            "team",
            "season",
            "week",
            "scoring_profile_id",
            "streamer_score",
            "candidate_reason",
            "source_freshness_json",
            "missing_data_flags",
        ),
        rough_ui_impact="Medium. It changes a segment board that already uses curated compatibility data.",
        rollback="Unset USE_COMPAT_SLEEPER_WATCH and restart Streamlit or Cloud Run.",
    ),
    USE_COMPAT_VIEWER_TEAM_CONTEXT: CompatFlagSpec(
        flag_name=USE_COMPAT_VIEWER_TEAM_CONTEXT,
        object_name="compat_viewer_team_context",
        helper_module="src.viewer_team_context",
        ui_area="Sleeper Viewer Team Review console context",
        validation_pattern="compat_viewer_team_context",
        required_columns=(
            "viewer_team_context_id",
            "league_id",
            "roster_id",
            "season",
            "week",
            "packet_json",
            "packet_text",
            "source_freshness_json",
            "missing_data_flags",
        ),
        rough_ui_impact="High. It changes viewer-team analysis packets and has less forgiving lookup behavior.",
        rollback="Unset USE_COMPAT_VIEWER_TEAM_CONTEXT and restart Streamlit or Cloud Run.",
    ),
}


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def list_compat_flags() -> list[dict[str, Any]]:
    """Return candidate compatibility flags in rollout order."""

    return [asdict(COMPAT_FLAG_SPECS[flag_name]) for flag_name in ROLLOUT_ORDER]


def check_compat_object_exists(
    flag_name: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    spec = _spec(flag_name)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    table_id = _table_id(client.project, dataset_id, spec.object_name)
    try:
        table = client.get_table(table_id)
    except NotFound:
        return {"flag_name": flag_name, "object_name": spec.object_name, "exists": False, "error": "not_found"}
    except Exception as exc:
        return {"flag_name": flag_name, "object_name": spec.object_name, "exists": False, "error": str(exc)}
    return {
        "flag_name": flag_name,
        "object_name": spec.object_name,
        "exists": True,
        "table_id": table_id,
        "table_type": getattr(table, "table_type", None),
    }


def check_compat_row_count(
    flag_name: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    spec = _spec(flag_name)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    table_id = _table_id(client.project, dataset_id, spec.object_name)
    try:
        table = client.get_table(table_id)
    except Exception as exc:
        return {"flag_name": flag_name, "object_name": spec.object_name, "row_count": None, "passed": False, "error": str(exc)}

    metadata_count = getattr(table, "num_rows", None)
    if isinstance(metadata_count, int) and metadata_count > 0:
        return {
            "flag_name": flag_name,
            "object_name": spec.object_name,
            "row_count": metadata_count,
            "row_count_source": "metadata",
            "passed": True,
        }

    sql = f"SELECT COUNT(1) AS row_count FROM `{table_id}`"
    rows = _query_rows(client, sql, _job_config([]))
    row_count = int((rows[0] if rows else {}).get("row_count") or 0)
    return {
        "flag_name": flag_name,
        "object_name": spec.object_name,
        "row_count": row_count,
        "row_count_source": "query",
        "passed": row_count > 0,
    }


def check_compat_required_columns(
    flag_name: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    spec = _spec(flag_name)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    try:
        table = client.get_table(_table_id(client.project, dataset_id, spec.object_name))
    except Exception as exc:
        return {"flag_name": flag_name, "object_name": spec.object_name, "passed": False, "missing_columns": list(spec.required_columns), "error": str(exc)}
    actual = {field.name.lower() for field in getattr(table, "schema", [])}
    missing = [column for column in spec.required_columns if column.lower() not in actual]
    return {
        "flag_name": flag_name,
        "object_name": spec.object_name,
        "required_columns": list(spec.required_columns),
        "missing_columns": missing,
        "passed": not missing,
    }


def check_compat_missing_data_rate(
    flag_name: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
    sample_limit: int = DEFAULT_SAMPLE_LIMIT,
) -> dict[str, Any]:
    spec = _spec(flag_name)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    table_id = _table_id(client.project, dataset_id, spec.object_name)
    column_check = check_compat_required_columns(flag_name, client=client, dataset_id=dataset_id)
    if not column_check.get("passed"):
        return {
            "flag_name": flag_name,
            "object_name": spec.object_name,
            "passed": False,
            "error": "required_columns_missing",
            "missing_columns": column_check.get("missing_columns", []),
        }

    safe_limit = max(1, min(int(sample_limit), 10000))
    sql = f"""
    SELECT
        COUNT(1) AS sampled_rows,
        COUNTIF(source_freshness_json IS NULL OR source_freshness_json = '') AS source_freshness_missing_rows,
        COUNTIF(missing_data_flags IS NULL OR missing_data_flags = '') AS missing_flags_missing_rows
    FROM (
        SELECT source_freshness_json, missing_data_flags
        FROM `{table_id}`
        LIMIT @sample_limit
    )
    """
    rows = _query_rows(client, sql, _job_config([("sample_limit", "INT64", safe_limit)]))
    row = rows[0] if rows else {}
    sampled_rows = int(row.get("sampled_rows") or 0)
    source_missing = int(row.get("source_freshness_missing_rows") or 0)
    flags_missing = int(row.get("missing_flags_missing_rows") or 0)
    return {
        "flag_name": flag_name,
        "object_name": spec.object_name,
        "sampled_rows": sampled_rows,
        "source_freshness_missing_rows": source_missing,
        "missing_flags_missing_rows": flags_missing,
        "source_freshness_missing_rate": _rate(source_missing, sampled_rows),
        "missing_flags_missing_rate": _rate(flags_missing, sampled_rows),
        "passed": sampled_rows > 0 and source_missing == 0 and flags_missing == 0,
    }


def check_compat_validation_results(
    flag_name: str,
    *,
    validations_dir: Path | str = VALIDATIONS_DIR,
) -> dict[str, Any]:
    spec = _spec(flag_name)
    validation_path = Path(validations_dir)
    files = sorted(path.name for path in validation_path.glob("*.sql") if spec.validation_pattern in path.name)
    return {
        "flag_name": flag_name,
        "object_name": spec.object_name,
        "validation_pattern": spec.validation_pattern,
        "validation_files": files,
        "validation_file_count": len(files),
        "passed": bool(files),
        "status": "discovered" if files else "missing_validation_files",
    }


def generate_rollout_readiness_report(
    flag_name: str,
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    spec = _spec(flag_name)
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    exists = check_compat_object_exists(flag_name, client=client, dataset_id=dataset_id)
    row_count = check_compat_row_count(flag_name, client=client, dataset_id=dataset_id) if exists.get("exists") else {"passed": False}
    columns = check_compat_required_columns(flag_name, client=client, dataset_id=dataset_id) if exists.get("exists") else {"passed": False, "missing_columns": list(spec.required_columns)}
    missing_rate = check_compat_missing_data_rate(flag_name, client=client, dataset_id=dataset_id) if exists.get("exists") and columns.get("passed") else {"passed": False}
    validations = check_compat_validation_results(flag_name)
    ready = all(
        [
            exists.get("exists"),
            row_count.get("passed"),
            columns.get("passed"),
            missing_rate.get("passed"),
            validations.get("passed"),
        ]
    )
    return {
        "flag_name": flag_name,
        "object_name": spec.object_name,
        "helper_module": spec.helper_module,
        "ui_area": spec.ui_area,
        "rough_ui_impact": spec.rough_ui_impact,
        "rollback": spec.rollback,
        "ready": ready,
        "recommend_enable": ready and flag_name == USE_COMPAT_TRADE_PLAYER_HISTORY,
        "checks": {
            "object_exists": exists,
            "row_count": row_count,
            "required_columns": columns,
            "missing_data_rate": missing_rate,
            "validation_files": validations,
        },
    }


def recommend_next_flag_to_enable(
    *,
    client: Any | None = None,
    dataset_id: str | None = None,
) -> dict[str, Any]:
    client = client or get_bigquery_client()
    dataset_id = dataset_id or get_bigquery_dataset()
    reports = []
    for flag_name in ROLLOUT_ORDER:
        report = generate_rollout_readiness_report(flag_name, client=client, dataset_id=dataset_id)
        reports.append(report)
        if report.get("ready"):
            return {
                "recommended_flag": flag_name,
                "reason": "First ready flag in rollout order.",
                "report": report,
                "evaluated_flags": [item["flag_name"] for item in reports],
            }
    return {
        "recommended_flag": None,
        "reason": "No compatibility flag passed readiness checks.",
        "evaluated_flags": [item["flag_name"] for item in reports],
        "reports": reports,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Streamlit compatibility rollout readiness.")
    parser.add_argument("--check", choices=ROLLOUT_ORDER, help="Compatibility flag to check.")
    parser.add_argument("--recommend-next", action="store_true", help="Recommend the next flag to enable.")
    parser.add_argument("--dataset", default=get_bigquery_dataset(), help="BigQuery dataset name.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    if not args.check and not args.recommend_next:
        raise SystemExit("Use --check FLAG or --recommend-next.")
    client = get_bigquery_client()
    if args.check:
        result = generate_rollout_readiness_report(args.check, client=client, dataset_id=args.dataset)
    else:
        result = recommend_next_flag_to_enable(client=client, dataset_id=args.dataset)
    print(json.dumps(result, indent=2, sort_keys=True, default=str))


def _spec(flag_name: str) -> CompatFlagSpec:
    try:
        return COMPAT_FLAG_SPECS[flag_name]
    except KeyError as exc:
        raise ValueError(f"Unknown compatibility rollout flag: {flag_name}") from exc


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    if not PROJECT_ID_RE.match(project_id):
        raise ValueError(f"Unsafe BigQuery project ID: {project_id}")
    if not IDENTIFIER_RE.match(dataset_id):
        raise ValueError(f"Unsafe BigQuery dataset ID: {dataset_id}")
    if not IDENTIFIER_RE.match(table_name):
        raise ValueError(f"Unsafe BigQuery table name: {table_name}")
    return f"{project_id}.{dataset_id}.{table_name}"


def _job_config(params: list[tuple[str, str, Any]]) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        maximum_bytes_billed=DEFAULT_MAX_BYTES_BILLED,
        query_parameters=[bigquery.ScalarQueryParameter(name, type_name, value) for name, type_name, value in params],
    )


def _query_rows(client: Any, sql: str, job_config: bigquery.QueryJobConfig) -> list[dict[str, Any]]:
    rows = client.query(sql, job_config=job_config).result()
    return [_row_to_dict(row) for row in rows]


def _row_to_dict(row: Any) -> dict[str, Any]:
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "items"):
        return dict(row.items())
    return dict(row)


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return numerator / denominator


if __name__ == "__main__":
    main()
