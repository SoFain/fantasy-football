"""Build isolated 2026 GNG positional candidate boards with Sleeper context."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
import sys

from google.cloud import bigquery

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_gng_advanced_hypotheses import weighted_average
from scripts.run_gng_position_candidate_expansion import percent_ranks
from src.ranking_owner_decisions import GNG_WATCHLIST_NAMES


FORMULAS = {
    "QB": ("q4_gng_bonus_proxy", {"profile": .30, "passing_yards": .15, "passing_fd_expected": .15, "qb_rushing": .15, "qb_ngs_efficiency": .10, "passing_cpoe": .05, "attempts": .10}),
    "RB": ("r7_h1_r2_compromise", {"profile": .65, "gng_weighted_opp": .125, "target_share": .05, "wopr": .04, "receiving_fd_expected": .035, "rushing_fd_expected": .035, "goal_line_opps": .04, "snap_share": .025}),
    "WR": ("w10_h5_floor_first", {"profile": .30, "gng_weighted_opp": .20, "xfp_share": .10, "opportunity_quality": .08, "snap_share": .08, "snap_stability": .08, "availability": .06, "receiving_fd_expected": .05, "target_share": .03, "wopr": .02}),
    "TE": ("h5_stability_hybrid", {"profile": .25, "gng_weighted_opp": .20, "first_down_any": .10, "xfp_share": .10, "opportunity_quality": .10, "snap_share": .08, "snap_stability": .07, "availability": .05, "ngs_any": .05}),
}
LIMITS = {"QB": 45, "RB": 80, "WR": 100, "TE": 35}
WATCHLIST_NAMES = GNG_WATCHLIST_NAMES


def build_query(project, brain, metrics):
    return f"""
