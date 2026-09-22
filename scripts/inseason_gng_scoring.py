"""Local GNG player-game scoring audit. Never writes warehouse or public data.

Yardage tiers are exclusive per https://support.sleeper.com/en/articles/3186339-what-stacks.
PBP supplements the nflverse player stats for long TDs, pick sixes and ST fumbles.
Output is a reconstruction, not a claim of reconciliation to Sleeper final scores.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.fantasy_scoring import GNG_KEEPER_SLEEPER_SCORING_SETTINGS as SETTINGS

FIELDS = {
    'pass_yd': 'passing_yards', 'pass_td': 'passing_tds',
    'pass_int': 'passing_interceptions', 'pass_sack': 'sacks_suffered',
    'pass_2pt': 'passing_2pt_conversions', 'pass_cmp_40p': 'passing_40',
    'rush_yd': 'rushing_yards', 'rush_td': 'rushing_tds',
    'rush_fd': 'rushing_first_downs', 'rush_2pt': 'rushing_2pt_conversions',
    'rush_40p': 'rushing_40', 'rec': 'receptions', 'rec_yd': 'receiving_yards',
    'rec_td': 'receiving_tds', 'rec_fd': 'receiving_first_downs',
    'rec_2pt': 'receiving_2pt_conversions', 'rec_40p': 'receiving_40',
    'st_td': 'special_teams_tds', 'kr_yd': 'kickoff_return_yards',
    'pr_yd': 'punt_return_yards', 'fum_lost': 'fumbles_lost_total',
    'fum_rec_td': 'fumble_recovery_tds',
}
SUPPLEMENTS = ('pass_td_50p', 'rush_td_50p', 'rec_td_50p', 'pass_int_td', 'st_ff', 'st_fum_rec')


def score_game(row: dict, extra: dict) -> tuple[float, dict]:
    """Require actual stat fields. Zero is valid; missing is an error."""
    required = set(FIELDS.values()) | {'completions', 'carries', 'position'}
    missing = sorted(k for k in required if row.get(k) is None)
    if missing:
        raise ValueError(f'Missing GNG scoring inputs: {missing}')
    stats = {key: float(row[field]) for key, field in FIELDS.items()}
    # nflverse includes touchdowns as first downs. Sleeper matchup scores exclude
    # them from first-down bonuses (2026 weeks 1-2, 42 rostered observations).
    stats['rush_fd'] = max(0, stats['rush_fd'] - stats['rush_td'])
    stats['rec_fd'] = max(0, stats['rec_fd'] - stats['rec_td'])
    stats.update({key: float(extra.get(key, 0)) for key in SUPPLEMENTS})
    stats['bonus_rec_wr'] = stats['rec'] if row['position'] == 'WR' else 0
    stats['bonus_rec_te'] = stats['rec'] if row['position'] == 'TE' else 0
    stats['bonus_pass_cmp_25'] = int(row['completions'] >= 25)
    stats['bonus_rush_att_20'] = int(row['carries'] >= 20)
    for prefix, lower, upper in [('pass', 300, 400), ('rush', 100, 200), ('rec', 100, 200)]:
        yards = stats[f'{prefix}_yd']
        stats[f'bonus_{prefix}_yd_{lower}'] = int(lower <= yards < upper)
        stats[f'bonus_{prefix}_yd_{upper}'] = int(yards >= upper)
    stats['bonus_rush_rec_yd_200'] = int(stats['rush_yd'] + stats['rec_yd'] >= 200)
    breakdown = {key: round(value * SETTINGS[key], 6) for key, value in stats.items()}
    return round(sum(breakdown.values()), 6), breakdown


def pbp_supplements(plays: list[dict]) -> tuple[dict, list]:
    result = defaultdict(lambda: defaultdict(float))
    flags = []
    def add(play, player, stat):
        if player:
            result[(play['game_id'], player)][stat] += 1
        else:
            flags.append({'game_id': play['game_id'], 'play_id': play.get('play_id'), 'reason': f'missing_{stat}_player'})
    for p in plays:
        if p.get('play_type') == 'no_play' or p.get('two_point_attempt') == 1:
            continue
        if p.get('pass_touchdown') == 1:
            if (p.get('passing_yards') or 0) >= 50:
                add(p, p.get('passer_player_id'), 'pass_td_50p')
            scorer = p.get('td_player_id') or p.get('receiver_player_id')
            yards = p.get('lateral_receiving_yards') if scorer == p.get('lateral_receiver_player_id') else p.get('receiving_yards')
            if (yards or 0) >= 50:
                add(p, scorer, 'rec_td_50p')
            if p.get('lateral_reception') == 1:
                flags.append({'game_id': p['game_id'], 'play_id': p.get('play_id'), 'reason': 'lateral_td_length_requires_official_reconciliation'})
        if p.get('rush_touchdown') == 1:
            scorer = p.get('td_player_id') or p.get('rusher_player_id')
            if (p.get('rushing_yards') or 0) >= 50:
                add(p, scorer, 'rush_td_50p')
            if p.get('lateral_rush') == 1:
                flags.append({'game_id': p['game_id'], 'play_id': p.get('play_id'), 'reason': 'lateral_rush_td_requires_official_reconciliation'})
        if p.get('interception') == 1 and p.get('return_touchdown') == 1:
            add(p, p.get('passer_player_id'), 'pass_int_td')
        special = any(p.get(key) == 1 for key in ('punt_attempt', 'kickoff_attempt', 'field_goal_attempt', 'extra_point_attempt'))
        if special:
            for i in (1, 2):
                forced = p.get(f'forced_fumble_player_{i}_player_id')
                if forced:
                    add(p, forced, 'st_ff')
                recovered = p.get(f'fumble_recovery_{i}_player_id')
                if recovered:
                    add(p, recovered, 'st_fum_rec')
                    if p.get(f'fumble_recovery_{i}_team') == p.get(f'fumbled_{i}_team'):
                        flags.append({'game_id': p['game_id'], 'play_id': p.get('play_id'), 'player_id': recovered, 'reason': 'own_team_st_fumble_recovery_requires_sleeper_reconciliation'})
    return result, flags


def main():
    import nflreadpy as nfl
    import polars as pl
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--season', type=int, default=2026)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    weekly = nfl.load_player_stats([args.season]).filter((pl.col('season_type') == 'REG') & pl.col('position').is_in(['QB', 'RB', 'WR', 'TE']))
    pbp = nfl.load_pbp([args.season]).filter(pl.col('season_type') == 'REG')
    supplements, flags = pbp_supplements(pbp.to_dicts())
    offensive_ids = set(weekly['player_id'].to_list())
    flags = [flag for flag in flags if not flag.get('player_id') or flag['player_id'] in offensive_ids]
    games = set(pbp['game_id'].to_list())
    output = []
    for row in weekly.to_dicts():
        if row['game_id'] not in games:
            raise ValueError(f"Missing PBP game {row['game_id']}")
        points, breakdown = score_game(row, supplements.get((row['game_id'], row['player_id']), {}))
        row_flags = [f['reason'] for f in flags if f['game_id'] == row['game_id'] and (not f.get('player_id') or f['player_id'] == row['player_id'])]
        output.append({key: row[key] for key in ('player_id', 'player_display_name', 'position', 'team', 'season', 'week', 'game_id')} | {'gng_points': None if row_flags else points, 'reconstructed_points': points, 'review_flags': row_flags, 'breakdown': breakdown})
    payload = {'season': args.season, 'status': 'requires_sleeper_reconciliation' if flags else 'reconstructed_not_sleeper_reconciled', 'games': len(games), 'rows': output, 'review_flags': flags, 'source': 'nflverse player_stats and pbp', 'scoring_source': 'src/fantasy_scoring.py GNG_KEEPER_SLEEPER_SCORING_SETTINGS', 'tier_rule_source': 'https://support.sleeper.com/en/articles/3186339-what-stacks'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(json.dumps({'season': args.season, 'rows': len(output), 'games': len(games), 'review_flags': flags, 'output': str(args.output)}))


if __name__ == '__main__':
    main()
