"""Cloud Run Job-ready dispatcher for long-running warehouse work."""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, Callable

from google.cloud import bigquery

from src.load import get_bigquery_project


DEFAULT_DATASET = "fantasy_football_brain"
JOB_RUNS_TABLE = "cloud_run_job_runs"
VALID_JOB_NAMES = (
    "ingest-nflverse",
    "ingest-sleeper-news",
    "ingest-sleeper-league",
    "ingest-context-events",
    "ingest-market-values",
    "ingest-college-stats",
    "materialize-analytics",
    "generate-pigskin-rankings",
    "generate-evidence-packets",
    "run-projections",
    "run-backtests",
    "validate-warehouse",
    "verify-external-context",
    "generate-content-briefs",
    "grade-claims",
)

logger = logging.getLogger("job_runner")


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AI vs Meatbags warehouse jobs.")
    parser.add_argument("--job-name", required=True, choices=VALID_JOB_NAMES)
    parser.add_argument("--project", default=get_bigquery_project())
    parser.add_argument("--dataset", default=get_bigquery_dataset())
    parser.add_argument("--season", type=int)
    parser.add_argument("--week", type=int)
    parser.add_argument("--season-start", type=int)
    parser.add_argument("--season-end", type=int)
    parser.add_argument("--week-start", type=int)
    parser.add_argument("--week-end", type=int)
    parser.add_argument("--league-id")
    parser.add_argument("--scoring-profile", default="ppr")
    parser.add_argument("--league-type", default="redraft")
    parser.add_argument("--roster-format", default="one_qb")
    parser.add_argument("--model-run-id")
    parser.add_argument("--market-source-id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--horizon", choices=("weekly", "ros", "dynasty"), default="weekly")
    parser.add_argument("--pattern", help="Validation file-name regex for validate-warehouse.")
    parser.add_argument("--player", help="Player name for verify-external-context.")
    parser.add_argument("--query", help="Explicit external verification query.")
    parser.add_argument("--team", help="Optional team context for external verification.")
    parser.add_argument("--max-results", type=int)
    parser.add_argument("--csv", help="CSV path for ingest-context-events.")
    parser.add_argument("--roster-id")
    parser.add_argument("--username")
    parser.add_argument("--display-name")
    parser.add_argument("--team-name")
    parser.add_argument("--positions", default="QB,RB,WR,TE")
    parser.add_argument("--position-limit", type=int)
    parser.add_argument("--refresh-sleeper", action="store_true")
    parser.add_argument("--write-disposition", default="WRITE_TRUNCATE", choices=("WRITE_TRUNCATE", "WRITE_APPEND"))
    parser.add_argument("--job-run-id")
    parser.add_argument("--backtest-name")
    parser.add_argument("--allow-large-backtest", action="store_true")
    parser.add_argument("--brief-type")
    parser.add_argument("--claim-id")
    parser.add_argument("--log-level", default=os.environ.get("LOG_LEVEL", "INFO"))
    return parser.parse_args(argv)


def run_job(
    args: argparse.Namespace,
    *,
    client: Any | None = None,
    dispatchers: dict[str, Callable[[argparse.Namespace, Any], dict[str, Any] | None]] | None = None,
) -> dict[str, Any]:
    client = client or bigquery.Client(project=args.project or get_bigquery_project())
    args.project = args.project or client.project
    _set_runtime_env(args)
    dispatchers = dispatchers or JOB_DISPATCHERS
    dispatcher = dispatchers.get(args.job_name)
    if dispatcher is None:
        raise ValueError(f"Unknown job name: {args.job_name}")

    started_at = datetime.now(timezone.utc)
    job_run_id = args.job_run_id or _generate_job_run_id(args.job_name)
    start_job_run(client, args, job_run_id, started_at)
    _log_status("job_started", job_run_id=job_run_id, job_name=args.job_name, dry_run=args.dry_run)

    try:
        result = dispatcher(args, client) or {}
        finished_at = datetime.now(timezone.utc)
        finish_job_run(
            client,
            args,
            job_run_id,
            started_at,
            finished_at,
            status="success",
            result=result,
        )
        _log_status("job_succeeded", job_run_id=job_run_id, job_name=args.job_name, result=result)
        return {
            "job_run_id": job_run_id,
            "job_name": args.job_name,
            "status": "success",
            "result": result,
        }
    except BaseException as exc:
        if isinstance(exc, KeyboardInterrupt):
            raise
        finished_at = datetime.now(timezone.utc)
        try:
            finish_job_run(
                client,
                args,
                job_run_id,
                started_at,
                finished_at,
                status="failed",
                error_message=str(exc),
                result={"error_type": exc.__class__.__name__},
            )
        except Exception:
            logger.exception("Failed to mark job_run_id=%s as failed.", job_run_id)
        _log_status("job_failed", job_run_id=job_run_id, job_name=args.job_name, error=str(exc))
        raise


