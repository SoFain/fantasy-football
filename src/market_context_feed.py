"""Build the market_context public dataset: Sleeper market consensus vs Pigskin boards.

Market consensus comes from Sleeper's projections endpoint (the same source the GNG
homepage market board uses), which carries format-specific ADP: adp_std, adp_ppr,
adp_half_ppr. Sleeper's documented API has no ADP endpoint; this is the endpoint the
Sleeper app itself uses. When ADP is unavailable for a player (sentinel >= 999) the
row falls back to the Sleeper search_rank basis from v_market_rankings_context.

REVIEW/CONTENT EVIDENCE ONLY. This dataset grounds article and show-prep market
claims. It is never a formula input and never moves a rank.
"""

from __future__ import annotations

import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.coaching_staff import canonical_json_bytes, sha256_hex

logger = logging.getLogger("market_context_feed")

DATASET_ID = "market_context"
DATASET_SCHEMA_VERSION = "1.0"
DEFAULT_BUCKET = "fantasy-football-498121-public-rankings"
ADP_SENTINEL = 999.0

PROJECTIONS_URL = (
    "https://api.sleeper.com/projections/nfl/{season}"
    "?season_type=regular&position[]=QB&position[]=RB&position[]=WR&position[]=TE&order_by=pts_std"
)
TRENDING_URL = "https://api.sleeper.app/v1/players/nfl/trending/{kind}?lookback_hours=24&limit=25"
STATE_URL = "https://api.sleeper.app/v1/state/nfl"

# Profile -> Sleeper ADP field. GNG Keeper has no Sleeper analog; standard ADP is the
# closest public consensus and is labeled as such.
PROFILE_ADP_FIELDS = {
    "standard": ("adp_std", "sleeper_adp_std"),
    "ppr": ("adp_ppr", "sleeper_adp_ppr"),
    "half_ppr": ("adp_half_ppr", "sleeper_adp_half_ppr"),
    "gng_keeper": ("adp_std", "sleeper_adp_std_proxy"),
}


def _fetch_json(url: str, timeout: int = 15):
    response = requests.get(
        url, timeout=timeout,
        headers={"Accept": "application/json", "User-Agent": "PigskinMarketContext/1.0"},
    )
    response.raise_for_status()
    return response.json()


def fetch_sleeper_market(season: str | None = None) -> dict:
    """One projections call plus two trending calls. Fail-soft: any failure returns
    an empty section so the dataset still publishes on the search_rank basis."""
    market: dict = {"season": season, "adp_by_player": {}, "trending_add": [], "trending_drop": []}
    try:
        if season is None:
            season = str(_fetch_json(STATE_URL).get("season") or datetime.now(timezone.utc).year)
        market["season"] = season
        rows = _fetch_json(PROJECTIONS_URL.format(season=season), timeout=30)
        for row in rows or []:
            player_id = str(row.get("player_id") or "")
            stats = row.get("stats") or {}
            if not player_id or not isinstance(stats, dict):
                continue
            adp = {
                field: value
                for field, value in stats.items()
                if field.startswith("adp") and isinstance(value, (int, float)) and value < ADP_SENTINEL
            }
            if adp:
                market["adp_by_player"][player_id] = adp
    except Exception as error:
        logger.warning("Sleeper projections/ADP unavailable; falling back to search_rank basis: %s", error)
    for kind in ("add", "drop"):
        try:
            market[f"trending_{kind}"] = [
                {"sleeper_player_id": str(row.get("player_id")), "count": int(row.get("count") or 0)}
                for row in _fetch_json(TRENDING_URL.format(kind=kind)) or []
                if row.get("player_id")
            ]
        except Exception as error:
            logger.warning("Sleeper trending/%s unavailable: %s", kind, error)
    return market


def fetch_board_rows(client, project_id: str, metrics_dataset: str) -> list[dict]:
    query = f"""
    SELECT scoring_profile_id, position, player_id, sleeper_player_id, player_name,
           current_team, pigskin_position_rank, pigskin_tier, ranking_version,
           sleeper_search_rank, market_position_rank AS search_rank_position_rank,
           market_overall_rank AS search_rank_overall_rank, market_snapshot_at
    FROM `{project_id}.{metrics_dataset}.v_market_rankings_context`
    ORDER BY scoring_profile_id, position, pigskin_position_rank
    """
    return [dict(row) for row in client.query(query).result()]


def gap_bucket(delta: int | None) -> str:
    if delta is None:
        return "NO_MARKET_SIGNAL"
    if delta >= 10:
        return "PIGSKIN_MUCH_HIGHER"
    if delta >= 4:
        return "PIGSKIN_HIGHER"
    if delta <= -10:
        return "MARKET_MUCH_HIGHER"
    if delta <= -4:
        return "MARKET_HIGHER"
    return "ALIGNED"


