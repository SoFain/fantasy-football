"""Read-only, held-out tested in-season shrinkage candidates. Never promotes boards."""
from __future__ import annotations
import argparse
import hashlib
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
import uuid
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import nflreadpy as nfl
from google.cloud import bigquery
from src.load import get_bigquery_client

VERSION = "inseason_observed_ppg_shrinkage_v1"
PROFILES = {"standard": 0.0, "half_ppr": 0.5, "ppr": 1.0}
GRID = [0, 1, 2, 4, 8, 16, 32, 1000000]


def base_sql(project: str, season: int = 2026, as_of_week: int = 2, rolling: bool = False, gng_table: str | None = None) -> str:
    cutoffs = 'GENERATE_ARRAY(1,17)' if rolling else f'[{as_of_week}]'
    gng_union = f"""UNION ALL
 SELECT season,week,player_id,player_name,position,team,score AS points,0 AS receptions,'gng_keeper' profile,score
 FROM `{gng_table}`
 QUALIFY COUNTIF(score IS NULL) OVER(PARTITION BY season,player_id)=0
 """ if gng_table else ''
    return f"""
WITH source AS (
 SELECT season,week,player_id,player_name,position,team,
 SAFE_CAST(JSON_VALUE(raw_payload_json,'$.fantasy_points') AS FLOAT64) points,
 receptions
 FROM `{project}.fantasy_football_brain.raw_nflverse_weekly`
 WHERE season BETWEEN 2015 AND 2025 AND position IN ('QB','RB','WR','TE')
 AND JSON_VALUE(raw_payload_json,'$.season_type')='REG'
 QUALIFY ROW_NUMBER() OVER(PARTITION BY season,week,player_id,team ORDER BY loaded_at DESC)=1
 UNION ALL
 SELECT season,week,player_id,player_display_name,position,team,fantasy_points,receptions
 FROM `{project}.fantasy_football_brain.weekly_metrics`
 WHERE season BETWEEN 2026 AND {season} AND season_type='REG' AND position IN ('QB','RB','WR','TE')
), scored AS (
 SELECT s.*,p.profile, points+p.reception_points*receptions score
 FROM source s CROSS JOIN UNNEST([
 STRUCT('standard' AS profile,0.0 AS reception_points),('half_ppr',0.5),('ppr',1.0)]) p
 {gng_union}
), seasons AS (
 SELECT profile,season,player_id,ANY_VALUE(position) position,AVG(score) prior_rate,COUNT(*) prior_games
 FROM scored GROUP BY profile,season,player_id
), position_prior AS (
 SELECT profile,season,position,APPROX_QUANTILES(prior_rate,100)[OFFSET(50)] prior_rate
 FROM seasons GROUP BY profile,season,position
), early AS (
 SELECT profile,season,player_id,as_of_week,ANY_VALUE(position) position,COUNT(*) observed_games,SUM(score) observed_points
 FROM scored CROSS JOIN UNNEST({cutoffs}) as_of_week WHERE week<=as_of_week GROUP BY profile,season,player_id,as_of_week
), outcome AS (
 SELECT profile,season,player_id,as_of_week,ANY_VALUE(position) position,
 AVG(IF(week=as_of_week+1,score,NULL)) weekly_actual,AVG(IF(week>as_of_week,score,NULL)) ros_actual
 FROM scored CROSS JOIN UNNEST({cutoffs}) as_of_week WHERE week>as_of_week GROUP BY profile,season,player_id,as_of_week
), samples AS (
 SELECT o.*,COALESCE(e.observed_games,0) observed_games,COALESCE(e.observed_points,0) observed_points,
 COALESCE(p.prior_rate,pp.prior_rate) prior_rate,p.prior_rate IS NULL prior_imputed
 FROM outcome o LEFT JOIN early e USING(profile,season,player_id,as_of_week)
 LEFT JOIN seasons p ON p.profile=o.profile AND p.season=o.season-1 AND p.player_id=o.player_id
 LEFT JOIN position_prior pp ON pp.profile=o.profile AND pp.season=o.season-1 AND pp.position=o.position
 WHERE o.season BETWEEN 2016 AND 2025
)
"""


