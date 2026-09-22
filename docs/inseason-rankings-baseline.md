# In-season production baseline candidates

Production verification, 2026-09-21 at 23:49 ET: the existing Windows scheduled task completed the full stats, ranking, publication, IONOS import and anonymous readback chain with result 0. The release targets Week 3 from Week 2 available observations. Each horizon has 808 Standard, Half-PPR and PPR players, plus 804 GNG players. NYG-LA Week 2 stats remain upstream-pending; four ambiguous GNG players remain explicitly unavailable. All 32 schedule team codes resolve, including Sleeper LAR to schedule LA.

`scripts/inseason_rankings.py` writes local candidate JSON only. It does not alter Fable scores, warehouse rankings, or published feeds. Version: `inseason_observed_ppg_shrinkage_v1`.

## Method

Per-game forecast is `(observed 2026 points + k * prior-season points per appearance) / (observed games + k)`. A player without prior-year observations uses the prior year's position median. No observation is invented as a zero. A player without current-year appearances retains that prior. Rates are floored at zero for output.

The candidate grid is 0, 1, 2, 4, 8, 16, 32 prior-equivalent games and prior-only. For each scoring profile, horizon and observation cutoff from Week 1 through Week 17, choose the lowest mean absolute error on 2016-2024, then evaluate that fixed choice on 2025. Cutoff 17 uses only 2021-2024 training seasons because earlier seasons had no regular-season Week 18. Historical feature aggregation, parameter scoring, and rank association run in BigQuery. Local code handles only summary results and current output rows.

Weekly forecasts target the week after the observation cutoff (initially Week 3). ROS forecasts multiply the separately calibrated per-game rate by actual remaining scheduled team games. These are distinct forecasts. They have no unvalidated matchup multiplier. A target-week bye produces zero weekly points. Injury designations remain explicit review flags and do not imply verified missed time.

Schedule matching normalizes known provider team aliases (`LAR` to `LA`, `WSH` to `WAS`, `JAC` to `JAX`) and fails if a roster team has no schedule match. An unknown team code must never become a false bye or zero-game ROS forecast.

## Evaluation limits

Historical evaluation includes players who have observed future appearances. Weekly targets are actual points in the following week; ROS targets are average points in observed games after the observation cutoff. This validates conditional per-appearance production, not future participation, snap opportunity, retirement, or injury absence. Rookies and players without prior observations use the same position-median fallback in training and current outputs.

Cross-position raw points ordering is a projected-points leaderboard, not a roster-value or replacement-value draft ranking. Positional lists use those same point forecasts. Do not describe the results as a validated availability or matchup model.

The public `/ranks` route and new Pigskin Studio conversations default to the separate VORP-interleaved overall board. Weekly and ROS remain opt-in point-projection views. Projection rows carry both GSIS and Sleeper player identifiers so Studio can attach current availability evidence to an exact Sleeper roster player without name guessing.

The current universe consists of active, rostered QB/RB/WR/TE players from the saved Sleeper safety view, including rostered IR and inactive designations. Teamless players are excluded. Availability remains an explicit warning without an invented absence duration. Players with little evidence carry visible flags. Completed games missing from the weekly source are named in the artifact coverage warnings.

## Scoring

Standard uses nflverse's standard fantasy points; Half-PPR adds 0.5 per reception and PPR adds 1.0. Historical sources cover 2015-2025, with the first year supplying priors. Current observations come from the scoped 2026 `weekly_metrics` refresh.

GNG uses the separate exact configured scoring reconstruction in `scripts/inseason_gng_scoring.py`. Long plays, pick-six penalties and special-teams events come from play-by-play. Yardage bonuses use exclusive tiers and first-down bonuses exclude touchdown plays. All 42 comparable current-season Sleeper roster observations matched to the cent. That check is a current sample, not blanket historical verification.

Any ambiguous GNG special-teams attribution makes that score null. Exclude the entire affected player-season from calibration rather than pretending the dropped game had no production. This excludes 32, 46, 32, 54, 22, 37, 25, 25, 22, 68 and 17 player-seasons in 2015 through 2025 respectively. The exclusions introduce cohort-selection bias, especially among returners, and remain visible in calibration metadata. Current affected players have no GNG numerical forecast and appear in `unavailable_players` with their reason. Initially those players are Jordan Whittington, Skyy Moore, Parker Washington and Jaylin Lane.

## Initial held-out results

All six selected models beat both baselines on 2025 conditional per-appearance MAE. Training selects weekly k=2 for every profile, ROS k=4 for Standard/Half-PPR and k=2 for PPR.

