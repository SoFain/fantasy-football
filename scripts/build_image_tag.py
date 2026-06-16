#!/usr/bin/env python
"""Generate immutable Artifact Registry image tags for staged releases."""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SHA_RE = re.compile(r"^[0-9a-fA-F]{7,40}$")
TIMESTAMP_RE = re.compile(r"^\d{8}T\d{6}Z$")
RELEASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,62}$")


def build_image_tag(
    channel: str,
    short_sha: str,
    timestamp: str | None = None,
    release_id: str | None = None,
) -> str:
    short_sha = normalize_short_sha(short_sha)
    if channel == "staging":
        return f"staging-{short_sha}-{normalize_timestamp(timestamp)}"
    if channel == "prod-candidate":
        return f"prod-candidate-{short_sha}-{normalize_timestamp(timestamp)}"
    if channel == "prod":
        if not release_id:
            raise ValueError("--release-id is required for prod tags")
        return f"prod-{short_sha}-{normalize_release_id(release_id)}"
    raise ValueError(f"Unsupported channel: {channel}")


def normalize_short_sha(value: str) -> str:
    if not SHA_RE.match(value):
        raise ValueError("SHA must be 7 to 40 hexadecimal characters")
    return value.lower()[:12]


def normalize_timestamp(value: str | None) -> str:
    if value is None:
        return datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    if not TIMESTAMP_RE.match(value):
        raise ValueError("timestamp must use YYYYMMDDTHHMMSSZ")
    return value


def normalize_release_id(value: str) -> str:
    if not RELEASE_ID_RE.match(value):
        raise ValueError(
            "release id must contain only letters, numbers, dot, underscore, or hyphen"
        )
    return value


def resolve_git_sha() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build an immutable Cloud Run image tag.")
    parser.add_argument(
        "--channel",
        choices=("staging", "prod-candidate", "prod"),
        default="staging",
        help="Release channel to tag.",
    )
    parser.add_argument("--sha", help="Git SHA to include. Defaults to the current HEAD.")
    parser.add_argument("--timestamp", help="UTC timestamp for staging or candidate tags.")
    parser.add_argument("--release-id", help="Required for prod tags.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sha = args.sha or resolve_git_sha()
    print(build_image_tag(args.channel, sha, args.timestamp, args.release_id))


if __name__ == "__main__":
    main()
