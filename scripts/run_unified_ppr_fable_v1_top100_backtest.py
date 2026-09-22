"""Run pooled realized-VORP folds and replacement sensitivity for unified PPR Fable v1."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
import sys

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.run_qb_fable_v1_backtest import build_qb_fable_v1_sql
from scripts.run_unified_fable_v1_top100_backtest import evaluate_fold, qb_detail_sql


VARIANTS = {
    "selected_rb30_wr44_te9": {"QB": 13, "RB": 30, "WR": 44, "TE": 9},
    "rb28_wr44_te9": {"QB": 13, "RB": 28, "WR": 44, "TE": 9},
    "rb32_wr44_te9": {"QB": 13, "RB": 32, "WR": 44, "TE": 9},
    "rb30_wr42_te9": {"QB": 13, "RB": 30, "WR": 42, "TE": 9},
    "rb30_wr46_te9": {"QB": 13, "RB": 30, "WR": 46, "TE": 9},
    "rb30_wr44_te10": {"QB": 13, "RB": 30, "WR": 44, "TE": 10},
}
HALF_VARIANTS={
    "selected_rb32_wr42_te9":{"QB":13,"RB":32,"WR":42,"TE":9},
    "rb30_wr42_te9":{"QB":13,"RB":30,"WR":42,"TE":9},
    "rb34_wr42_te9":{"QB":13,"RB":34,"WR":42,"TE":9},
    "rb32_wr40_te9":{"QB":13,"RB":32,"WR":40,"TE":9},
    "rb32_wr44_te9":{"QB":13,"RB":32,"WR":44,"TE":9},
    "rb32_wr42_te10":{"QB":13,"RB":32,"WR":42,"TE":10},
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", default="fantasy-football-498121")
    parser.add_argument("--dataset", default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset", default="fantasy_football_advanced_metrics")
    parser.add_argument("--scoring-profile",choices=("ppr","half_ppr"),default="ppr")
    parser.add_argument("--json-output", type=Path, default=Path("output/unified-ppr-fable-v1-top100-backtest.json"))
    args = parser.parse_args()
    client = bigquery.Client(project=args.project)
    historical = [dict(row) for row in client.query(f"""
WITH seasons AS (
  SELECT season,position,source_player_key player_id,COUNT(*) games_played,
    SAFE_DIVIDE(SUM(total_fantasy_points),COUNT(*)) standard_ppg
  FROM `{args.project}.{args.dataset}.analytics_player_fantasy_points_by_profile`
  WHERE scoring_profile_id='{args.scoring_profile}' AND position IN ('QB','RB','WR','TE') AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
  GROUP BY season,position,player_id HAVING games_played>=6
)
SELECT *, ROW_NUMBER() OVER(PARTITION BY season,position ORDER BY standard_ppg DESC,player_id) position_rank FROM seasons
""").result()]
    scored_rows=[]
    specs=(
        ("RB","v_rb_fable_01_scored_seasons","rb_fable_01_score+0.02*z_target_share-0.02*z_ngt_tpg"),
        ("WR","v_wr_fable_v1_scored_seasons","wr_fable_v1_score"),
        ("TE","v_te_fable_v1a_scored_seasons","te_fable_v1a_no_man_score"),
    )
    for position,view,score in specs:
        rows=client.query(f"""
WITH target AS (
 SELECT season,source_player_key player_id,COUNT(*) games,SAFE_DIVIDE(SUM(total_fantasy_points),COUNT(*)) target_ppg
 FROM `{args.project}.{args.dataset}.analytics_player_fantasy_points_by_profile`
 WHERE scoring_profile_id='{args.scoring_profile}' AND position='{position}' AND season BETWEEN 2023 AND 2025 AND week BETWEEN 1 AND 18
 GROUP BY season,player_id HAVING games>=6)
SELECT scored.season,scored.candidate_internal_player_id player_id,scored.player_name,{score} score,target.target_ppg target_standard_ppg
FROM `{args.project}.{args.metrics_dataset}.{view}` scored
JOIN target ON target.season=scored.season+1 AND target.player_id=scored.candidate_internal_player_id
WHERE scored.season BETWEEN 2022 AND 2024 AND {score} IS NOT NULL
""").result()
        scored_rows.extend({**dict(row),"position":position} for row in rows)
    qb_rows=client.query(qb_detail_sql(args.project,args.dataset)).result()
    scored_rows.extend({"season":row["input_season"],"player_id":row["player_id_internal"],"player_name":dict(row).get("player_name") or row["player_id_internal"],"position":"QB","score":row["qb_fable_v1_score"],"target_standard_ppg":row["target_standard_ppg"]} for row in qb_rows)
    result={"variants":{}}
    variants=VARIANTS if args.scoring_profile=="ppr" else HALF_VARIANTS
    for name,replacement in variants.items():
        folds=[evaluate_fold(season,scored_rows,historical,replacement) for season in (2022,2023,2024)]
        aggregate={
            "average_realized_vorp_spearman":mean(fold["realized_vorp_spearman"] for fold in folds),
            "average_positive_vorp_captured_at_100":mean(fold["positive_vorp_captured_at_100"] for fold in folds),
            "average_top_24_hit_rate":mean(fold["top_24_hit_rate"] for fold in folds),
            "average_top_50_hit_rate":mean(fold["top_50_hit_rate"] for fold in folds),
            "average_top_100_hit_rate":mean(fold["top_100_hit_rate"] for fold in folds),
            "qb_proxy":"QB Fable v1 prior-season queue; QB scoring is unchanged but active guarded QB lacks matching folds",
        }
        result["variants"][name]={"replacement_rank":replacement,"aggregate":aggregate,"folds":folds}
    args.json_output.parent.mkdir(parents=True,exist_ok=True)
    args.json_output.write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8")
    print(json.dumps({name:value["aggregate"] for name,value in result["variants"].items()},indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
