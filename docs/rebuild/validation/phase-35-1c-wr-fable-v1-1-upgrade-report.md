# Phase 35.1C WR Fable v1.1 Upgrade Report

## Final Recommendation

`WR FABLE V1.1 NEEDS ONE SIMPLE TWEAK`

Do not replace WR Fable v1 with the current v1.1 blend. The upgrade restores Malik Nabers, reduces top-12 busts from two to one, improves top-6 precision, and slightly lowers band regret. It also loses top-12 precision, points capture, and one elite miss versus v1. The team-environment modifier adds no material lift and slightly worsens rank correlation and pairwise ordering.

The simple next version should keep v1 scoring for fully qualified latest seasons and use the two-season blend only for carry-forward injury cases. Team environment and alpha-role context should remain review flags until a historical modifier demonstrates lift.

## What Changed

- Added dynamic two-season rate blending with latest route-based weights capped from 0.35 to 0.70.
- Separated two-year availability from on-field performance.
- Added carry-forward eligibility for at least three games or 75 routes when the prior season qualified.
- Added a source-backed team environment score for 2022-2025.
- Added current-board-only team and alpha-role adjustments from the newest Sleeper snapshot.
- Created an append-only, idempotent weekly Sleeper player archive and status-change view.
- Prepared a disabled Cloud Run Job and Scheduler preview in `docs/rebuild/cloud-scheduler-plan.md`. No resource was created.

## Backtest Comparison

| Variant | Rows | Spearman | Top 6 | Top 12 | Top 24 | Pts@12 | Pts@24 | NDCG@24 | Pairwise | Regret | Elite misses | Top-12 busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| WR Fable v1 | 320 | 0.738 | 0.278 | 0.639 | 0.625 | 0.917 | 0.893 | 0.849 | 0.769 | 0.266 | 8 | 2 |
| v1.1 two-season blend | 337 | 0.735 | 0.389 | 0.583 | 0.611 | 0.898 | 0.877 | 0.846 | 0.768 | 0.252 | 9 | 1 |
| v1.1 plus team environment | 337 | 0.734 | 0.389 | 0.583 | 0.611 | 0.898 | 0.877 | 0.846 | 0.767 | 0.252 | 9 | 1 |

The blend adds 17 complete fold rows through carry-forward coverage: zero in 2022, one in 2023, and six in 2024 among rows reaching the target join. The team environment is now complete for all 32 teams in every source season. It changes 30, 34, and 31 scored rows across the three folds, but does not improve aggregate selection metrics.

Fold detail for the preferred v1.1 blend:

| Fold | Rows | Spearman | Top 6 | Top 12 | Pts@12 | NDCG@24 | Pairwise | Elite misses | Busts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 to 2023 | 109 | 0.756 | 0.167 | 0.583 | 0.924 | 0.877 | 0.777 | 3 | 0 |
| 2023 to 2024 | 113 | 0.686 | 0.333 | 0.583 | 0.915 | 0.808 | 0.745 | 3 | 1 |
| 2024 to 2025 | 115 | 0.764 | 0.667 | 0.583 | 0.855 | 0.851 | 0.781 | 3 | 0 |

Role-change misses remain: Evans, Deebo, Collins, Higgins, Godwin, McLaurin, Olave, Smith-Njigba, and Watson. The environment modifier changes a few ranks but does not eliminate any elite miss. Keenan Allen remains the only v1.1 predicted top-12 bust.

## Current 2025-Source Top 40

This is a current review board, not a 2026 outcome test. `Blend` is v1.1 base score minus v1 score. `Avail` is the change in the age/availability component. Context is capped at +/-0.08.