def start_job_run(client: Any, args: argparse.Namespace, job_run_id: str, started_at: datetime) -> None:
    row = {
        "job_run_id": job_run_id,
        "job_name": args.job_name,
        "job_type": args.job_name.split("-", 1)[0],
        "cloud_run_job_name": os.environ.get("CLOUD_RUN_JOB") or args.job_name,
        "cloud_run_execution_name": os.environ.get("CLOUD_RUN_EXECUTION"),
        "model_run_id": args.model_run_id,
        "feature_config_version_id": None,
        "scoring_profile_id": args.scoring_profile,
        "league_type_id": args.league_type,
        "roster_format_id": args.roster_format,
        "project_id": args.project,
        "dataset_id": args.dataset,
        "season": args.season,
        "week": args.week,
        "league_id": args.league_id,
        "status": "running",
        "started_at": _format_timestamp(started_at),
        "finished_at": None,
        "duration_seconds": None,
        "row_count": None,
        "bytes_processed": None,
        "source_freshness_snapshot_id": None,
        "error_message": None,
        "log_url": None,
        "created_by": os.environ.get("K_SERVICE") or "job_runner",
        "metadata_json": json.dumps(_args_metadata(args), sort_keys=True),
    }
    table_id = _table_id(client.project, args.dataset, JOB_RUNS_TABLE)
    if hasattr(client, "load_table_from_json"):
        job_config = bigquery.LoadJobConfig(write_disposition=bigquery.WriteDisposition.WRITE_APPEND)
        job = client.load_table_from_json([row], table_id, job_config=job_config)
        job.result()
        errors = getattr(job, "errors", None)
        if errors:
            raise RuntimeError(f"Failed to load job run {job_run_id}: {errors}")
        return

    errors = client.insert_rows_json(table_id, [row])
    if errors:
        raise RuntimeError(f"Failed to insert job run {job_run_id}: {errors}")


