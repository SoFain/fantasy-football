"""Export canonical rankings and optionally publish immutable public JSON snapshots."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

from google.api_core.exceptions import NotFound, PreconditionFailed
from google.cloud import bigquery, storage
from google.oauth2.credentials import Credentials

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.public_rankings_feed import (  # noqa: E402
    SCHEMA_VERSION,
    SCORING_PROFILES,
    build_profile_payload,
    json_bytes,
    sha256_hex,
)


DEFAULT_PROJECT = "fantasy-football-498121"
DEFAULT_DATASET = "fantasy_football_brain"
DEFAULT_METRICS_DATASET = "fantasy_football_advanced_metrics"
DEFAULT_BUCKET = "fantasy-football-498121-public-rankings"
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"
MANIFEST_CACHE_CONTROL = "public, max-age=300, must-revalidate"
IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9_-]+$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--dataset", default=DEFAULT_DATASET)
    parser.add_argument("--metrics-dataset", default=DEFAULT_METRICS_DATASET)
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument("--profile", action="append", choices=SCORING_PROFILES)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "output" / "public-rankings")
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Upload immutable snapshots and update the current manifest. Without this flag, only local artifacts are written.",
    )
    parser.add_argument(
        "--gcloud-auth",
        action="store_true",
        help="Use the active gcloud user access token for Cloud Storage instead of local ADC.",
    )
    parser.add_argument(
        "--dataset-entry",
        action="append",
        type=Path,
        default=None,
        help=(
            "Path to a dataset manifest-entry JSON (e.g. the coaching staff entry emitted by "
            "the coaching-staff-feed job). Merged into the manifest under 'datasets'. The "
            "referenced immutable object must already exist in the bucket; this publisher "
            "remains the single writer of v1/manifest.json."
        ),
    )
    return parser.parse_args()


def validate_identifier(value: str, label: str) -> None:
    if not IDENTIFIER_RE.fullmatch(value):
        raise ValueError(f"Invalid {label}: {value!r}")


def fetch_overall_rows(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    metrics_dataset_id: str,
    scoring_profile_id: str,
) -> list[dict[str, Any]]:
    sql = f"""
    SELECT
      board_version,
      generated_at,
      overall_rank,
      player_id,
      board.player_name,
      IF(safety.sleeper_player_id IS NULL, board.current_team, safety.team) AS current_team,
      board.position,
      position_rank,
      projected_ppg,
      replacement_rank,
      replacement_ppg,
      vorp,
      availability_multiplier,
      onesie_multiplier,
      adjusted_vorp,
      position_source_version,
      position_rank_source,
      risk_flags,
      qb_backtest_proxy_disclosed,
      COALESCE(safety.current_board_rank_eligible, FALSE) AS current_board_rank_eligible
    FROM `{project_id}.{dataset_id}.unified_draft_rankings_current` AS board
    LEFT JOIN `{project_id}.{metrics_dataset_id}.v_ranking_post_formula_safety` AS safety
      ON safety.position = board.position
      AND (
        safety.gsis_id = board.player_id
        OR safety.sleeper_player_id = board.player_id
        OR CONCAT('sleeper:', safety.sleeper_player_id) = board.player_id
      )
    WHERE board.scoring_profile_id = @scoring_profile_id
    ORDER BY overall_rank
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id)
        ]
    )
    return [dict(row) for row in client.query(sql, job_config=config).result()]


