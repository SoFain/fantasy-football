"""Feature-flagged Cloud Run Jobs helpers for Streamlit Data Ops."""

from __future__ import annotations

import json
import os
import re
import shutil
import shlex
import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

USE_CLOUD_RUN_JOBS_FOR_DATA_OPS = "USE_CLOUD_RUN_JOBS_FOR_DATA_OPS"
CLOUD_RUN_JOBS_ENABLED = "CLOUD_RUN_JOBS_ENABLED"
DATA_OPS_ALLOW_JOB_TRIGGER = "DATA_OPS_ALLOW_JOB_TRIGGER"
DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_REGION = "us-central1"
JOB_RUNS_TABLE = "cloud_run_job_runs"
TRUE_VALUES = {"1", "true", "yes", "y", "on"}
SENSITIVE_KEY_RE = re.compile(r"(api[_-]?key|token|secret|password|credential)", re.IGNORECASE)


@dataclass(frozen=True)
class JobArgSpec:
    value_type: str = "string"
    required: bool = False
    choices: tuple[str, ...] = ()


@dataclass(frozen=True)
class DataOpsJob:
    job_name: str
    description: str
    arg_specs: Mapping[str, JobArgSpec]

    @property
    def required_args(self) -> tuple[str, ...]:
        return tuple(name for name, spec in self.arg_specs.items() if spec.required)

    @property
    def allowed_args(self) -> tuple[str, ...]:
        return tuple(self.arg_specs)


COMMON_CONTEXT_ARGS = {
    "scoring-profile": JobArgSpec(),
    "league-type": JobArgSpec(choices=("redraft", "dynasty")),
    "roster-format": JobArgSpec(choices=("one_qb", "superflex")),
    "model-run-id": JobArgSpec(),
}

CONFIGURED_JOBS: dict[str, DataOpsJob] = {
    "ingest-nflverse": DataOpsJob(
        "ingest-nflverse",
        "Run nflverse ingestion through the Cloud Run job runner.",
        {
            "season": JobArgSpec("int"),
            "write-disposition": JobArgSpec(choices=("WRITE_TRUNCATE", "WRITE_APPEND")),
        },
    ),
    "ingest-sleeper-news": DataOpsJob(
        "ingest-sleeper-news",
        "Refresh Sleeper player status, news, and trending context.",
        {},
    ),
    "ingest-sleeper-league": DataOpsJob(
        "ingest-sleeper-league",
        "Load one Sleeper league and viewer team snapshot.",
        {
            "league-id": JobArgSpec(required=True),
            "week": JobArgSpec("int", required=True),
            "roster-id": JobArgSpec(),
            "username": JobArgSpec(),
            "display-name": JobArgSpec(),
            "team-name": JobArgSpec(),
        },
    ),
    "ingest-market-values": DataOpsJob(
        "ingest-market-values",
        "Refresh market value baselines.",
        {"league-type": JobArgSpec(choices=("redraft", "dynasty"))},
    ),
    "materialize-analytics": DataOpsJob(
        "materialize-analytics",
        "Refresh analytics, trade, sleeper watch, and LLM packet marts.",
        {
            "season": JobArgSpec("int"),
            "week": JobArgSpec("int"),
            **COMMON_CONTEXT_ARGS,
        },
    ),
    "generate-pigskin-rankings": DataOpsJob(
        "generate-pigskin-rankings",
        "Generate Pigskin rankings from curated evidence.",
        {
            "positions": JobArgSpec(),
            "position-limit": JobArgSpec("int"),
            "limit": JobArgSpec("int"),
            "refresh-sleeper": JobArgSpec("bool"),
            **COMMON_CONTEXT_ARGS,
        },
    ),
    "generate-evidence-packets": DataOpsJob(
        "generate-evidence-packets",
        "Build segment evidence packets for show prep.",
        {
            "season": JobArgSpec("int"),
            "week": JobArgSpec("int"),
            "limit": JobArgSpec("int"),
            **COMMON_CONTEXT_ARGS,
        },
    ),
    "run-projections": DataOpsJob(
        "run-projections",
        "Run projection and ranking outputs.",
        {
            "season": JobArgSpec("int", required=True),
            "week": JobArgSpec("int", required=True),
            "horizon": JobArgSpec(choices=("weekly", "ros", "dynasty")),
            "limit": JobArgSpec("int"),
            **COMMON_CONTEXT_ARGS,
        },
    ),
    "run-backtests": DataOpsJob(
        "run-backtests",
        "Run projection backtests across a bounded season and week window.",
        {
            "season-start": JobArgSpec("int", required=True),
            "season-end": JobArgSpec("int", required=True),
            "week-start": JobArgSpec("int"),
            "week-end": JobArgSpec("int"),
            "horizon": JobArgSpec(choices=("weekly", "ros", "dynasty")),
            "market-source-id": JobArgSpec(),
            "backtest-name": JobArgSpec(),
            "allow-large-backtest": JobArgSpec("bool"),
            **COMMON_CONTEXT_ARGS,
        },
    ),
    "validate-warehouse": DataOpsJob(
        "validate-warehouse",
        "Run BigQuery validation SQL through the job runner.",
        {
            "pattern": JobArgSpec(),
            "fail-fast": JobArgSpec("bool"),
        },
    ),
    "verify-external-context": DataOpsJob(
        "verify-external-context",
        "Run one bounded external context verification.",
        {
            "player": JobArgSpec(required=True),
            "query": JobArgSpec(),
            "team": JobArgSpec(),
            "season": JobArgSpec("int"),
            "max-results": JobArgSpec("int"),
        },
    ),
}

