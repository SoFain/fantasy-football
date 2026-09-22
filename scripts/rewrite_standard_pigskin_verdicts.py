"""Rewrite active Standard Pigskin verdicts with Gemini without changing ranks."""
from __future__ import annotations

import argparse,json,os
from datetime import datetime,timezone
from pathlib import Path

from google import genai
from google.genai import types
from google.cloud import bigquery


WRITE_GATE="ALLOW_STANDARD_VERDICT_REWRITE"
LIMITS={"QB":45,"RB":80,"WR":100,"TE":35}


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--project",default="fantasy-football-498121");parser.add_argument("--dataset",default="fantasy_football_brain");parser.add_argument("--metrics-dataset",default="fantasy_football_advanced_metrics");parser.add_argument("--model",default=os.environ.get("GEMINI_MODEL","gemini-3.5-flash"));parser.add_argument("--output",type=Path,default=Path("output/standard-pigskin-verdict-refresh.json"));parser.add_argument("--apply",action="store_true");args=parser.parse_args()
    api_key=os.environ.get("GEMINI_API_KEY");
    if not api_key: raise RuntimeError("GEMINI_API_KEY is required")
    warehouse=bigquery.Client(project=args.project)
    rows=[dict(row) for row in warehouse.query(f"""
SELECT ranking_version,player_id,player_name,current_team,position,rank,tier,ranking_score,
 avg_ppr,avg_opportunity,avg_efficiency,avg_total_epa,avg_wopr,avg_target_share,avg_carry_share,
 sleeper_depth_chart_order,sleeper_injury_status,rank_source,risk_flags
FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings`
WHERE is_active AND scoring_profile_id='standard' AND rank<=CASE position
 WHEN 'QB' THEN 45 WHEN 'RB' THEN 80 WHEN 'WR' THEN 100 WHEN 'TE' THEN 35 ELSE 0 END
ORDER BY position,rank
""").result()]
    if len(rows)!=260: raise RuntimeError(f"Expected 260 Standard display rows, got {len(rows)}")
    client=genai.Client(api_key=api_key);verdicts=[]
    for start in range(0,len(rows),20):
        batch=rows[start:start+20]
        prompt="""You are Pigskin, a sharp fantasy-football analyst. Return a JSON array with one object per supplied player: player_id, position, verdict. Write one specific 18-40 word verdict grounded only in supplied metrics. Defend or critically explain the listed Standard rank. Do not propose a different rank, invent injury recovery, use markdown, or mention missing data. Avoid repeated templates.\nPLAYERS:\n"""+json.dumps(batch,default=str)
        response=client.models.generate_content(model=args.model,contents=prompt,config=types.GenerateContentConfig(response_mime_type="application/json"))
        parsed=json.loads(response.text)
        if not isinstance(parsed,list): raise ValueError("Gemini verdict response must be a JSON array")
        verdicts.extend(parsed)
    expected={(row["player_id"],row["position"]) for row in rows};seen=set();clean=[]
    for item in verdicts:
        key=(str(item.get("player_id") or ""),str(item.get("position") or ""));verdict=" ".join(str(item.get("verdict") or "").split())
        if key not in expected or key in seen: raise ValueError(f"Unexpected or duplicate verdict key: {key}")
        if not 12<=len(verdict.split())<=50: raise ValueError(f"Verdict length failed for {key}: {verdict}")
        seen.add(key);clean.append({"player_id":key[0],"position":key[1],"pigskin_verdict":verdict})
    if seen!=expected: raise ValueError(f"Missing {len(expected-seen)} verdicts")
    payload={"generated_at":datetime.now(timezone.utc).isoformat(),"model":args.model,"rows":clean};args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    if not args.apply: print(json.dumps({"generated":len(clean),"applied":False,"model":args.model}));return 0
    if os.environ.get(WRITE_GATE)!="true": raise PermissionError(f"{WRITE_GATE}=true is required")
    rollback=f"{args.project}.{args.metrics_dataset}.standard_pigskin_verdict_rollback_20260712";stage=f"{args.project}.{args.metrics_dataset}.standard_pigskin_verdict_refresh_stage"
    warehouse.query(f"CREATE OR REPLACE TABLE `{rollback}` AS SELECT ranking_version,player_id,position,pigskin_verdict FROM `{args.project}.{args.dataset}.analytics_pigskin_rankings` WHERE is_active AND scoring_profile_id='standard'").result()
    warehouse.load_table_from_json(clean,stage,job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE",autodetect=True)).result()
    warehouse.query(f"""UPDATE `{args.project}.{args.dataset}.analytics_pigskin_rankings` target SET pigskin_verdict=source.pigskin_verdict,model_name=CONCAT(COALESCE(model_name,''),'|verdict:{args.model}') FROM `{stage}` source WHERE target.is_active AND target.scoring_profile_id='standard' AND target.player_id=source.player_id AND target.position=source.position""").result()
    print(json.dumps({"generated":len(clean),"applied":True,"model":args.model,"rollback":rollback}));return 0


if __name__=="__main__": raise SystemExit(main())