def fetch_positional_rows(
    client: bigquery.Client,
    project_id: str,
    dataset_id: str,
    metrics_dataset_id: str,
    scoring_profile_id: str,
) -> list[dict[str, Any]]:
    sql = f"""
    SELECT
      rankings.ranking_version,
      rankings.generated_at,
      rankings.position,
      rankings.rank,
      tier,
      rankings.player_id,
      rankings.player_name,
      IF(safety.sleeper_player_id IS NULL, rankings.current_team, safety.team) AS current_team,
      roster_status,
      ranking_score,
      confidence_score,
      pigskin_verdict,
      rank_rationale,
      gng_context.context AS ranking_context,
      risk_flags,
      what_would_change_mind,
      model_name,
      prompt_version,
      rankings.ranking_eligibility,
      rankings.rank_source,
      llm_adjustment_code,
      llm_adjustment_detail,
      llm_rank_delta,
      COALESCE(safety.current_board_rank_eligible, FALSE) AS current_board_rank_eligible
    FROM `{project_id}.{dataset_id}.analytics_pigskin_rankings` AS rankings
    LEFT JOIN `{project_id}.{metrics_dataset_id}.v_ranking_post_formula_safety` AS safety
      ON safety.position = rankings.position
      AND (
        safety.gsis_id = rankings.player_id
        OR safety.sleeper_player_id = rankings.player_id
        OR CONCAT('sleeper:', safety.sleeper_player_id) = rankings.player_id
      )
    LEFT JOIN `{project_id}.{metrics_dataset_id}.gng_2026_rank_context` AS gng_context
      ON @scoring_profile_id = 'gng_keeper'
      AND gng_context.scoring_profile_id = rankings.scoring_profile_id
      AND gng_context.position = rankings.position
      AND gng_context.player_id = rankings.player_id
      AND gng_context.rank = rankings.rank
      AND gng_context.formula_id = rankings.model_name
    WHERE rankings.is_active
      AND rankings.scoring_profile_id = @scoring_profile_id
      AND rankings.position IN ('QB', 'RB', 'WR', 'TE')
    ORDER BY position, rank
    """
    config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("scoring_profile_id", "STRING", scoring_profile_id)
        ]
    )
    return [dict(row) for row in client.query(sql, job_config=config).result()]


def public_url(bucket_name: str, object_name: str) -> str:
    return f"https://storage.googleapis.com/{bucket_name}/{quote(object_name, safe='/')}"


def fetch_current_datasets(bucket: storage.Bucket | None, bucket_name: str) -> dict[str, dict[str, Any]]:
    """Carry forward the datasets listed in the current live manifest.

    The manifest is rebuilt in full on every publish. Without carry-forward, a
    scheduled publish that passes no --dataset-entry would silently drop
    previously published datasets (coaching_staff). Entries supplied via
    --dataset-entry override carried ones of the same name.
    """
    raw: bytes | None = None
    if bucket is not None:
        try:
            raw = bucket.blob("v1/manifest.json").download_as_bytes()
        except NotFound:
            return {}
    else:
        from urllib.request import Request, urlopen

        try:
            request = Request(
                public_url(bucket_name, "v1/manifest.json"),
                headers={"User-Agent": "publish-public-rankings"},
            )
            with urlopen(request, timeout=30) as response:
                raw = response.read()
        except Exception:
            return {}
    try:
        manifest = json.loads(raw)
    except (TypeError, ValueError):
        return {}
    datasets = manifest.get("datasets")
    if not isinstance(datasets, dict):
        return {}
    carried: dict[str, dict[str, Any]] = {}
    for name, entry in datasets.items():
        if (
            isinstance(name, str)
            and IDENTIFIER_RE.fullmatch(name)
            and isinstance(entry, dict)
            and all(key in entry for key in ("object", "url", "sha256", "bytes"))
        ):
            carried[name] = entry
    return carried


