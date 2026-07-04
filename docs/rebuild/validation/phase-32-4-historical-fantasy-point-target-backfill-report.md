# Phase 32.4 Historical Fantasy-Point Target Backfill Report

Final decision: **ROLLING BACKTEST NOW UNBLOCKED**

Phase 32.4 found a real historical nflverse stat source, added a scoped historical nflverse fantasy-point materialization path, backfilled 2015 through 2024 weekly fantasy-point targets for PPR, Half PPR, Standard, and GNG Keeper, and proved rolling trend-aware formula dry-runs can now cover target seasons 2017 through 2025. No production or staging deploy occurred. No final Pigskin rankings were regenerated. No Pigskin chat call, live Sleeper API call, Cloud Run Job trigger, Scheduler job creation, champion activation, or Pigskin exposure of formula/backtest tables occurred.

## Git State

Changed files:

- `src/fantasy_scoring.py`
- `src/materialize_fantasy_points.py`
- `tests/test_fantasy_scoring.py`
- `tests/test_materialize_fantasy_points.py`
- `docs/rebuild/validation/phase-32-4-historical-fantasy-point-target-backfill-report.md`

Commit hash: recorded in the final response after commit.

The existing untracked historical validation backlog remains outside this package.

## Historical Source Audit

Candidate sources inspected:

| Source | 2015-2024 coverage | Field status | Decision |
|---|---:|---|---|
| `raw_nflverse_weekly` | complete QB/RB/WR/TE regular-season source rows | Core columns plus complete raw payload scoring fields | usable |
| `stg_player_week_stats` | complete QB/RB/WR/TE rows, 0 null identity count | Clean player-week identity and common weekly stats | usable as identity/staging join |
| `player_week_advanced_metrics` | complete source feature rows | Not enough raw scoring stats by itself | source features only |
| `analytics_player_weekly_truth` | 2025 only | Missing 2015-2024 targets | not used for backfill |
| `analytics_player_fantasy_points_by_profile` | 2025 only before this phase | Target output table | backfilled |

Fields found in `raw_nflverse_weekly.raw_payload_json` and used for scoring:

- passing yards, passing touchdowns, passing interceptions, passing two-point conversions
- rushing yards, rushing touchdowns, rushing attempts, rushing first downs, rushing two-point conversions
- receptions, receiving yards, receiving touchdowns, receiving first downs, receiving two-point conversions
- rushing fumbles lost, receiving fumbles lost, sack fumbles lost
- special teams touchdowns, fumble recovery touchdowns
- sacks suffered and completions for GNG Keeper-supported weekly bonuses

The materializer does not calculate from `player_week_advanced_metrics`, and it does not treat missing required scoring fields as zero. Historical nflverse mode validates required raw scoring fields before building rows.

## Feasibility Matrix

| Season range | Source rows available | Identity coverage | Required fields | Can build profile points |
|---|---:|---:|---|---|
| 2015-2020 | yes, 17 regular-season weeks | 0 null identity count | complete | yes |
| 2021-2024 | yes, 18 regular-season weeks | 0 null identity count | complete | yes |
| 2025 | already present | already present | already present | preserved |

Backfilled profile rows by season:

| Season | Rows per profile |
|---:|---:|
| 2015 | 5,423 |
| 2016 | 5,413 |
| 2017 | 5,442 |
| 2018 | 5,356 |
| 2019 | 5,412 |
| 2020 | 5,530 |
| 2021 | 5,856 |
| 2022 | 5,818 |
| 2023 | 5,811 |
| 2024 | 5,848 |
| 2025 | 6,043, unchanged |

2015 through 2024 total by position and profile:

| Position | Rows per profile |
|---|---:|
| QB | 6,220 |
| RB | 14,779 |
| TE | 11,653 |
| WR | 23,257 |

## Code Changes

`src/materialize_fantasy_points.py` now supports:

- `--source historical-nflverse`
- bounded `--season-start`, `--season-end`, `--week-start`, `--week-end`
- bounded `--position`
- direct scoring from `raw_nflverse_weekly` joined to `stg_player_week_stats`
- required scoring-field validation before scoring
- existing merge behavior into `analytics_player_fantasy_points_by_profile`

`src/fantasy_scoring.py` now supports available GNG Keeper weekly components:

- sacks suffered through `pass_sack`
- rushing first downs through `rush_fd`
- receiving first downs through `rec_fd`
- 25-completion bonus
- passing yardage thresholds
- 20-rush-attempt bonus
- rushing, receiving, and combined yardage thresholds

No long-touchdown bonuses were fabricated. Those require play-level long touchdown derivation and remain a known gap for exact GNG scoring.