def finish_job_run(
    client: Any,
    args: argparse.Namespace,
    job_run_id: str,
    started_at: datetime,
    finished_at: datetime,
    *,
    status: str,
    result: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> None:
    result = result or {}
    sql = f"""
    UPDATE `{_table_id(client.project, args.dataset, JOB_RUNS_TABLE)}`
    SET
        status = @status,
        finished_at = @finished_at,
        duration_seconds = @duration_seconds,
        row_count = @row_count,
        bytes_processed = @bytes_processed,
        model_run_id = COALESCE(@model_run_id, model_run_id),
        feature_config_version_id = @feature_config_version_id,
        source_freshness_snapshot_id = @source_freshness_snapshot_id,
        error_message = @error_message,
        metadata_json = @metadata_json
    WHERE job_run_id = @job_run_id
    """
    client.query(sql, job_config=bigquery.QueryJobConfig(query_parameters=[
        bigquery.ScalarQueryParameter("job_run_id", "STRING", job_run_id),
        bigquery.ScalarQueryParameter("status", "STRING", status),
        bigquery.ScalarQueryParameter("finished_at", "TIMESTAMP", _format_timestamp(finished_at)),
        bigquery.ScalarQueryParameter("duration_seconds", "FLOAT64", (finished_at - started_at).total_seconds()),
        bigquery.ScalarQueryParameter("row_count", "INT64", _optional_int(result.get("row_count"))),
        bigquery.ScalarQueryParameter("bytes_processed", "INT64", _optional_int(result.get("bytes_processed"))),
        bigquery.ScalarQueryParameter("model_run_id", "STRING", result.get("model_run_id") or args.model_run_id),
        bigquery.ScalarQueryParameter("feature_config_version_id", "STRING", result.get("feature_config_version_id")),
        bigquery.ScalarQueryParameter("source_freshness_snapshot_id", "STRING", result.get("source_freshness_snapshot_id")),
        bigquery.ScalarQueryParameter("error_message", "STRING", error_message),
        bigquery.ScalarQueryParameter("metadata_json", "STRING", json.dumps(result, sort_keys=True, default=str)),
    ])).result()


def dispatch_ingest_nflverse(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    if args.dry_run:
        return {"row_count": 0, "dry_run": True, "skipped": "src.pipeline has no dry-run mode"}
    from src.pipeline import run_pipeline, setup_logging

    setup_logging()
    seasons = [args.season] if args.season else [_current_season()]
    run_pipeline(seasons=seasons, write_disposition=args.write_disposition, dataset_name=args.dataset)
    return {"row_count": 0, "seasons": seasons}


def dispatch_ingest_sleeper_news(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    if args.dry_run:
        return {"row_count": 0, "dry_run": True, "skipped": "Sleeper news ingest has no dry-run mode"}
    from src.ingest_news import load_realtime_news

    load_realtime_news()
    return {"row_count": 0}


def dispatch_ingest_sleeper_league(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    if args.dry_run:
        _require(args.league_id, "--league-id is required")
        return {"row_count": 0, "dry_run": True, "league_id": args.league_id}
    _require(args.league_id, "--league-id is required")
    _require(args.week, "--week is required")
    from src.ingest_sleeper_league import ingest_sleeper_league

    ingest_sleeper_league(
        args.league_id,
        args.week,
        roster_id=args.roster_id,
        username=args.username,
        display_name=args.display_name,
        team_name=args.team_name,
        dataset_name=args.dataset,
    )
    return {"row_count": 0, "league_id": args.league_id}


def dispatch_ingest_context_events(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    if args.dry_run:
        return {"row_count": 0, "dry_run": True, "csv": args.csv}
    from src.ingest_context_events import load_context_events

    table = load_context_events(args.csv or _default_context_csv(), dataset_name=args.dataset)
    return {"row_count": getattr(table, "num_rows", 0) if table is not None else 0}


def dispatch_ingest_market_values(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    if args.dry_run:
        return {"row_count": 0, "dry_run": True, "league_type": args.league_type}
    from src.fetch_market_values import fetch_fantasycalc_values, upload_to_bigquery

    data = fetch_fantasycalc_values(is_dynasty=args.league_type != "redraft")
    if data:
        upload_to_bigquery(data, args.project, args.dataset)
    return {"row_count": len(data or [])}


def dispatch_ingest_college_stats(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    if args.dry_run:
        return {"row_count": 0, "dry_run": True, "skipped": "College ingest has no dry-run mode"}
    _require(args.season, "--season is required")
    _call_module_main("src.ingest_college_data", [
        "--season",
        str(args.season),
        "--dataset",
        args.dataset,
    ])
    return {"row_count": 0, "season": args.season}


def dispatch_materialize_analytics(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    from src.materialize import materialize_all
    from src.materialize_fantasy_points import materialize_fantasy_points
    from src.materialize_llm_packets import materialize_llm_packets
    from src.materialize_sleeper_watch import materialize_sleeper_watch
    from src.materialize_trade_assets import materialize_trade_assets

    jobs = materialize_all(client, dataset_id=args.dataset, dry_run=args.dry_run)
    row_count = 0
    row_count += len(materialize_fantasy_points(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        scoring_profile_ids=[args.scoring_profile],
        dry_run=args.dry_run,
        allow_large_query=True,
    ))
    row_count += materialize_trade_assets(
        client,
        dataset_id=args.dataset,
        scoring_profile_ids=[args.scoring_profile],
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        model_run_id=args.model_run_id,
        dry_run=args.dry_run,
    )
    row_count += materialize_sleeper_watch(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        league_id=args.league_id,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        model_run_id=args.model_run_id,
        dry_run=args.dry_run,
    )
    row_count += materialize_llm_packets(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        scoring_profile_ids=[args.scoring_profile],
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        model_run_id=args.model_run_id,
        dry_run=args.dry_run,
    )
    bytes_processed = sum(getattr(job, "total_bytes_processed", 0) or 0 for job in jobs)
    return {"row_count": row_count, "bytes_processed": bytes_processed}


def dispatch_generate_pigskin_rankings(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    from src.generate_pigskin_rankings import generate_rankings, parse_positions

    ranking_version, row_count = generate_rankings(
        dataset_id=args.dataset,
        project_id=args.project,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        positions=parse_positions(args.positions),
        position_limit=args.position_limit or args.limit,
        refresh_sleeper=args.refresh_sleeper,
        dry_run=args.dry_run,
    )
    return {"row_count": row_count, "ranking_version": ranking_version}


def dispatch_generate_evidence_packets(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    from src.materialize_llm_packets import materialize_llm_packets
    from src.segment_packets import (
        build_fraud_watch_packets,
        build_sleeper_breakout_packets,
        save_fraud_watch_packets,
        save_sleeper_breakout_packets,
    )

    fraud_packets = build_fraud_watch_packets(
        season=args.season,
        week=args.week,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        model_run_id=args.model_run_id,
        limit=args.limit,
        client=client,
        dataset_id=args.dataset,
    )
    breakout_packets = build_sleeper_breakout_packets(
        season=args.season,
        week=args.week,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        model_run_id=args.model_run_id,
        limit=args.limit,
        client=client,
        dataset_id=args.dataset,
    )
    if not args.dry_run:
        save_fraud_watch_packets(fraud_packets, client=client, dataset_id=args.dataset)
        save_sleeper_breakout_packets(breakout_packets, client=client, dataset_id=args.dataset)
    llm_rows = materialize_llm_packets(
        client,
        dataset_id=args.dataset,
        season=args.season,
        week=args.week,
        scoring_profile_ids=[args.scoring_profile],
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        model_run_id=args.model_run_id,
        dry_run=args.dry_run,
    )
    return {
        "row_count": len(fraud_packets) + len(breakout_packets) + llm_rows,
        "fraud_packets": len(fraud_packets),
        "sleeper_breakout_packets": len(breakout_packets),
        "llm_packet_rows": llm_rows,
    }


def dispatch_run_projections(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    from src.projection_engine import run_projection

    _require(args.season, "--season is required")
    _require(args.week, "--week is required")
    result = run_projection(
        horizon=args.horizon,
        season=args.season,
        week=args.week,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        dry_run=args.dry_run,
        limit=args.limit,
        client=client,
        dataset_id=args.dataset,
    )
    return {
        "row_count": result.get("projection_rows", 0),
        "model_run_id": result.get("model_run_id"),
        "source_freshness_snapshot_id": result.get("source_freshness_snapshot_id"),
        "feature_config_version_id": result.get("feature_config_version_id"),
        "projection_rows": result.get("projection_rows", 0),
        "ranking_rows": result.get("ranking_rows", 0),
    }


def dispatch_run_backtests(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    from src.backtesting import run_backtest

    season_start = args.season_start if args.season_start is not None else args.season
    season_end = args.season_end if args.season_end is not None else season_start
    _require(season_start, "--season-start or --season is required")
    _require(season_end, "--season-end or --season is required")
    result = run_backtest(
        client=client,
        dataset_id=args.dataset,
        model_run_id=args.model_run_id,
        horizon=args.horizon,
        season_start=season_start,
        season_end=season_end,
        week_start=args.week_start,
        week_end=args.week_end,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        backtest_name=args.backtest_name,
        market_source_id=args.market_source_id,
        dry_run=args.dry_run,
        allow_large_backtest=args.allow_large_backtest,
    )
    return {
        "row_count": result.get("player_week_rows", 0),
        "backtest_run_id": result.get("backtest_run_id"),
        "model_run_id": result.get("model_run_id"),
        "status": result.get("status"),
        "player_week_rows": result.get("player_week_rows", 0),
        "summary_rows": result.get("summary_rows", 0),
        "calibration_rows": result.get("calibration_rows", 0),
        "market_rows": result.get("market_rows", 0),
        "missing_data_flags": result.get("missing_data_flags", []),
    }


def dispatch_validate_warehouse(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    cmd = [
        sys.executable,
        "scripts/run_bigquery_validations.py",
        "--project",
        args.project,
        "--dataset",
        args.dataset,
    ]
    if args.dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--run")
    if args.pattern:
        cmd.extend(["--pattern", args.pattern])
    completed = subprocess.run(cmd, check=True)
    return {"row_count": 0, "returncode": completed.returncode, "pattern": args.pattern}


def dispatch_verify_external_context(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    _require(args.player, "--player is required")
    if args.dry_run:
        return {"row_count": 0, "dry_run": True, "player": args.player}
    from src.verify_player_context import verify_player_context

    stored_count = verify_player_context(
        args.player,
        query=args.query,
        team=args.team,
        season=args.season,
        max_results=args.max_results,
        dataset_name=args.dataset,
    )
    return {"row_count": stored_count, "player": args.player}


def dispatch_generate_content_briefs(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    del client
    _require(args.brief_type, "--brief-type is required")
    _require(args.season, "--season is required")
    if args.dry_run:
        return {
            "row_count": 0,
            "brief_type": args.brief_type,
            "season": args.season,
            "week": args.week,
            "dry_run": True,
            "skipped": "content brief generation preview only",
        }
    argv = [
        "--brief-type",
        args.brief_type,
        "--season",
        str(args.season),
        "--scoring-profile",
        args.scoring_profile,
        "--league-type",
        args.league_type,
        "--roster-format",
        args.roster_format,
    ]
    if args.week is not None:
        argv.extend(["--week", str(args.week)])
    if args.model_run_id:
        argv.extend(["--model-run-id", args.model_run_id])
    _call_module_main("src.content_briefs", argv)
    return {
        "row_count": 0,
        "brief_type": args.brief_type,
        "season": args.season,
        "week": args.week,
        "dry_run": args.dry_run,
    }


def dispatch_grade_claims(args: argparse.Namespace, client: Any) -> dict[str, Any]:
    from src.claim_grading import run_claim_grading

    result = run_claim_grading(
        claim_id=args.claim_id,
        season=args.season,
        week=args.week,
        model_run_id=args.model_run_id,
        scoring_profile_id=args.scoring_profile,
        league_type_id=args.league_type,
        roster_format_id=args.roster_format,
        client=client,
        dataset_id=args.dataset,
        dry_run=args.dry_run,
    )
    return {
        "row_count": result.get("grade_count", 0),
        "claim_grading_run_id": (result.get("run") or {}).get("claim_grading_run_id"),
        "grade_count": result.get("grade_count", 0),
        "scorecard_count": result.get("scorecard_count", 0),
        "dry_run": args.dry_run,
    }


JOB_DISPATCHERS: dict[str, Callable[[argparse.Namespace, Any], dict[str, Any] | None]] = {
    "ingest-nflverse": dispatch_ingest_nflverse,
    "ingest-sleeper-news": dispatch_ingest_sleeper_news,
    "ingest-sleeper-league": dispatch_ingest_sleeper_league,
    "ingest-context-events": dispatch_ingest_context_events,
    "ingest-market-values": dispatch_ingest_market_values,
    "ingest-college-stats": dispatch_ingest_college_stats,
    "materialize-analytics": dispatch_materialize_analytics,
    "generate-pigskin-rankings": dispatch_generate_pigskin_rankings,
    "generate-evidence-packets": dispatch_generate_evidence_packets,
    "run-projections": dispatch_run_projections,
    "run-backtests": dispatch_run_backtests,
    "validate-warehouse": dispatch_validate_warehouse,
    "verify-external-context": dispatch_verify_external_context,
    "generate-content-briefs": dispatch_generate_content_briefs,
    "grade-claims": dispatch_grade_claims,
}


def _call_module_main(module_name: str, argv: list[str]) -> None:
    old_argv = sys.argv[:]
    try:
        sys.argv = [module_name, *argv]
        module = __import__(module_name, fromlist=["main"])
        try:
            module.main()
        except SystemExit as exc:
            if exc.code not in (0, None):
                raise RuntimeError(f"{module_name} exited with code {exc.code}") from exc
    finally:
        sys.argv = old_argv


def _set_runtime_env(args: argparse.Namespace) -> None:
    os.environ["BQ_PROJECT"] = args.project
    os.environ["BQ_DATASET"] = args.dataset


def _args_metadata(args: argparse.Namespace) -> dict[str, Any]:
    return {
        key: value
        for key, value in vars(args).items()
        if key not in {"query"}
    }


def _log_status(event: str, **payload: Any) -> None:
    logger.info(json.dumps({"event": event, **payload}, sort_keys=True, default=str))


def _table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    _validate_identifier(dataset_id, "dataset_id")
    _validate_identifier(table_name, "table_name")
    return f"{project_id}.{dataset_id}.{table_name}"


def _validate_identifier(value: str, label: str) -> None:
    if not value.replace("_", "a").isalnum() or "." in value:
        raise ValueError(f"Invalid BigQuery {label}: {value!r}")


def _require(value: Any, message: str) -> None:
    if value in (None, ""):
        raise ValueError(message)


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _generate_job_run_id(job_name: str) -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{job_name}-{stamp}-{uuid.uuid4().hex[:8]}"


def _current_season() -> int:
    return datetime.now(timezone.utc).year


def _default_context_csv() -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "context_events.csv")


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))
    try:
        result = run_job(args)
    except BaseException as exc:
        if isinstance(exc, KeyboardInterrupt):
            raise
        logger.exception("Cloud Run job failed: %s", exc)
        raise SystemExit(1) from exc
    print(json.dumps(result, sort_keys=True, default=str))


if __name__ == "__main__":
    main()