WITH identity_keys AS (
 SELECT key,REGEXP_REPLACE(COALESCE(gsis_id,player_id_internal),r'^(gsis|sleeper):','') canonical_player_id,
  sleeper_player_id,source_confidence,updated_at
 FROM `{project}.{brain}.player_identity_bridge`
 CROSS JOIN UNNEST([REGEXP_REPLACE(player_id_internal,r'^(gsis|sleeper):',''),gsis_id,sleeper_player_id]) key
 WHERE key IS NOT NULL
 QUALIFY ROW_NUMBER() OVER(PARTITION BY key ORDER BY source_confidence DESC,updated_at DESC)=1
), points_raw AS (
 SELECT REGEXP_REPLACE(player_id_internal,r'^(gsis|sleeper):','') player_id,ANY_VALUE(player_display_name HAVING MAX season) player_name,
  ANY_VALUE(team HAVING MAX season) source_team,position,AVG(total_fantasy_points) profile,
  COUNTIF(season=2025) current_games
 FROM `{project}.{brain}.analytics_player_fantasy_points_by_profile`
 WHERE scoring_profile_id='gng_keeper' AND COALESCE(league_type_id,'redraft')='redraft'
  AND COALESCE(roster_format_id,'one_qb')='one_qb'
  AND season BETWEEN 2023 AND 2025 AND position IN ('QB','RB','WR','TE')
 GROUP BY player_id,position HAVING current_games>=4
), points AS (
 SELECT points_raw.* EXCEPT(player_id),COALESCE(identity_keys.canonical_player_id,points_raw.player_id) player_id
 FROM points_raw LEFT JOIN identity_keys ON identity_keys.key=points_raw.player_id
), adv AS (
 SELECT REGEXP_REPLACE(player_id_internal,r'^(gsis|sleeper):','') player_id,position,
  AVG(weighted_opportunity_gng_keeper) gng_weighted_opp,AVG(passing_yards) passing_yards,
  AVG(passing_cpoe) passing_cpoe,AVG(qb_rushing_baseline_score) qb_rushing,AVG(attempts) attempts,
  AVG(goal_line_opportunities) goal_line_opps,AVG(target_share) target_share,AVG(wopr) wopr,
  AVG(offensive_snap_share) snap_share,AVG(snap_role_stability) snap_stability,AVG(availability_score) availability
 FROM `{project}.{brain}.player_season_advanced_metrics`
 WHERE metric_version='advanced_player_metrics_v1' AND season_type='REG' AND season BETWEEN 2023 AND 2025
 GROUP BY player_id,position
), pbp AS (
 SELECT REGEXP_REPLACE(player_id_internal,r'^(gsis|sleeper):','') player_id,position,
  AVG(receiving_xfp_share) receiving_xfp_share,AVG(rushing_xfp_share) rushing_xfp_share,
  AVG(opportunity_quality_score) opportunity_quality,AVG(receiving_first_down_exp_pbp) receiving_fd_expected,
  AVG(rushing_first_down_exp_pbp) rushing_fd_expected,AVG(passing_first_down_exp_pbp) passing_fd_expected
 FROM `{project}.{brain}.player_week_pbp_opportunity_metrics`
 WHERE source_version='ffopportunity_pbp_latest' AND season BETWEEN 2023 AND 2025
 GROUP BY player_id,position
), ngs AS (
 SELECT REGEXP_REPLACE(player_id_internal,r'^(gsis|sleeper):','') player_id,position,
  AVG(ngs_passing_efficiency_score) qb_ngs_efficiency,AVG(ngs_receiving_efficiency_score) receiving_ngs,
  AVG(ngs_rushing_efficiency_score) rushing_ngs
 FROM `{project}.{brain}.player_week_ngs_metrics`
 WHERE source_version='nflverse_ngs_direct_latest' AND season BETWEEN 2023 AND 2025
 GROUP BY player_id,position
), sleeper AS (
 SELECT *,REGEXP_REPLACE(LOWER(player_name),r'[^a-z0-9]','') normalized_name,
  COUNT(*) OVER(PARTITION BY REGEXP_REPLACE(LOWER(player_name),r'[^a-z0-9]',''),position) normalized_name_count
 FROM `{project}.{metrics}.v_ranking_post_formula_safety`
), bridge AS (
 SELECT key player_id,sleeper_player_id,source_confidence,updated_at
 FROM `{project}.{brain}.player_identity_bridge`
 CROSS JOIN UNNEST([REGEXP_REPLACE(player_id_internal,r'^(gsis|sleeper):',''),gsis_id,sleeper_player_id]) key
 WHERE sleeper_player_id IS NOT NULL AND key IS NOT NULL
 QUALIFY ROW_NUMBER() OVER(PARTITION BY key ORDER BY source_confidence DESC,updated_at DESC)=1
), aliases AS (
 SELECT '00-0037157' player_id,'8122' sleeper_player_id UNION ALL
 SELECT '00-0039373','11579' UNION ALL
 SELECT '00-0036988','7670'
)
SELECT points.*,adv.* EXCEPT(player_id,position),pbp.* EXCEPT(player_id,position),ngs.* EXCEPT(player_id,position),
 COALESCE(pbp.receiving_xfp_share,pbp.rushing_xfp_share) xfp_share,
 COALESCE(pbp.receiving_fd_expected,pbp.rushing_fd_expected,pbp.passing_fd_expected) first_down_any,
 COALESCE(ngs.receiving_ngs,ngs.rushing_ngs,ngs.qb_ngs_efficiency) ngs_any,
 sleeper.sleeper_player_id,sleeper.team sleeper_team,sleeper.active sleeper_active,sleeper.status sleeper_status,
 sleeper.injury_status sleeper_injury_status,sleeper.depth_chart_position sleeper_depth_chart_position,
 sleeper.depth_chart_order sleeper_depth_chart_order,sleeper.years_exp sleeper_years_exp,sleeper.fetched_at sleeper_fetched_at,
 sleeper.post_formula_adjustment sleeper_role_adjustment,sleeper.sleeper_hard_review,
 sleeper.review_flags_json sleeper_review_flags_json
FROM points
LEFT JOIN adv USING(player_id,position)
LEFT JOIN pbp USING(player_id,position)
LEFT JOIN ngs USING(player_id,position)
LEFT JOIN bridge USING(player_id)
LEFT JOIN aliases USING(player_id)
LEFT JOIN sleeper ON sleeper.position=points.position AND (
 sleeper.sleeper_player_id=COALESCE(aliases.sleeper_player_id,bridge.sleeper_player_id) OR
 (COALESCE(aliases.sleeper_player_id,bridge.sleeper_player_id) IS NULL AND sleeper.normalized_name_count=1
  AND sleeper.normalized_name=REGEXP_REPLACE(LOWER(points.player_name),r'[^a-z0-9]','')))