| v1.1 | Old | Std | Player | Source to current | Score | Blend | Avail | Bucket | Alpha | Sleeper | Reason |
|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---|---|
| 1 | 1 | 3 | Amon-Ra St. Brown | DET to DET | 1.910 | -0.020 | 0.004 | 0 | 0.00 | Active, depth 1 | stable blend |
| 2 | 5 | 4 | Ja'Marr Chase | CIN to CIN | 1.803 | 0.173 | 0.006 | 0 | 0.00 | Active, depth 1 | two-year blend lift |
| 3 | 3 | 2 | Puka Nacua | LA to LAR | 1.753 | 0.009 | -0.009 | 0 | 0.00 | Active, depth 1 | stable blend |
| 4 | 4 | 8 | Rashee Rice | KC to KC | 1.682 | 0.048 | 0.002 | 0 | 0.00 | Active, Questionable, depth 1 | stable blend |
| 5 | 2 | 1 | Jaxon Smith-Njigba | SEA to SEA | 1.639 | -0.263 | 0.004 | 0 | 0.00 | Active, depth 1 | two-year blend drag |
| 6 | 6 | 13 | Davante Adams | LA to LAR | 1.552 | 0.059 | 0.001 | 0 | 0.00 | Active, depth 2 | stable blend |
| 7 | 7 | 5 | Drake London | ATL to ATL | 1.513 | 0.091 | 0.015 | 0 | 0.00 | Active, Questionable, depth 1 | stable blend |
| 8 | n/a | 18 | Malik Nabers | NYG to NYG | 1.384 | n/a | n/a | 0 | 0.00 | Active, Questionable, depth 1 | carry-forward restored |
| 9 | 15 | 7 | A.J. Brown | PHI to NE | 1.299 | 0.204 | -0.001 | 1 | 0.03 | Active, depth 1 | team/role context |
| 10 | 13 | 9 | Justin Jefferson | MIN to MIN | 1.282 | 0.200 | 0.004 | 0 | 0.00 | Active, depth 1 | two-year blend lift |
| 11 | 9 | 11 | George Pickens | DAL to DAL | 1.236 | -0.010 | -0.003 | 0 | 0.00 | Active, depth 2 | stable blend |
| 12 | 10 | 15 | Nico Collins | HST to HOU | 1.192 | 0.086 | -0.004 | 0 | 0.00 | Active, depth 1 | stable blend |
| 13 | 11 | 14 | CeeDee Lamb | DAL to DAL | 1.164 | 0.069 | 0.008 | 0 | 0.00 | Active, depth 1 | stable blend |
| 14 | 14 | 10 | Garrett Wilson | NYJ to NYJ | 1.124 | 0.076 | 0.027 | 0 | 0.00 | Active, depth 1 | stable blend |
| 15 | 8 | 6 | Chris Olave | NO to NO | 1.057 | -0.207 | -0.016 | 0 | 0.00 | Active, depth 1 | two-year blend drag |
| 16 | 12 | 12 | Zay Flowers | BLT to BAL | 1.017 | -0.069 | 0.004 | 0 | 0.00 | Active, depth 1 | stable blend |
| 17 | 17 | 16 | Tetairoa McMillan | CAR to CAR | 1.002 | 0.017 | 0.004 | 0 | 0.00 | Active, Questionable, depth 1 | stable blend |
| 18 | 26 | 24 | Tee Higgins | CIN to CIN | 0.993 | 0.288 | -0.004 | 0 | 0.00 | Active, depth 2 | two-year blend lift |
| 19 | 29 | 29 | Mike Evans | TB to SF | 0.948 | 0.201 | 0.015 | 1 | 0.03 | Active, depth 1 | team/role context |
| 20 | 21 | 25 | Courtland Sutton | DEN to DEN | 0.946 | 0.135 | 0.002 | 0 | 0.00 | Active, depth 2 | stable blend |
| 21 | 25 | 21 | Terry McLaurin | WAS to WAS | 0.864 | 0.140 | 0.020 | 0 | 0.00 | Active, depth 1 | stable blend |
| 22 | 16 | 17 | Wan'Dale Robinson | NYG to TEN | 0.854 | -0.109 | 0.006 | -1 | 0.00 | Active, depth 2 | team/role context |
| 23 | 27 | 20 | DeVonta Smith | PHI to PHI | 0.835 | 0.135 | -0.006 | 0 | 0.00 | Active, depth 1 | stable blend |
| 24 | 20 | 26 | Emeka Egbuka | TB to TB | 0.827 | 0.007 | 0.004 | 0 | 0.00 | Active, depth 1 | stable blend |
| 25 | 19 | 34 | DK Metcalf | PIT to PIT | 0.786 | -0.043 | 0.004 | 0 | 0.00 | Active, depth 1 | stable blend |
| 26 | 18 | 19 | Rome Odunze | CHI to CHI | 0.770 | -0.089 | 0.015 | 0 | 0.00 | Active, depth 1 | stable blend |
| 27 | n/a | n/a | Tyreek Hill | MIA to unknown | 0.765 | n/a | n/a | 0 | 0.00 | Active, Questionable, depth  | carry-forward restored |
| 28 | 24 | 30 | Quentin Johnston | LAC to LAC | 0.752 | 0.019 | 0.008 | 0 | 0.00 | Active, depth 2 | stable blend |
| 29 | 36 | 35 | Ladd McConkey | LAC to LAC | 0.741 | 0.117 | 0.004 | 0 | 0.00 | Active, Questionable, depth 1 | stable blend |
| 30 | 22 | 22 | Jaylen Waddle | MIA to DEN | 0.707 | -0.138 | 0.001 | 1 | 0.03 | Active, depth 1 | team/role context |
| 31 | 28 | 37 | Jauan Jennings | SF to MIN | 0.705 | 0.106 | 0.004 | -1 | -0.03 | Active, depth 3 | team/role context |
| 32 | 33 | 27 | Jameson Williams | DET to DET | 0.703 | 0.070 | -0.001 | 0 | 0.00 | Active, depth 2 | stable blend |
| 33 | 31 | 36 | Romeo Doubs | GB to NE | 0.691 | -0.013 | -0.004 | 1 | 0.00 | Active, depth 2 | team/role context |
| 34 | 38 | 28 | Jakobi Meyers | JAX to JAX | 0.685 | 0.093 | 0.001 | 0 | 0.00 | Active, depth 3 | stable blend |
| 35 | 42 | 33 | Jordan Addison | MIN to MIN | 0.677 | 0.148 | 0.006 | 0 | 0.00 | Active, depth 2 | stable blend |
| 36 | 45 | 49 | Brian Thomas | JAX to JAX | 0.668 | 0.278 | 0.011 | 0 | 0.00 | Active, depth 1 | two-year blend lift |
| 37 | 49 | 61 | Chris Godwin | TB to TB | 0.640 | 0.389 | -0.003 | 0 | 0.00 | Active, depth 2 | two-year blend lift |
| 38 | 40 | n/a | Keenan Allen | LAC to unknown | 0.622 | 0.061 | -0.004 | 0 | 0.00 | Active, depth  | stable blend |
| 39 | 37 | n/a | Stefon Diggs | NE to unknown | 0.616 | -0.002 | -0.020 | 0 | 0.00 | Active, depth  | availability drag |
| 40 | 44 | 58 | Josh Downs | IND to IND | 0.602 | 0.205 | -0.001 | 0 | 0.00 | Active, depth 2 | two-year blend lift |

