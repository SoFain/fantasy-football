"""Run three-fold unified GNG VORP backtests for the selected positional formulas."""
from __future__ import annotations

import argparse,json
from pathlib import Path
from statistics import mean
import sys

from google.cloud import bigquery

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.run_unified_fable_v1_top100_backtest import evaluate_fold


VARIANTS={
 "selected_qb15_rb36_wr55_te12":{"QB":15,"RB":36,"WR":55,"TE":12},
 "qb13":{"QB":13,"RB":36,"WR":55,"TE":12},"qb17":{"QB":17,"RB":36,"WR":55,"TE":12},
 "rb34":{"QB":15,"RB":34,"WR":55,"TE":12},"rb38":{"QB":15,"RB":38,"WR":55,"TE":12},
 "wr52":{"QB":15,"RB":36,"WR":52,"TE":12},"wr58":{"QB":15,"RB":36,"WR":58,"TE":12},
 "te10":{"QB":15,"RB":36,"WR":55,"TE":10},"te14":{"QB":15,"RB":36,"WR":55,"TE":14},
}


def main():
 parser=argparse.ArgumentParser();parser.add_argument("--project",default="fantasy-football-498121");parser.add_argument("--dataset",default="fantasy_football_brain");parser.add_argument("--output",type=Path,default=Path("output/unified-gng-2026-top100-backtest.json"));args=parser.parse_args()
 client=bigquery.Client(project=args.project)
 historical=[dict(row) for row in client.query(f"""
WITH seasons AS (
 SELECT season,position,source_player_key player_id,COUNT(*) games_played,AVG(total_fantasy_points) standard_ppg
 FROM `{args.project}.{args.dataset}.analytics_player_fantasy_points_by_profile`
 WHERE scoring_profile_id='gng_keeper' AND position IN ('QB','RB','WR','TE') AND season BETWEEN 2022 AND 2025 AND week BETWEEN 1 AND 18
 GROUP BY season,position,player_id HAVING games_played>=6)
SELECT *,ROW_NUMBER() OVER(PARTITION BY season,position ORDER BY standard_ppg DESC,player_id) position_rank FROM seasons
""").result()]
 round1=json.loads(Path("output/gng-position-candidate-expansion.json").read_text(encoding="utf-8"))["scored_rows"]
 round2=json.loads(Path("output/gng-position-candidate-expansion-round2.json").read_text(encoding="utf-8"))["scored_rows"]
 advanced=json.loads(Path("output/gng-advanced-hypotheses.json").read_text(encoding="utf-8"))["scored_rows"]
 selected=[]
 for row in round1:
  if row["position"]=="QB": selected.append({**row,"score":row["q4_gng_bonus_proxy"],"target_standard_ppg":row["target_ppg"]})
 for row in round2:
  field="r7_h1_r2_compromise" if row["position"]=="RB" else "w10_h5_floor_first"
  selected.append({**row,"score":row[field],"target_standard_ppg":row["target_ppg"]})
 for row in advanced: selected.append({**row,"score":row["h5_stability_hybrid"],"target_standard_ppg":row["target_ppg"]})
 result={"variants":{}}
 for name,replacement in VARIANTS.items():
  folds=[evaluate_fold(season,selected,historical,replacement) for season in (2022,2023,2024)]
  fields=("realized_vorp_spearman","positive_vorp_captured_at_100","top_24_hit_rate","top_50_hit_rate","top_100_hit_rate")
  aggregate={f"average_{field}":mean(fold[field] for fold in folds) for field in fields}
  aggregate["average_composition"]={position:mean(fold["composition"][position] for fold in folds) for position in ("QB","RB","WR","TE")}
  result["variants"][name]={"replacement_rank":replacement,"aggregate":aggregate,"folds":folds}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({name:value["aggregate"] for name,value in result["variants"].items()},indent=2));return 0


if __name__=="__main__": raise SystemExit(main())
