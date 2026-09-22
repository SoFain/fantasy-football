"""Build and materialize the review-only unified 2026 GNG overall board."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date,datetime
import json
from pathlib import Path
import sys

from google.cloud import bigquery

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.build_unified_fable_v1_top100 import OVERALL_BOARD_SIZE,assert_position_order,fit_log_curve,interleave


REPLACEMENT={"QB":13,"RB":36,"WR":55,"TE":12}


def apply_position_locked_overall_floor(board, *, player_name, minimum_overall):
    target=next(row for row in board if row["player_name"]==player_name)
    if target["overall_rank"]>=minimum_overall: return board
    unconstrained=[row for row in board if not (row["position"]==target["position"] and row["position_rank"]>=target["position_rank"])]
    ceiling=unconstrained[minimum_overall-2]["adjusted_vorp"]
    guarded=[]
    for row in board:
        order_score=row["adjusted_vorp"]
        if row["position"]==target["position"] and row["position_rank"]>=target["position_rank"]:
            offset=row["position_rank"]-target["position_rank"]+1
            order_score=min(order_score,ceiling-offset*1e-6)
        guarded.append({**row,"raw_adjusted_vorp":row.get("raw_adjusted_vorp",row["adjusted_vorp"]),"adjusted_vorp":order_score,"_order_score":order_score})
    guarded.sort(key=lambda row:(-row["_order_score"],row["overall_rank"]))
    return [{key:value for key,value in {**row,"overall_rank":rank}.items() if key!="_order_score"} for rank,row in enumerate(guarded,1)]


def apply_position_locked_floors(board, floors):
    queues={position:[row for row in board if row["position"]==position] for position in ("QB","RB","WR","TE")}
    output=[]
    while len(output)<len(board):
        next_rank=len(output)+1
        eligible=[]
        for queue in queues.values():
            if queue and next_rank>=floors.get(queue[0]["player_name"],1): eligible.append(queue[0])
        if not eligible: raise ValueError(f"No position queue eligible at overall rank {next_rank}")
        selected=min(eligible,key=lambda row:row["overall_rank"])
        queues[selected["position"]].pop(0);output.append({**selected,"overall_rank":next_rank})
    return output


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--project",default="fantasy-football-498121");parser.add_argument("--brain-dataset",default="fantasy_football_brain");parser.add_argument("--metrics-dataset",default="fantasy_football_advanced_metrics");parser.add_argument("--apply",action="store_true");parser.add_argument("--output",type=Path,default=Path("output/unified-gng-2026-top150.json"));args=parser.parse_args()
    client=bigquery.Client(project=args.project)
    historical=[dict(row) for row in client.query(f"""
WITH seasons AS (
 SELECT season,position,source_player_key player_id,COUNT(*) games_played,AVG(total_fantasy_points) ppg
 FROM `{args.project}.{args.brain_dataset}.analytics_player_fantasy_points_by_profile`
 WHERE scoring_profile_id='gng_keeper' AND position IN ('QB','RB','WR','TE') AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
 GROUP BY season,position,player_id HAVING games_played>=6
)
SELECT *,ROW_NUMBER() OVER(PARTITION BY season,position ORDER BY ppg DESC,player_id) position_rank FROM seasons
""").result()]
    source=[dict(row) for row in client.query(f"""
SELECT * FROM `{args.project}.{args.metrics_dataset}.gng_2026_positional_boards_with_rookies` ORDER BY position,rank
""").result()]
    queues={position:[row for row in source if row["position"]==position] for position in REPLACEMENT}
    curves={};availability={}
    for position,replacement in REPLACEMENT.items():
        rows=[row for row in historical if row["position"]==position and row["position_rank"]<=max(replacement+12,24)]
        curves[position]=fit_log_curve([(row["position_rank"],row["ppg"]) for row in rows])
        cohort=[row for row in historical if row["position"]==position and row["position_rank"]<=replacement]
        availability[position]=sum(min(row["games_played"]/17,1) for row in cohort)/len(cohort)
    board=interleave(queues,curves,availability,replacement_rank=REPLACEMENT)
    qb4=next(row["player_name"] for row in board if row["position"]=="QB" and row["position_rank"]==4)
    board=apply_position_locked_floors(board,{"Jeremiyah Love":20,qb4:25})
    assert_position_order(board)
    for row in board:
        row["source_position_rank"]=row.pop("rank");row["guardrail_labels"]=row.get("sleeper_review_flags_json") or "[]"
        for key,value in tuple(row.items()):
            if isinstance(value,(date,datetime)): row[key]=value.isoformat()
    metadata={"replacement_rank":REPLACEMENT,"curves":{p:{"a":curves[p][0],"b":curves[p][1]} for p in curves},"availability":availability,"composition":dict(Counter(row["position"] for row in board))}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps({"metadata":metadata,"board":board},indent=2,default=str)+"\n",encoding="utf-8")
    if args.apply:
        table=f"{args.project}.{args.metrics_dataset}.unified_gng_2026_top150_review"
        config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE",autodetect=True)
        client.load_table_from_json(board,table,job_config=config).result()
    print(json.dumps({"applied":args.apply,**metadata},indent=2));return 0


if __name__=="__main__": raise SystemExit(main())
