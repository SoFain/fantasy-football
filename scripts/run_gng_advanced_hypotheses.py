"""Backtest five GNG formula hypotheses over standard and advanced metrics."""
from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path
import sys
from statistics import mean
from google.cloud import bigquery
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.run_ppr_fable_transfer_backtest import summarize

HYPOTHESES=("h1_profile_points","h2_standard_opportunity","h3_gng_weighted_opportunity","h4_bonus_first_down","h5_stability_hybrid")

def weighted_average(row, weighted_fields):
 numerator=sum(weight*row[field] for field,weight in weighted_fields if row.get(field) is not None)
 denominator=sum(weight for field,weight in weighted_fields if row.get(field) is not None)
 return numerator/denominator if denominator else None

def player_audit(rows):
 predicted=sorted(rows,key=lambda row:(-row["score"],row["player_name"]))
 actual=sorted(rows,key=lambda row:(-row["target_ppg"],row["player_name"]))
 actual_rank={row["player_id"]:rank for rank,row in enumerate(actual,1)}
 ranked=[{**row,"predicted_rank":rank,"actual_rank":actual_rank[row["player_id"]]} for rank,row in enumerate(predicted,1)]
 fields=("player_id","player_name","predicted_rank","actual_rank","target_ppg","target_points")
 select=lambda row:{field:row[field] for field in fields}
 return {
  "elite_misses":[select(row) for row in ranked if row["actual_rank"]<=12 and row["predicted_rank"]>24],
  "top12_busts":[select(row) for row in ranked if row["predicted_rank"]<=12 and row["actual_rank"]>36],
 }

