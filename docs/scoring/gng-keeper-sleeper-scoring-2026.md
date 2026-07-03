# GNG Keeper Sleeper Scoring 2026

Source: owner-supplied Phase 31.9 prompt.

Sleeper league ID: `1369406895588143104`

Season: `2026`

No live Sleeper API call was made when creating this repo copy.

## Player Scoring

Passing:

- `pass_yd = 0.02`
- `pass_td = 5.0`
- `pass_td_50p = 0.5`
- `pass_2pt = 2.0`
- `pass_int = -2.0`
- `pass_int_td = -4.0`
- `pass_sack = -1.0`
- `pass_cmp_40p = 0.5`
- `bonus_pass_cmp_25 = 1.0`
- `bonus_pass_yd_300 = 1.0`
- `bonus_pass_yd_400 = 2.0`

Rushing:

- `rush_yd = 0.04`
- `rush_td = 6.0`
- `rush_td_50p = 1.0`
- `rush_40p = 1.0`
- `rush_fd = 0.1`
- `rush_2pt = 2.0`
- `bonus_rush_att_20 = 1.0`
- `bonus_rush_yd_100 = 1.0`
- `bonus_rush_yd_200 = 2.0`
- `bonus_rush_rec_yd_200 = 1.0`

Receiving:

- `rec = 0.1`
- `bonus_rec_wr = 0.1`
- `bonus_rec_te = 0.2`
- `rec_yd = 0.04`
- `rec_td = 6.0`
- `rec_td_50p = 0.5`
- `rec_40p = 0.5`
- `rec_fd = 0.1`
- `rec_2pt = 2.0`
- `bonus_rec_yd_100 = 1.0`
- `bonus_rec_yd_200 = 2.0`
- `bonus_rush_rec_yd_200 = 1.0`

## Preservation Policy

The current `gng_keeper` seed stores directly supported player scoring in `settings` and preserves bonus or Sleeper-specific keys in `unmapped_settings`.

Kicker, defense, special-teams, fumble, points-allowed, and yards-allowed keys were not present in the Phase 31.9 prompt text. Add them to this file and the `gng_keeper` scoring JSON if the full owner report is supplied later.