def active_gcloud_credentials() -> Credentials:
    executable = shutil.which("gcloud") or shutil.which("gcloud.cmd")
    if not executable:
        raise RuntimeError("gcloud executable was not found on PATH")
    completed = subprocess.run(
        [executable, "auth", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
    )
    token = completed.stdout.strip()
    if not token:
        raise RuntimeError("gcloud returned an empty access token")
    return Credentials(token=token)


def upload_immutable(bucket: storage.Bucket, object_name: str, content: bytes) -> None:
    blob = bucket.blob(object_name)
    digest = sha256_hex(content)
    blob.cache_control = IMMUTABLE_CACHE_CONTROL
    blob.content_type = "application/json; charset=utf-8"
    blob.metadata = {"sha256": digest, "immutable": "true"}
    try:
        blob.upload_from_string(
            content,
            content_type="application/json; charset=utf-8",
            if_generation_match=0,
        )
        return
    except PreconditionFailed:
        existing = bucket.blob(object_name)
        if existing.download_as_bytes() != content:
            raise RuntimeError(f"Immutable object collision at gs://{bucket.name}/{object_name}")


def update_current_manifest(bucket: storage.Bucket, content: bytes) -> None:
    object_name = "v1/manifest.json"
    blob = bucket.blob(object_name)
    generation = 0
    try:
        blob.reload()
        generation = int(blob.generation)
    except NotFound:
        pass
    blob.cache_control = MANIFEST_CACHE_CONTROL
    blob.content_type = "application/json; charset=utf-8"
    blob.metadata = {"sha256": sha256_hex(content), "mutable_pointer": "true"}
    blob.upload_from_string(
        content,
        content_type="application/json; charset=utf-8",
        if_generation_match=generation,
    )


def main() -> int:
    args = parse_args()
    validate_identifier(args.project, "project")
    validate_identifier(args.dataset, "dataset")
    validate_identifier(args.metrics_dataset, "metrics dataset")
    profiles = tuple(args.profile or SCORING_PROFILES)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    bigquery_client = bigquery.Client(project=args.project)
    storage_client = None
    if args.publish:
        credentials = active_gcloud_credentials() if args.gcloud_auth else None
        storage_client = storage.Client(project=args.project, credentials=credentials)
    bucket = storage_client.bucket(args.bucket) if storage_client else None
    if bucket is not None and not bucket.exists():
        raise RuntimeError(f"Publication bucket does not exist: gs://{args.bucket}")

    profile_entries: dict[str, dict[str, Any]] = {}
    for profile in profiles:
        payload = build_profile_payload(
            project_id=args.project,
            dataset_id=args.dataset,
            scoring_profile_id=profile,
            overall_rows=fetch_overall_rows(
                bigquery_client, args.project, args.dataset, args.metrics_dataset, profile
            ),
            positional_rows=fetch_positional_rows(
                bigquery_client, args.project, args.dataset, args.metrics_dataset, profile
            ),
        )
        content = json_bytes(payload)
        digest = sha256_hex(content)
        object_name = f"v1/boards/{profile}/sha256-{digest}.json"
        local_path = args.output_dir / f"{profile}.json"
        local_path.write_bytes(content)
        if bucket is not None:
            upload_immutable(bucket, object_name, content)
        profile_entries[profile] = {
            "board_version": payload["board_version"],
            "source_generated_at": payload["source_generated_at"],
            "object": object_name,
            "url": public_url(args.bucket, object_name),
            "sha256": digest,
            "bytes": len(content),
            "overall_count": payload["overall"]["count"],
            "position_counts": {
                position: board["count"] for position, board in payload["positions"].items()
            },
            "warnings": payload["warnings"],
        }

    dataset_entries: dict[str, dict[str, Any]] = fetch_current_datasets(bucket, args.bucket)
    for entry_path in args.dataset_entry or []:
        entry = json.loads(entry_path.read_text(encoding="utf-8"))
        name = entry.get("dataset")
        if not isinstance(name, str) or not IDENTIFIER_RE.fullmatch(name):
            raise ValueError(f"Dataset entry {entry_path} has a missing or invalid 'dataset' id.")
        for required in ("object", "url", "sha256", "bytes", "source_generated_at"):
            if required not in entry:
                raise ValueError(f"Dataset entry {name!r} is missing {required!r}.")
        if bucket is not None and not bucket.blob(entry["object"]).exists():
            raise RuntimeError(
                f"Dataset {name!r} references gs://{args.bucket}/{entry['object']} "
                "which does not exist. Upload the immutable object before publishing the manifest."
            )
        dataset_entries[name] = entry

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "published_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "profiles": profile_entries,
    }
    if dataset_entries:
        # Site importers iterate manifest['profiles'] only, so this key is
        # additive and safe for existing consumers.
        manifest["datasets"] = dataset_entries
    manifest_content = json_bytes(manifest)
    manifest_digest = sha256_hex(manifest_content)
    immutable_manifest_name = f"v1/manifests/sha256-{manifest_digest}.json"
    (args.output_dir / "manifest.json").write_bytes(manifest_content)
    if bucket is not None:
        upload_immutable(bucket, immutable_manifest_name, manifest_content)
        update_current_manifest(bucket, manifest_content)

    result = {
        "published": bool(bucket),
        "bucket": args.bucket,
        "manifest": public_url(args.bucket, "v1/manifest.json") if bucket else None,
        "immutable_manifest": public_url(args.bucket, immutable_manifest_name) if bucket else None,
        "profiles": profile_entries,
        "datasets": sorted(dataset_entries),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