| Profile / horizon | Selected MAE | Current-only MAE | Prior-only MAE |
|---|---:|---:|---:|
| Standard weekly | 3.608 | 3.883 | 3.867 |
| Standard ROS | 2.291 | 2.700 | 2.466 |
| Half-PPR weekly | 3.925 | 4.240 | 4.266 |
| Half-PPR ROS | 2.546 | 2.965 | 2.757 |
| PPR weekly | 4.313 | 4.641 | 4.714 |
| PPR ROS | 2.808 | 3.262 | 3.083 |

The artifact retains complete selected-model metrics and baseline comparisons. The `.backtest.json` sidecar retains the entire grid. These results concern per-game error, not the error of projected ROS totals.

## Reproduction and automation boundary

`venv\Scripts\python.exe scripts\inseason_rankings.py --season 2026 --as-of-week 2 --backtest` reproduces the rolling evaluation and local candidates. Normal runs load frozen parameters and evaluation results from `docs/inseason-shrinkage-v1-calibration.json`; they do not select weights again using the holdout. With no week argument, the script selects the latest fully scored week in the schedule and forecasts the next week. Unsupported prediction boundaries abort generation.

The release gate is weighted aggregate held-out MAE across all seventeen cutoffs, separately for each profile and horizon. The training-selected model must beat both aggregate baselines. Individual cutoff failures remain visible diagnostics and do not retune or cherry-pick the held-out results. This acceptance rule was established during the current research review. Repeated player appearances across cutoffs are correlated, so sample counts are not independent observations and no statistical significance claim is made.

| Profile / horizon | Aggregate MAE | Current-only | Prior-only |
|---|---:|---:|---:|
| Standard weekly | 3.687 | 3.745 | 4.090 |
| Standard ROS | 2.411 | 2.568 | 2.833 |
| Half-PPR weekly | 4.026 | 4.100 | 4.526 |
| Half-PPR ROS | 2.662 | 2.831 | 3.163 |
| PPR weekly | 4.420 | 4.502 | 5.010 |
| PPR ROS | 2.936 | 3.119 | 3.525 |
| GNG weekly | 3.386 | 3.454 | 3.706 |
| GNG ROS | 2.089 | 2.235 | 2.488 |

Each weekly comparison covers 5,687 held-out cohort samples; each ROS comparison covers 8,977. Artifacts include model and schema versions, source table modification timestamps, and experimental status. Review of this concrete method and its limits precedes any new-formula publication.

GNG instead has 5,491 weekly and 8,738 ROS held-out samples after the scoring exclusions. Historical GNG JSON lives under `output/inseason-gng/{year}.json`, with 2015 through the current season required. Rebuild a year with `scripts/inseason_gng_scoring.py --season <year> --output output/inseason-gng/<year>.json`. Refresh the current year before each scheduled candidate build. Candidate generation loads these observations into a unique BigQuery research table with a two-hour expiry, queries it under a five-GB cap, and deletes it afterward. No production source or ranking table is replaced.

`--release-artifacts` emits `build/feeds/inseason_rankings.json` and its manifest entry only after all four profiles pass the frozen aggregate gates. The release carries `release_status=validated_experimental`. The remote object name is content-addressed; this script does not upload it. Ordinary local candidate generation never emits a manifest entry.

Production preparation commands, in order:

```powershell
venv\Scripts\python.exe scripts\refresh_current_season_stats.py --season 2026 --apply
venv\Scripts\python.exe scripts\inseason_gng_scoring.py --season 2026 --output output/inseason-gng/2026.json
venv\Scripts\python.exe scripts\inseason_rankings.py --season 2026 --release-artifacts
```

The publishing wrapper uploads the exact bytes named by the emitted manifest entry before adding that entry to the public manifest, then imports it on IONOS. A preparation failure must retain the previous release and report the failure.

After regular-season Week 18 completes, the wrapper skips the in-season generation/upload step and retains the last in-season dataset. Core statistics and existing-board publication continue. It must not attempt an unsupported Week 19 regular-season forecast.

The generator returns exit code 20 with `status=season_complete` when all regular-season schedule games have scores. The wrapper treats that code as an intentional in-season skip and never reattaches stale local release artifacts. Other nonzero generator exits remain failures. Live verification checks the in-season object's hash, release gate, all four profiles and both horizons, rank integrity and coverage provenance. Its freshness check permits the intentionally retained final dataset only after verifying schedule completion. The remote import trigger rejects missing or failed in-season import results.

If a historical GNG cache is missing, rebuild each missing season with the scorer command above using the relevant year and matching output filename, then rerun preparation. Do not replace missing exact scoring with a different scoring profile or partial GNG reconstruction. Historical caches are local generated artifacts; the formulas, scorer, frozen calibration and recovery instructions are version-controlled.