## Required Player Audits

### Malik Nabers

- Latest season: 4 games, 136 routes, 35 targets. Latest WOPR 0.610, NGT targets/game 8.84, red-zone targets/game 1.00, YPRR 1.99, EPA/target 0.593.
- Previous season: 556 routes, 170 targets, WOPR 0.687, NGT targets/game 10.40, red-zone targets/game 0.99, YPRR 2.17, EPA/target 0.617.
- Dynamic latest weight: 0.405 for opportunity and efficiency. Blended WOPR 0.656, NGT targets/game 9.77, YPRR 2.10, EPA/target 0.607.
- Latest availability is 0.235. Two-year availability is 0.429. Availability remains a separate deduction.
- Carry-forward eligibility is true. Nabers is restored from no v1 rank to v1.1 WR8, versus Current Standard WR18. Sleeper lists NYG, Active, Questionable, depth order 1.

### A.J. Brown

- Source season: PHI, 15 games, 484 routes, 121 targets, WOPR 0.542, NGT targets/game 8.07, YPRR 2.07.
- Prior season: PHI, 360 routes, 97 targets, WOPR 0.690, NGT targets/game 7.46, YPRR 3.00.
- Blended WOPR is 0.586 and blended YPRR is 2.44. The blend lifts his base score by 0.204.
- Sleeper current team is NE, Active, depth order 1. PHI environment z is -0.063 and NE is 1.761, producing situation bucket +1.
- Team adjustment is +0.05 and alpha-role adjustment is +0.03, reaching the +0.08 cap. Brown moves from old Fable WR15 to v1.1 WR9, versus Current Standard WR7.

### Other Named Reviews

