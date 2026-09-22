"""Render the 2026 player situation slice as a JSON feed dataset.

Mirrors coaching_staff_feed: builds a content-addressed immutable object for
the public feed's `datasets` map, plus the manifest entry the publisher merges.
Never touches the mutable manifest.

The dataset is the article engine's context source: for every player with a
2025 stats season, his current team/QB/coaching situation, change flags, age,
a `metric_basis` naming which team-season his metrics describe, and a uniform
advanced-metrics block aggregated from the 2025 weekly truth.
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from src.coaching_staff import canonical_json_bytes, sha256_hex

logger = logging.getLogger("situation_feed")

DATASET_ID = "player_situation"
DATASET_SCHEMA_VERSION = "1.1"
DEFAULT_BUCKET = "fantasy-football-498121-public-rankings"

CONTEXT_SQL = """
WITH gng_points AS (
  -- GNG parity: GNG Keeper PPG rides alongside standard everywhere.
  SELECT
    COALESCE(source_player_key, REGEXP_REPLACE(player_id_internal, r'^gsis:', '')) AS player_id,
    ROUND(AVG(total_fantasy_points), 2) AS gng_ppg_2025
  FROM `{project}.{dataset}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id = 'gng_keeper' AND season = 2025
  GROUP BY 1
),
metrics AS (
  SELECT
    player_id,
    COUNT(DISTINCT week) AS games_2025,
    ROUND(AVG(fantasy_points), 2) AS std_ppg_2025,
    ROUND(AVG(fantasy_points_ppr), 2) AS ppr_ppg_2025,
    ROUND(SAFE_DIVIDE(SUM(targets), COUNT(DISTINCT week)), 2) AS targets_per_game,
    ROUND(AVG(target_share) * 100, 1) AS target_share_pct,
    ROUND(AVG(wopr), 3) AS wopr,
    ROUND(SAFE_DIVIDE(SUM(carries), COUNT(DISTINCT week)), 2) AS carries_per_game,
    ROUND(SAFE_DIVIDE(SUM(red_zone_touches), COUNT(DISTINCT week)), 2) AS red_zone_touches_per_game,
    SUM(touchdowns) AS touchdowns_2025,
    ROUND(AVG(epa_per_opportunity), 3) AS epa_per_opportunity,
    ROUND(AVG(opportunity_score), 1) AS opportunity_score,
    ROUND(AVG(efficiency_score), 1) AS efficiency_score,
    ROUND(AVG(passing_epa), 3) AS passing_epa_per_week
  FROM `{project}.{dataset}.analytics_player_weekly_truth`
  WHERE season = 2025 AND season_type = 'REG'
  GROUP BY player_id
)
SELECT
  s.player_id_internal AS gsis_id,
  s.sleeper_player_id,
  s.player_name,
  s.position,
  s.stats_season,
  s.team_from,
  s.team_to,
  s.team_changed,
  s.qb_from,
  s.qb_to,
  s.qb_quality_from,
  s.qb_quality_to,
  s.qb_quality_delta,
  s.qb_changed,
  s.age_at_season,
  s.head_coach,
  s.offensive_coordinator,
  s.hc_changed,
  s.oc_changed,
  s.flags_json,
  s.metric_basis,
  s.games_prev,
  s.ppg_prev,
  s.gng_ppg_prev,
  s.qb_quality_from_gng,
  s.qb_quality_to_gng,
  s.qb_quality_delta_gng,
  g.gng_ppg_2025,
  m.* EXCEPT (player_id)
FROM `{project}.{dataset}.analytics_player_situation` s
LEFT JOIN metrics m ON m.player_id = s.player_id_internal
LEFT JOIN gng_points g ON g.player_id = s.player_id_internal
WHERE s.situation_for_season = 2026
ORDER BY s.position, s.player_name
"""


def fetch_context_rows(client, project: str, dataset: str) -> list[dict]:
    sql = CONTEXT_SQL.format(project=project, dataset=dataset)
    return [dict(row) for row in client.query(sql).result()]


def _round_opt(value, digits=2):
    return None if value is None else round(float(value), digits)


def player_entry(row: dict) -> dict:
    """One player's situation + metrics, shaped for the public dataset."""
    try:
        flags = json.loads(row.get("flags_json") or "[]")
    except (TypeError, ValueError):
        flags = []
    metrics = {
        "games": row.get("games_2025"),
        "std_ppg": _round_opt(row.get("std_ppg_2025")),
        "ppr_ppg": _round_opt(row.get("ppr_ppg_2025")),
        "gng_ppg": _round_opt(row.get("gng_ppg_2025")),
        "targets_per_game": _round_opt(row.get("targets_per_game")),
        "target_share_pct": _round_opt(row.get("target_share_pct"), 1),
        "wopr": _round_opt(row.get("wopr"), 3),
        "carries_per_game": _round_opt(row.get("carries_per_game")),
        "red_zone_touches_per_game": _round_opt(row.get("red_zone_touches_per_game")),
        "touchdowns": row.get("touchdowns_2025"),
        "epa_per_opportunity": _round_opt(row.get("epa_per_opportunity"), 3),
        "opportunity_score": _round_opt(row.get("opportunity_score"), 1),
        "efficiency_score": _round_opt(row.get("efficiency_score"), 1),
        "passing_epa_per_week": _round_opt(row.get("passing_epa_per_week"), 3),
    }
    return {
        "gsis_id": row.get("gsis_id"),
        "sleeper_player_id": row.get("sleeper_player_id"),
        "player_name": row.get("player_name"),
        "position": row.get("position"),
        "situation": {
            "team": row.get("team_to"),
            "team_2025": row.get("team_from"),
            "team_changed": bool(row.get("team_changed")),
            "qb": row.get("qb_to"),
            "qb_2025": row.get("qb_from"),
            "qb_changed": bool(row.get("qb_changed")),
            "qb_quality_2025_ppg": _round_opt(row.get("qb_quality_to")),
            "qb_quality_prior_ppg": _round_opt(row.get("qb_quality_from")),
            "qb_quality_delta_ppg": _round_opt(row.get("qb_quality_delta")),
            "qb_quality_delta_gng_ppg": _round_opt(row.get("qb_quality_delta_gng")),
            "age": _round_opt(row.get("age_at_season"), 1),
            "head_coach": row.get("head_coach"),
            "offensive_coordinator": row.get("offensive_coordinator"),
            "hc_changed": row.get("hc_changed"),
            "oc_changed": row.get("oc_changed"),
            "flags": flags,
            "metric_basis": row.get("metric_basis"),
        },
        "metrics": {k: v for k, v in metrics.items() if v is not None},
    }


def build_dataset(rows: list[dict], *, source_generated_at: str) -> dict:
    players = [player_entry(row) for row in rows]
    flagged = sum(1 for p in players if p["situation"]["flags"])
    movers = sum(1 for p in players if p["situation"]["team_changed"])
    return {
        "dataset": DATASET_ID,
        "schema_version": DATASET_SCHEMA_VERSION,
        "title": "Player Situation Layer 2026",
        "description": (
            "Per-player situation context for the 2026 season: current team, QB, and "
            "coaching versus the 2025 season the player's metrics describe, with change "
            "flags, age, and a uniform 2025 advanced-metrics block. metric_basis names "
            "the team-season behind every metric; treat any change flag as reason to "
            "caveat production-based conclusions."
        ),
        "source_generated_at": source_generated_at,
        "player_count": len(players),
        "team_changed_count": movers,
        "flagged_count": flagged,
        "players": players,
    }


def build_situation_feed(
    dataset_name: str = "fantasy_football_brain",
    out_dir: str | None = None,
    bucket: str = DEFAULT_BUCKET,
    client=None,
    generated_at=None,
) -> dict:
    if client is None:
        from google.cloud import bigquery

        from src.load import get_bigquery_project

        client = bigquery.Client(project=get_bigquery_project())

    rows = fetch_context_rows(client, client.project, dataset_name)
    if not rows:
        raise RuntimeError(
            "analytics_player_situation has no 2026 rows. Run build-situation-layer first."
        )

    source_generated_at = (generated_at or datetime.now(timezone.utc)).isoformat()
    dataset = build_dataset(rows, source_generated_at=source_generated_at)
    content = canonical_json_bytes(dataset)
    digest = sha256_hex(content)
    object_name = f"v1/datasets/{DATASET_ID}/sha256-{digest}.json"
    url = f"https://storage.googleapis.com/{bucket}/{object_name}"

    entry = {
        "dataset": DATASET_ID,
        "dataset_version": f"{DATASET_ID}-{DATASET_SCHEMA_VERSION}-{''.join(ch for ch in source_generated_at if ch.isdigit())[:14]}",
        "schema_version": DATASET_SCHEMA_VERSION,
        "source_generated_at": source_generated_at,
        "object": object_name,
        "url": url,
        "sha256": digest,
        "bytes": len(content),
        "player_count": dataset["player_count"],
        "team_changed_count": dataset["team_changed_count"],
        "warnings": [],
    }

    out_dir_path = Path(out_dir or (Path(__file__).resolve().parents[1] / "build" / "feeds"))
    out_dir_path.mkdir(parents=True, exist_ok=True)
    object_artifact = out_dir_path / f"{DATASET_ID}.json"
    entry_artifact = out_dir_path / f"{DATASET_ID}.manifest-entry.json"
    object_artifact.write_bytes(content)
    entry_artifact.write_bytes(canonical_json_bytes(entry))
    logger.info("Wrote situation dataset (%s players, %s movers) to %s",
                dataset["player_count"], dataset["team_changed_count"], object_artifact)

    return {
        "row_count": len(rows),
        "object": object_name,
        "url": url,
        "sha256": digest,
        "object_artifact": str(object_artifact),
        "manifest_entry_artifact": str(entry_artifact),
        "manifest_entry": entry,
    }


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Build the player situation JSON feed object.")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    result = build_situation_feed(dataset_name=args.dataset, out_dir=args.out_dir)
    print(json.dumps({k: v for k, v in result.items() if k != "manifest_entry"}, indent=2))


if __name__ == "__main__":
    main()