"""


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--project",default="fantasy-football-498121")
    parser.add_argument("--brain-dataset",default="fantasy_football_brain")
    parser.add_argument("--metrics-dataset",default="fantasy_football_advanced_metrics")
    parser.add_argument("--table",default="gng_2026_positional_candidate_boards")
    parser.add_argument("--output",type=Path,default=Path("output/gng-2026-positional-candidate-boards.json"))
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args(); client=bigquery.Client(project=args.project)
    rows=[dict(row) for row in client.query(build_query(args.project,args.brain_dataset,args.metrics_dataset)).result()]
    live_position_ranks={(row["position"],re.sub(r"[^a-z0-9]","",row["player_name"].lower())):row["rank"] for row in map(dict,client.query(f"""
SELECT position,player_name,rank FROM `{args.project}.{args.brain_dataset}.analytics_pigskin_rankings`
WHERE is_active AND scoring_profile_id='gng_keeper' AND position IN ('QB','RB','WR','TE')
""").result())}
    generated_at=datetime.now(timezone.utc).isoformat(); candidate_pool=[]; unranked_watchlist=[]
    for position,(formula,weights) in FORMULAS.items():
        candidates=[row for row in rows if row["position"]==position]
        for field in weights:
            ranks=percent_ranks(candidates,field)
            for index,row in enumerate(candidates): row[f"p_{field}"]=ranks.get(index)
        scored=[]
        for row in candidates:
            base=weighted_average(row,tuple((f"p_{field}",weight) for field,weight in weights.items()))
            row["formula_score"]=base
            row["current_score"]=base+(row.get("sleeper_role_adjustment") or 0.0) if base is not None else None
            row["formula_id"]=formula
            row["sleeper_hard_review"]=row.get("sleeper_hard_review") is not False
            row["sleeper_review_flags_json"]=row.get("sleeper_review_flags_json") or '["SLEEPER_CONTEXT_MISSING"]'
            scored.append(row)
        scored.sort(key=lambda row:(-(row["current_score"] or -1),row["player_name"]))
        rank=0
        for formula_rank,row in enumerate(scored,1):
            item={
                "generated_at":generated_at,"season":2026,"scoring_profile_id":"gng_keeper","position":position,
                "rank":None,"formula_rank":formula_rank,"player_id":row["player_id"],"player_name":row["player_name"],"source_team":row["source_team"],
                "current_team":row.get("sleeper_team"),"formula_id":formula,"formula_score":row["formula_score"],
                "sleeper_role_adjustment":row["sleeper_role_adjustment"],"current_score":row["current_score"],
                "sleeper_player_id":row.get("sleeper_player_id"),"sleeper_active":row.get("sleeper_active"),
                "sleeper_status":row.get("sleeper_status"),"sleeper_injury_status":row.get("sleeper_injury_status"),
                "sleeper_depth_chart_position":row.get("sleeper_depth_chart_position"),"sleeper_depth_chart_order":row.get("sleeper_depth_chart_order"),
                "sleeper_hard_review":row["sleeper_hard_review"],"sleeper_review_flags_json":row["sleeper_review_flags_json"],
                "sleeper_fetched_at":row.get("sleeper_fetched_at").isoformat() if row.get("sleeper_fetched_at") else None,
            }
            no_current_team=not row.get("sleeper_team")
            teamless="SLEEPER_TEAMLESS" in row["sleeper_review_flags_json"]
            owner_watchlist=row["player_name"] in WATCHLIST_NAMES and row["sleeper_hard_review"]
            if no_current_team or owner_watchlist:
                item["watchlist_reason"]=(
                    "TEAMLESS_UNRANKED"
                    if teamless
                    else "CURRENT_TEAM_UNKNOWN_UNRANKED"
                    if no_current_team
                    else "OWNER_APPROVED_WATCHLIST"
                )
                unranked_watchlist.append(item)
                continue
            rank+=1;item["rank"]=rank;candidate_pool.append(item)
            if rank>=LIMITS[position]+25: break
    board=[row for row in candidate_pool if row["rank"]<=LIMITS[row["position"]]]
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(board,indent=2)+"\n",encoding="utf-8")
    rookie_query=f"""
