"""CLI entrypoint for running Phase 1 and Phase 2 materializations."""

import argparse
import logging
import sys
from google.cloud import bigquery

from src.load import get_bigquery_project
from src.materialize_fantasy_points import materialize_fantasy_points
from src.materialize_player_profiles import materialize_player_profiles
from src.materialize_trade_assets import materialize_trade_assets
from src.materialize_llm_packets import materialize_llm_packets
from src.materialize_sleeper_watch import materialize_sleeper_watch
from src.materialize_viewer_team_context import materialize_viewer_team_context
from src.materialize_packets import materialize_packets

logger = logging.getLogger("run_materializer")


def run_all(client: bigquery.Client, dataset: str, season: int | None, week: int | None, league_id: str | None, dry_run: bool) -> None:
    logger.info("Starting materialization of all compatibility marts...")

    logger.info("1/7. Materializing fantasy points by profile...")
    materialize_fantasy_points(client, dataset_id=dataset, season=season, week=week, dry_run=dry_run)

    logger.info("2/7. Materializing player profiles...")
    materialize_player_profiles(client, dataset_id=dataset, season=season, week=week, dry_run=dry_run)

    logger.info("3/7. Materializing trade assets...")
    materialize_trade_assets(client, dataset_id=dataset, dry_run=dry_run)

    logger.info("4/7. Materializing LLM player context packets...")
    materialize_llm_packets(client, dataset_id=dataset, season=season, week=week, dry_run=dry_run)

    logger.info("5/7. Materializing Sleeper Watch candidates...")
    materialize_sleeper_watch(client, dataset_id=dataset, season=season, week=week, league_id=league_id, dry_run=dry_run)

    logger.info("6/7. Materializing Sleeper viewer team context...")
    materialize_viewer_team_context(client, dataset_id=dataset, season=season, week=week, league_id=league_id, dry_run=dry_run)

    logger.info("7/7. Materializing precomputed review packets and projections...")
    materialize_packets(client, dataset_id=dataset, dry_run=dry_run)

    logger.info("All compatibility marts materialized successfully.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BigQuery compatibility materialization jobs.")
    parser.add_argument(
        "--target",
        choices=["all", "fantasy-points", "player-profiles", "trade-assets", "llm-packets", "sleeper-watch", "viewer-team", "packets"],
        default="all",
        help="Specify which materialization task to run."
    )
    parser.add_argument("--project", default=get_bigquery_project(), help="GCP project ID.")
    parser.add_argument("--dataset", default="fantasy_football_brain", help="BigQuery dataset name.")
    parser.add_argument("--season", type=int, help="NFL season year.")
    parser.add_argument("--week", type=int, help="NFL week number.")
    parser.add_argument("--league-id", help="Optional Sleeper league ID.")
    parser.add_argument("--dry-run", action="store_true", help="Perform dry run without writing tables.")
    parser.add_argument("--log-level", default="INFO", help="Logging level.")

    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s"
    )

    client = bigquery.Client(project=args.project)

    try:
        if args.target == "all":
            run_all(client, args.dataset, args.season, args.week, args.league_id, args.dry_run)
        elif args.target == "fantasy-points":
            materialize_fantasy_points(client, dataset_id=args.dataset, season=args.season, week=args.week, dry_run=args.dry_run)
        elif args.target == "player-profiles":
            materialize_player_profiles(client, dataset_id=args.dataset, season=args.season, week=args.week, dry_run=args.dry_run)
        elif args.target == "trade-assets":
            materialize_trade_assets(client, dataset_id=args.dataset, dry_run=args.dry_run)
        elif args.target == "llm-packets":
            materialize_llm_packets(client, dataset_id=args.dataset, season=args.season, week=args.week, dry_run=args.dry_run)
        elif args.target == "sleeper-watch":
            materialize_sleeper_watch(client, dataset_id=args.dataset, season=args.season, week=args.week, league_id=args.league_id, dry_run=args.dry_run)
        elif args.target == "viewer-team":
            materialize_viewer_team_context(
                client,
                dataset_id=args.dataset,
                season=args.season,
                week=args.week,
                league_id=args.league_id,
                dry_run=args.dry_run,
            )
        elif args.target == "packets":
            materialize_packets(client, dataset_id=args.dataset, dry_run=args.dry_run)

        print(f"Materialization target '{args.target}' completed successfully.")
    except Exception as exc:
        logger.error("Materialization failed", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