def build_dataset(board_rows: list[dict], market: dict, *, source_generated_at: str) -> dict:
    adp_by_player = market["adp_by_player"]
    profiles: dict[str, dict] = {}
    for (profile,), _ in {(row["scoring_profile_id"],): None for row in board_rows}.items():
        adp_field, source_id = PROFILE_ADP_FIELDS.get(profile, ("adp_std", "sleeper_adp_std_proxy"))
        rows = [row for row in board_rows if row["scoring_profile_id"] == profile]
        # Market position rank basis: ADP ordering within each position across this
        # profile's board universe; search_rank basis fills players without ADP.
        by_position: dict[str, list] = {}
        for row in rows:
            by_position.setdefault(row["position"], []).append(row)
        players = []
        for position, position_rows in by_position.items():
            with_adp = [
                (adp_by_player.get(str(row["sleeper_player_id"]), {}).get(adp_field), row)
                for row in position_rows
            ]
            ranked = sorted((pair for pair in with_adp if pair[0] is not None), key=lambda pair: pair[0])
            adp_rank = {id(row): index for index, (_, row) in enumerate(ranked, 1)}
            # Fallback basis ranks search_rank WITHIN this board cohort so its scale is
            # comparable to the board (a 35-row TE board must not produce "market TE198").
            search_ranked = sorted(
                (row for row in position_rows if row["sleeper_search_rank"] is not None),
                key=lambda row: row["sleeper_search_rank"],
            )
            cohort_search_rank = {id(row): index for index, row in enumerate(search_ranked, 1)}
            for adp_value, row in with_adp:
                if adp_value is not None:
                    market_rank = adp_rank[id(row)]
                    basis = source_id
                else:
                    market_rank = cohort_search_rank.get(id(row))
                    basis = "sleeper_search_rank" if market_rank is not None else None
                delta = (market_rank - row["pigskin_position_rank"]) if market_rank is not None else None
                players.append({
                    "player_id": row["player_id"],
                    "sleeper_player_id": row["sleeper_player_id"],
                    "player_name": row["player_name"],
                    "position": position,
                    "team": row["current_team"],
                    "pigskin_position_rank": row["pigskin_position_rank"],
                    "pigskin_tier": row["pigskin_tier"],
                    "market_adp": adp_value,
                    "market_position_rank": market_rank,
                    "market_delta": delta,
                    "market_gap_bucket": gap_bucket(delta),
                    "market_source_id": basis,
                })
        players.sort(key=lambda p: (p["position"], p["pigskin_position_rank"]))
        profiles[profile] = {
            "adp_field": adp_field,
            "player_count": len(players),
            "with_market_signal": sum(1 for p in players if p["market_position_rank"] is not None),
            "players": players,
        }
    return {
        "dataset": DATASET_ID,
        "schema_version": DATASET_SCHEMA_VERSION,
        "title": "Sleeper Market Consensus vs Pigskin Boards",
        "description": (
            "Per-player market consensus context from Sleeper: format-specific ADP from the "
            "Sleeper projections endpoint (adp_std / adp_ppr / adp_half_ppr; GNG Keeper uses "
            "standard ADP as a labeled proxy), with Sleeper search_rank as fallback, joined to "
            "the active Pigskin positional boards. market_delta is market position rank minus "
            "Pigskin position rank: positive means Pigskin is higher on the player than the "
            "market. Quote these numbers for any market/ADP claim; never estimate market "
            "opinion from memory. Market data never influences Pigskin ranks."
        ),
        "source_generated_at": source_generated_at,
        "sleeper_season": market.get("season"),
        "adp_available": bool(adp_by_player),
        "trending_add": market["trending_add"],
        "trending_drop": market["trending_drop"],
        "profiles": profiles,
    }


def build_market_context_feed(
    metrics_dataset: str = "fantasy_football_advanced_metrics",
    out_dir: str | None = None,
    bucket: str = DEFAULT_BUCKET,
    client=None,
    generated_at=None,
    market: dict | None = None,
) -> dict:
    if client is None:
        from google.cloud import bigquery

        from src.load import get_bigquery_project

        client = bigquery.Client(project=get_bigquery_project())

    board_rows = fetch_board_rows(client, client.project, metrics_dataset)
    if not board_rows:
        raise RuntimeError("v_market_rankings_context returned no active board rows.")

    market = market if market is not None else fetch_sleeper_market()
    source_generated_at = (generated_at or datetime.now(timezone.utc)).isoformat()
    dataset = build_dataset(board_rows, market, source_generated_at=source_generated_at)

    content = canonical_json_bytes(dataset)
    digest = sha256_hex(content)
    object_name = f"v1/datasets/{DATASET_ID}/sha256-{digest}.json"
    entry = {
        "dataset": DATASET_ID,
        "dataset_version": f"{DATASET_ID}-{DATASET_SCHEMA_VERSION}-{''.join(ch for ch in source_generated_at if ch.isdigit())[:14]}",
        "schema_version": DATASET_SCHEMA_VERSION,
        "source_generated_at": source_generated_at,
        "object": object_name,
        "url": f"https://storage.googleapis.com/{bucket}/{object_name}",
        "sha256": digest,
        "bytes": len(content),
        "adp_available": dataset["adp_available"],
        "warnings": [] if dataset["adp_available"] else ["sleeper_adp_unavailable_search_rank_basis"],
    }

    out_dir_path = Path(out_dir or (Path(__file__).resolve().parents[1] / "build" / "feeds"))
    out_dir_path.mkdir(parents=True, exist_ok=True)
    object_artifact = out_dir_path / f"{DATASET_ID}.json"
    entry_artifact = out_dir_path / f"{DATASET_ID}.manifest-entry.json"
    object_artifact.write_bytes(content)
    entry_artifact.write_bytes(canonical_json_bytes(entry))
    logger.info("Wrote market context dataset (%s board rows, adp_available=%s) to %s",
                len(board_rows), dataset["adp_available"], object_artifact)

    return {
        "row_count": len(board_rows),
        "adp_available": dataset["adp_available"],
        "object": object_name,
        "url": entry["url"],
        "sha256": digest,
        "object_artifact": str(object_artifact),
        "manifest_entry_artifact": str(entry_artifact),
        "manifest_entry": entry,
    }


def main():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Build the market context JSON feed object.")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--out-dir", default=None)
    args = parser.parse_args()
    result = build_market_context_feed(metrics_dataset=args.metrics_dataset, out_dir=args.out_dir)
    print(json.dumps({k: v for k, v in result.items() if k != "manifest_entry"}, indent=2))


if __name__ == "__main__":
    main()