WITH sleeper AS (
 SELECT *,REGEXP_REPLACE(LOWER(full_name),r'[^a-z0-9]','') normalized_name
 FROM `{args.project}.{args.metrics_dataset}.sleeper_current_player_context`
 WHERE active AND team IS NOT NULL AND status IN ('Active','ACT') AND years_exp=0
  AND position IN ('QB','RB','WR','TE')
 QUALIFY ROW_NUMBER() OVER(PARTITION BY sleeper_player_id ORDER BY fetched_at DESC)=1
), market AS (
 SELECT *,REGEXP_REPLACE(LOWER(display_name),r'[^a-z0-9]','') normalized_name
 FROM `{args.project}.{args.brain_dataset}.market_consensus_baseline_current`
 WHERE season=2026 AND scoring_profile_id='ppr' AND source_id='manual_market_values'
 QUALIFY ROW_NUMBER() OVER(PARTITION BY position,REGEXP_REPLACE(LOWER(display_name),r'[^a-z0-9]','') ORDER BY updated_at DESC)=1
)
SELECT sleeper.sleeper_player_id,sleeper.full_name player_name,sleeper.position,sleeper.team current_team,
 sleeper.status,sleeper.injury_status,sleeper.depth_chart_position,sleeper.depth_chart_order,
 sleeper.years_exp,sleeper.fetched_at,market.rank_position market_position_rank,
 market.rank_overall market_overall_rank,market.market_value
FROM sleeper LEFT JOIN market USING(normalized_name,position)
ORDER BY position,COALESCE(market.rank_position,999),COALESCE(depth_chart_order,99),player_name
"""
    rookie_rows=[]
    rookie_counts={position:0 for position in FORMULAS}
    for row in client.query(rookie_query).result():
        item=dict(row);rookie_counts[item["position"]]+=1
        item.update({"generated_at":generated_at,"season":2026,"scoring_profile_id":"gng_keeper","formula_id":FORMULAS[item["position"]][0],"review_flag":"ROOKIE_CONTEXT_REQUIRED"})
        item["fetched_at"]=item["fetched_at"].isoformat() if item.get("fetched_at") else None
        rookie_rows.append(item)
    merged=[]
    for position in FORMULAS:
        entries=[]
        for veteran in (row for row in candidate_pool if row["position"]==position):
            item=dict(veteran);item["merge_priority"]=float(veteran["rank"]);item["rank_source"]="gng_formula";entries.append(item)
        for rookie in (row for row in rookie_rows if row["position"]==position and row.get("market_position_rank") is not None):
            depth=rookie.get("depth_chart_order");penalty=0 if depth==1 else 3 if depth==2 else 10 if depth==3 else 20
            priority=float(rookie["market_position_rank"]+penalty)
            if priority>LIMITS[position]: continue
            entries.append({"generated_at":generated_at,"season":2026,"scoring_profile_id":"gng_keeper","position":position,
             "player_id":f"sleeper:{rookie['sleeper_player_id']}","player_name":rookie["player_name"],"source_team":None,
             "current_team":rookie["current_team"],"formula_id":FORMULAS[position][0],"formula_score":None,
             "sleeper_role_adjustment":0.0,"current_score":None,"sleeper_player_id":rookie["sleeper_player_id"],
             "sleeper_active":True,"sleeper_status":rookie["status"],"sleeper_injury_status":rookie["injury_status"],
             "sleeper_depth_chart_position":rookie["depth_chart_position"],"sleeper_depth_chart_order":depth,
             "sleeper_hard_review":False,"sleeper_review_flags_json":json.dumps(["ROOKIE_CONTEXT_REQUIRED"]),
             "sleeper_fetched_at":rookie["fetched_at"],"merge_priority":priority,"rank_source":"market_rookie_overlay"})
        if position=="WR":
            for row in entries:
                live_rank=live_position_ranks.get(("WR",re.sub(r"[^a-z0-9]","",row["player_name"].lower())))
                row["live_position_rank"]=live_rank
                if live_rank is not None and live_rank<=6: row["merge_priority"]=min(row["merge_priority"],6+live_rank)
                elif live_rank is not None and live_rank<=12: row["merge_priority"]=min(row["merge_priority"],12+live_rank)
        entries.sort(key=lambda row:(row["merge_priority"],row["rank_source"]=="market_rookie_overlay",row["player_name"]))
        for rank,item in enumerate(entries[:LIMITS[position]],1): item["rank"]=rank;merged.append(item)
    if args.apply:
        table_id=f"{args.project}.{args.metrics_dataset}.{args.table}"
        config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE",autodetect=True)
        client.load_table_from_json(board,table_id,job_config=config).result()
        rookie_table=f"{args.project}.{args.metrics_dataset}.gng_2026_rookie_review"
        if rookie_rows:
            client.load_table_from_json(rookie_rows,rookie_table,job_config=config).result()
        merged_table=f"{args.project}.{args.metrics_dataset}.gng_2026_positional_boards_with_rookies"
        client.load_table_from_json(merged,merged_table,job_config=config).result()
        client.load_table_from_json(unranked_watchlist,f"{args.project}.{args.metrics_dataset}.gng_2026_unranked_watchlist",job_config=config).result()
        review_sql=f"""
