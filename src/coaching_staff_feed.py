"""Render coaching_staff_current as a JSON feed object for the public feed.

The platform's public feed is JSON, content-addressed, and published to the
Cloud Storage bucket the ranking project owns:

    https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json

Immutable board/dataset objects live at v1/.../sha256-<digest>.json; the single
mutable v1/manifest.json is rebuilt in full by scripts/publish_public_rankings.py
in the ranking project. This job therefore does exactly two things and never
touches the manifest:

  1. Builds the coaching staff dataset object and writes it locally (and, behind
     an explicit --publish gate, uploads it as an immutable object).
  2. Emits the manifest entry the ranking publisher should merge under a
     `datasets` key, so coaching staff is listed alongside the ranking profiles.

Writing the manifest here would clobber the ranking profiles, so it is not done.
See docs/rebuild/coaching-staff-layer.md for the integration handoff.
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.coaching_staff import (
    DATASET_ID,
    build_dataset,
    canonical_json_bytes,
    manifest_entry,
    sha256_hex,
)

logger = logging.getLogger("coaching_staff_feed")

TABLE_NAME = "coaching_staff_current"
DEFAULT_BUCKET = "fantasy-football-498121-public-rankings"

FEED_COLUMNS = (
    "team_abbr",
    "role",
    "role_title",
    "role_rank",
    "coach_name",
    "is_vacant",
    "verification_status",
)


def fetch_rows(client, dataset_name: str) -> list[dict]:
    table_id = f"{client.project}.{dataset_name}.{TABLE_NAME}"
    columns = ", ".join(FEED_COLUMNS)
    sql = f"SELECT {columns} FROM `{table_id}` ORDER BY team_abbr, role_rank"
    return [dict(row) for row in client.query(sql).result()]


def _object_name(digest: str) -> str:
    return f"v1/datasets/{DATASET_ID}/sha256-{digest}.json"


def _public_url(bucket: str, object_name: str) -> str:
    return f"https://storage.googleapis.com/{bucket}/{object_name}"


def build_coaching_staff_feed(
    dataset_name: str = "fantasy_football_brain",
    out_dir: str | None = None,
    source_url: str = "",
    bucket: str = DEFAULT_BUCKET,
    publish: bool = False,
    client=None,
    generated_at=None,
) -> dict:
    if client is None:
        from google.cloud import bigquery

        from src.load import get_bigquery_project

        client = bigquery.Client(project=get_bigquery_project())

    rows = fetch_rows(client, dataset_name)
    if not rows:
        raise RuntimeError(
            "coaching_staff_current is empty. Run ingest-coaching-staff before building the feed."
        )

    source_generated_at = (generated_at or datetime.now(timezone.utc)).isoformat()
    dataset = build_dataset(rows, source_generated_at=source_generated_at, source_url=source_url)
    content = canonical_json_bytes(dataset)
    digest = sha256_hex(content)
    object_name = _object_name(digest)
    url = _public_url(bucket, object_name)

    warnings = []
    if dataset["vacant_count"] or dataset["pending_count"]:
        warnings.append(
            f"{dataset['vacant_count']} vacant and {dataset['pending_count']} unverified coaches; "
            "populate data/coaching_staff.csv from the source page and re-run ingest-coaching-staff."
        )
    entry = manifest_entry(
        content=content,
        object_name=object_name,
        url=url,
        source_generated_at=source_generated_at,
        dataset=dataset,
        warnings=warnings,
    )

    out_dir_path = Path(out_dir or _default_out_dir())
    out_dir_path.mkdir(parents=True, exist_ok=True)
    object_artifact = out_dir_path / f"{DATASET_ID}.json"
    entry_artifact = out_dir_path / f"{DATASET_ID}.manifest-entry.json"
    object_artifact.write_bytes(content)
    entry_artifact.write_bytes(canonical_json_bytes(entry))
    logger.info("Wrote coaching staff dataset (%s teams) to %s", dataset["team_count"], object_artifact)

    published = False
    if publish:
        _upload_immutable(bucket, object_name, content)
        published = True
        logger.info("Uploaded immutable coaching staff object to gs://%s/%s", bucket, object_name)
        logger.info("Manifest NOT updated. Merge this entry via the ranking publisher: %s", json.dumps(entry))

    return {
        "row_count": len(rows),
        "object": object_name,
        "url": url,
        "sha256": digest,
        "bytes": len(content),
        "published": published,
        "warnings": warnings,
        "manifest_entry": entry,
        "object_artifact": str(object_artifact),
        "manifest_entry_artifact": str(entry_artifact),
    }


def _upload_immutable(bucket_name: str, object_name: str, content: bytes) -> None:
    """Upload a content-addressed object, refusing to overwrite (immutability).

    Mirrors the ranking publisher's ifGenerationMatch=0 precondition. An
    identical object re-upload is treated as success; a digest collision with
    different bytes is impossible, so only a true precondition failure raises.
    """
    from google.api_core.exceptions import PreconditionFailed
    from google.cloud import storage

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_name)
    blob.metadata = {"sha256": sha256_hex(content), "immutable": "true"}
    try:
        blob.upload_from_string(content, content_type="application/json", if_generation_match=0)
    except PreconditionFailed:
        # The object already exists. Content addressing guarantees identical
        # bytes, so this is idempotent, not an error.
        logger.info("Immutable object already present, skipping: %s", object_name)


def _default_out_dir() -> str:
    return str(Path(__file__).resolve().parents[1] / "build" / "feeds")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    parser = argparse.ArgumentParser(description="Build the coaching staff JSON feed object.")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--out-dir", default=None, help="Local artifact directory. Defaults to build/feeds/.")
    parser.add_argument("--source-url", default="")
    parser.add_argument("--bucket", default=DEFAULT_BUCKET)
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Upload the immutable object to Cloud Storage. Never updates the manifest.",
    )
    args = parser.parse_args()
    result = build_coaching_staff_feed(
        dataset_name=args.dataset,
        out_dir=args.out_dir,
        source_url=args.source_url,
        bucket=args.bucket,
        publish=args.publish,
    )
    print(json.dumps({k: v for k, v in result.items() if k != "manifest_entry"}, indent=2))


if __name__ == "__main__":
    main()