## Dry-Run Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --source historical-nflverse --season-start 2015 --season-end 2024 --week-start 1 --week-end 18 --position QB,RB,WR,TE --scoring-profile-id ppr --scoring-profile-id half_ppr --scoring-profile-id standard --scoring-profile-id gng_keeper --dry-run --allow-large-query
```

Result:

- source rows: 55,909
- built rows: 223,636
- profiles: `ppr`, `half_ppr`, `standard`, `gng_keeper`
- positions: QB, RB, WR, TE
- wrote: false
- source validation: complete, 0 missing required fields

## Controlled Write Result

Command:

```powershell
.\venv\Scripts\python.exe -m src.materialize_fantasy_points --source historical-nflverse --season-start 2015 --season-end 2024 --week-start 1 --week-end 18 --position QB,RB,WR,TE --scoring-profile-id ppr --scoring-profile-id half_ppr --scoring-profile-id standard --scoring-profile-id gng_keeper --allow-large-query
```

Result:

- source rows: 55,909
- written or merged profile rows: 223,636
- target table: `analytics_player_fantasy_points_by_profile`
- scope: seasons 2015 through 2024, weeks 1 through 18, QB/RB/WR/TE, four active profiles
- existing 2025 rows preserved

Post-write checks:

- duplicate grain count: 0
- impossible fantasy point values: 0
- null player ID count: 0
- GNG supplemental fields present in source stats: 55,909 rows with `sacks_taken`, `rushing_first_downs`, and `receiving_first_downs`

Sample profile differences were visible. Example, Davante Adams 2024 week 15:

- Standard: 33.8
- Half PPR: 38.3
- PPR: 42.8
- GNG Keeper: 25.32

## Rolling Backtest Dry-Run Coverage

After the backfill, valid rolling target pairs are available for all four profiles:

| Source window | Target season | Status |
|---|---:|---|
| 2014-2016 | 2017 | dry-run passed |
| 2015-2017 | 2018 | dry-run passed |
| 2016-2018 | 2019 | dry-run passed |
| 2017-2019 | 2020 | dry-run passed |
| 2018-2020 | 2021 | dry-run passed |
| 2019-2021 | 2022 | dry-run passed |
| 2020-2022 | 2023 | dry-run passed |
| 2021-2023 | 2024 | dry-run passed |
| 2022-2024 | 2025 | dry-run passed |

Each dry-run used:

- `candidate_family=trend_v2`
- `source_window_years=3`
- source seasons strictly before target season
- target weeks 1 through 18
- QB/RB/WR/TE
- `ppr`, `half_ppr`, `standard`, and `gng_keeper`

The nine dry-runs produced candidate summaries without writing backtest tables. The largest result shapes were roughly 59k candidate result rows per target season. The 2025 target pair remained consistent with Phase 32.3.

Early trend finding:

- RB trend-opportunity candidates stayed the strongest class in several seasons, but did not prove a stable 70 percent high-confidence result across multiple target years from this dry-run summary alone.
- WR and TE candidates varied by season. TE still needs formula work.
- No champion should be activated from this phase.

## Production Ranking No-Change

`analytics_pigskin_rankings` active final rows remained unchanged:

- PPR: QB 45, RB 80, WR 100, TE 60
- Half PPR: QB 45, RB 80, WR 100, TE 60
- Standard: QB 45, RB 80, WR 100, TE 60
- GNG Keeper: QB 45, RB 80, WR 100, TE 60

`ranking_formula_champions` row count remains 0.

## Checks Run

Passed:

- `.\venv\Scripts\python.exe scripts\check_deployment_safety.py`
- `.\venv\Scripts\python.exe -m py_compile src\fantasy_scoring.py src\materialize_fantasy_points.py`
- `.\venv\Scripts\python.exe -m compileall -q src scripts`
- `.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_materialize_fantasy_points`
- `.\venv\Scripts\python.exe -m unittest tests.test_fantasy_scoring tests.test_materialize_fantasy_points tests.test_ranking_formula_backtests`
- `.\venv\Scripts\python.exe -m unittest discover tests`
- `.\venv\Scripts\python.exe scripts\run_bigquery_migrations.py --list-pending`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --dry-run`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern fantasy`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_backtest`
- `.\venv\Scripts\python.exe scripts\run_bigquery_validations.py --run --pattern ranking_formula`

Validation results:

- fantasy validations: 6 passed, 0 failed
- ranking backtest validations: 3 passed, 0 failed
- ranking formula validations: 6 passed, 0 failed
- pending migrations: none

The fantasy identity validation returned an informational warning row with `missing_identity_rate = 0.0`.

PowerShell surfaced some unittest output as native-command noise because progress/log output was written through stderr, but the unittest runner reported `OK`.

## Remaining Gaps

- `analytics_player_weekly_truth` remains 2025-only. The rolling backtest target is now unblocked because `analytics_player_fantasy_points_by_profile` has historical target rows, but the weekly truth mart itself was not backfilled.
- Exact GNG Keeper long-touchdown bonuses are not implemented. They need play-level long touchdown derivation from `stg_play_player_events` or raw PBP before exact GNG historical scoring can be claimed.
- The Phase 32.4 rolling dry-runs were not written to ranking backtest tables. That should happen in a separate tournament phase.
- No champions were activated.

## Recommended Next Phase

Phase 32.5 should run the full rolling multi-year algorithm tournament, write the bounded results under a new backtest version, and compare v0, v1, and v2 candidates across the now-unblocked target seasons.