| Player | v1.1 | Old | Standard | Current team | Blend effect | Availability effect | Context | Review |
|---|---:|---:|---:|---|---:|---:|---:|---|
| Rashee Rice | 4 | 4 | 8 | KC | +0.048 | +0.002 | 0.00 | Active, Questionable, depth 1. No prior qualified blend. |
| Davante Adams | 6 | 6 | 13 | LAR | +0.059 | +0.001 | 0.00 | Active, depth 2. Strong red-zone role remains the driver. |
| Chris Olave | 15 | 8 | 6 | NO | -0.207 | -0.016 | 0.00 | Two-season blend drags the current board despite solving injury carry-forward elsewhere. |
| Tee Higgins | 18 | 26 | 24 | CIN | +0.288 | -0.004 | 0.00 | Prior opportunity lifts him eight slots. |
| DK Metcalf | 25 | 19 | 34 | PIT | -0.043 | +0.004 | 0.00 | Current team is unchanged from 2025 source; depth 1. |
| Keenan Allen | 38 | 40 | n/a | unknown | +0.061 | -0.004 | 0.00 | Sleeper status Active but team/depth missing. Review flag required. |
| Stefon Diggs | 39 | 37 | n/a | unknown | -0.002 | -0.020 | 0.00 | Active, but team/depth missing. Two-year availability is 0.841. |
| Deebo Samuel | 45 | 39 | n/a | unknown | -0.030 | -0.002 | 0.00 | Outside top 40. Active, but team/depth missing. |

## Sleeper Weekly Archive

- Snapshot date: `2026-07-10`.
- Source: one live Sleeper NFL player-map fetch.
- Archived rows: 12,200.
- Duplicate `(snapshot_date, sleeper_player_id)` rows: 0.
- Same-date rerun retained exactly 12,200 rows, proving idempotency.
- `sleeper_current_player_context` refresh completed.
- `v_sleeper_player_status_changes` returns zero rows with only one snapshot. It will compare newest and previous dates after the next weekly archive.
- No Cloud Run Job or Scheduler resource was created. The future schedule remains disabled in documentation.

## Objects And Files

Research views:

- `v_wr_team_environment`
- `v_wr_fable_v11_metric_inputs`
- `v_wr_fable_v11_scored_seasons`
- `v_wr_fable_v11_backtest_prep`
- `v_wr_fable_v11_current_board`
- `v_sleeper_player_status_changes`

Research tables:

- `sleeper_current_player_context`
- `sleeper_player_snapshot_history`

Files changed for Phase 35.1C:

- the five WR v1.1 SQL view files
- `scripts/build_wr_fable_v11_layer.py`
- `scripts/run_wr_fable_v11_backtest.py`
- `scripts/build_sleeper_current_player_context.py`
- `tests/test_wr_fable_v11.py`
- `bigquery/AGENTS.md`
- `src/AGENTS.md`
- `docs/rebuild/cloud-scheduler-plan.md`
- this report

Generated local evidence under `output/` is excluded from release packaging.

## Validation Results

- Focused unit tests: 25 passed across WR Fable v1.1, WR Fable v1, and Sleeper current-context coverage.
- Python compilation passed for the WR layer builder, backtest runner, and Sleeper context builder. `compileall -q src scripts` also passed.
- `scripts/check_deployment_safety.py` passed all checks.
- BigQuery validation discovery completed through validation 245.
- The backtest prep view contains 511 rows across source seasons 2022-2024 and target seasons 2023-2025. It contains zero 2026 rows and zero duplicate player-season grains.
- Team environment coverage is 128 of 128 team-season rows with a non-null score: 32 teams in each source season from 2022 through 2025.
- The current board contains 158 rows and 158 unique players.
- Sleeper snapshot history contains 12,200 rows with zero duplicate `(snapshot_date, sleeper_player_id)` grains. The one-snapshot status-change view correctly returns zero rows.
- The historical research views contain zero Sleeper relation references. A broad text scan matched one explanatory SQL comment only. They also contain zero market, end-zone, or 2026 references.
- The active production rankings table contains zero WR Fable v1.1 rows.
- A read-only Cloud Run Job lookup found no `archive-sleeper-player-snapshot` job. Cloud Scheduler listing was unavailable because the Scheduler API is disabled. No Scheduler command that creates or enables a resource was run.
- `git diff --check` passed. Existing line-ending warnings remain informational.
- The shared worktree has 94 pre-existing or concurrent status entries. This phase did not stage, commit, revert, or package them.

## Safety And Next Step

No live ranking changed. No champion was activated. No app or job was deployed. No Scheduler resource was created. No 2026 outcome, market input, fabricated metric, Gemini call, or Pigskin chat call was used.

Recommended next work: create WR Fable v1.1A with one rule. Use WR Fable v1 for latest-season-qualified players, and use the v1.1 two-season calculation only when carry-forward eligibility is required. Keep team and alpha context visible as review flags, not score adjustments, until a better historical team-change test shows lift.