DATA_OPS_ACTION_TO_JOB = {
    "statistics_ingestion": "ingest-nflverse",
    "realtime_news": "ingest-sleeper-news",
    "sleeper_viewer_team": "ingest-sleeper-league",
    "market_values": "ingest-market-values",
    "pigskin_rankings": "generate-pigskin-rankings",
    "validation_sweep": "validate-warehouse",
    "player_context_verification": "verify-external-context",
}


class _FallbackScalarQueryParameter:
    def __init__(self, name: str, field_type: str, value: Any):
        self.name = name
        self.field_type = field_type
        self.value = value


class _FallbackQueryJobConfig:
    def __init__(self, query_parameters: list[Any] | None = None):
        self.query_parameters = query_parameters or []


class _FallbackBigQuery:
    ScalarQueryParameter = _FallbackScalarQueryParameter
    QueryJobConfig = _FallbackQueryJobConfig

    class Client:
        def __init__(self, *args: Any, **kwargs: Any):
            raise ImportError("google-cloud-bigquery is required for live Cloud Run Job status reads.")


def get_bigquery_module() -> Any:
    try:
        from google.cloud import bigquery
        return bigquery
    except ImportError:
        return _FallbackBigQuery


def list_configured_jobs() -> list[dict[str, Any]]:
    """Return Cloud Run Jobs exposed to Data Ops."""

    return [
        {
            "job_name": job.job_name,
            "cloud_run_job_name": cloud_run_job_name(job.job_name),
            "description": job.description,
            "required_args": list(job.required_args),
            "allowed_args": list(job.allowed_args),
        }
        for job in CONFIGURED_JOBS.values()
    ]


def map_data_ops_action_to_job(action_name: str) -> str | None:
    return DATA_OPS_ACTION_TO_JOB.get(action_name)


def cloud_run_jobs_feature_enabled(environ: Mapping[str, str] | None = None) -> bool:
    env = environ if environ is not None else os.environ
    return _truthy(env.get(USE_CLOUD_RUN_JOBS_FOR_DATA_OPS)) and _truthy(env.get(CLOUD_RUN_JOBS_ENABLED, "true"))


def data_ops_job_trigger_allowed(environ: Mapping[str, str] | None = None) -> bool:
    env = environ if environ is not None else os.environ
    return _truthy(env.get(DATA_OPS_ALLOW_JOB_TRIGGER))


def should_use_cloud_run_jobs_for_data_ops(environ: Mapping[str, str] | None = None) -> bool:
    return cloud_run_jobs_feature_enabled(environ)


