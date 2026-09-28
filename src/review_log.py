"""Append-only local log for judgment calls the pipeline records instead of blocking on.

Owner rule (2026-09-27): uncertain decisions are left as the formula produced
them and logged, never hard-coded and never allowed to fail the daily cron.
Each gate that used to stop on a judgment call appends its cases here so the
owner (and later the AI decision layer, docs/ai-decision-layer.md) can review
them. Structural gates still fail closed and do not use this log.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

REVIEW_LOG_DIR = Path("output") / "review-log"


def append_review_items(kind: str, items: list[dict[str, Any]], *, log_dir: Path = REVIEW_LOG_DIR) -> Path | None:
    """Append one JSON line per item to `<log_dir>/<kind>.jsonl`; return the path, or None when empty."""
    if not items:
        return None
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"{kind}.jsonl"
    logged_at = datetime.now(timezone.utc).isoformat()
    with path.open("a", encoding="utf-8") as handle:
        for item in items:
            handle.write(json.dumps({"logged_at": logged_at, "kind": kind, **item}, default=str) + "\n")
    return path