def backtest_sql(project: str, gng_table: str | None = None) -> str:
    return base_sql(project,rolling=True,gng_table=gng_table) + f"""
, predictions AS (
 SELECT s.*,k,horizon,
 IF(horizon='weekly',weekly_actual,ros_actual) actual,
 IF(k=1000000,prior_rate,IF(observed_games+k=0,prior_rate,
 SAFE_DIVIDE(observed_points+k*prior_rate,observed_games+k))) predicted
 FROM samples s CROSS JOIN UNNEST({GRID}) k CROSS JOIN UNNEST(['weekly','ros']) horizon
), ranked AS (
 SELECT *, RANK() OVER(PARTITION BY profile,season,horizon,k,as_of_week ORDER BY predicted) pred_rank,
 RANK() OVER(PARTITION BY profile,season,horizon,k,as_of_week ORDER BY actual) actual_rank
 FROM predictions WHERE actual IS NOT NULL AND predicted IS NOT NULL
)
SELECT profile,horizon,k,as_of_week,IF(season=2025,'holdout_2025','train_2016_2024') split,
COUNT(*) sample_count,AVG(ABS(predicted-actual)) mae,
CORR(pred_rank,actual_rank) rank_correlation,COUNTIF(prior_imputed) imputed_prior_count
FROM ranked GROUP BY profile,horizon,k,split,as_of_week ORDER BY as_of_week,profile,horizon,split,k
"""


def choose_models(results):
    selected = {}
    for profile in sorted({r['profile'] for r in results}):
        selected[profile] = {}
        for horizon in ('weekly','ros'):
            subset = [r for r in results if r['profile']==profile and r['horizon']==horizon]
            best = min((r for r in subset if r['split']=='train_2016_2024'), key=lambda r:(r['mae'],r['k']))
            held = next(r for r in subset if r['split']=='holdout_2025' and r['k']==best['k'])
            baselines = [r for r in subset if r['split']=='holdout_2025' and r['k'] in (0,1000000)]
            selected[profile][horizon] = dict(k=best['k'], training=best, holdout=held, baselines=baselines,
                validated=held['mae']<=min(r['mae'] for r in baselines))
    return selected


def predicted_rate(points, games, prior, k):
    return prior if k==1000000 or games+k==0 else (points+k*prior)/(games+k)


def remaining_team_schedule(schedule, team, as_of_week):
    # Sleeper and nflverse use different Rams abbreviations. Normalize only
    # known aliases and fail closed on an unmapped team instead of a fake bye.
    normalized={'LAR':'LA','WSH':'WAS','JAC':'JAX'}.get(team,team)
    if normalized not in set(schedule.home_team) | set(schedule.away_team):
        raise ValueError(f'Roster team {team!r} does not match the season schedule')
    return schedule.loc[(schedule.home_team.eq(normalized) | schedule.away_team.eq(normalized)) & schedule.week.gt(as_of_week)]


