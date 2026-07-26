# Streamlit Compatibility Rollout (Retired)

Status: **retired as a cloud rollout**. This document described a gradual, flag-gated migration of Streamlit UI reads onto compatibility objects. The Streamlit Cloud Run service was retired before the flags were ever promoted, which completed the production migration by removing the deployed legacy side; the app itself survives as a local studio tool.

What this means in practice:

- The `USE_COMPAT_*` flags no longer gate anything in the cloud. `src/compat_flags.py`, `tests/test_streamlit_compat_rollout.py`, and `app.py` remain in the repo for the local studio surface only, with every flag default-off.
- The backend helpers are no longer "the flagged path". They are the only path.
- No rollback procedure applies. There is no legacy branch to fall back to.

## What The Helpers Became

| Backend helper | Compatibility object | Replaced |
| --- | --- | --- |
| `src/player_profiles.py` | `compat_player_profiles_current` | direct joins across `player_rosters`, `player_contracts`, `depth_charts`, `college_player_stats`, `rookie_scouting_metrics` |
| `src/sleeper_watch.py` | `compat_sleeper_watch_candidates` | direct `weekly_metrics` and raw Sleeper roster scans |
| `src/trade_assets.py` | `compat_trade_assets_current` | direct `market_values` reads |
| `src/trade_history.py` | `compat_trade_player_history` | direct `weekly_metrics` history reads |
| `src/viewer_team_context.py` | `compat_viewer_team_context` | joins across `sleeper_viewer_team_snapshots`, `sleeper_roster_players`, `sleeper_lineups`, `sleeper_available_players` |

Each helper is Streamlit-free and independently tested. Call them directly; do not reintroduce a flag layer.

## Limitations Carried Forward

These were documented as compat-path limitations and remain true of the objects themselves:

- `compat_player_profiles_current` stores some profile fields as JSON summaries. Legacy display-only fields such as headshot, height, weight, jersey number, and draft details are not all present as explicit columns.
- `compat_viewer_team_context` lookup requires `roster_id` or a future `manager_id`. It will not resolve from league-only, username, team name, or display name.
- Packet coverage is incomplete until the materialization jobs seed real rows. A missing packet should be surfaced honestly rather than backfilled from a raw-table scan.

For the current read contract and what still lacks a consumer, see [ui-query-debt-register.md](ui-query-debt-register.md).
