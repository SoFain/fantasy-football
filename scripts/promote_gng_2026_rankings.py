"""Guarded promotion package for 2026 GNG positional and unified rankings."""
from __future__ import annotations

import argparse,os
from datetime import datetime,timezone

from google.cloud import bigquery


WRITE_GATE="ALLOW_GNG_2026_PRODUCTION_PROMOTION"


def build_sql(project,brain,metrics,version):
    live=f"`{project}.{brain}.analytics_pigskin_rankings`";unified=f"`{project}.{brain}.unified_draft_rankings_current`"
    positional=f"`{project}.{metrics}.gng_2026_positional_boards_with_rookies`";overall=f"`{project}.{metrics}.unified_gng_2026_top150_review`"
    return f"""
BEGIN TRANSACTION;
UPDATE {live} SET is_active=FALSE
WHERE is_active AND scoring_profile_id='gng_keeper' AND league_type_id='redraft' AND roster_format_id='one_qb';
INSERT INTO {live}
 (ranking_version,generated_at,adjudicated_at,season,ranking_phase,format,position,rank,tier,
  player_id,player_name,current_team,stat_season,ranking_score,raw_ranking_score,candidate_rank,
  candidate_ranking_score,rank_rationale,pigskin_verdict,what_would_change_mind,risk_flags,
  model_name,prompt_version,data_snapshot_label,is_active,sleeper_player_id,sleeper_team,sleeper_active,
  sleeper_status,sleeper_injury_status,sleeper_depth_chart_position,sleeper_depth_chart_order,
  ranking_eligibility,rank_source,model_run_id,scoring_profile_id,league_type_id,roster_format_id,
  llm_adjustment_code,llm_adjustment_detail,llm_adjustment_evidence,llm_rank_delta)
SELECT '{version}',CURRENT_TIMESTAMP(),CURRENT_TIMESTAMP(),2026,'preseason','GNG Keeper',position,rank,
 CASE WHEN rank<=12 THEN 'elite' WHEN rank<=24 THEN 'starter' ELSE 'depth' END,
 player_id,player_name,current_team,2025,ROUND(100-0.5*rank,1),formula_score,rank,current_score,
 CONCAT('Deterministic ',formula_id,' with current Sleeper context.'),'FORMULA_LOCKED',
 'Revisit on team, depth-chart, injury evidence, or rookie-system change.',sleeper_review_flags_json,
 formula_id,'gng-2026-v1','2023-2025 plus Sleeper 2026-07-11',TRUE,CAST(sleeper_player_id AS STRING),current_team,
 sleeper_active,sleeper_status,sleeper_injury_status,sleeper_depth_chart_position,sleeper_depth_chart_order,
 IF(rank_source='market_rookie_overlay','rookie_overlay','eligible_current_sleeper_player'),rank_source,
 '{version}','gng_keeper','redraft','one_qb','NONE','No LLM adjustment','Deterministic formula and Sleeper layer',0
FROM {positional};
DELETE FROM {unified} WHERE scoring_profile_id='gng_keeper';
INSERT INTO {unified}
 (board_version,generated_at,scoring_profile_id,overall_rank,player_id,player_name,current_team,position,
  position_rank,projected_ppg,replacement_rank,replacement_ppg,vorp,availability_multiplier,
  onesie_multiplier,adjusted_vorp,position_source_version,position_rank_source,risk_flags,qb_backtest_proxy_disclosed)
SELECT '{version}',CURRENT_TIMESTAMP(),'gng_keeper',overall_rank,player_id,player_name,current_team,position,
 position_rank,projected_ppg,replacement_rank,replacement_ppg,vorp,availability_multiplier,
 onesie_multiplier,adjusted_vorp,formula_id,rank_source,guardrail_labels,FALSE
FROM {overall};
COMMIT TRANSACTION;
"""


def main():
 p=argparse.ArgumentParser();p.add_argument("--project",default="fantasy-football-498121");p.add_argument("--brain-dataset",default="fantasy_football_brain");p.add_argument("--metrics-dataset",default="fantasy_football_advanced_metrics");p.add_argument("--apply",action="store_true");args=p.parse_args()
 client=bigquery.Client(project=args.project);version="gng-formula-2026-"+datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
 preflight=f"""SELECT
 (SELECT COUNT(*) FROM `{args.project}.{args.metrics_dataset}.gng_2026_positional_boards_with_rookies`) positional_rows,
 (SELECT COUNT(*) FROM `{args.project}.{args.metrics_dataset}.unified_gng_2026_top150_review`) unified_rows,
 (SELECT COUNTIF(sleeper_hard_review) FROM `{args.project}.{args.metrics_dataset}.unified_gng_2026_top150_review`) hard_reviews,
 (SELECT COUNTIF(current_team IS NULL) FROM `{args.project}.{args.metrics_dataset}.gng_2026_positional_boards_with_rookies`) teamless_positional,
 (SELECT COUNTIF(current_team IS NULL) FROM `{args.project}.{args.metrics_dataset}.unified_gng_2026_top150_review`) teamless_unified,
 (SELECT COUNT(*) FROM (
   SELECT position,COUNT(*) row_count,COUNT(DISTINCT rank) distinct_ranks,MIN(rank) min_rank,MAX(rank) max_rank
   FROM `{args.project}.{args.metrics_dataset}.gng_2026_positional_boards_with_rookies`
   GROUP BY position
   HAVING row_count!=distinct_ranks OR min_rank!=1 OR max_rank!=row_count
 )) noncontiguous_positions,
 (SELECT COUNT(*) FROM `{args.project}.{args.metrics_dataset}.unified_gng_2026_top150_review` overall
   JOIN `{args.project}.{args.metrics_dataset}.gng_2026_positional_boards_with_rookies` positional
     USING(player_id,position)
   WHERE overall.position_rank!=positional.rank) queue_mismatches"""
 state=dict(next(iter(client.query(preflight).result())))
 if state!={"positional_rows":260,"unified_rows":150,"hard_reviews":0,"teamless_positional":0,"teamless_unified":0,"noncontiguous_positions":0,"queue_mismatches":0}: raise RuntimeError(f"Preflight failed: {state}")
 sql=build_sql(args.project,args.brain_dataset,args.metrics_dataset,version)
 if not args.apply:
  job=client.query(sql,job_config=bigquery.QueryJobConfig(dry_run=True,use_query_cache=False));print({"dry_run":True,"bytes":job.total_bytes_processed,"preflight":state,"version":version});return 0
 if os.getenv(WRITE_GATE)!="true": raise PermissionError(f"{WRITE_GATE}=true is required")
 rollback=f"""CREATE OR REPLACE TABLE `{args.project}.{args.metrics_dataset}.gng_2026_production_rollback_positional` AS SELECT * FROM `{args.project}.{args.brain_dataset}.analytics_pigskin_rankings` WHERE is_active AND scoring_profile_id='gng_keeper'; CREATE OR REPLACE TABLE `{args.project}.{args.metrics_dataset}.gng_2026_production_rollback_unified` AS SELECT * FROM `{args.project}.{args.brain_dataset}.unified_draft_rankings_current` WHERE scoring_profile_id='gng_keeper';"""
 client.query(rollback).result();client.query(sql).result();print({"applied":True,"version":version,"preflight":state});return 0


if __name__=="__main__": raise SystemExit(main())