CREATE OR REPLACE TABLE `{args.project}.{args.metrics_dataset}.gng_2026_top30_review` AS
WITH live AS (
 SELECT position,rank live_rank,player_name,
  REGEXP_REPLACE(LOWER(player_name),r'[^a-z0-9]','') normalized_name
 FROM `{args.project}.{args.brain_dataset}.analytics_pigskin_rankings`
 WHERE is_active AND scoring_profile_id='gng_keeper'
), board AS (
 SELECT *,REGEXP_REPLACE(LOWER(player_name),r'[^a-z0-9]','') normalized_name
 FROM `{merged_table}` WHERE rank<=30
)
SELECT board.position,board.rank candidate_rank,live.live_rank,
 live.live_rank-board.rank rank_delta,board.player_id,board.player_name,board.current_team,
 board.rank_source,board.formula_id,board.formula_score,board.current_score,
 board.sleeper_injury_status,board.sleeper_hard_review,board.sleeper_review_flags_json,
 ARRAY_TO_STRING(ARRAY(
  SELECT reason FROM UNNEST([
   IF(board.sleeper_hard_review,'SLEEPER_HARD_REVIEW',NULL),
   IF(board.sleeper_injury_status IS NOT NULL,'INJURY_REVIEW',NULL),
   IF(board.rank_source='market_rookie_overlay','ROOKIE_OVERLAY',NULL),
   IF(ABS(COALESCE(live.live_rank-board.rank,0))>=10,'LIVE_RANK_DELTA_10_PLUS',NULL),
   IF(live.live_rank IS NULL,'NOT_ON_LIVE_GNG_BOARD',NULL)
  ]) reason WHERE reason IS NOT NULL
 ),'|') review_reasons
FROM board LEFT JOIN live USING(position,normalized_name)
ORDER BY board.position,board.rank
"""
        client.query(review_sql).result()
    summary={position:{"rows":sum(row["position"]==position for row in board),"hard_reviews":sum(row["position"]==position and row["sleeper_hard_review"] for row in board),"flagged":sum(row["position"]==position and row["sleeper_review_flags_json"]!="[]" for row in board)} for position in FORMULAS}
    inserted={position:sum(row["position"]==position and row["rank_source"]=="market_rookie_overlay" for row in merged) for position in FORMULAS}
    no_team_counts={position:sum(row["position"]==position and row["current_team"] is None for row in unranked_watchlist) for position in FORMULAS}
    print(json.dumps({"applied":args.apply,"table":f"{args.project}.{args.metrics_dataset}.{args.table}","summary":summary,"no_current_team_unranked":no_team_counts,"rookie_review":rookie_counts,"rookies_inserted":inserted},indent=2));return 0


if __name__=="__main__": raise SystemExit(main())