def main()->int:
 parser=argparse.ArgumentParser(); parser.add_argument("--project",default="fantasy-football-498121"); parser.add_argument("--dataset",default="fantasy_football_brain"); parser.add_argument("--json-output",type=Path,default=Path("output/gng-advanced-hypotheses.json")); args=parser.parse_args()
 client=bigquery.Client(project=args.project)
 sql=f"""
WITH mart AS (
 SELECT target_season,position,player_id_internal player_id,ANY_VALUE(player_name) player_name,
  AVG(profile_points_score) profile_points,AVG(opportunity_score_proxy) opportunity,
  AVG(efficiency_score_proxy) efficiency,AVG(role_stability_score) role_stability,
  AVG(red_zone_usage_score) red_zone_usage,AVG(goal_line_usage_score) goal_line_usage,
  AVG(xfp_share_3yr) xfp_share,AVG(fantasy_points_over_expectation_3yr) fpoe,
  AVG(offensive_snap_share_3yr) snap_share,AVG(snap_role_stability_3yr) snap_stability,
  AVG(availability_score_3yr) availability,AVG(opportunity_quality_score_3yr) opportunity_quality,
  AVG(high_value_first_down_opportunity_score_3yr) high_value_first_down,
  AVG(receiving_chain_mover_score_3yr) receiving_chain,AVG(rushing_chain_mover_score_3yr) rushing_chain,
  AVG(COALESCE(ngs_receiving_efficiency_score_3yr,ngs_rushing_efficiency_score_3yr,ngs_qb_passing_efficiency_score_3yr)) ngs_efficiency,
  SUM(target_fantasy_points) target_points,AVG(target_fantasy_points) target_ppg,COUNTIF(target_fantasy_points IS NOT NULL) target_games
 FROM `{args.project}.{args.dataset}.ranking_backtest_feature_mart`
 WHERE scoring_profile_id='gng_keeper' AND target_season BETWEEN 2023 AND 2025
  AND source_window_end_season<target_season AND position IN ('QB','RB','WR','TE')
 GROUP BY target_season,position,player_id HAVING target_games>=6
), advanced AS (
 SELECT season,player_id_internal player_id,AVG(weighted_opportunity_gng_keeper) gng_weighted_opportunity,
  AVG(receiving_first_down_rate) receiving_fd_rate,AVG(rushing_first_down_rate) rushing_fd_rate,
  AVG(passing_first_down_rate) passing_fd_rate,AVG(passing_epa_per_dropback) passing_epa,
  AVG(receiving_epa_per_target) receiving_epa,AVG(rushing_epa_per_carry) rushing_epa
 FROM `{args.project}.{args.dataset}.player_season_advanced_metrics`
 WHERE metric_version='advanced_player_metrics_v1' AND season_type='REG' AND season BETWEEN 2022 AND 2024
 GROUP BY season,player_id
), joined AS (
 SELECT mart.*,advanced.* EXCEPT(season,player_id)
 FROM mart LEFT JOIN advanced ON advanced.season=mart.target_season-1 AND advanced.player_id=mart.player_id
), pct AS (
 SELECT joined.*,
  IF(profile_points IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY profile_points)) p_points,
  IF(opportunity IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY opportunity)) p_opp,
  IF(efficiency IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY efficiency)) p_eff,
  IF(role_stability IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY role_stability)) p_role,
  IF(gng_weighted_opportunity IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY gng_weighted_opportunity)) p_gng_opp,
  IF(COALESCE(receiving_fd_rate,rushing_fd_rate,passing_fd_rate) IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY COALESCE(receiving_fd_rate,rushing_fd_rate,passing_fd_rate))) p_fd,
  IF(high_value_first_down IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY high_value_first_down)) p_hvfd,
  IF(COALESCE(passing_epa,receiving_epa,rushing_epa) IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY COALESCE(passing_epa,receiving_epa,rushing_epa))) p_epa,
  IF(xfp_share IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY xfp_share)) p_xfp,
  IF(opportunity_quality IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY opportunity_quality)) p_quality,
  IF(snap_share IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY snap_share)) p_snap,
  IF(snap_stability IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY snap_stability)) p_stability,
  IF(availability IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY availability)) p_avail,
  IF(ngs_efficiency IS NULL,NULL,PERCENT_RANK() OVER(PARTITION BY target_season,position ORDER BY ngs_efficiency)) p_ngs
 FROM joined
)
SELECT target_season-1 season,target_season,position,player_id,player_name,target_points,target_ppg,
 profile_points,opportunity,efficiency,role_stability,gng_weighted_opportunity,
 receiving_fd_rate,rushing_fd_rate,passing_fd_rate,high_value_first_down,
 passing_epa,receiving_epa,rushing_epa,xfp_share,opportunity_quality,snap_share,
 snap_stability,availability,ngs_efficiency,
 p_points,p_opp,p_eff,p_role,p_gng_opp,p_fd,p_hvfd,p_epa,p_xfp,p_quality,p_snap,p_stability,p_avail,p_ngs,
 p_points h1_profile_points,
 .45*p_points+.30*p_opp+.15*p_eff+.10*p_role h2_standard_opportunity,
 .35*p_points+.40*p_gng_opp+.15*p_opp+.10*p_epa h3_gng_weighted_opportunity,
 .30*p_points+.25*p_gng_opp+.15*p_fd+.15*p_hvfd+.10*p_epa+.05*p_quality h4_bonus_first_down,
 .25*p_points+.20*p_gng_opp+.10*p_fd+.10*p_xfp+.10*p_quality+.08*p_snap+.07*p_stability+.05*p_avail+.05*p_ngs h5_stability_hybrid
FROM pct
"""
 rows=[dict(r) for r in client.query(sql).result()]
 for row in rows:
  row["h1_profile_points"]=row["p_points"]
  row["h2_standard_opportunity"]=weighted_average(row,(("p_points",.45),("p_opp",.30),("p_eff",.15),("p_role",.10)))
  row["h3_gng_weighted_opportunity"]=weighted_average(row,(("p_points",.35),("p_gng_opp",.40),("p_opp",.15),("p_epa",.10)))
  row["h4_bonus_first_down"]=weighted_average(row,(("p_points",.30),("p_gng_opp",.25),("p_fd",.15),("p_hvfd",.15),("p_epa",.10),("p_quality",.05)))
  row["h5_stability_hybrid"]=weighted_average(row,(("p_points",.25),("p_gng_opp",.20),("p_fd",.10),("p_xfp",.10),("p_quality",.10),("p_snap",.08),("p_stability",.07),("p_avail",.05),("p_ngs",.05)))
  row["rb_h1_h4_80_20"]=.8*row["h1_profile_points"]+.2*row["h4_bonus_first_down"]
 for season in (2022,2023,2024):
  wr_fold=[row for row in rows if row["position"]=="WR" and row["season"]==season]
  elite_ids={row["player_id"] for row in sorted(wr_fold,key=lambda row:(-row["h3_gng_weighted_opportunity"],row["player_name"]))[:12]}
  for row in wr_fold:
   row["wr_h3_top12_h5_rest"]=2+row["h3_gng_weighted_opportunity"] if row["player_id"] in elite_ids else row["h5_stability_hybrid"]
 result={"coverage":{},"results":{},"scored_rows":[]}
 for position in ("QB","RB","WR","TE"):
  pos=[r for r in rows if r["position"]==position]
  coverage_fields=("profile_points","opportunity","efficiency","role_stability",
   "gng_weighted_opportunity","receiving_fd_rate","rushing_fd_rate","passing_fd_rate",
   "high_value_first_down","passing_epa","receiving_epa","rushing_epa","xfp_share",
   "opportunity_quality","snap_share","snap_stability","availability","ngs_efficiency")
  result["coverage"][position]={
   "rows":len(pos),
   "raw_features":{field:sum(r.get(field) is not None for r in pos) for field in coverage_fields},
   "hypothesis_scores":{h:sum(r.get(h) is not None for r in pos) for h in HYPOTHESES},
  }
  for h in HYPOTHESES:
   folds={}
   for season in (2022,2023,2024):
    fold=[{"player_id":r["player_id"],"player_name":r["player_name"],"score":r[h],"target_ppg":r["target_ppg"],"target_points":r["target_points"]} for r in pos if r["season"]==season and r.get(h) is not None]
    folds[f"{season}_to_{season+1}"]=summarize(fold)
   audits={}
   for season in (2022,2023,2024):
    fold=[{"player_id":r["player_id"],"player_name":r["player_name"],"score":r[h],"target_ppg":r["target_ppg"],"target_points":r["target_points"]} for r in pos if r["season"]==season and r.get(h) is not None]
    audits[f"{season}_to_{season+1}"]=player_audit(fold)
   fields=("spearman","pairwise","top12_precision","top24_precision","points_at_12","points_at_24","ndcg_at_24")
   agg={f"average_{f}":mean(v[f] for v in folds.values()) for f in fields}; agg["total_elite_misses"]=sum(v["elite_misses"] for v in folds.values()); agg["total_top12_busts"]=sum(v["top12_busts"] for v in folds.values())
   result["results"][f"{position}_{h}"]={"aggregate":agg,"folds":folds,"player_audit":audits}
  if position=="TE":
   result["scored_rows"].extend({"season":r["season"],"position":"TE","player_id":r["player_id"],"player_name":r["player_name"],"target_ppg":r["target_ppg"],"h5_stability_hybrid":r["h5_stability_hybrid"]} for r in pos)
 shortlist={"QB":("h1_profile_points","h2_standard_opportunity"),"RB":("h1_profile_points","rb_h1_h4_80_20"),"WR":("h3_gng_weighted_opportunity","h5_stability_hybrid","wr_h3_top12_h5_rest"),"TE":("h2_standard_opportunity","h5_stability_hybrid")}
 for position,candidates in shortlist.items():
  pos=[row for row in rows if row["position"]==position]
  for candidate in candidates:
   folds={}; audits={}
   for season in (2022,2023,2024):
    fold=[{"player_id":r["player_id"],"player_name":r["player_name"],"score":r[candidate],"target_ppg":r["target_ppg"],"target_points":r["target_points"]} for r in pos if r["season"]==season]
    key=f"{season}_to_{season+1}"; folds[key]=summarize(fold); audits[key]=player_audit(fold)
   fields=("spearman","pairwise","top12_precision","top24_precision","points_at_12","points_at_24","ndcg_at_24")
   agg={f"average_{field}":mean(fold[field] for fold in folds.values()) for field in fields}; agg["total_elite_misses"]=sum(fold["elite_misses"] for fold in folds.values()); agg["total_top12_busts"]=sum(fold["top12_busts"] for fold in folds.values())
   result.setdefault("shortlist",{})[f"{position}_{candidate}"]={"aggregate":agg,"folds":folds,"player_audit":audits}
 parser_output={k:v["aggregate"] for k,v in result["results"].items()}; args.json_output.parent.mkdir(parents=True,exist_ok=True); args.json_output.write_text(json.dumps(result,indent=2,default=str)+"\n",encoding="utf-8"); print(json.dumps(parser_output,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