def build_job_overrides(
    job_name: str,
    args: Mapping[str, Any] | None,
    env_overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate Data Ops job args and build Cloud Run container overrides."""

    normalized_args = validate_job_args(job_name, args or {})
    safe_env = validate_env_overrides(env_overrides or {})
    container_args = ["--job-name", job_name]
    for key, value in normalized_args.items():
        if value in (None, ""):
            continue
        if isinstance(value, bool):
            if value:
                container_args.append(f"--{key}")
            continue
        container_args.extend([f"--{key}", str(value)])

    return {
        "job_name": job_name,
        "cloud_run_job_name": cloud_run_job_name(job_name),
        "container_args": container_args,
        "env_overrides": dict(safe_env),
    }


def trigger_cloud_run_job(
    job_name: str,
    args: Mapping[str, Any] | None,
    env_overrides: Mapping[str, Any] | None = None,
    dry_run: bool = False,
    *,
    client: Any | None = None,
    allow_trigger: bool | None = None,
) -> dict[str, Any]:
    """Preview or explicitly trigger a Cloud Run Job through gcloud."""

    overrides = build_job_overrides(job_name, args or {}, env_overrides)
    command = build_gcloud_execute_command(overrides)
    if dry_run:
        return {
            "status": "dry_run",
            "job_name": job_name,
            "command": command,
            "command_preview": command_to_string(command),
            "overrides": redact_payload(overrides),
        }

    allowed = data_ops_job_trigger_allowed() if allow_trigger is None else allow_trigger
    if not cloud_run_jobs_feature_enabled() or not allowed:
        raise PermissionError(
            "Cloud Run Job triggering requires USE_CLOUD_RUN_JOBS_FOR_DATA_OPS=true "
            "and DATA_OPS_ALLOW_JOB_TRIGGER=true."
        )
    if shutil.which("gcloud") is None:
        raise RuntimeError("gcloud is required for live Cloud Run Job triggers in this deployment path.")

    bq = get_bigquery_module()
    client = client or bq.Client(project=get_cloud_run_project())
    job_run_id = record_cloud_run_job_trigger(
        job_name,
        command,
        args or {},
        status="trigger_requested",
        client=client,
    )
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    execution_name = parse_execution_name(completed.stdout)
    final_status = "triggered" if completed.returncode == 0 else "trigger_failed"
    error_message = completed.stderr.strip() or None
    update_cloud_run_job_trigger(
        job_run_id,
        final_status,
        execution_name=execution_name,
        error_message=error_message,
        client=client,
    )
    if completed.returncode != 0:
        raise RuntimeError(error_message or f"gcloud exited with code {completed.returncode}")
    return {
        "status": final_status,
        "job_run_id": job_run_id,
        "job_name": job_name,
        "execution_name": execution_name,
        "command_preview": command_to_string(command),
        "stdout": completed.stdout.strip(),
    }


def get_cloud_run_job_execution_status(
    execution_name: str,
    *,
    client: Any | None = None,
    limit: int = 1,
) -> list[dict[str, Any]]:
    if not execution_name:
        raise ValueError("execution_name is required")
    bq = get_bigquery_module()
    client = client or bq.Client(project=get_cloud_run_project())
    dataset_id = get_bigquery_dataset()
    table_id = bigquery_table_id(client.project, dataset_id, JOB_RUNS_TABLE)
    sql = f"""
    SELECT
        job_run_id,
        job_name,
        cloud_run_job_name,
        cloud_run_execution_name,
        status,
        started_at,
        finished_at,
        error_message,
        metadata_json
    FROM `{table_id}`
    WHERE cloud_run_execution_name = @execution_name
    ORDER BY started_at DESC
    LIMIT @limit
    """
    query_job = client.query(
        sql,
        job_config=bq.QueryJobConfig(query_parameters=[
            bq.ScalarQueryParameter("execution_name", "STRING", execution_name),
            bq.ScalarQueryParameter("limit", "INT64", limit),
        ]),
    )
    return [dict(row) for row in query_job.result()]


def record_cloud_run_job_trigger(
    job_name: str,
    command: list[str],
    args: Mapping[str, Any],
    *,
    execution_name: str | None = None,
    status: str = "trigger_requested",
    client: Any | None = None,
    error_message: str | None = None,
) -> str:
    if job_name not in CONFIGURED_JOBS:
        raise ValueError(f"Unknown Cloud Run job: {job_name}")
    bq = get_bigquery_module()
    client = client or bq.Client(project=get_cloud_run_project())
    dataset_id = get_bigquery_dataset()
    normalized_args = validate_job_args(job_name, args)
    job_run_id = f"streamlit-{job_name}-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    row = {
        "job_run_id": job_run_id,
        "job_name": job_name,
        "job_type": job_name.split("-", 1)[0],
        "cloud_run_job_name": cloud_run_job_name(job_name),
        "cloud_run_execution_name": execution_name,
        "model_run_id": normalized_args.get("model-run-id"),
        "feature_config_version_id": None,
        "scoring_profile_id": normalized_args.get("scoring-profile"),
        "league_type_id": normalized_args.get("league-type"),
        "roster_format_id": normalized_args.get("roster-format"),
        "project_id": get_cloud_run_project(),
        "dataset_id": dataset_id,
        "season": _optional_int(normalized_args.get("season") or normalized_args.get("season-start")),
        "week": _optional_int(normalized_args.get("week") or normalized_args.get("week-start")),
        "league_id": normalized_args.get("league-id"),
        "status": status,
        "started_at": now,
        "finished_at": now if status.endswith("failed") else None,
        "duration_seconds": None,
        "row_count": None,
        "bytes_processed": None,
        "source_freshness_snapshot_id": None,
        "error_message": error_message,
        "log_url": None,
        "created_by": "streamlit_data_ops",
        "metadata_json": json.dumps({
            "args": redact_payload(normalized_args),
            "command": command_to_string(command),
            "source": "streamlit_data_ops",
        }, sort_keys=True),
    }
    errors = client.insert_rows_json(bigquery_table_id(client.project, dataset_id, JOB_RUNS_TABLE), [row])
    if errors:
        raise RuntimeError(f"Failed to record Cloud Run Job trigger: {errors}")
    return job_run_id


def update_cloud_run_job_trigger(
    job_run_id: str,
    status: str,
    *,
    execution_name: str | None = None,
    error_message: str | None = None,
    client: Any | None = None,
) -> None:
    bq = get_bigquery_module()
    client = client or bq.Client(project=get_cloud_run_project())
    dataset_id = get_bigquery_dataset()
    table_id = bigquery_table_id(client.project, dataset_id, JOB_RUNS_TABLE)
    sql = f"""
    UPDATE `{table_id}`
    SET
        status = @status,
        cloud_run_execution_name = COALESCE(@execution_name, cloud_run_execution_name),
        finished_at = IF(@status = 'trigger_failed', CURRENT_TIMESTAMP(), finished_at),
        error_message = @error_message
    WHERE job_run_id = @job_run_id
    """
    client.query(
        sql,
        job_config=bq.QueryJobConfig(query_parameters=[
            bq.ScalarQueryParameter("job_run_id", "STRING", job_run_id),
            bq.ScalarQueryParameter("status", "STRING", status),
            bq.ScalarQueryParameter("execution_name", "STRING", execution_name),
            bq.ScalarQueryParameter("error_message", "STRING", error_message),
        ]),
    ).result()


def get_recent_cloud_run_job_runs(limit: int = 50, *, client: Any | None = None) -> list[dict[str, Any]]:
    limit = max(1, min(int(limit), 200))
    bq = get_bigquery_module()
    client = client or bq.Client(project=get_cloud_run_project())
    dataset_id = get_bigquery_dataset()
    table_id = bigquery_table_id(client.project, dataset_id, JOB_RUNS_TABLE)
    sql = f"""
    SELECT
        job_run_id,
        job_name,
        cloud_run_job_name,
        cloud_run_execution_name,
        status,
        started_at,
        finished_at,
        season,
        week,
        error_message
    FROM `{table_id}`
    ORDER BY started_at DESC
    LIMIT @limit
    """
    query_job = client.query(
        sql,
        job_config=bq.QueryJobConfig(query_parameters=[
            bq.ScalarQueryParameter("limit", "INT64", limit),
        ]),
    )
    return [dict(row) for row in query_job.result()]


def validate_job_args(job_name: str, args: Mapping[str, Any]) -> dict[str, Any]:
    job = CONFIGURED_JOBS.get(job_name)
    if job is None:
        raise ValueError(f"Unknown Cloud Run job: {job_name}")
    normalized: dict[str, Any] = {}
    for raw_key, raw_value in args.items():
        key = str(raw_key).strip().replace("_", "-")
        if key not in job.arg_specs:
            raise ValueError(f"Argument {raw_key!r} is not allowed for {job_name}")
        spec = job.arg_specs[key]
        normalized[key] = coerce_arg_value(key, raw_value, spec)

    for key, spec in job.arg_specs.items():
        if spec.required and normalized.get(key) in (None, "", False):
            raise ValueError(f"Argument {key!r} is required for {job_name}")
    return normalized


def validate_env_overrides(env_overrides: Mapping[str, Any]) -> dict[str, str]:
    safe_env: dict[str, str] = {}
    for raw_key, raw_value in env_overrides.items():
        key = str(raw_key).strip()
        if not key:
            continue
        if SENSITIVE_KEY_RE.search(key):
            raise ValueError(f"Refusing to pass sensitive environment override: {key}")
        if not key.replace("_", "A").isalnum():
            raise ValueError(f"Invalid environment variable name: {key!r}")
        safe_env[key] = str(raw_value)
    return safe_env


def coerce_arg_value(key: str, value: Any, spec: JobArgSpec) -> Any:
    if value in (None, ""):
        return None
    if spec.value_type == "int":
        try:
            value = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Argument {key!r} must be an integer") from exc
    elif spec.value_type == "bool":
        if isinstance(value, bool):
            pass
        else:
            value = _truthy(str(value))
    else:
        value = str(value)
    if spec.choices and value not in spec.choices:
        raise ValueError(f"Argument {key!r} must be one of {', '.join(spec.choices)}")
    return value


def build_gcloud_execute_command(overrides: Mapping[str, Any]) -> list[str]:
    command = [
        "gcloud",
        "run",
        "jobs",
        "execute",
        str(overrides["cloud_run_job_name"]),
        "--region",
        get_cloud_run_region(),
        "--project",
        get_cloud_run_project(),
        "--format=json",
    ]
    container_args = [str(value) for value in overrides["container_args"]]
    if container_args:
        command.extend(["--args", ",".join(_escape_gcloud_arg(value) for value in container_args)])
    env_overrides = overrides.get("env_overrides") or {}
    if env_overrides:
        command.extend([
            "--update-env-vars",
            ",".join(f"{key}={value}" for key, value in sorted(env_overrides.items())),
        ])
    return command


def command_to_string(command: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in command)


def redact_payload(payload: Any) -> Any:
    if isinstance(payload, Mapping):
        redacted: dict[str, Any] = {}
        for key, value in payload.items():
            redacted[str(key)] = "[REDACTED]" if SENSITIVE_KEY_RE.search(str(key)) else redact_payload(value)
        return redacted
    if isinstance(payload, list):
        return [redact_payload(value) for value in payload]
    return payload


def parse_execution_name(stdout: str) -> str | None:
    if not stdout.strip():
        return None
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None
    metadata = payload.get("metadata", {}) if isinstance(payload, dict) else {}
    name = payload.get("name") or metadata.get("name")
    return str(name) if name else None


def cloud_run_job_name(job_name: str) -> str:
    prefix = os.environ.get("CLOUD_RUN_JOB_PREFIX", "")
    return f"{prefix}{job_name}"


def get_cloud_run_project() -> str:
    return (
        os.environ.get("CLOUD_RUN_PROJECT")
        or os.environ.get("BQ_PROJECT")
        or os.environ.get("GCP_PROJECT")
        or os.environ.get("GOOGLE_CLOUD_PROJECT")
        or _get_repo_default_project()
    )


def get_cloud_run_region() -> str:
    return os.environ.get("CLOUD_RUN_REGION") or DEFAULT_REGION


def get_bigquery_dataset() -> str:
    return (
        os.environ.get("BQ_DATASET")
        or os.environ.get("BIGQUERY_DATASET")
        or os.environ.get("DATASET_NAME")
        or DEFAULT_DATASET
    )


def bigquery_table_id(project_id: str, dataset_id: str, table_name: str) -> str:
    _validate_bigquery_identifier(dataset_id, "dataset_id")
    _validate_bigquery_identifier(table_name, "table_name")
    return f"{project_id}.{dataset_id}.{table_name}"


def _validate_bigquery_identifier(value: str, label: str) -> None:
    if not value.replace("_", "A").isalnum() or "." in value:
        raise ValueError(f"Invalid BigQuery {label}: {value!r}")


def _truthy(value: Any) -> bool:
    return str(value or "false").strip().lower() in TRUE_VALUES


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _escape_gcloud_arg(value: str) -> str:
    return value.replace("\\", "\\\\").replace(",", "\\,")


def _get_repo_default_project() -> str:
    try:
        from src.load import get_bigquery_project
        return get_bigquery_project()
    except Exception:
        return "fantasy-football-498121"