def stage_gng(client, directory: Path, season: int):
    """Expiring research staging only; callers must delete it after querying."""
    rows=[]
    watchlist=[]
    for year in range(2015,season+1):
        payload=json.loads((directory/f'{year}.json').read_text(encoding='utf-8'))
        for r in payload['rows']:
            rows.append(dict(player_id=r['player_id'],player_name=r['player_display_name'],season=r['season'],week=r['week'],position=r['position'],team=r['team'],score=r['gng_points']))
            if year==season and r['gng_points'] is None:
                watchlist.append(dict(player_id=r['player_id'],player_name=r['player_display_name'],team=r['team'],position=r['position'],reason='Exact GNG special-teams scoring requires reconciliation',flags=r['review_flags']))
    table_id=f'{client.project}.fantasy_football_brain.inseason_gng_research_{uuid.uuid4().hex}'
    schema=[bigquery.SchemaField(k,'INTEGER' if k in ('season','week') else 'FLOAT' if k=='score' else 'STRING') for k in rows[0]]
    table=bigquery.Table(table_id,schema=schema);table.expires=datetime.now(timezone.utc)+timedelta(hours=2)
    client.create_table(table)
    try:client.load_table_from_json(rows,table_id,job_config=bigquery.LoadJobConfig(schema=schema,write_disposition='WRITE_EMPTY')).result()
    except Exception:
        client.delete_table(table_id,not_found_ok=True)
        raise
    return table_id,watchlist


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',default='output/inseason-rankings-2026-week3.json')
    parser.add_argument('--season',type=int,default=datetime.now(timezone.utc).year)
    parser.add_argument('--as-of-week',type=int)
    parser.add_argument('--backtest',action='store_true',help='Reproduce all rolling calibration summaries read-only')
    parser.add_argument('--gng-directory',type=Path,default=Path('output/inseason-gng'))
    parser.add_argument('--release-artifacts',action='store_true',help='Emit validated local release bytes and manifest entry; does not upload')
    args=parser.parse_args()
    schedule=nfl.load_schedules([args.season]).to_pandas()
    schedule=schedule.loc[schedule.game_type.eq('REG')]
    if args.as_of_week is None:
        complete=schedule.groupby('week').apply(lambda s: bool(s.home_score.notna().all() and s.away_score.notna().all()),include_groups=False)
        args.as_of_week=max([int(w) for w,done in complete.items() if done],default=0)
    if args.as_of_week==18 and schedule.home_score.notna().all() and schedule.away_score.notna().all():
        print(json.dumps({'status':'season_complete','season':args.season,'action':'Retain the last in-season dataset; continue core statistics and ranking publication.'}))
        raise SystemExit(20)
    if not 1 <= args.as_of_week < 18:
        parser.error('Requires a completed regular-season week from 1 through 17')
    target_week=args.as_of_week+1
    client=get_bigquery_client()
    config=bigquery.QueryJobConfig(maximum_bytes_billed=5_000_000_000)
    calibration=json.loads((Path(__file__).resolve().parents[1]/'docs/inseason-shrinkage-v1-calibration.json').read_text())
    selected=calibration['models_by_week'].get(str(args.as_of_week))
    if not selected:
        raise ValueError(f'No frozen calibration for as-of week {args.as_of_week}')
    expected_profiles={'standard','half_ppr','ppr','gng_keeper'}
    if set(selected)!=expected_profiles or set(calibration['aggregate_validation'])!=expected_profiles:
        raise ValueError('All four calibrated scoring profiles are required')
    if any(not model['validated'] for horizons in calibration['aggregate_validation'].values() for model in horizons.values()):
        raise ValueError('Frozen model did not pass its aggregate holdout baseline gate')
    gng_table,gng_watchlist=stage_gng(client,args.gng_directory,args.season)
    sql=base_sql(client.project,args.season,args.as_of_week,gng_table=gng_table)+f"""
 SELECT u.gsis_id player_id,u.sleeper_player_id,u.player_name,u.team,u.position,u.injury_status,u.status,
 profile,COALESCE(e.observed_games,0) observed_games,COALESCE(e.observed_points,0) observed_points,
 COALESCE(p.prior_rate,pp.prior_rate) prior_rate,p.prior_rate IS NULL prior_imputed
 FROM `{client.project}.fantasy_football_advanced_metrics.v_ranking_post_formula_safety` u
 CROSS JOIN UNNEST(['standard','half_ppr','ppr','gng_keeper']) profile
 LEFT JOIN early e ON e.player_id=u.gsis_id AND e.season={args.season} AND e.profile=profile
 LEFT JOIN seasons p ON p.player_id=u.gsis_id AND p.season={args.season-1} AND p.profile=profile
 LEFT JOIN position_prior pp ON pp.position=u.position AND pp.season={args.season-1} AND pp.profile=profile
 WHERE u.team IS NOT NULL AND u.team!='' AND u.position IN ('QB','RB','WR','TE')
 AND u.active
 """
    try:
        results=[dict(r) for r in client.query(backtest_sql(client.project,gng_table),job_config=config).result()] if args.backtest else []
        candidates=[dict(r) for r in client.query(sql,job_config=config).result()]
    finally:client.delete_table(gng_table,not_found_ok=True)
    loaded={r.game_id for r in client.query(f"SELECT DISTINCT game_id FROM `{client.project}.fantasy_football_brain.weekly_metrics` WHERE season={args.season} AND week<={args.as_of_week}").result()}
    missing=sorted(set(schedule.loc[schedule.week.le(args.as_of_week) & schedule.home_score.notna() & schedule.away_score.notna(),'game_id'])-loaded)
    warnings=["Experimental per-appearance production baseline; no validated matchup, depth-chart or availability model.","Historical evaluation conditions on observed future appearances; it does not validate injury or playing-time forecasts.","Overall ordering is projected points, not positional scarcity or replacement value."]
    for profile,horizons in selected.items():
        for horizon,model in horizons.items():
            if not model['validated']:warnings.append(f'{profile} {horizon}: this cutoff did not beat both baselines in 2025; the overall rolling model passed its aggregate holdout gate.')
    if missing:warnings.append("Completed games awaiting source stats: "+', '.join(missing))
    freshness={}
    for table_name in ('raw_nflverse_weekly','weekly_metrics'):
        table=client.get_table(f'{client.project}.fantasy_football_brain.{table_name}')
        freshness[table_name]=table.modified.isoformat()
    freshness['gng_current_local_reconstruction']=datetime.fromtimestamp((args.gng_directory/f'{args.season}.json').stat().st_mtime,timezone.utc).isoformat()
    artifact=dict(schema_version='1.0',model_version=VERSION,version=VERSION,status='experimental',season=args.season,as_of_week=args.as_of_week,target_week=target_week,generated_at=datetime.now(timezone.utc).isoformat(),source_cutoff=f'{args.season} regular season through Week {args.as_of_week}, available source games only',source_timestamps=freshness,coverage_warnings=warnings,profiles={},validation=selected,aggregate_validation=calibration['aggregate_validation'])
    for profile in ('standard','half_ppr','ppr','gng_keeper'):
        boards={}
        for horizon in ('weekly','ros'):
            model=selected[profile][horizon]
            rows=[]
            for r in candidates:
                if r['profile']!=profile:continue
                if profile=='gng_keeper' and r['player_id'] in {w['player_id'] for w in gng_watchlist}:continue
                teamgames=remaining_team_schedule(schedule,r['team'],args.as_of_week)
                remaining=len(teamgames)
                thisweek=teamgames.loc[teamgames.week.eq(target_week)]
                rate=max(0.0,predicted_rate(r['observed_points'],r['observed_games'],r['prior_rate'],model['k']))
                flags=[]
                if r['prior_imputed']:flags.append('prior_season_position_median_fallback')
                if r['observed_games']<2:flags.append('fewer_than_two_observed_games')
                if r['injury_status']:flags.append('availability_unverified: '+str(r['injury_status']))
                if r['status'] and r['status']!='Active':flags.append('roster_status: '+str(r['status']))
                if horizon=='weekly' and thisweek.empty:flags.append(f'bye_no_week{target_week}_game')
                projected=rate*(remaining if horizon=='ros' else int(not thisweek.empty))
                rows.append(dict(player_id=r['player_id'] or 'sleeper:'+str(r['sleeper_player_id']),sleeper_player_id=str(r['sleeper_player_id'] or ''),player_name=r['player_name'],team=r['team'],position=r['position'],projected_points=round(projected,3),projected_ppg=round(rate,3),remaining_games=remaining,flags=flags,
                  rationale=f"Experimental {VERSION}: {r['observed_points']:.2f} points across {r['observed_games']} observed {args.season} games; prior rate {r['prior_rate']:.2f}, prior-equivalent games k={model['k']}, chosen on 2016-2024. No matchup or unconfirmed absence adjustment.",
                  observed_games=r['observed_games'],observed_points=r['observed_points'],prior_rate=r['prior_rate'],prior_equivalent_games=model['k']))
            rows.sort(key=lambda r:(-r['projected_points'],r['player_id']))
            positions={}
            for i,row in enumerate(rows,1):
                positions[row['position']]=positions.get(row['position'],0)+1
                row.update(rank=i,position_rank=positions[row['position']])
            boards[horizon]=rows
        artifact['profiles'][profile]=boards
    artifact['profiles']['gng_keeper']['watchlist']=gng_watchlist
    artifact['profiles']['gng_keeper']['unavailable_players']=gng_watchlist
    artifact['gng_scoring_exclusions']=calibration['gng_scoring_exclusions']
    artifact['gng_scoring_reconciliation']={'source':'Sleeper league 1369406895588143104 rostered 2026 Week 1-2 observations','matched':42,'compared':42,'scope':'Current observed roster sample only; historical games were not Sleeper-reconciled.'}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(artifact,indent=2),encoding='utf-8')
    if results:path.with_suffix('.backtest.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    if args.release_artifacts:
        artifact['release_status']='validated_experimental'
        unavailable_count=len({row['player_id'] for row in gng_watchlist})
        artifact['coverage_warnings'].append(
            f'GNG excludes ambiguous special-teams player-seasons from calibration; {unavailable_count} current players remain unavailable pending scoring reconciliation.'
            if unavailable_count else
            'GNG excludes ambiguous historical special-teams player-seasons from calibration. No current players remain unavailable for scoring reconciliation.'
        )
        release=Path('build/feeds');release.mkdir(parents=True,exist_ok=True)
        content=json.dumps(artifact,sort_keys=True,separators=(',',':'),allow_nan=False).encode('utf-8')
        digest=hashlib.sha256(content).hexdigest()
        obj=f'v1/datasets/inseason_rankings/sha256-{digest}.json'
        (release/'inseason_rankings.json').write_bytes(content)
        (release/'inseason_rankings.manifest-entry.json').write_text(json.dumps(dict(dataset='inseason_rankings',object=obj,url=f'https://storage.googleapis.com/fantasy-football-498121-public-rankings/{obj}',sha256=digest,bytes=len(content),source_generated_at=artifact['generated_at'],model_version=VERSION),indent=2),encoding='utf-8')
    print(json.dumps({'path':str(path),'validation':selected,'counts':{p:{h:len(artifact['profiles'][p][h]) for h in ('weekly','ros')} for p in PROFILES}},indent=2))


if __name__=='__main__':main()
