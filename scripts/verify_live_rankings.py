"""Verify anonymous feed bytes and freshness after a coordinated release."""
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from urllib.request import urlopen


def verify_inseason(raw, entry):
    if hashlib.sha256(raw).hexdigest() != entry['sha256']:
        raise ValueError('In-season public SHA-256 mismatch')
    if len(raw) != entry['bytes']:
        raise ValueError('In-season byte count mismatch')
    data=json.loads(raw)
    if data.get('release_status')!='validated_experimental' or data.get('schema_version')!='1.0':
        raise ValueError('In-season release was not validated')
    if not data.get('model_version') or not data.get('source_cutoff'):
        raise ValueError('In-season source provenance missing')
    if data.get('target_week')!=data.get('as_of_week',0)+1 or not 2 <= data['target_week'] <= 18:
        raise ValueError('In-season horizon cutoff is invalid')
    warnings=data.get('coverage_warnings')
    if not isinstance(warnings,list) or any(not isinstance(w,str) for w in warnings):
        raise ValueError('In-season coverage warnings missing or malformed')
    if data.get('generated_at')!=entry.get('source_generated_at'):
        raise ValueError('In-season manifest timestamp disagrees with artifact')
    generated=datetime.fromisoformat(data['generated_at'].replace('Z','+00:00'))
    if generated.tzinfo is None:
        raise ValueError('In-season timestamp must include its timezone')
    if datetime.now(timezone.utc)-generated>timedelta(hours=26):
        # A completed season deliberately retains its final dataset.
        import nflreadpy as nfl
        schedule=nfl.load_schedules([data['season']]).to_pandas()
        regular=schedule.loc[schedule.game_type.eq('REG')]
        if regular.empty or not (regular.home_score.notna().all() and regular.away_score.notna().all()):
            raise ValueError('In-season source older than 26 hours during an unfinished season')
    expected={'standard','ppr','half_ppr','gng_keeper'}
    if set(data.get('profiles',{}))!=expected:
        raise ValueError('In-season release must contain all four profiles')
    counts={}
    for profile,boards in data['profiles'].items():
        counts[profile]={}
        for horizon in ('weekly','ros'):
            if data.get('aggregate_validation',{}).get(profile,{}).get(horizon,{}).get('validated') is not True:
                raise ValueError(f'{profile}/{horizon}: aggregate validation missing or failed')
            rows=boards.get(horizon)
            if not isinstance(rows,list) or not 40<=len(rows)<=2000:
                raise ValueError(f'{profile}/{horizon}: incomplete in-season board')
            ids=set();positions={};previous=float('inf')
            for rank,row in enumerate(rows,1):
                player_id=row.get('player_id');position=row.get('position')
                if not player_id or player_id in ids or position not in ('QB','RB','WR','TE') or row.get('rank')!=rank:
                    raise ValueError(f'{profile}/{horizon}: invalid identity or rank')
                ids.add(player_id);positions[position]=positions.get(position,0)+1
                if row.get('position_rank')!=positions[position]:
                    raise ValueError(f'{profile}/{horizon}: invalid positional rank')
                for metric in ('projected_points','projected_ppg'):
                    value=row.get(metric)
                    if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<0:
                        raise ValueError(f'{profile}/{horizon}: invalid projection')
                if row['projected_points']>previous or not row.get('rationale') or not row.get('team'):
                    raise ValueError(f'{profile}/{horizon}: invalid order or provenance')
                previous=row['projected_points']
            if len(positions)!=4:
                raise ValueError(f'{profile}/{horizon}: missing position')
            counts[profile][horizon]=len(rows)
        for missing in boards.get('unavailable_players',[]):
            if not missing.get('player_id') or not missing.get('reason'):
                raise ValueError(f'{profile}: unavailable player needs identity and reason')
    return dict(model_version=data['model_version'],target_week=data['target_week'],sha256_verified=True,counts=counts,coverage_warnings=warnings)


def main():
    stamp = int(datetime.now(timezone.utc).timestamp())
    url = f'https://storage.googleapis.com/fantasy-football-498121-public-rankings/v1/manifest.json?verify={stamp}'
    with urlopen(url, timeout=30) as response:
        manifest = json.load(response)
    profiles = manifest['profiles']
    if set(profiles) != {'standard', 'ppr', 'half_ppr', 'gng_keeper'}:
        raise ValueError('The public manifest must include all four profiles')
    summary = {}
    for profile, entry in profiles.items():
        with urlopen(entry['url'], timeout=30) as response:
            raw = response.read()
        if hashlib.sha256(raw).hexdigest() != entry['sha256']:
            raise ValueError(f'{profile}: public SHA-256 mismatch')
        board = json.loads(raw)
        overall = board['overall']['players']
        if len(overall) != 150 or len({p['player_id'] for p in overall}) != 150:
            raise ValueError(f'{profile}: expected 150 unique overall players')
        generated = datetime.fromisoformat(entry['source_generated_at'].replace('Z', '+00:00'))
        if datetime.now(timezone.utc) - generated > timedelta(hours=26):
            raise ValueError(f'{profile}: source older than 26 hours')
        if entry.get('warnings'):
            raise ValueError(f'{profile}: publisher warnings: {entry["warnings"]}')
        players = overall + [p for position in board['positions'].values() for p in position['players']]
        if any(not isinstance(p.get('current_season'), dict) for p in players):
            raise ValueError(f'{profile}: missing current-season context')
        summary[profile] = dict(version=entry['board_version'], overall=150, total_rows=len(players), sha256_verified=True)
    if entry:=manifest.get('datasets',{}).get('inseason_rankings'):
        with urlopen(entry['url'],timeout=30) as response:
            summary['inseason_rankings']=verify_inseason(response.read(),entry)
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
