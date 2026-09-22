# GNG player-game scoring reconstruction

Run `venv\Scripts\python.exe scripts\inseason_gng_scoring.py --season 2026 --output output\inseason-gng\2026.json` for a local-only scoring audit. This does not change warehouse rows, projections, or public rankings.

The script combines nflverse player-game stats with play-by-play supplements. It uses `GNG_KEEPER_SLEEPER_SCORING_SETTINGS` in `src/fantasy_scoring.py` for QB, RB, WR, and TE scoring. Kicker and team-defense rules are outside this audit.

Every configured offensive and individual return category is represented. Yardage bonus tiers are exclusive, as specified by [Sleeper](https://support.sleeper.com/en/articles/3186339-what-stacks). Long touchdown bonuses and pick-six penalties stack with their ordinary touchdown or interception categories. nflverse rushing and receiving first downs include touchdowns; subtract touchdowns before applying Sleeper first-down bonuses.

On September 21, 2026, the settings returned by Sleeper league `1369406895588143104` exactly matched the repository settings. After the first-down adjustment, all 42 comparable rostered player-games in weeks 1 and 2 matched Sleeper `players_points` to the cent. Evidence is local at `output/inseason-gng/sleeper-2026-reconciliation.json`. This verifies those observations, not every historical scoring edge case.

Ambiguous lateral touchdown attribution and own-team special-teams fumble recoveries generate review flags. Affected rows expose `gng_points: null` and preserve `reconstructed_points` for investigation. Never substitute the latter into a supposedly exact backtest or production board. Historical evaluation must explicitly exclude flagged observations and report the exclusions; a missing outcome must not become zero. A current player with a flagged game needs reconciliation before an exact player aggregate is claimed.

The same script accepts historical seasons. All required stat columns were available for the 2015 source sample. The 2026 source initially covered 16 Week 1 games and 15 Week 2 games; do not call Week 2 complete until the remaining game appears upstream.

Validation: `venv\Scripts\python.exe -m unittest tests.test_inseason_gng_scoring`.
