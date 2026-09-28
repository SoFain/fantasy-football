"""Publish the validated unified PPR overall board without changing positional rankings."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys

from google.cloud import bigquery

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

from scripts.build_unified_fable_v1_top100 import OVERALL_BOARD_SIZE
from scripts.promote_unified_fable_v1_standard_top100 import schema, validate_active_position_ranks


WRITE_GATE="ALLOW_UNIFIED_PPR_FABLE_V1_TOP100_PROMOTION"
BOARD_VERSION="unified-ppr-fable-v1-20260711"


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--project",default="fantasy-football-498121")
    parser.add_argument("--dataset",default="fantasy_football_brain")
    parser.add_argument("--scoring-profile",choices=("ppr","half_ppr"),default="ppr")
    parser.add_argument("--board",type=Path,default=Path("output/unified-ppr-fable-v1-top150.json"))
    parser.add_argument("--board-version")
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    profile_label=args.scoring_profile.replace("_","-")
    board_version=args.board_version or datetime.now(timezone.utc).strftime(f"unified-{profile_label}-fable-v1-%Y%m%d%H%M%S")
    board=json.loads(args.board.read_text(encoding="utf-8"))["board"]
    if len(board)!=OVERALL_BOARD_SIZE or len({row["player_id"] for row in board})!=OVERALL_BOARD_SIZE:
        raise ValueError(f"board must contain {OVERALL_BOARD_SIZE} unique players")
    client=bigquery.Client(project=args.project)
    active_rows=[dict(row) for row in client.query(f"""
SELECT player_id,position,rank,ranking_version
FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
WHERE is_active AND scoring_profile_id='{args.scoring_profile}' AND position IN ('QB','RB','WR','TE')
QUALIFY ROW_NUMBER() OVER(PARTITION BY position,player_id ORDER BY generated_at DESC)=1
""").result()]
    validate_active_position_ranks(board,active_rows)
    if any(not row.get("current_team") for row in board):
        raise ValueError("unified board contains a teamless player")
    if not args.apply:
        print(json.dumps({"board_version":board_version,"rows":OVERALL_BOARD_SIZE,"active_position_ranks_valid":True,"writes":False},indent=2)); return 0
    if os.environ.get(WRITE_GATE,"").lower()!="true": raise RuntimeError(f"{WRITE_GATE}=true is required")
    current=f"{args.project}.{args.dataset}.unified_draft_rankings_current"
    history=f"{args.project}.{args.dataset}.unified_draft_rankings_history"
    client.create_table(bigquery.Table(current,schema=schema()),exists_ok=True)
    client.create_table(bigquery.Table(history,schema=schema()+[bigquery.SchemaField("archived_at","TIMESTAMP",mode="REQUIRED")]),exists_ok=True)
    client.query(f"INSERT INTO `{history}` SELECT live_rows.*,CURRENT_TIMESTAMP() FROM `{current}` live_rows WHERE scoring_profile_id='{args.scoring_profile}' AND NOT EXISTS(SELECT 1 FROM `{history}` h WHERE h.board_version=live_rows.board_version AND h.player_id=live_rows.player_id)").result()
    client.query(f"DELETE FROM `{current}` WHERE scoring_profile_id='{args.scoring_profile}'").result()
    now=datetime.now(timezone.utc).isoformat()
    payload=[{"board_version":board_version,"generated_at":now,"scoring_profile_id":args.scoring_profile,"overall_rank":row["overall_rank"],"player_id":row["player_id"],"player_name":row["player_name"],"current_team":row.get("current_team"),"position":row["position"],"position_rank":row["position_rank"],"projected_ppg":row["projected_ppg"],"replacement_rank":row["replacement_rank"],"replacement_ppg":row["replacement_ppg"],"vorp":row["vorp"],"availability_multiplier":row["availability_multiplier"],"onesie_multiplier":row["onesie_multiplier"],"adjusted_vorp":row["adjusted_vorp"],"position_source_version":row.get("ranking_version") or f"{args.scoring_profile}-fable-v1-review-20260711","position_rank_source":row.get("rank_source"),"risk_flags":row.get("risk_flags"),"qb_backtest_proxy_disclosed":True} for row in board]
    load_job=client.load_table_from_json(
        payload,
        current,
        job_config=bigquery.LoadJobConfig(
            schema=schema(),
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        ),
    )
    load_job.result()
    if load_job.errors: raise RuntimeError(load_job.errors)
    count=next(iter(client.query(f"SELECT COUNT(*) row_count FROM `{current}` WHERE scoring_profile_id='{args.scoring_profile}' AND board_version='{board_version}'").result()))["row_count"]
    if count!=OVERALL_BOARD_SIZE: raise RuntimeError(f"expected {OVERALL_BOARD_SIZE} rows, got {count}")
    print(json.dumps({"board_version":board_version,"rows":count,"writes":True},indent=2)); return 0


if __name__=="__main__": raise SystemExit(main())
